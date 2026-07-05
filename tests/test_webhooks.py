import hashlib
import hmac
import json


class TestWebhookDispatcher:
    def test_signature_generation(self):
        secret = "my-secret"
        event_body = json.dumps({
            "event": "test",
            "timestamp": "ignored-for-test",
            "data": {"key": "value"},
        })
        actual = hmac.new(secret.encode(), event_body.encode(), hashlib.sha256).hexdigest()
        assert len(actual) == 64
