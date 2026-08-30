from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.prompt_config import PROMPTS
from app.models import OptionSignalMapping, Prompt, PromptOption, SignalObservation, UserSignal
from app.schemas import ResponseCreate
from app.services.response_service import submit_response


def test_seeded_mappings_match_the_spec(db_session: Session) -> None:
    for prompt_data in PROMPTS:
        prompt = db_session.scalar(
            select(Prompt).where(Prompt.prompt_id == prompt_data["prompt_id"])
        )
        assert prompt is not None
        assert prompt.question_text == prompt_data["question_text"]

        for option_data in prompt_data["options"]:
            option = db_session.scalar(
                select(PromptOption).where(
                    PromptOption.prompt_uid == prompt.uid,
                    PromptOption.option_key == option_data["key"],
                )
            )
            assert option is not None
            assert option.option_text == option_data["text"]

            actual = {
                mapping.signal_id: mapping.value
                for mapping in db_session.scalars(
                    select(OptionSignalMapping).where(
                        OptionSignalMapping.option_id == option.id
                    )
                )
            }
            assert actual == option_data["mappings"]


@pytest.mark.parametrize(
    ("prompt_id", "option_key", "expected"),
    [
        ("P04", "C", {"C01": 1.0, "C02": 0.9, "AUX02": -0.7}),
        ("P07", "C", {"L01": -0.2, "L02": 0.7, "L03": 1.0}),
        ("P09", "D", {"R03": 0.4, "R04": 0.5, "R05": 0.3, "R06": 1.0}),
    ],
)
def test_selected_options_produce_deterministic_observations(
    db_session: Session,
    prompt_id: str,
    option_key: str,
    expected: dict[str, float],
) -> None:
    response = submit_response(
        db_session,
        ResponseCreate(user_id="u_mapping", prompt_id=prompt_id, selected_option=option_key),
    )
    observations = {
        observation.signal_id: observation.value
        for observation in db_session.scalars(
            select(SignalObservation).where(SignalObservation.response_id == response.id)
        )
    }
    assert observations == expected


def test_zero_signal_is_observed_not_unknown(db_session: Session) -> None:
    submit_response(
        db_session,
        ResponseCreate(user_id="u_zero", prompt_id="P06", selected_option="B"),
    )
    depth = db_session.scalar(
        select(UserSignal).where(
            UserSignal.user_id == "u_zero",
            UserSignal.signal_id == "C06",
        )
    )
    assert depth is not None
    assert depth.value == 0.0
    assert depth.evidence_count == 1


def test_duplicate_submission_replaces_observations(db_session: Session) -> None:
    first = submit_response(
        db_session,
        ResponseCreate(user_id="u_duplicate", prompt_id="P04", selected_option="C"),
    )
    second = submit_response(
        db_session,
        ResponseCreate(user_id="u_duplicate", prompt_id="P04", selected_option="A"),
    )
    assert second.id == first.id

    observations = {
        observation.signal_id: observation.value
        for observation in db_session.scalars(
            select(SignalObservation).where(SignalObservation.response_id == second.id)
        )
    }
    assert observations == {"C01": -0.8, "C02": -0.7, "AUX02": 0.4}

