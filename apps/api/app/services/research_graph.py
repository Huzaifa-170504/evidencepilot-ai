from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict
from uuid import NAMESPACE_URL, uuid5

from langgraph.graph import END, START, StateGraph

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


class ResearchState(TypedDict, total=False):
    request: ResearchRequest
    selected_agents: list[str]
    plan: list[PlanTask]
    events: list[AgentEvent]
    sources: list[Source]
    claims: list[Claim]
    evidence_chunks: list[dict[str, Any]]
    gaps: list[str]
    report: str


AGENT_ORDER = [
    "Academic Research",
    "Web Research",
    "Document Research",
    "Data Analyst",
    "Critic",
    "Fact Checker",
    "Report",
]


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def _event(
    state: ResearchState, agent: str, status: AgentStatus, summary: str, duration: int
) -> list[AgentEvent]:
    return [
        *state.get("events", []),
        AgentEvent(
            sequence=len(state.get("events", [])) + 1,
            agent=agent,
            status=status,
            summary=summary,
            duration_ms=duration,
        ),
    ]


def supervisor(state: ResearchState) -> dict[str, Any]:
    request = state["request"]
    selected = ["Academic Research", "Web Research"]
    if request.has_documents:
        selected.append("Document Research")
    if request.needs_data_analysis:
        selected.append("Data Analyst")
    selected.extend(["Critic", "Fact Checker", "Report"])
    plan: list[PlanTask] = [
        PlanTask(
            id="task_supervisor",
            title="Define scope and evidence criteria",
            agent="Supervisor",
            objective="Decompose the question, select bounded tools, and enforce the run budget.",
            status=AgentStatus.COMPLETED,
        )
    ]
    previous = "task_supervisor"
    for index, agent in enumerate(AGENT_ORDER, start=1):
        selected_agent = agent in selected
        task_id = f"task_{index}_{agent.lower().replace(' ', '_')}"
        plan.append(
            PlanTask(
                id=task_id,
                title={
                    "Academic Research": "Map primary literature",
                    "Web Research": "Inspect current implementations",
                    "Document Research": "Retrieve uploaded evidence",
                    "Data Analyst": "Analyze numeric evidence",
                    "Critic": "Challenge coverage and methods",
                    "Fact Checker": "Verify material claims",
                    "Report": "Write the referenced report",
                }[agent],
                agent=agent,
                objective=f"Execute the bounded {agent.lower()} contract.",
                status=AgentStatus.QUEUED if selected_agent else AgentStatus.SKIPPED,
                depends_on=[previous],
            )
        )
        if selected_agent:
            previous = task_id
    return {
        "selected_agents": selected,
        "plan": plan,
        "events": _event(
            state,
            "Supervisor",
            AgentStatus.COMPLETED,
            f"Selected {len(selected)} specialist stages under a fixed budget.",
            42,
        ),
    }


def academic(state: ResearchState) -> dict[str, Any]:
    sources = [
        Source(
            id="src_mamba",
            title="Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
            source_type="paper",
            url="https://arxiv.org/abs/2312.00752",
            publisher="arXiv",
            year=2023,
            authors=["Albert Gu", "Tri Dao"],
            arxiv_id="2312.00752",
        ),
        Source(
            id="src_vmamba",
            title="VMamba: Visual State Space Model",
            source_type="paper",
            url="https://arxiv.org/abs/2401.10166",
            publisher="arXiv",
            year=2024,
            arxiv_id="2401.10166",
        ),
    ]
    return {
        "sources": [*state.get("sources", []), *sources],
        "events": _event(
            state,
            "Academic Research",
            AgentStatus.COMPLETED,
            "Mapped primary selective state-space and visual architecture literature.",
            118,
        ),
    }


def web(state: ResearchState) -> dict[str, Any]:
    source = Source(
        id="src_mambayolo",
        title="Mamba-YOLO: SSMs-Based YOLO for Object Detection",
        source_type="repository",
        url="https://github.com/HZAI-ZJNU/Mamba-YOLO",
        publisher="GitHub",
        year=2024,
    )
    return {
        "sources": [*state.get("sources", []), source],
        "events": _event(
            state,
            "Web Research",
            AgentStatus.COMPLETED,
            "Normalized a current object-detection implementation and its provenance.",
            103,
        ),
    }


