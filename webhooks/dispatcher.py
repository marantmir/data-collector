import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class WebhookDispatcher:
    def __init__(self):
        self.client = httpx.Client(timeout=10)

    def dispatch(
        self,
        event: str,
        payload: dict,
        target_url: str,
        secret: Optional[str] = None,
    ) -> bool:
        body = json.dumps({
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        })

        headers = {"Content-Type": "application/json"}

        if secret:
            signature = hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature

        try:
            response = self.client.post(target_url, content=body, headers=headers)
            response.raise_for_status()
            logger.info(f"Webhook {event} -> {target_url}: {response.status_code}")
            return True
        except Exception as e:
            logger.error(f"Webhook {event} -> {target_url} failed: {e}")
            return False


def notify_company_update(
    cnpj: str,
    changes: dict,
    webhook_url: str,
    secret: Optional[str] = None,
) -> bool:
    dispatcher = WebhookDispatcher()
    return dispatcher.dispatch(
        event="company.updated",
        payload={"cnpj": cnpj, "changes": changes},
        target_url=webhook_url,
        secret=secret,
    )


def notify_new_collection(
    spider: str,
    items_collected: int,
    webhook_url: str,
    secret: Optional[str] = None,
) -> bool:
    dispatcher = WebhookDispatcher()
    return dispatcher.dispatch(
        event="collection.completed",
        payload={"spider": spider, "items_collected": items_collected},
        target_url=webhook_url,
        secret=secret,
    )
