from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas import NextPromptRead, PromptRead
from app.services.prompt_service import get_next_prompt, get_onboarding_prompts

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/onboarding", response_model=list[PromptRead])
def onboarding_prompts(db: Session = Depends(get_db)) -> list[PromptRead]:
    return get_onboarding_prompts(db)


@router.get("/next", response_model=NextPromptRead)
def next_prompt(
    user_id: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
) -> NextPromptRead:
    return NextPromptRead(prompt=get_next_prompt(db, user_id))

