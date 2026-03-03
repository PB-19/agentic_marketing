from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # Must run before any module that reads env vars

from fastapi import FastAPI
from backend.database import engine, Base
from backend.models import user as _user_models          # noqa: F401 — registers models with Base.metadata
from backend.models import event_log as _event_log_models  # noqa: F401
from backend.models import idea_analytics as _analytics_models  # noqa: F401
from backend.routers.auth import router as auth_router
from backend.routers.research import router as research_router
from backend.routers.webpage import router as webpage_router
from backend.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — creating DB tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("DB tables ready")
    yield
    await engine.dispose()
    logger.info("DB engine disposed — shutdown complete")


app = FastAPI(title="Agentic Marketing API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(research_router)
app.include_router(webpage_router)
