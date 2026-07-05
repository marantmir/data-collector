import logging
import uuid
from typing import Any

import scrapy
from scrapy.http import Response

from config import settings

logger = logging.getLogger(__name__)


class BaseBusinessSpider(scrapy.Spider):
    custom_settings = {
        "CONCURRENT_REQUESTS": settings.crawler_concurrent_requests,
        "DOWNLOAD_DELAY": settings.crawler_download_delay,
    }

    source_id: uuid.UUID | None = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if "source_id" in kwargs:
            self.source_id = uuid.UUID(kwargs["source_id"])

    def start_requests(self) -> Any:
        raise NotImplementedError

    def parse(self, response: Response, **kwargs: Any) -> Any:
        raise NotImplementedError

    def _log_result(self, item_type: str, identifier: str, status: str = "collected") -> None:
        logger.info(f"[{self.name}] {item_type} {identifier}: {status}")
