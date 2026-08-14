from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import get_current_user
from app.config import get_settings
from app.schemas import AuthUser
from app.services.research_tools import AcademicTools
from app.store import get_store

router = APIRouter(tags=["tools"])


@router.get("/projects/{project_id}/document-search")
async def search_project_documents(
    project_id: UUID,
    query: str = Query(min_length=2, max_length=500),
    limit: int = Query(default=5, ge=1, le=10),
    user: AuthUser = Depends(get_current_user),
):
    store = get_store(get_settings())
    if not await store.get_project(user, project_id):
        raise HTTPException(status_code=404, detail="Project not found.")
    return {
        "project_id": str(project_id),
        "query": query,
        "results": await store.search_chunks(user, project_id, query, limit=limit),
    }


@router.get("/academic/search")
async def search_academic_metadata(
    query: str = Query(min_length=3, max_length=300),
    limit: int = Query(default=5, ge=1, le=10),
    _: AuthUser = Depends(get_current_user),
):
    tools = AcademicTools(get_settings())
    arxiv, crossref = (
        await tools.search_arxiv(query, limit),
        await tools.search_crossref(query, limit),
    )
    return {"query": query, "arxiv": arxiv.__dict__, "crossref": crossref.__dict__}
