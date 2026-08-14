from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_root_links_to_operational_endpoints() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "EvidencePilot AI API",
        "status": "healthy",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "readiness": "/ready",
        "api_prefix": "/api/v1",
    }


def test_health_exposes_versioned_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "EvidencePilot AI API",
        "version": "1.0.0",
        "environment": "development",
    }


def test_readiness_describes_runtime_dependencies() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["dependencies"] == {
        "demo_workflow": "ready",
        "database": "in-memory",
        "document_storage": "local-test",
        "model_provider": "deterministic",
    }
