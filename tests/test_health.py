
from fastapi.testclient import TestClient

from app.api.routes.health import check_database
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_versioned_health_includes_service_and_checks(monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.health.check_database",
        lambda: "healthy",
    )

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "HR Platform API"
    assert data["version"] == "0.1.0"
    assert data["checks"]["database"] == "healthy"
    assert data["checks"]["redis"] == "not_configured"
    assert data["checks"]["worker"] == "not_configured"
    assert data["status"] == "degraded"
