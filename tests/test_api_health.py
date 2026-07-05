from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestAPIHealth:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
