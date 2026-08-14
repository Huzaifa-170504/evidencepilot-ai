from fastapi import APIRouter

from app.config import get_settings
from app.schemas import ApiRootResponse, HealthResponse, ReadyResponse

router = APIRouter(tags=["system"])


@router.get("/", response_model=ApiRootResponse, include_in_schema=False)
def root() -> ApiRootResponse:
    settings = get_settings()
    return ApiRootResponse(
        service=settings.app_name,
        status="healthy",
        version=settings.app_version,
        documentation="/docs",
        health="/health",
        readiness="/ready",
        api_prefix=settings.api_prefix,
    )


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
            "database": "supabase" if settings.supabase_enabled else "in-memory",
            "document_storage": "supabase-private" if settings.supabase_enabled else "local-test",
            "model_provider": settings.provider_mode,
        },
    )
