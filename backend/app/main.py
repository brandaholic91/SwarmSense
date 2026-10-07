import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app import db
from app.core.config import get_settings
from app.core.internal_auth import internal_auth_middleware
from app.routers import runs, status


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    db.apply_schema()
    yield


def _setup_logging() -> None:
    """A `swarmsense.*` naplók (pl. a futásonkénti összefoglaló sor) látszódjanak.

    Az uvicorn csak a saját loggereit állítja be, a gyökér szintje WARNING marad,
    ezért az INFO sorok elvesznének. Hívásonként legfeljebb egy handler kerül fel.
    """
    logger = logging.getLogger("swarmsense")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(handler)


def create_app() -> FastAPI:
    _setup_logging()
    settings = get_settings()
    docs_url = None if settings.is_production else "/docs"
    redoc_url = None if settings.is_production else "/redoc"

    app = FastAPI(lifespan=lifespan, docs_url=docs_url, redoc_url=redoc_url)
    app.add_middleware(BaseHTTPMiddleware, dispatch=internal_auth_middleware)
    app.include_router(runs.router)
    app.include_router(status.router)

    @app.get("/")
    def read_root() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
