from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.schemas import ResearchDepth, ResearchRequest, ResearchRun
from app.services.demo_research import build_demo_run

router = APIRouter(tags=["research"])


@router.get("/demo", response_model=ResearchRun)
def get_demo_workspace() -> ResearchRun:
    return build_demo_run(
        ResearchRequest(
            question="Compare Mamba architectures for object detection and identify research gaps",
            depth=ResearchDepth.STANDARD,
        )
    )


@router.post("/research/demo", response_model=ResearchRun, status_code=status.HTTP_201_CREATED)
def create_demo_research(request: ResearchRequest) -> ResearchRun:
    settings = get_settings()
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo research is disabled in this environment.",
        )
    return build_demo_run(request)
