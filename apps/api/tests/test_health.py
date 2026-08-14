from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_exposes_versioned_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "EvidencePilot AI API",
        "version": "0.1.0",
        "environment": "development",
    }


def test_readiness_describes_phase_boundaries() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["dependencies"]["database"] == "planned-phase-2"
