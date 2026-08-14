from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid5

from app.schemas import (
    AgentEvent,
    AgentStatus,
    Claim,
    ClaimVerdict,
    PlanTask,
    ResearchRequest,
    ResearchRun,
    RunMetrics,
    RunStatus,
    Source,
)


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def build_demo_run(request: ResearchRequest) -> ResearchRun:
    """Return a deterministic, evidence-linked research run for Phase 1."""

    run_id = _stable_id("run", f"{request.depth}:{request.question.lower()}")
    sources = [
        Source(
            id="src_mamba",
            title="Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
            source_type="paper",
            url="https://arxiv.org/abs/2312.00752",
            publisher="arXiv",
            year=2023,
        ),
        Source(
            id="src_vmamba",
            title="VMamba: Visual State Space Model",
            source_type="paper",
            url="https://arxiv.org/abs/2401.10166",
            publisher="arXiv",
            year=2024,
        ),
        Source(
            id="src_mambayolo",
            title="Mamba-YOLO: SSMs-Based YOLO for Object Detection",
            source_type="repository",
            url="https://github.com/HZAI-ZJNU/Mamba-YOLO",
            publisher="GitHub",
            year=2024,
        ),
    ]
    plan = [
        PlanTask(
            id="task_plan",
            title="Define research scope",
            agent="Supervisor",
            objective="Decompose the question and select bounded specialist tasks.",
            status=AgentStatus.COMPLETED,
        ),
        PlanTask(
            id="task_academic",
            title="Map foundational literature",
            agent="Academic Research",
            objective="Identify primary Mamba and visual state-space sources.",
            status=AgentStatus.COMPLETED,
        ),
        PlanTask(
            id="task_web",
            title="Inspect implementations",
            agent="Web Research",
            objective="Compare implementation evidence and object-detection adaptations.",
            status=AgentStatus.COMPLETED,
        ),
        PlanTask(
            id="task_document",
            title="Search uploaded documents",
            agent="Document Research",
            objective="Retrieve project PDFs when available.",
            status=AgentStatus.SKIPPED,
        ),
        PlanTask(
            id="task_critic",
            title="Challenge conclusions",
            agent="Critic",
            objective="Find unsupported generalizations and missing comparisons.",
            status=AgentStatus.COMPLETED,
        ),
        PlanTask(
            id="task_verify",
            title="Verify material claims",
            agent="Fact Checker",
            objective="Link every material statement to stored evidence.",
            status=AgentStatus.COMPLETED,
        ),
    ]
    events = [
        AgentEvent(
            sequence=1,
            agent="Supervisor",
            status=AgentStatus.COMPLETED,
            summary="Created a five-stage plan and skipped document retrieval because no PDF was supplied.",
            duration_ms=180,
        ),
        AgentEvent(
            sequence=2,
            agent="Academic Research",
            status=AgentStatus.COMPLETED,
            summary="Mapped selective state-space foundations and visual adaptations.",
            duration_ms=420,
        ),
        AgentEvent(
            sequence=3,
            agent="Web Research",
            status=AgentStatus.COMPLETED,
            summary="Collected an object-detection implementation and normalized source metadata.",
            duration_ms=360,
        ),
        AgentEvent(
            sequence=4,
            agent="Critic",
            status=AgentStatus.COMPLETED,
            summary="Flagged the lack of uniform training budgets and hardware-normalized benchmarks.",
            duration_ms=210,
        ),
        AgentEvent(
            sequence=5,
            agent="Fact Checker",
            status=AgentStatus.COMPLETED,
            summary="Verified two core claims and marked one ecosystem-level conclusion partial.",
            duration_ms=240,
        ),
        AgentEvent(
            sequence=6,
            agent="Report",
            status=AgentStatus.COMPLETED,
            summary="Produced an evidence-linked technical brief with explicit limitations.",
            duration_ms=290,
        ),
    ]
    claims = [
        Claim(
            id="claim_linear",
            text="Selective state-space models are designed to scale linearly with sequence length.",
            verdict=ClaimVerdict.VERIFIED,
            confidence=0.96,
            source_ids=["src_mamba"],
        ),
        Claim(
            id="claim_visual",
            text="Visual Mamba variants adapt state-space scanning to two-dimensional visual features.",
            verdict=ClaimVerdict.VERIFIED,
            confidence=0.92,
            source_ids=["src_vmamba"],
        ),
        Claim(
            id="claim_detection",
            text="Mamba-based detection is promising, but comparisons are not yet uniform across compute budgets.",
            verdict=ClaimVerdict.PARTIAL,
            confidence=0.78,
            source_ids=["src_vmamba", "src_mambayolo"],
        ),
    ]
    report = f"""# Research brief

## Question

{request.question}

## Executive finding

Mamba-style selective state-space models offer a credible route to long-range visual context with linear sequence scaling. Visual adaptations change how features are scanned in two dimensions, while detection projects integrate those blocks into multi-scale pipelines. The strongest open gap is not the absence of models; it is the absence of uniformly controlled comparisons across training recipes, hardware, input resolution, and deployment latency.

## Evidence

1. The foundational selective state-space design motivates input-dependent sequence processing with linear scaling [src_mamba].
2. VMamba demonstrates a visual state-space design organized around two-dimensional selective scanning [src_vmamba].
3. Mamba-YOLO provides an object-detection implementation that makes the research direction directly testable [src_mambayolo].

## Research gaps

- Hardware-normalized latency and memory comparisons against modern convolutional and attention baselines.
- Ablations that isolate state-space blocks from augmentation and training-recipe improvements.
- Boundary-sensitive and small-object evaluation for detection and segmentation.
- Reproducible deployment studies on edge hardware.

## Limitations

This Phase 1 response is deterministic mock evidence used to validate product contracts. Live discovery, PDF retrieval, and provider-backed verification arrive in later phases.
"""
    return ResearchRun(
        id=run_id,
        question=request.question,
        depth=request.depth,
        status=RunStatus.COMPLETED,
        created_at=datetime.now(UTC),
        plan=plan,
        events=events,
        sources=sources,
        claims=claims,
        metrics=RunMetrics(
            sources_found=len(sources),
            papers_analyzed=2,
            claims_verified=2,
            agents_executed=6,
            total_duration_ms=sum(event.duration_ms for event in events),
        ),
        report_markdown=report,
    )
