from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.documents import router as documents_router
from app.routes.health import router as health_router
from app.routes.memories import router as memories_router
from app.routes.projects import router as projects_router
from app.routes.research import router as research_router
from app.routes.runs import router as runs_router
from app.routes.tools import router as tools_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    get_settings()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Evidence-first research orchestration API.",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(research_router, prefix=settings.api_prefix)
    application.include_router(projects_router, prefix=settings.api_prefix)
    application.include_router(documents_router, prefix=settings.api_prefix)
    application.include_router(runs_router, prefix=settings.api_prefix)
    application.include_router(memories_router, prefix=settings.api_prefix)
    application.include_router(tools_router, prefix=settings.api_prefix)
    return application


app = create_app()
