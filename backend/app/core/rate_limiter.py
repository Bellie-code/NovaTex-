import time
from fastapi import HTTPException
from app.utils.redis_client import redis_client


def rate_limit(key: str, limit: int = 5, window_seconds: int = 60):
    """
    key: user identifier (like IP or email)
    limit: max requests
    window_seconds: time window
    """

    now = int(time.time())
    redis_key = f"rate:{key}"

    count = redis_client.get(redis_key)

    if count is None:
        redis_client.set(redis_key, 1, ex=window_seconds)
        return

    count = int(count)

    if count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Try later.")

    redis_client.incr(redis_key)
