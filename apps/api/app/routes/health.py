from fastapi import APIRouter

from app.config import get_settings
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get("/ready", response_model=ReadyResponse)
def ready() -> ReadyResponse:
    settings = get_settings()
    return ReadyResponse(
        ready=True,
        dependencies={
            "demo_workflow": "ready" if settings.demo_mode else "disabled",
            "database": "planned-phase-2",
            "model_provider": "planned-phase-4",
        },
    )
