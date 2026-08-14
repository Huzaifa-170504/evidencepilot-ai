from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.config import get_settings
from app.schemas import ApiMessage, AuthUser, Memory
from app.store import get_store

router = APIRouter(tags=["memory"])


@router.get("/projects/{project_id}/memories", response_model=list[Memory])
async def list_memories(
    project_id: UUID, user: AuthUser = Depends(get_current_user)
) -> list[Memory]:
    store = get_store(get_settings())
    if not await store.get_project(user, project_id):
        raise HTTPException(status_code=404, detail="Project not found.")
    return await store.list_memories(user, project_id)


@router.delete("/memories/{memory_id}", response_model=ApiMessage)
async def delete_memory(memory_id: UUID, user: AuthUser = Depends(get_current_user)) -> ApiMessage:
    if not await get_store(get_settings()).delete_memory(user, memory_id):
        raise HTTPException(status_code=404, detail="Memory not found.")
    return ApiMessage(message="Saved memory deleted.")
