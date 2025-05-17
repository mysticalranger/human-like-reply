import hashlib
import time
from typing import Dict, Any, Optional, Tuple
import json

# Simple in-memory cache
cache: Dict[str, Tuple[Any, float]] = {}
CACHE_EXPIRY = 60 * 60 * 24  # 24 hours in seconds

def generate_cache_key(platform: str, post_text: str) -> str:
    """Generate a unique cache key based on platform and post text"""
    combined = f"{platform.lower()}:{post_text}"
    return hashlib.md5(combined.encode()).hexdigest()

def get_cached_reply(platform: str, post_text: str) -> Optional[str]:
    """Retrieve a cached reply if it exists and is not expired"""
    cache_key = generate_cache_key(platform, post_text)
    
    if cache_key in cache:
        cached_value, timestamp = cache[cache_key]
        
        # Check if cache is still valid
        if time.time() - timestamp < CACHE_EXPIRY:
            return cached_value
        
        # Remove expired cache entry
        del cache[cache_key]
    
    return None

def cache_reply(platform: str, post_text: str, reply: str) -> None:
    """Store a reply in the cache"""
    cache_key = generate_cache_key(platform, post_text)
    cache[cache_key] = (reply, time.time())

# Clean up expired cache entries periodically
def cleanup_cache() -> None:
    """Remove expired entries from the cache"""
    current_time = time.time()
    expired_keys = [
        key for key, (_, timestamp) in cache.items()
        if current_time - timestamp > CACHE_EXPIRY
    ]
    
    for key in expired_keys:
        del cache[key]