import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from app import db
from app.core.config import get_settings
from app.core.internal_auth import internal_auth_middleware
from app.routers import runs, status
from app.services import cleanup


logger = logging.getLogger("swarmsense.main")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    db.apply_schema()
    try:
        if db.seed_sample_if_missing():
            logger.info("sample run loaded from seed")
    except Exception as exc:
        # sérült seed ne állítsa meg az indulást; csak a kivétel típusa kerül a naplóba
        logger.error("sample seed failed: %s", type(exc).__name__)
    cleanup_task = asyncio.create_task(cleanup.cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


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
