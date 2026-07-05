import json
import logging
from datetime import timedelta
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    import redis as redis_module

    redis_client = redis_module.from_url(settings.redis_url)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning("Redis indisponível, cache desativado")


def _key(cnpj: str, prefix: str = "cnpj") -> str:
    clean = "".join(c for c in cnpj if c.isdigit())
    return f"{prefix}:{clean}"


def get_cached(cnpj: str, ttl: timedelta = timedelta(hours=24)) -> Optional[dict]:
    if not REDIS_AVAILABLE:
        return None
    try:
        data = redis_client.get(_key(cnpj))
        if data:
            logger.debug(f"Cache hit: {cnpj}")
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
    return None


def set_cached(cnpj: str, data: dict, ttl: timedelta = timedelta(hours=24)) -> None:
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(_key(cnpj), int(ttl.total_seconds()), json.dumps(data, default=str))
        logger.debug(f"Cache set: {cnpj}")
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


def invalidate(cnpj: str) -> None:
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.delete(_key(cnpj))
        logger.debug(f"Cache invalidated: {cnpj}")
    except Exception as e:
        logger.warning(f"Cache delete error: {e}")
