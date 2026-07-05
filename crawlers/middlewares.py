import logging
import random
from typing import Any

from scrapy import Request, Spider
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/17.2",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
]


class RandomUserAgentMiddleware:
    def process_request(self, request: Request, spider: Spider) -> None:
        request.headers["User-Agent"] = random.choice(USER_AGENTS)


class SmartRetryMiddleware(RetryMiddleware):
    def process_response(self, request: Request, response: Any, spider: Spider) -> Any:
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            logger.warning(f"Retry {request.url} - status {response.status}")
            return self._retry(request, reason, spider) or response
        return response
