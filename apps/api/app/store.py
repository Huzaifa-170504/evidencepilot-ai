from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx

from app.config import Settings
from app.schemas import (
    AuthUser,
    Document,
    DocumentRegister,
    DocumentStatus,
    Memory,
    Project,
    ProjectCreate,
    ProjectUpdate,
    ResearchRun,
    RunStatus,
)


class StoreError(RuntimeError):
    pass


class InMemoryStore:
    def __init__(self) -> None:
        self.projects: dict[UUID, Project] = {}
        self.documents: dict[UUID, Document] = {}
        self.memories: dict[UUID, Memory] = {}
        self.chunks: dict[UUID, list[dict[str, Any]]] = {}
        self.upload_bytes: dict[UUID, bytes] = {}
        self.runs: dict[str, tuple[UUID, UUID, ResearchRun]] = {}

    async def list_projects(self, user: AuthUser) -> list[Project]:
        return [project for project in self.projects.values() if project.owner_id == user.id]

    async def create_project(self, user: AuthUser, data: ProjectCreate) -> Project:
        now = datetime.now(UTC)
        project = Project(
            id=uuid4(),
            owner_id=user.id,
            name=data.name,
            description=data.description,
            created_at=now,
            updated_at=now,
        )
        self.projects[project.id] = project
        return project

    async def get_project(self, user: AuthUser, project_id: UUID) -> Project | None:
        project = self.projects.get(project_id)
        return project if project and project.owner_id == user.id else None

    async def update_project(
        self, user: AuthUser, project_id: UUID, data: ProjectUpdate
    ) -> Project | None:
        project = await self.get_project(user, project_id)
        if not project:
            return None
        updated = project.model_copy(
            update={
                **data.model_dump(exclude_none=True),
                "updated_at": datetime.now(UTC),
            }
        )
        self.projects[project_id] = updated
        return updated

    async def delete_project(self, user: AuthUser, project_id: UUID) -> bool:
        if not await self.get_project(user, project_id):
            return False
        self.projects.pop(project_id)
        return True

    async def register_document(
        self, user: AuthUser, project_id: UUID, data: DocumentRegister
    ) -> Document:
        now = datetime.now(UTC)
        document = Document(
            id=uuid4(),
            project_id=project_id,
            owner_id=user.id,
            status=DocumentStatus.UPLOADED,
            created_at=now,
            updated_at=now,
            **data.model_dump(),
        )
        self.documents[document.id] = document
        return document

    async def list_documents(self, user: AuthUser, project_id: UUID) -> list[Document]:
        return [
            document
            for document in self.documents.values()
            if document.project_id == project_id and document.owner_id == user.id
        ]

    async def get_document(self, user: AuthUser, document_id: UUID) -> Document | None:
        document = self.documents.get(document_id)
        return document if document and document.owner_id == user.id else None

    async def update_document(self, document: Document, **values: Any) -> Document:
        updated = document.model_copy(update={**values, "updated_at": datetime.now(UTC)})
        self.documents[document.id] = updated
        return updated

    async def delete_document(self, user: AuthUser, document_id: UUID) -> bool:
        document = await self.get_document(user, document_id)
        if not document:
            return False
        self.documents.pop(document_id)
        self.chunks.pop(document_id, None)
        return True

    async def save_chunks(self, document_id: UUID, chunks: list[dict[str, Any]]) -> None:
        self.chunks[document_id] = chunks

    async def search_chunks(
        self, user: AuthUser, project_id: UUID, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        candidates: list[dict[str, Any]] = []
        for document in await self.list_documents(user, project_id):
            for chunk in self.chunks.get(document.id, []):
                text = chunk["content"].lower()
                score = sum(term in text for term in terms) / max(len(terms), 1)
                if score:
                    candidates.append({**chunk, "filename": document.filename, "score": score})
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]

    async def list_memories(self, user: AuthUser, project_id: UUID) -> list[Memory]:
        return [
            memory
            for memory in self.memories.values()
            if memory.owner_id == user.id and memory.project_id == project_id
        ]

    async def delete_memory(self, user: AuthUser, memory_id: UUID) -> bool:
        memory = self.memories.get(memory_id)
        if not memory or memory.owner_id != user.id:
            return False
        self.memories.pop(memory_id)
        return True

    async def save_upload_bytes(self, document_id: UUID, content: bytes) -> None:
        self.upload_bytes[document_id] = content

    async def download_document(self, user: AuthUser, storage_path: str) -> bytes:
        document = next(
            (
                item
                for item in self.documents.values()
                if item.storage_path == storage_path and item.owner_id == user.id
            ),
            None,
        )
        if not document or document.id not in self.upload_bytes:
            raise StoreError("Document bytes are not available in local storage.")
        return self.upload_bytes[document.id]

    async def save_run(self, user: AuthUser, project_id: UUID, run: ResearchRun) -> None:
        self.runs[run.id] = (user.id, project_id, run)

    async def get_run(self, user: AuthUser, run_id: str) -> ResearchRun | None:
        record = self.runs.get(run_id)
        return record[2] if record and record[0] == user.id else None

    async def update_run_status(
        self, user: AuthUser, run_id: str, run_status: RunStatus
    ) -> ResearchRun | None:
        record = self.runs.get(run_id)
        if not record or record[0] != user.id:
            return None
        updated = record[2].model_copy(update={"status": run_status})
        self.runs[run_id] = (record[0], record[1], updated)
        return updated


