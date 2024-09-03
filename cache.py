import os
import json
import hashlib
import logging
from functools import wraps
from redis import asyncio as aioredis
import asyncio
import logfire

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_EXPIRATION = 6 * 30 * 24 * 60 * 60 # 6 month
CACHE_PREFIX = "llm_server:"

# Add Logfire configuration
logfire.configure(
    token=os.getenv("LOGFIRE_TOKEN"),
    send_to_logfire="if-token-present",
    scrubbing=False
)

def redis_cache(expire=CACHE_EXPIRATION):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with aioredis.from_url(REDIS_URL, encoding="utf8", decode_responses=True) as redis:
                # Generate a more readable cache key
                key_parts = [func.__name__]
                for k, v in kwargs.items():
                    if k == 'request':
                        # Hash the request body
                        request_hash = hashlib.md5(json.dumps(v, sort_keys=True).encode()).hexdigest()
                        key_parts.append(f"{k}:{request_hash}")
                    else:
                        key_parts.append(f"{k}:{v}")
                
                cache_key = f"{CACHE_PREFIX}{':'.join(key_parts)}"

                # Try to get the cached result
                cached_result = await redis.get(cache_key)
                if cached_result:
                    parsed_result = json.loads(cached_result)
                    logfire.info("Cache hit", extra={
                        "cache_key": cache_key,
                        "cached_result": parsed_result
                    })
                    return parsed_result

                # If not cached, call the function
                result = await func(*args, **kwargs)

                # Cache the result
                await asyncio.create_task(redis.setex(cache_key, expire, json.dumps(result)))
                logfire.info("Cache miss", extra={
                    "cache_key": cache_key,
                    "new_result": result
                })

            return result
        return wrapper
    return decorator