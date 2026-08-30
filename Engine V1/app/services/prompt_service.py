from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Prompt, Response
from app.schemas import PromptOptionRead, PromptRead


def serialize_prompt(prompt: Prompt) -> PromptRead:
    return PromptRead(
        prompt_id=prompt.prompt_id,
        version=prompt.version,
        area_id=prompt.area_id,
        area_name=prompt.area.name,
        question_type=prompt.question_type,
        question_text=prompt.question_text,
        options=[
            PromptOptionRead(
                key=option.option_key,
                text=option.option_text,
                display_order=option.display_order,
            )
            for option in sorted(prompt.options, key=lambda item: item.display_order)
        ],
    )


def get_onboarding_prompts(db: Session) -> list[PromptRead]:
    prompts = db.scalars(
        select(Prompt)
        .options(joinedload(Prompt.area), joinedload(Prompt.options))
        .where(Prompt.is_active.is_(True))
        .order_by(Prompt.prompt_id)
    ).unique()
    return [serialize_prompt(prompt) for prompt in prompts]


def get_next_prompt(db: Session, user_id: str) -> PromptRead | None:
    answered_prompt_uids = {
        row[0]
        for row in db.execute(select(Response.prompt_uid).where(Response.user_id == user_id))
    }
    prompt = db.scalars(
        select(Prompt)
        .options(joinedload(Prompt.area), joinedload(Prompt.options))
        .where(Prompt.is_active.is_(True), Prompt.uid.not_in(answered_prompt_uids))
        .order_by(Prompt.prompt_id)
    ).first()
    return serialize_prompt(prompt) if prompt else None