class SupabaseStore:  # pragma: no cover - exercised against a connected Supabase project
    """RLS-preserving PostgREST and Storage adapter.

    The authenticated user's JWT is forwarded to Supabase, so database policy is
    the final authorization boundary. Service-role credentials are never needed
    by browser code.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _headers(self, user: AuthUser, *, representation: bool = False) -> dict[str, str]:
        token = user.access_token or self.settings.supabase_publishable_key
        headers = {
            "apikey": self.settings.supabase_publishable_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        if representation:
            headers["Prefer"] = "return=representation"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        user: AuthUser,
        *,
        params: dict[str, str] | None = None,
        json: Any = None,
        representation: bool = False,
    ) -> Any:
        url = f"{self.settings.supabase_url}/rest/v1/{path}"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.request(
                method,
                url,
                headers=self._headers(user, representation=representation),
                params=params,
                json=json,
            )
        if response.status_code >= 400:
            raise StoreError(f"Supabase request failed ({response.status_code}).")
        return response.json() if response.content else None

    async def list_projects(self, user: AuthUser) -> list[Project]:
        rows = await self._request(
            "GET", "projects", user, params={"select": "*", "order": "updated_at.desc"}
        )
        return [Project.model_validate(row) for row in rows]

    async def create_project(self, user: AuthUser, data: ProjectCreate) -> Project:
        rows = await self._request(
            "POST",
            "projects",
            user,
            json={"owner_id": str(user.id), **data.model_dump()},
            representation=True,
        )
        return Project.model_validate(rows[0])

    async def get_project(self, user: AuthUser, project_id: UUID) -> Project | None:
        rows = await self._request(
            "GET",
            "projects",
            user,
            params={"id": f"eq.{project_id}", "select": "*", "limit": "1"},
        )
        return Project.model_validate(rows[0]) if rows else None

    async def update_project(
        self, user: AuthUser, project_id: UUID, data: ProjectUpdate
    ) -> Project | None:
        rows = await self._request(
            "PATCH",
            "projects",
            user,
            params={"id": f"eq.{project_id}"},
            json=data.model_dump(exclude_none=True),
            representation=True,
        )
        return Project.model_validate(rows[0]) if rows else None

    async def delete_project(self, user: AuthUser, project_id: UUID) -> bool:
        rows = await self._request(
            "DELETE",
            "projects",
            user,
            params={"id": f"eq.{project_id}", "select": "id"},
            representation=True,
        )
        return bool(rows)

    async def register_document(
        self, user: AuthUser, project_id: UUID, data: DocumentRegister
    ) -> Document:
        rows = await self._request(
            "POST",
            "documents",
            user,
            json={"owner_id": str(user.id), "project_id": str(project_id), **data.model_dump()},
            representation=True,
        )
        return Document.model_validate(rows[0])

    async def list_documents(self, user: AuthUser, project_id: UUID) -> list[Document]:
        rows = await self._request(
            "GET",
            "documents",
            user,
            params={"project_id": f"eq.{project_id}", "select": "*", "order": "created_at.desc"},
        )
        return [Document.model_validate(row) for row in rows]

    async def get_document(self, user: AuthUser, document_id: UUID) -> Document | None:
        rows = await self._request(
            "GET",
            "documents",
            user,
            params={"id": f"eq.{document_id}", "select": "*", "limit": "1"},
        )
        return Document.model_validate(rows[0]) if rows else None

    async def update_document(self, document: Document, **values: Any) -> Document:
        service_user = AuthUser(
            id=document.owner_id,
            access_token=self.settings.supabase_service_role_key
            or self.settings.supabase_publishable_key,
        )
        rows = await self._request(
            "PATCH",
            "documents",
            service_user,
            params={"id": f"eq.{document.id}"},
            json=values,
            representation=True,
        )
        return Document.model_validate(rows[0])

    async def delete_document(self, user: AuthUser, document_id: UUID) -> bool:
        rows = await self._request(
            "DELETE",
            "documents",
            user,
            params={"id": f"eq.{document_id}", "select": "id"},
            representation=True,
        )
        return bool(rows)

    async def download_document(self, user: AuthUser, storage_path: str) -> bytes:
        url = f"{self.settings.supabase_url}/storage/v1/object/authenticated/{self.settings.storage_bucket}/{storage_path}"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.get(url, headers=self._headers(user))
        if response.status_code >= 400:
            raise StoreError("Unable to download the private document from Supabase Storage.")
        return response.content

    async def delete_storage_object(self, user: AuthUser, storage_path: str) -> None:
        url = f"{self.settings.supabase_url}/storage/v1/object/{self.settings.storage_bucket}"
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.delete(
                url,
                headers=self._headers(user),
                json={"prefixes": [storage_path]},
            )
        if response.status_code >= 400:
            raise StoreError("Unable to delete the private storage object.")

    async def save_chunks(self, document_id: UUID, chunks: list[dict[str, Any]]) -> None:
        document_user = AuthUser(
            id=UUID(chunks[0]["owner_id"]),
            access_token=self.settings.supabase_service_role_key
            or self.settings.supabase_publishable_key,
        )
        await self._request(
            "DELETE", "document_chunks", document_user, params={"document_id": f"eq.{document_id}"}
        )
        await self._request(
            "POST", "document_chunks", document_user, json=chunks, representation=False
        )

    async def search_chunks(
        self, user: AuthUser, project_id: UUID, query: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        from app.services.embeddings import HashingEmbeddingProvider

        embedding = HashingEmbeddingProvider(self.settings.embedding_dimensions).embed(query)
        rows = await self._request(
            "POST",
            "rpc/hybrid_search_document_chunks",
            user,
            json={
                "query_text": query,
                "query_embedding": embedding,
                "target_project_id": str(project_id),
                "match_count": limit,
            },
        )
        return rows or []

    async def list_memories(self, user: AuthUser, project_id: UUID) -> list[Memory]:
        rows = await self._request(
            "GET",
            "memories",
            user,
            params={"project_id": f"eq.{project_id}", "select": "*", "order": "created_at.desc"},
        )
        return [Memory.model_validate(row) for row in rows]

    async def delete_memory(self, user: AuthUser, memory_id: UUID) -> bool:
        rows = await self._request(
            "DELETE",
            "memories",
            user,
            params={"id": f"eq.{memory_id}", "select": "id"},
            representation=True,
        )
        return bool(rows)

    async def save_run(self, user: AuthUser, project_id: UUID, run: ResearchRun) -> None:
        await self._request(
            "POST",
            "research_runs",
            user,
            json={
                "id": run.id,
                "project_id": str(project_id),
                "owner_id": str(user.id),
                "question": run.question,
                "depth": run.depth,
                "status": run.status,
                "plan": [task.model_dump(mode="json") for task in run.plan],
                "metrics": run.metrics.model_dump(mode="json"),
                "final_report_markdown": run.report_markdown,
                "snapshot": run.model_dump(mode="json"),
                "correlation_id": run.correlation_id,
                "completed_at": datetime.now(UTC).isoformat(),
            },
        )
        await self._request(
            "POST",
            "agent_tasks",
            user,
            json=[
                {
                    "run_id": run.id,
                    "project_id": str(project_id),
                    "owner_id": str(user.id),
                    "task_key": task.id,
                    "agent_name": task.agent,
                    "title": task.title,
                    "objective": task.objective,
                    "status": task.status,
                    "dependencies": task.depends_on,
                }
                for task in run.plan
            ],
        )
        await self._request(
            "POST",
            "agent_events",
            user,
            json=[
                {
                    "run_id": run.id,
                    "project_id": str(project_id),
                    "owner_id": str(user.id),
                    "sequence": event.sequence,
                    "agent_name": event.agent,
                    "status": event.status,
                    "summary": event.summary,
                    "duration_ms": event.duration_ms,
                    "safe_metadata": event.safe_metadata,
                }
                for event in run.events
            ],
        )
        await self._request(
            "POST",
            "sources",
            user,
            json=[
                {
                    "id": source.id,
                    "run_id": run.id,
                    "project_id": str(project_id),
                    "owner_id": str(user.id),
                    "title": source.title,
                    "source_type": source.source_type,
                    "url": str(source.url) if source.url else None,
                    "publisher": source.publisher,
                    "publication_year": source.year,
                    "authors": source.authors,
                    "doi": source.doi,
                    "arxiv_id": source.arxiv_id,
                    "document_id": str(source.document_id) if source.document_id else None,
                    "page_number": source.page_number,
                    "excerpt": source.excerpt,
                }
                for source in run.sources
            ],
        )
        await self._request(
            "POST",
            "claims",
            user,
            json=[
                {
                    "id": claim.id,
                    "run_id": run.id,
                    "project_id": str(project_id),
                    "owner_id": str(user.id),
                    "claim_text": claim.text,
                    "verdict": claim.verdict,
                    "confidence": claim.confidence,
                    "source_ids": claim.source_ids,
                    "rationale": claim.rationale,
                }
                for claim in run.claims
            ],
        )

    async def get_run(self, user: AuthUser, run_id: str) -> ResearchRun | None:
        rows = await self._request(
            "GET",
            "research_runs",
            user,
            params={"id": f"eq.{run_id}", "select": "snapshot", "limit": "1"},
        )
        return ResearchRun.model_validate(rows[0]["snapshot"]) if rows else None

    async def update_run_status(
        self, user: AuthUser, run_id: str, run_status: RunStatus
    ) -> ResearchRun | None:
        run = await self.get_run(user, run_id)
        if not run:
            return None
        updated = run.model_copy(update={"status": run_status})
        await self._request(
            "PATCH",
            "research_runs",
            user,
            params={"id": f"eq.{run_id}"},
            json={"status": run_status, "snapshot": updated.model_dump(mode="json")},
        )
        return updated


memory_store = InMemoryStore()


def get_store(settings: Settings) -> InMemoryStore | SupabaseStore:
    return SupabaseStore(settings) if settings.supabase_enabled else memory_store
