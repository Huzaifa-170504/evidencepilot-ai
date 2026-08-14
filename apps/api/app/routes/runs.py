from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.auth import get_current_user
from app.config import get_settings
from app.rate_limit import client_key, limiter
from app.schemas import (
    AgentEvent,
    AuthUser,
    Claim,
    ResearchRequest,
    ResearchRun,
    RunCreate,
    RunStatus,
    Source,
)
from app.services.research_graph import execute_research
from app.store import StoreError, get_store

router = APIRouter(tags=["runs"])


@router.post(
    "/projects/{project_id}/runs",
    response_model=ResearchRun,
    status_code=status.HTTP_201_CREATED,
)
async def create_run(
    project_id: UUID,
    payload: RunCreate,
    request: Request,
    user: AuthUser = Depends(get_current_user),
) -> ResearchRun:
    settings = get_settings()
    store = get_store(settings)
    project = await store.get_project(user, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if user.is_demo:
        limiter.check(
            client_key(request, "research"),
            settings.max_public_runs_per_day,
            timedelta(days=1),
        )
    documents = await store.list_documents(user, project_id)
    ready_documents = [document for document in documents if document.status == "ready"]
    evidence = await store.search_chunks(user, project_id, payload.question, limit=5)
    run = execute_research(
        ResearchRequest(
            question=payload.question,
            depth=payload.depth,
            project_id=project_id,
            has_documents=bool(ready_documents),
            needs_data_analysis=payload.needs_data_analysis,
        ),
        evidence_chunks=evidence,
    ).model_copy(update={"id": f"run_{uuid4().hex}", "demo": user.is_demo})
    try:
        await store.save_run(user, project_id, run)
    except StoreError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return run


async def _run_or_404(run_id: str, user: AuthUser) -> ResearchRun:
    run = await get_store(get_settings()).get_run(user, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found.")
    return run


@router.get("/runs/{run_id}", response_model=ResearchRun)
async def get_run(run_id: str, user: AuthUser = Depends(get_current_user)) -> ResearchRun:
    return await _run_or_404(run_id, user)


@router.get("/runs/{run_id}/events", response_model=list[AgentEvent])
async def get_run_events(
    run_id: str, user: AuthUser = Depends(get_current_user)
) -> list[AgentEvent]:
    return (await _run_or_404(run_id, user)).events


@router.get("/runs/{run_id}/claims", response_model=list[Claim])
async def get_run_claims(run_id: str, user: AuthUser = Depends(get_current_user)) -> list[Claim]:
    return (await _run_or_404(run_id, user)).claims


@router.get("/runs/{run_id}/sources", response_model=list[Source])
async def get_run_sources(run_id: str, user: AuthUser = Depends(get_current_user)) -> list[Source]:
    return (await _run_or_404(run_id, user)).sources


@router.get("/runs/{run_id}/report")
async def get_run_report(
    run_id: str,
    download: bool = False,
    user: AuthUser = Depends(get_current_user),
) -> Response:
    run = await _run_or_404(run_id, user)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="evidencepilot-{run_id}.md"'
    return Response(run.report_markdown, media_type="text/markdown; charset=utf-8", headers=headers)


@router.post("/runs/{run_id}/cancel", response_model=ResearchRun)
async def cancel_run(run_id: str, user: AuthUser = Depends(get_current_user)) -> ResearchRun:
    run = await get_store(get_settings()).update_run_status(user, run_id, RunStatus.CANCELLED)
    if not run:
        raise HTTPException(status_code=404, detail="Research run not found.")
    return run


@router.post("/runs/{run_id}/resume", response_model=ResearchRun)
async def resume_run(run_id: str, user: AuthUser = Depends(get_current_user)) -> ResearchRun:
    existing = await _run_or_404(run_id, user)
    if existing.status not in {RunStatus.CANCELLED, RunStatus.FAILED}:
        return existing
    run = await get_store(get_settings()).update_run_status(user, run_id, RunStatus.RUNNING)
    assert run is not None
    return run
