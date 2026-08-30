from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Response
from app.schemas import ResponseCreate
from app.services.response_service import submit_response
from app.services.similarity_service import compare_users, get_similarity_result
from tests.conftest import answer_all_prompts, answer_prompt


def test_evidence_references_real_responses(db_session: Session) -> None:
    answer_all_prompts(db_session, "u_a", "B")
    answer_all_prompts(db_session, "u_b", "B")

    result = compare_users(db_session, "u_a", "u_b")
    response_ids = {
        response.id
        for response in db_session.scalars(
            select(Response).where(Response.user_id.in_(["u_a", "u_b"]))
        )
    }

    assert result.evidence
    for evidence in result.evidence:
        assert evidence.person_a.response_id in response_ids
        assert evidence.person_b.response_id in response_ids
        assert evidence.similarity_score == 1.0
        assert evidence.strength == "very_high"
        assert evidence.person_a.prompt_version == 1
        assert evidence.person_b.prompt_version == 1


def test_evidence_keeps_prompt_option_snapshot_after_response_update(db_session: Session) -> None:
    answer_prompt(db_session, "snap_a", "P01", "A")
    answer_prompt(db_session, "snap_b", "P01", "B")
    result = compare_users(db_session, "snap_a", "snap_b")
    assert result.evidence[0].person_b.option == "B"

    submit_response(
        db_session,
        ResponseCreate(user_id="snap_b", prompt_id="P01", selected_option="D"),
    )
    old_fetched = get_similarity_result(db_session, result.id)
    fetched = compare_users(db_session, "snap_a", "snap_b")

    assert old_fetched.evidence[0].person_b.option == "B"
    assert fetched.evidence[0].person_b.option == "D"
