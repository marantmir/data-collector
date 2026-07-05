import logging

logger = logging.getLogger(__name__)


def alert_failure(spider_name: str, error: str) -> None:
    logger.error(f"[ALERT] Spider {spider_name} failed: {error}")


def alert_rate_limit(spider_name: str, url: str) -> None:
    logger.warning(f"[ALERT] Rate limit hit for {spider_name} at {url}")


def alert_data_quality(spider_name: str, field: str, message: str) -> None:
    logger.warning(f"[ALERT] Data quality issue in {spider_name}: {field} - {message}")