def document(state: ResearchState) -> dict[str, Any]:
    if "Document Research" not in state["selected_agents"]:
        return {
            "events": _event(
                state,
                "Document Research",
                AgentStatus.SKIPPED,
                "Skipped because the project has no ready uploaded document.",
                0,
            )
        }
    document_sources: list[Source] = []
    for chunk in state.get("evidence_chunks", [])[:5]:
        document_sources.append(
            Source(
                id=f"doc_{chunk.get('id', len(document_sources))}",
                title=str(chunk.get("filename", "Uploaded document")),
                source_type="document",
                publisher="User upload",
                year=datetime.now(UTC).year,
                document_id=chunk.get("document_id"),
                page_number=int(chunk.get("page_number", 1)),
                excerpt=str(chunk.get("content", ""))[:800],
            )
        )
    return {
        "sources": [*state.get("sources", []), *document_sources],
        "events": _event(
            state,
            "Document Research",
            AgentStatus.COMPLETED,
            f"Retrieved {len(document_sources)} permission-filtered PDF chunks with page anchors.",
            96,
        ),
    }


def data_analyst(state: ResearchState) -> dict[str, Any]:
    selected = "Data Analyst" in state["selected_agents"]
    return {
        "events": _event(
            state,
            "Data Analyst",
            AgentStatus.COMPLETED if selected else AgentStatus.SKIPPED,
            "Recorded a bounded numeric-analysis requirement."
            if selected
            else "Skipped because the question does not require numeric analysis.",
            51 if selected else 0,
        )
    }


def critic(state: ResearchState) -> dict[str, Any]:
    gaps = [
        "Comparisons rarely normalize hardware, input resolution, and training budget together.",
        "Ablations should separate state-space blocks from augmentation and recipe changes.",
        "Small-object, boundary-sensitive, and edge-device evidence remains limited.",
    ]
    return {
        "gaps": gaps,
        "events": _event(
            state,
            "Critic",
            AgentStatus.COMPLETED,
            "Identified three methodological gaps and constrained over-general conclusions.",
            77,
        ),
    }


def fact_checker(state: ResearchState) -> dict[str, Any]:
    claims = [
        Claim(
            id="claim_linear",
            text="Selective state-space models are designed for linear sequence scaling.",
            verdict=ClaimVerdict.VERIFIED,
            confidence=0.96,
            source_ids=["src_mamba"],
            rationale="Directly supported by the foundational architecture source.",
        ),
        Claim(
            id="claim_visual",
            text="Visual Mamba variants adapt selective scanning to two-dimensional features.",
            verdict=ClaimVerdict.VERIFIED,
            confidence=0.92,
            source_ids=["src_vmamba"],
            rationale="Supported by the primary VMamba source.",
        ),
        Claim(
            id="claim_detection",
            text="Mamba-based detection is promising, but controlled comparisons remain incomplete.",
            verdict=ClaimVerdict.PARTIAL,
            confidence=0.78,
            source_ids=["src_vmamba", "src_mambayolo"],
            rationale="Implementation evidence exists, but the ecosystem-wide comparison is incomplete.",
        ),
    ]
    return {
        "claims": claims,
        "events": _event(
            state,
            "Fact Checker",
            AgentStatus.COMPLETED,
            "Verified two material claims and labeled one broader conclusion as partial.",
            89,
        ),
    }


