import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.cost_enforcement import cost_enforcement_middleware
from app.core.internal_auth import internal_auth_middleware
from app.routers import (
    auth,
    operator,
    qualifier,
    run_sessions,
    runs,
    status,
    unsubscribe,
    waitlist,
)


def _init_sentry(dsn: str) -> None:
    """Initialize Sentry once. Idempotent — skips if already initialized."""
    if not sentry_sdk.is_initialized():
        sentry_sdk.init(dsn=dsn)


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.sentry_dsn:
        _init_sentry(str(settings.sentry_dsn))
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"

    app = FastAPI(docs_url=docs_url, redoc_url=redoc_url)
    # Middleware registration order (innermost → outermost):
    # cost_enforcement (innermost) → internal_auth → CORS (outermost).
    # CORS is outermost so its headers are present on all responses (401/402/503).
    # internal_auth fires before cost_enforcement so unauthorized callers don't
    # trigger unnecessary DB reads.
    app.add_middleware(BaseHTTPMiddleware, dispatch=cost_enforcement_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=internal_auth_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.frontend_origin).rstrip("/")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(runs.router)
    app.include_router(qualifier.router)
    app.include_router(run_sessions.router)
    app.include_router(auth.router)
    app.include_router(status.router)
    app.include_router(waitlist.router)
    app.include_router(operator.router)
    app.include_router(unsubscribe.router)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
