from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.config import get_settings
from app.schemas import ApiMessage, AuthUser, Project, ProjectCreate, ProjectUpdate
from app.store import StoreError, get_store

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[Project])
async def list_projects(user: AuthUser = Depends(get_current_user)) -> list[Project]:
    try:
        return await get_store(get_settings()).list_projects(user)
    except StoreError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, user: AuthUser = Depends(get_current_user)
) -> Project:
    try:
        return await get_store(get_settings()).create_project(user, payload)
    except StoreError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: UUID, user: AuthUser = Depends(get_current_user)) -> Project:
    project = await get_store(get_settings()).get_project(user, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    user: AuthUser = Depends(get_current_user),
) -> Project:
    project = await get_store(get_settings()).update_project(user, project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.delete("/{project_id}", response_model=ApiMessage)
async def delete_project(
    project_id: UUID, user: AuthUser = Depends(get_current_user)
) -> ApiMessage:
    deleted = await get_store(get_settings()).delete_project(user, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found.")
    return ApiMessage(message="Project and its owned research data were deleted.")