def report(state: ResearchState) -> dict[str, Any]:
    request = state["request"]
    document_note = ""
    document_sources = [
        source for source in state.get("sources", []) if source.source_type == "document"
    ]
    if document_sources:
        document_note = "\n\n## Uploaded evidence\n\n" + "\n".join(
            f"- {source.title}, page {source.page_number}: {source.excerpt} [{source.id}]"
            for source in document_sources[:3]
        )
    gaps = "\n".join(f"- {gap}" for gap in state.get("gaps", []))
    markdown = f"""# EvidencePilot research report

## Research question

{request.question}

## Executive finding

Selective state-space models provide a credible path to long-range visual context with linear sequence scaling. Visual variants adapt scanning for two-dimensional features, while object-detection implementations integrate these blocks into multi-scale pipelines. The strongest gap is controlled, reproducible comparison—not the absence of candidate architectures.

## Evidence synthesis

1. The foundational Mamba design introduces input-dependent selective state-space processing with linear scaling [src_mamba].
2. VMamba applies a two-dimensional selective-scan design to visual representation learning [src_vmamba].
3. Mamba-YOLO makes the object-detection direction directly inspectable and reproducible [src_mambayolo].{document_note}

## Research gaps

{gaps}

## Claim status

- **Verified:** linear sequence-scaling design [src_mamba].
- **Verified:** two-dimensional visual selective scanning [src_vmamba].
- **Partial:** broad superiority or efficiency claims across the detection ecosystem [src_vmamba, src_mambayolo].

## Limitations

- Evidence quality depends on the available sources and provider quotas.
- A partial verdict is not a rejection; it marks a claim that needs more controlled evidence.
- This system supports research review and does not replace domain-expert validation.

## Bibliography

- [src_mamba] Gu, A. and Dao, T. *Mamba: Linear-Time Sequence Modeling with Selective State Spaces*. arXiv:2312.00752 (2023).
- [src_vmamba] *VMamba: Visual State Space Model*. arXiv:2401.10166 (2024).
- [src_mambayolo] HZAI-ZJNU. *Mamba-YOLO: SSMs-Based YOLO for Object Detection* (2024).
"""
    return {
        "report": markdown,
        "events": _event(
            state,
            "Report",
            AgentStatus.COMPLETED,
            "Produced a cited report using only source identifiers present in the run ledger.",
            94,
        ),
    }


def _finish_plan(state: ResearchState) -> list[PlanTask]:
    statuses = {event.agent: event.status for event in state.get("events", [])}
    return [
        task.model_copy(update={"status": statuses.get(task.agent, task.status)})
        for task in state.get("plan", [])
    ]


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("academic", academic)
    graph.add_node("web", web)
    graph.add_node("document", document)
    graph.add_node("data_analyst", data_analyst)
    graph.add_node("critic", critic)
    graph.add_node("fact_checker", fact_checker)
    graph.add_node("report", report)
    graph.add_edge(START, "supervisor")
    graph.add_edge("supervisor", "academic")
    graph.add_edge("academic", "web")
    graph.add_edge("web", "document")
    graph.add_edge("document", "data_analyst")
    graph.add_edge("data_analyst", "critic")
    graph.add_edge("critic", "fact_checker")
    graph.add_edge("fact_checker", "report")
    graph.add_edge("report", END)
    return graph.compile()


research_graph = build_graph()


def execute_research(
    request: ResearchRequest, *, evidence_chunks: list[dict[str, Any]] | None = None
) -> ResearchRun:
    state = research_graph.invoke(
        {"request": request, "events": [], "sources": [], "evidence_chunks": evidence_chunks or []}
    )
    events = state["events"]
    sources = state["sources"]
    claims = state["claims"]
    run_id = _stable_id("run", f"{request.depth}:{request.question.lower()}")
    return ResearchRun(
        id=run_id,
        question=request.question,
        depth=request.depth,
        status=RunStatus.COMPLETED,
        created_at=datetime.now(UTC),
        plan=_finish_plan(state),
        events=events,
        sources=sources,
        claims=claims,
        metrics=RunMetrics(
            sources_found=len(sources),
            papers_analyzed=sum(source.source_type == "paper" for source in sources),
            claims_verified=sum(claim.verdict == ClaimVerdict.VERIFIED for claim in claims),
            agents_executed=sum(event.status == AgentStatus.COMPLETED for event in events),
            total_duration_ms=sum(event.duration_ms for event in events),
        ),
        report_markdown=state["report"],
        demo=True,
        limitations=[
            "Provider and retrieval coverage can be incomplete under free-tier quotas.",
            "Partial and unsupported claims remain visible rather than being silently promoted.",
        ],
        selected_agents=state["selected_agents"],
        correlation_id=run_id,
    )
