from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth import get_current_user
from app.config import get_settings
from app.schemas import (
    ApiMessage,
    AuthUser,
    Document,
    DocumentRegister,
    DocumentStatus,
    IngestionResult,
)
from app.security import sanitize_filename, validate_pdf_bytes
from app.services.pdf_ingestion import chunks_for_storage, parse_pdf
from app.store import InMemoryStore, StoreError, SupabaseStore, get_store

router = APIRouter(tags=["documents"])


async def _owned_project(project_id: UUID, user: AuthUser):
    store = get_store(get_settings())
    if not await store.get_project(user, project_id):
        raise HTTPException(status_code=404, detail="Project not found.")
    return store


@router.get("/projects/{project_id}/documents", response_model=list[Document])
async def list_documents(
    project_id: UUID, user: AuthUser = Depends(get_current_user)
) -> list[Document]:
    store = await _owned_project(project_id, user)
    return await store.list_documents(user, project_id)


@router.post(
    "/projects/{project_id}/documents",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
)
async def register_document(
    project_id: UUID,
    payload: DocumentRegister,
    user: AuthUser = Depends(get_current_user),
) -> Document:
    """Register a PDF uploaded directly to the private Supabase bucket."""

    store = await _owned_project(project_id, user)
    filename = sanitize_filename(payload.filename)
    expected_prefix = f"{user.id}/{project_id}/"
    if not payload.storage_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=400, detail="Storage path does not belong to this user and project."
        )
    data = payload.model_copy(update={"filename": filename})
    try:
        return await store.register_document(user, project_id, data)
    except StoreError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post(
    "/projects/{project_id}/documents/local-upload",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
)
async def local_upload_document(
    project_id: UUID,
    file: UploadFile = File(...),
    user: AuthUser = Depends(get_current_user),
) -> Document:
    """Local-only upload fallback; production browsers upload to Supabase directly."""

    settings = get_settings()
    store = await _owned_project(project_id, user)
    if isinstance(store, SupabaseStore):
        raise HTTPException(
            status_code=409,
            detail="Upload directly to the private Supabase bucket, then register its metadata.",
        )
    content = await file.read(settings.max_upload_bytes + 1)
    try:
        checksum = validate_pdf_bytes(content, max_bytes=settings.max_upload_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    filename = sanitize_filename(file.filename or "document.pdf")
    storage_path = f"{user.id}/{project_id}/local-{checksum[:12]}-{filename}"
    document = await store.register_document(
        user,
        project_id,
        DocumentRegister(
            filename=filename,
            storage_path=storage_path,
            mime_type="application/pdf",
            size_bytes=len(content),
            checksum_sha256=checksum,
        ),
    )
    assert isinstance(store, InMemoryStore)
    await store.save_upload_bytes(document.id, content)
    return document


@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: UUID, user: AuthUser = Depends(get_current_user)) -> Document:
    document = await get_store(get_settings()).get_document(user, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.post("/documents/{document_id}/ingest", response_model=IngestionResult)
async def ingest_document(
    document_id: UUID, user: AuthUser = Depends(get_current_user)
) -> IngestionResult:
    settings = get_settings()
    store = get_store(settings)
    document = await store.get_document(user, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    document = await store.update_document(
        document, status=DocumentStatus.PROCESSING, processing_error=None
    )
    try:
        content = await store.download_document(user, document.storage_path)
        parsed = parse_pdf(
            content,
            max_bytes=settings.max_upload_bytes,
            max_pages=settings.max_pdf_pages,
        )
        chunks = chunks_for_storage(
            parsed,
            document_id=str(document.id),
            project_id=str(document.project_id),
            owner_id=str(document.owner_id),
            dimensions=settings.embedding_dimensions,
        )
        await store.save_chunks(document.id, chunks)
        document = await store.update_document(
            document,
            status=DocumentStatus.READY,
            checksum_sha256=parsed.checksum_sha256,
            page_count=parsed.page_count,
        )
        return IngestionResult(
            document=document,
            chunk_count=len(chunks),
            possible_scan_pages=parsed.possible_scan_pages,
        )
    except (StoreError, ValueError) as exc:
        await store.update_document(
            document,
            status=DocumentStatus.FAILED,
            processing_error=str(exc)[:500],
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/documents/{document_id}", response_model=ApiMessage)
async def delete_document(
    document_id: UUID, user: AuthUser = Depends(get_current_user)
) -> ApiMessage:
    store = get_store(get_settings())
    document = await store.get_document(user, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    if isinstance(store, SupabaseStore):
        await store.delete_storage_object(user, document.storage_path)
    await store.delete_document(user, document_id)
    return ApiMessage(message="Document, chunks, and private storage object were deleted.")
