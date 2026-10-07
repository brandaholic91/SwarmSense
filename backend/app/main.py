from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.internal_auth import internal_auth_middleware
from app.routers import runs, status


def create_app() -> FastAPI:
    settings = get_settings()
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"

    app = FastAPI(docs_url=docs_url, redoc_url=redoc_url)
    # Middleware registration order (innermost → outermost):
    # internal_auth (innermost) → CORS (outermost).
    # CORS is outermost so its headers are present on all responses (401 too).
    app.add_middleware(BaseHTTPMiddleware, dispatch=internal_auth_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.frontend_origin).rstrip("/")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(runs.router)
    app.include_router(status.router)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
