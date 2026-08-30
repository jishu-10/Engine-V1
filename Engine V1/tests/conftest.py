from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.data.prompt_config import PROMPTS
from app.db.base import Base
from app.main import app
from app.schemas import ResponseCreate
from app.seed import seed_database
from app.services.response_service import submit_response


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )
    with TestingSessionLocal() as session:
        seed_database(session)
        yield session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def answer_prompt(db: Session, user_id: str, prompt_id: str, option: str):
    return submit_response(
        db,
        ResponseCreate(
            user_id=user_id,
            prompt_id=prompt_id,
            selected_option=option,
        ),
    )


def answer_all_prompts(db: Session, user_id: str, option: str = "A") -> None:
    for prompt in PROMPTS:
        answer_prompt(db, user_id, prompt["prompt_id"], option)

