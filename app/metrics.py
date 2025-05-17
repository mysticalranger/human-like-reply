import time
from datetime import datetime
import json
import os
from typing import Dict, List, Any
import asyncio
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("metrics.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("reply_metrics")

# In-memory metrics store
metrics_store: Dict[str, Any] = {
    "requests": 0,
    "cache_hits": 0,
    "generation_times": [],
    "platform_counts": {"linkedin": 0, "twitter": 0, "instagram": 0},
    "error_count": 0,
    "hourly_usage": {},
    "avg_reply_length": 0,
    "total_reply_length": 0
}

async def log_request(platform: str, post_text: str, cached: bool, start_time: float, end_time: float, 
                      reply_length: int, error: bool = False) -> None:
    """Log metrics for a request"""
    current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
    generation_time = end_time - start_time
    
    # Update metrics
    metrics_store["requests"] += 1
    
    if cached:
        metrics_store["cache_hits"] += 1
    
    if not error:
        metrics_store["generation_times"].append(generation_time)
        metrics_store["platform_counts"][platform] += 1
        metrics_store["total_reply_length"] += reply_length
        metrics_store["avg_reply_length"] = metrics_store["total_reply_length"] / (metrics_store["requests"] - metrics_store["error_count"])
    else:
        metrics_store["error_count"] += 1
    
    # Update hourly usage
    if current_hour not in metrics_store["hourly_usage"]:
        metrics_store["hourly_usage"][current_hour] = 0
    metrics_store["hourly_usage"][current_hour] += 1
    
    # Log detailed request info
    logger.info(
        f"Request - Platform: {platform}, Cached: {cached}, "
        f"Time: {generation_time:.2f}s, Length: {reply_length}, Error: {error}"
    )
    
    # Periodically save metrics to disk
    if metrics_store["requests"] % 10 == 0:
        await save_metrics()

async def save_metrics() -> None:
    """Save metrics to disk"""
    try:
        with open("reply_metrics.json", "w") as f:
            json.dump(metrics_store, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save metrics: {e}")

def get_metrics_summary() -> Dict[str, Any]:
    """Get a summary of current metrics"""
    total_requests = metrics_store["requests"]
    cache_hit_rate = (metrics_store["cache_hits"] / total_requests) * 100 if total_requests > 0 else 0
    avg_time = sum(metrics_store["generation_times"]) / len(metrics_store["generation_times"]) if metrics_store["generation_times"] else 0
    
    return {
        "total_requests": total_requests,
        "cache_hit_rate": f"{cache_hit_rate:.1f}%",
        "avg_generation_time": f"{avg_time:.2f}s",
        "platform_distribution": metrics_store["platform_counts"],
        "error_rate": f"{(metrics_store['error_count'] / total_requests * 100):.1f}%" if total_requests > 0 else "0%",
        "avg_reply_length": int(metrics_store["avg_reply_length"])
    }