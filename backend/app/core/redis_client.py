from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_redis: Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        retry_on_timeout=True,
    )
    try:
        await _redis.ping()
        logger.info("Redis connected: %s", settings.redis_url)
    except RedisError as exc:
        logger.warning("Redis unavailable — caching disabled: %s", exc)
        await _redis.aclose()
        _redis = None


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
        logger.info("Redis connection closed")


def get_redis() -> Redis | None:
    return _redis
