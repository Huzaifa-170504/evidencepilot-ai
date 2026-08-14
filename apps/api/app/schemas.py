from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ResearchDepth(StrEnum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
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


class AgentEvent(BaseModel):
    sequence: int
    agent: str
    status: AgentStatus
    summary: str
    duration_ms: int = Field(ge=0)


class Source(BaseModel):
    id: str
    title: str
    source_type: str
    url: HttpUrl
    publisher: str
    year: int


class Claim(BaseModel):
    id: str
    text: str
    verdict: ClaimVerdict
    confidence: float = Field(ge=0, le=1)
    source_ids: list[str]


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


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


class ReadyResponse(BaseModel):
    ready: bool
    dependencies: dict[str, str]
