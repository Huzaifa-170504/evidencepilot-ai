from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_demo_run_is_complete_and_evidence_linked() -> None:
    response = client.post(
        "/api/v1/research/demo",
        json={
            "question": "Compare Mamba models for modern object detection",
            "depth": "standard",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    source_ids = {source["id"] for source in payload["sources"]}
    cited_ids = {source_id for claim in payload["claims"] for source_id in claim["source_ids"]}

    assert payload["status"] == "completed"
    assert payload["metrics"]["agents_executed"] == 6
    assert cited_ids <= source_ids
    assert any(task["status"] == "skipped" for task in payload["plan"])
    assert "Phase 1" in payload["report_markdown"]


def test_research_question_validation() -> None:
    response = client.post(
        "/api/v1/research/demo",
        json={"question": "Mamba?", "depth": "quick"},
    )

    assert response.status_code == 422
