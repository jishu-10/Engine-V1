from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.seed import seed_database

# Import models so SQLAlchemy metadata is fully populated for optional local startup.
from app import models as _models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)
    if settings.seed_on_startup:
        with SessionLocal() as db:
            seed_database(db)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health", tags=["health"])
def root_health_check() -> dict[str, str]:
    return {"status": "ok"}

