from __future__ import annotations

import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
DEMO_HEADERS = {"X-EvidencePilot-Demo": "1"}


def make_pdf() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_textbox(
        fitz.Rect(40, 40, 550, 790),
        "Mamba Object Detection Evidence\n" + "Selective state space evidence for detection. " * 80,
        fontsize=10,
    )
    content = document.tobytes()
    document.close()
    return content


def test_authentication_is_required_for_private_routes() -> None:
    response = client.get("/api/v1/projects")
    assert response.status_code == 401


def test_project_document_rag_and_run_lifecycle() -> None:
    created = client.post(
        "/api/v1/projects",
        headers=DEMO_HEADERS,
        json={"name": "PDF evidence workspace", "description": "Integration test"},
    )
    assert created.status_code == 201
    project = created.json()
    project_id = project["id"]

    listed = client.get("/api/v1/projects", headers=DEMO_HEADERS)
    assert any(item["id"] == project_id for item in listed.json())
    fetched = client.get(f"/api/v1/projects/{project_id}", headers=DEMO_HEADERS)
    assert fetched.status_code == 200
    updated = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=DEMO_HEADERS,
        json={"name": "Updated evidence workspace"},
    )
    assert updated.json()["name"] == "Updated evidence workspace"

    uploaded = client.post(
        f"/api/v1/projects/{project_id}/documents/local-upload",
        headers=DEMO_HEADERS,
        files={"file": ("paper.pdf", make_pdf(), "application/pdf")},
    )
    assert uploaded.status_code == 201
    document_id = uploaded.json()["id"]
    assert client.get(f"/api/v1/documents/{document_id}", headers=DEMO_HEADERS).status_code == 200

    ingested = client.post(f"/api/v1/documents/{document_id}/ingest", headers=DEMO_HEADERS)
    assert ingested.status_code == 200
    assert ingested.json()["document"]["status"] == "ready"
    assert ingested.json()["chunk_count"] >= 1

    documents = client.get(f"/api/v1/projects/{project_id}/documents", headers=DEMO_HEADERS)
    assert len(documents.json()) == 1
    search = client.get(
        f"/api/v1/projects/{project_id}/document-search",
        headers=DEMO_HEADERS,
        params={"query": "selective state space detection", "limit": 5},
    )
    assert search.status_code == 200
    assert search.json()["results"][0]["page_number"] == 1

    run_response = client.post(
        f"/api/v1/projects/{project_id}/runs",
        headers=DEMO_HEADERS,
        json={
            "question": "What does the uploaded paper say about Mamba object detection?",
            "depth": "standard",
        },
    )
    assert run_response.status_code == 201
    run = run_response.json()
    run_id = run["id"]
    assert "Document Research" in run["selected_agents"]
    assert any(source["source_type"] == "document" for source in run["sources"])

    assert client.get(f"/api/v1/runs/{run_id}", headers=DEMO_HEADERS).status_code == 200
    assert client.get(f"/api/v1/runs/{run_id}/events", headers=DEMO_HEADERS).json()
    assert client.get(f"/api/v1/runs/{run_id}/claims", headers=DEMO_HEADERS).json()
    assert client.get(f"/api/v1/runs/{run_id}/sources", headers=DEMO_HEADERS).json()
    report = client.get(f"/api/v1/runs/{run_id}/report?download=true", headers=DEMO_HEADERS)
    assert report.status_code == 200
    assert "attachment" in report.headers["content-disposition"]
    cancelled = client.post(f"/api/v1/runs/{run_id}/cancel", headers=DEMO_HEADERS)
    assert cancelled.json()["status"] == "cancelled"
    resumed = client.post(f"/api/v1/runs/{run_id}/resume", headers=DEMO_HEADERS)
    assert resumed.json()["status"] == "running"

    memories = client.get(f"/api/v1/projects/{project_id}/memories", headers=DEMO_HEADERS)
    assert memories.status_code == 200
    assert (
        client.delete(
            "/api/v1/memories/00000000-0000-0000-0000-000000000099", headers=DEMO_HEADERS
        ).status_code
        == 404
    )

    deleted_document = client.delete(f"/api/v1/documents/{document_id}", headers=DEMO_HEADERS)
    assert deleted_document.status_code == 200
    deleted_project = client.delete(f"/api/v1/projects/{project_id}", headers=DEMO_HEADERS)
    assert deleted_project.status_code == 200
    assert client.get(f"/api/v1/projects/{project_id}", headers=DEMO_HEADERS).status_code == 404


def test_invalid_local_upload_is_rejected() -> None:
    project = client.post(
        "/api/v1/projects", headers=DEMO_HEADERS, json={"name": "Unsafe upload test"}
    ).json()
    response = client.post(
        f"/api/v1/projects/{project['id']}/documents/local-upload",
        headers=DEMO_HEADERS,
        files={"file": ("fake.pdf", b"not really a pdf", "application/pdf")},
    )
    assert response.status_code == 400
