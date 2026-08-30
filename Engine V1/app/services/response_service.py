from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    OptionSignalMapping,
    Prompt,
    PromptOption,
    Response,
    SignalObservation,
)
from app.schemas import ResponseCreate, ResponseRead
from app.services.profile_service import recalculate_user_signals
from app.services.user_service import get_or_create_user


def _find_active_prompt(db: Session, prompt_id: str) -> Prompt:
    prompt = db.scalar(
        select(Prompt).where(Prompt.prompt_id == prompt_id, Prompt.is_active.is_(True))
    )
    if prompt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active prompt {prompt_id} was not found.",
        )
    return prompt


def _find_option(db: Session, prompt: Prompt, option_key: str) -> PromptOption:
    option = db.scalar(
        select(PromptOption).where(
            PromptOption.prompt_uid == prompt.uid,
            PromptOption.option_key == option_key.upper(),
        )
    )
    if option is None:
        raise HTTPException(
            status_code=422,
            detail=f"Option {option_key} is not valid for prompt {prompt.prompt_id}.",
        )
    return option


def serialize_response(response: Response) -> ResponseRead:
    return ResponseRead(
        id=response.id,
        user_id=response.user_id,
        prompt_id=response.prompt.prompt_id,
        selected_option=response.selected_option.option_key,
        prompt_version=response.prompt_version,
        optional_text=response.optional_text,
        created_at=response.created_at,
        updated_at=response.updated_at,
    )


def submit_response(db: Session, payload: ResponseCreate) -> ResponseRead:
    user = get_or_create_user(db, payload.user_id)
    prompt = _find_active_prompt(db, payload.prompt_id)
    option = _find_option(db, prompt, payload.selected_option)

    response = db.scalar(
        select(Response).where(
            Response.user_id == user.id,
            Response.prompt_uid == prompt.uid,
        )
    )
    if response is None:
        response = Response(
            user_id=user.id,
            prompt_uid=prompt.uid,
            selected_option_id=option.id,
            prompt_version=prompt.version,
            optional_text=payload.optional_text,
        )
        db.add(response)
        db.flush()
    else:
        response.selected_option_id = option.id
        response.prompt_version = prompt.version
        response.optional_text = payload.optional_text
        db.flush()
        db.execute(delete(SignalObservation).where(SignalObservation.response_id == response.id))

    mappings = db.scalars(
        select(OptionSignalMapping).where(OptionSignalMapping.option_id == option.id)
    ).all()
    for mapping in mappings:
        db.add(
            SignalObservation(
                user_id=user.id,
                signal_id=mapping.signal_id,
                response_id=response.id,
                value=mapping.value,
                weight=mapping.weight,
            )
        )

    db.flush()
    recalculate_user_signals(db, user.id)
    db.commit()
    db.refresh(response)
    return serialize_response(response)


def get_responses(db: Session, user_id: str) -> list[ResponseRead]:
    responses = db.scalars(
        select(Response).where(Response.user_id == user_id).order_by(Response.created_at)
    ).all()
    return [serialize_response(response) for response in responses]
