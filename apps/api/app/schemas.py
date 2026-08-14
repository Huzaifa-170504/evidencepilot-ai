from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ResearchDepth(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class ClaimVerdict(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"
    CONFLICTING = "conflicting"


class ResearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=12, max_length=2_000)
    depth: ResearchDepth = ResearchDepth.STANDARD
    project_id: UUID | None = None
    has_documents: bool = False
    needs_data_analysis: bool = False

    @field_validator("question")
    @classmethod
    def question_must_contain_words(cls, value: str) -> str:
        if len(value.split()) < 3:
            raise ValueError("question must contain at least three words")
        return value


class PlanTask(BaseModel):
    id: str
    title: str
    agent: str
    objective: str
    status: AgentStatus
    depends_on: list[str] = Field(default_factory=list)


class AgentEvent(BaseModel):
    sequence: int
    agent: str
    status: AgentStatus
    summary: str
    duration_ms: int = Field(ge=0)
    safe_metadata: dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    id: str
    title: str
    source_type: str
    url: HttpUrl | None = None
    publisher: str
    year: int
    authors: list[str] = Field(default_factory=list)
    doi: str | None = None
    arxiv_id: str | None = None
    document_id: UUID | None = None
    page_number: int | None = Field(default=None, ge=1)
    excerpt: str | None = Field(default=None, max_length=2_000)


class Claim(BaseModel):
    id: str
    text: str
    verdict: ClaimVerdict
    confidence: float = Field(ge=0, le=1)
    source_ids: list[str]
    rationale: str | None = Field(default=None, max_length=1_000)


class RunMetrics(BaseModel):
    sources_found: int = Field(ge=0)
    papers_analyzed: int = Field(ge=0)
    claims_verified: int = Field(ge=0)
    agents_executed: int = Field(ge=0)
    total_duration_ms: int = Field(ge=0)


class ResearchRun(BaseModel):
    id: str
    question: str
    depth: ResearchDepth
    status: RunStatus
    created_at: datetime
    plan: list[PlanTask]
    events: list[AgentEvent]
    sources: list[Source]
    claims: list[Claim]
    metrics: RunMetrics
    report_markdown: str
    demo: bool = True
    limitations: list[str] = Field(default_factory=list)
    selected_agents: list[str] = Field(default_factory=list)
    correlation_id: str | None = None


class AuthUser(BaseModel):
    id: UUID
    email: str | None = None
    access_token: str | None = Field(default=None, exclude=True)
    is_demo: bool = False


class Profile(BaseModel):
    id: UUID
    display_name: str | None = None
    report_preferences: dict[str, Any] = Field(default_factory=dict)
    memory_enabled: bool = True


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1_000)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1_000)


class Project(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str = ""
    is_public_demo: bool = False
    created_at: datetime
    updated_at: datetime


class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentRegister(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: str = Field(min_length=1, max_length=255)
    storage_path: str = Field(min_length=5, max_length=700)
    mime_type: str = Field(pattern=r"^application/pdf$")
    size_bytes: int = Field(gt=0, le=10 * 1024 * 1024)
    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")


class Document(BaseModel):
    id: UUID
    project_id: UUID
    owner_id: UUID
    filename: str
    storage_path: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str | None = None
    page_count: int | None = None
    status: DocumentStatus
    processing_error: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentChunk(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    page_number: int
    content: str
    section_heading: str | None = None
    char_start: int = 0
    char_end: int = 0
    score: float | None = None


class IngestionResult(BaseModel):
    document: Document
    chunk_count: int = Field(ge=0)
    possible_scan_pages: list[int] = Field(default_factory=list)


class RunCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=12, max_length=2_000)
    depth: ResearchDepth = ResearchDepth.STANDARD
    needs_data_analysis: bool = False


class Memory(BaseModel):
    id: UUID
    project_id: UUID | None = None
    owner_id: UUID
    memory_type: str
    title: str
    content: str
    enabled: bool = True
    created_at: datetime


class MessageCreate(BaseModel):
    content: str = Field(min_length=2, max_length=4_000)


class Message(BaseModel):
    id: UUID
    project_id: UUID
    owner_id: UUID
    role: str
    content: str
    created_at: datetime


class ApiMessage(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class ReadyResponse(BaseModel):
    ready: bool
    dependencies: dict[str, str]
