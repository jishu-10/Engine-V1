from __future__ import annotations

from math import isclose

from sqlalchemy.orm import Session

from app.services.similarity_service import (
    _weighted_average,
    calculate_signal_similarity,
    compare_users,
)
from app.services.user_service import create_user
from tests.conftest import answer_all_prompts, answer_prompt


def test_signal_similarity_boundaries() -> None:
    assert calculate_signal_similarity(0.8, 0.8) == 1.0
    assert calculate_signal_similarity(-1.0, 1.0) == 0.0
    assert calculate_signal_similarity(-1.0, 0.0) == 0.5
    assert isclose(calculate_signal_similarity(0.8, 0.6), 0.9)


def test_identical_profiles_score_one_with_full_coverage(db_session: Session) -> None:
    answer_all_prompts(db_session, "u_a", "A")
    answer_all_prompts(db_session, "u_b", "A")

    result = compare_users(db_session, "u_a", "u_b")

    assert result.overall_score == 1.0
    assert result.evidence_coverage == 1.0
    assert len(result.evidence) == 5
    assert all(area.score == 1.0 for area in result.area_results)


def test_partial_profiles_exclude_missing_signals(db_session: Session) -> None:
    answer_prompt(db_session, "u_a", "P01", "A")
    answer_prompt(db_session, "u_a", "P02", "A")
    answer_prompt(db_session, "u_b", "P01", "D")

    result = compare_users(db_session, "u_a", "u_b")

    values = next(area for area in result.area_results if area.area_id == "values_priorities")
    communication = next(area for area in result.area_results if area.area_id == "communication_social")
    assert values.compared_signals == 1
    assert isclose(values.score or 0, 0.1)
    assert communication.score is None
    assert result.overall_score == values.score
    assert {item.signal_id for item in result.evidence} == {"V01"}


def test_zero_values_compare_as_real_values(db_session: Session) -> None:
    answer_prompt(db_session, "u_a", "P06", "B")
    answer_prompt(db_session, "u_b", "P06", "B")

    result = compare_users(db_session, "u_a", "u_b")
    communication = next(area for area in result.area_results if area.area_id == "communication_social")

    assert communication.compared_signals == 2
    assert communication.score == 1.0
    assert result.overall_score == 1.0


def test_opposite_signal_boundary_is_not_treated_as_compatibility(db_session: Session) -> None:
    answer_prompt(db_session, "u_a", "P03", "A")
    answer_prompt(db_session, "u_b", "P03", "D")

    result = compare_users(db_session, "u_a", "u_b")

    values = next(area for area in result.area_results if area.area_id == "values_priorities")
    assert values.compared_signals == 2
    assert values.score == 0.0
    assert result.overall_score == 0.0


def test_both_partially_completed_profiles_compare_only_overlap(db_session: Session) -> None:
    answer_prompt(db_session, "partial_a", "P01", "A")
    answer_prompt(db_session, "partial_a", "P04", "C")
    answer_prompt(db_session, "partial_b", "P04", "B")
    answer_prompt(db_session, "partial_b", "P09", "A")

    result = compare_users(db_session, "partial_a", "partial_b")

    communication = next(area for area in result.area_results if area.area_id == "communication_social")
    values = next(area for area in result.area_results if area.area_id == "values_priorities")
    connection = next(area for area in result.area_results if area.area_id == "connection_style")
    assert communication.compared_signals == 2
    assert communication.score is not None
    assert values.score is None
    assert connection.score is None
    assert {item.area_id for item in result.evidence} == {"communication_social"}


def test_no_comparable_signals_returns_null_similarity_not_zero(db_session: Session) -> None:
    create_user(db_session, "empty_a")
    create_user(db_session, "empty_b")

    result = compare_users(db_session, "empty_a", "empty_b")

    assert result.overall_score is None
    assert result.overall_score_percent is None
    assert result.evidence_coverage == 0.0
    assert result.evidence == []
    assert all(area.score is None for area in result.area_results)


def test_missing_signal_is_absent_rather_than_artificial_zero(db_session: Session) -> None:
    answer_prompt(db_session, "missing_a", "P01", "A")
    answer_prompt(db_session, "missing_b", "P02", "A")

    result = compare_users(db_session, "missing_a", "missing_b")

    assert result.overall_score is None
    assert result.evidence == []
    assert all(area.compared_signals == 0 for area in result.area_results)


def test_confidence_weighted_average_handles_different_weights() -> None:
    assert _weighted_average([(1.0, 1.0), (0.0, 3.0)]) == 0.25
    assert _weighted_average([(0.5, 0.0), (1.0, 0.0)]) is None


def test_auxiliary_signals_do_not_affect_primary_similarity(db_session: Session) -> None:
    answer_prompt(db_session, "aux_a", "P04", "B")
    answer_prompt(db_session, "aux_b", "P04", "B")

    result = compare_users(db_session, "aux_a", "aux_b")

    assert result.overall_score == 1.0
    assert {item.signal_id for item in result.evidence} == {"C01", "C02"}
    assert "AUX02" not in {item.signal_id for item in result.evidence}


def test_similarity_result_records_version_metadata(db_session: Session) -> None:
    answer_prompt(db_session, "version_a", "P01", "A")
    answer_prompt(db_session, "version_b", "P01", "B")

    result = compare_users(db_session, "version_a", "version_b")

    assert result.algorithm_version == "similarity_v1"
    assert result.ontology_version == "1.0"
    assert result.mapping_version == "1.0"
    assert result.llm_prompt_version == "1.0"
    assert result.prompt_versions == {
        "user_a": {"P01": 1},
        "user_b": {"P01": 1},
    }
