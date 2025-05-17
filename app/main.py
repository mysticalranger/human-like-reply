from fastapi import FastAPI, HTTPException
from app.models import ReplyRequest, ReplyResponse
from app.ai import generate_reply
from app.db import save_reply, setup_schema_validation
from app.cache import get_cached_reply, cache_reply, cleanup_cache
from app.metrics import log_request, get_metrics_summary
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import asyncio
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start cache cleanup task
    cleanup_task = asyncio.create_task(periodic_cache_cleanup())
    yield
    # Cancel cleanup task on shutdown
    cleanup_task.cancel()

async def periodic_cache_cleanup():
    """Periodically clean up the cache"""
    while True:
        await asyncio.sleep(3600)  # Run every hour
        cleanup_cache()

app = FastAPI(
    title="Human-like Social Media Reply Generator",
    description="Generate authentic, human-like replies to social media posts using generative AI.",
    version="0.1.0",
    lifespan=lifespan
)

def normalize_platform(platform: str) -> str:
    """Normalize platform names to standard format"""
    if platform.lower() == "insta":
        return "instagram"
    return platform

# Add a new endpoint for metrics
@app.get("/metrics", tags=["Monitoring"])
async def metrics_endpoint():
    """Get generation metrics and statistics"""
    return get_metrics_summary()

# Update your reply endpoint
@app.post("/reply", response_model=ReplyResponse, tags=["Reply Generation"])
async def reply_endpoint(request: ReplyRequest):
    """
    Generate a human-like reply to a social media post and store the request/response in the database.
    """
    start_time = time.time()
    error = False
    generated_reply = ""
    
    try:
        # Normalize platform name
        platform = normalize_platform(request.platform)
        
        # Check cache first
        cached_reply = get_cached_reply(platform, request.post_text)
        
        if cached_reply:
            # Using cached reply
            generated_reply = cached_reply
            is_cached = True
        else:
            # Generate new reply
            generated_reply = await generate_reply(platform, request.post_text)
            cache_reply(platform, request.post_text, generated_reply)
            is_cached = False
        
        timestamp = datetime.now(timezone.utc).isoformat()
        reply_record = {
            "platform": platform,
            "post_text": request.post_text,
            "generated_reply": generated_reply,
            "timestamp": timestamp,
            "cached": is_cached
        }
        
        # Only save to DB if it's a new reply
        if not is_cached:
            await save_reply(reply_record)
            
        end_time = time.time()
        # Log metrics (non-blocking)
        asyncio.create_task(log_request(
            platform=platform,
            post_text=request.post_text,
            cached=is_cached,
            start_time=start_time,
            end_time=end_time,
            reply_length=len(generated_reply)
        ))
            
        return ReplyResponse(**reply_record)
    except Exception as e:
        error = True
        end_time = time.time()
        
        # Log error metrics
        asyncio.create_task(log_request(
            platform=request.platform,
            post_text=request.post_text,
            cached=False,
            start_time=start_time,
            end_time=end_time,
            reply_length=len(generated_reply) if generated_reply else 0,
            error=True
        ))
        
        raise HTTPException(status_code=500, detail=str(e))

