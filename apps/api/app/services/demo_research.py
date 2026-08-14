from app.schemas import ResearchRequest, ResearchRun
from app.services.research_graph import execute_research


def build_demo_run(request: ResearchRequest) -> ResearchRun:
    """Return the deterministic, evidence-linked recruiter snapshot."""

    return execute_research(request)
