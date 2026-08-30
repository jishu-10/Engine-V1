from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.llm_service import generate_explanation_for_result
from app.services.similarity_service import compare_users
from tests.conftest import answer_prompt


class GoodProvider:
    def generate_similarity_explanation(self, evidence_payload):
        return {
            "title": "You both lean toward honesty",
            "explanation": "You both show a similar truth/honesty orientation in the supplied evidence.",
            "evidence_ids": [evidence_payload[0]["evidence_id"]],
        }


class BadEvidenceProvider:
    def generate_similarity_explanation(self, evidence_payload):
        return {
            "title": "Looks grounded",
            "explanation": "This references an evidence id from nowhere.",
            "evidence_ids": ["not_real"],
        }


class MissingEvidenceProvider:
    def generate_similarity_explanation(self, evidence_payload):
        return {
            "title": "Honesty overlap",
            "explanation": "This omits evidence references.",
            "evidence_ids": [],
        }


class GenericUngroundedProvider:
    def generate_similarity_explanation(self, evidence_payload):
        return {
            "title": "You two align",
            "explanation": "There is a meaningful similarity here.",
            "evidence_ids": [evidence_payload[0]["evidence_id"]],
        }


class UnsupportedClaimProvider:
    def generate_similarity_explanation(self, evidence_payload):
        return {
            "title": "You are compatible",
            "explanation": "This makes a compatibility claim that V1 does not support.",
            "evidence_ids": [evidence_payload[0]["evidence_id"]],
        }


class FailingProvider:
    def generate_similarity_explanation(self, evidence_payload):
        raise RuntimeError("provider failed")


def _result_id(db_session: Session) -> str:
    answer_prompt(db_session, "llm_a", "P01", "A")
    answer_prompt(db_session, "llm_b", "P01", "B")
    return compare_users(db_session, "llm_a", "llm_b").id


def test_valid_llm_output_is_stored(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=GoodProvider(),
    )

    assert explanation.generated_by == "llm"
    assert explanation.evidence_ids


def test_malformed_evidence_reference_falls_back(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=BadEvidenceProvider(),
    )

    assert explanation.generated_by == "fallback"
    assert explanation.evidence_ids


def test_missing_evidence_reference_falls_back(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=MissingEvidenceProvider(),
    )

    assert explanation.generated_by == "fallback"


def test_generic_ungrounded_claim_falls_back(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=GenericUngroundedProvider(),
    )

    assert explanation.generated_by == "fallback"


def test_unsupported_claim_falls_back(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=UnsupportedClaimProvider(),
    )

    assert explanation.generated_by == "fallback"
    assert "compatibility" not in explanation.explanation.lower()


def test_provider_failure_falls_back(db_session: Session) -> None:
    result_id = _result_id(db_session)
    explanation = generate_explanation_for_result(
        db_session,
        result_id,
        use_llm=True,
        provider=FailingProvider(),
    )

    assert explanation.generated_by == "fallback"
