from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import (
    Prompt,
    Response,
    Signal,
    SignalObservation,
    SimilarityArea,
    SimilarityAreaResult,
    SimilarityEvidence,
    SimilarityResult,
    User,
    UserSignal,
)
from app.schemas import (
    EvidenceResponseRef,
    SimilarityAreaResultRead,
    SimilarityEvidenceRead,
    SimilarityResultRead,
)
from app.services.profile_service import get_profile_completion, recalculate_user_signals


@dataclass(frozen=True)
class EvidenceCandidate:
    area_id: str
    signal_id: str
    signal_similarity: float
    person_a_response_id: str
    person_b_response_id: str


@dataclass(frozen=True)
class SignalComparison:
    signal_id: str
    area_id: str
    similarity: float
    pair_confidence: float
    evidence_candidate: EvidenceCandidate


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def calculate_signal_similarity(value_a: float, value_b: float, minimum: float = -1.0, maximum: float = 1.0) -> float:
    distance = abs(value_a - value_b)
    possible_distance = maximum - minimum
    if possible_distance <= 0:
        return 1.0
    return clamp(1.0 - (distance / possible_distance))


def _strength(score: float) -> str:
    if score >= 0.90:
        return "very_high"
    if score >= 0.80:
        return "high"
    if score >= 0.70:
        return "medium"
    return "low"


def _require_user(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} was not found.",
        )
    return user


def _observation_rows(db: Session, user_id: str, signal_id: str) -> list[SignalObservation]:
    return db.scalars(
        select(SignalObservation)
        .join(Response)
        .where(
            SignalObservation.user_id == user_id,
            SignalObservation.signal_id == signal_id,
        )
    ).all()


def _best_evidence_candidate(
    db: Session,
    user_a_id: str,
    user_b_id: str,
    signal: Signal,
    signal_similarity: float,
) -> EvidenceCandidate:
    observations_a = _observation_rows(db, user_a_id, signal.id)
    observations_b = _observation_rows(db, user_b_id, signal.id)
    if not observations_a or not observations_b:
        raise ValueError("Cannot create evidence without observations for both users.")

    best_pair = None
    best_pair_similarity = -1.0
    for observation_a in observations_a:
        for observation_b in observations_b:
            pair_similarity = calculate_signal_similarity(
                observation_a.value,
                observation_b.value,
                signal.min_value,
                signal.max_value,
            )
            if pair_similarity > best_pair_similarity:
                best_pair_similarity = pair_similarity
                best_pair = (observation_a, observation_b)

    assert best_pair is not None
    return EvidenceCandidate(
        area_id=signal.area_id,
        signal_id=signal.id,
        signal_similarity=signal_similarity,
        person_a_response_id=best_pair[0].response_id,
        person_b_response_id=best_pair[1].response_id,
    )


def _signal_comparisons(db: Session, user_a_id: str, user_b_id: str) -> list[SignalComparison]:
    signals_a = {
        item.signal_id: item
        for item in db.scalars(select(UserSignal).where(UserSignal.user_id == user_a_id))
    }
    signals_b = {
        item.signal_id: item
        for item in db.scalars(select(UserSignal).where(UserSignal.user_id == user_b_id))
    }
    common_signal_ids = sorted(set(signals_a) & set(signals_b))
    comparisons: list[SignalComparison] = []

    for signal_id in common_signal_ids:
        signal = db.get(Signal, signal_id)
        if signal is None or not signal.is_primary:
            continue
        user_signal_a = signals_a[signal_id]
        user_signal_b = signals_b[signal_id]
        similarity = calculate_signal_similarity(
            user_signal_a.value,
            user_signal_b.value,
            signal.min_value,
            signal.max_value,
        )
        pair_confidence = min(user_signal_a.confidence, user_signal_b.confidence)
        comparisons.append(
            SignalComparison(
                signal_id=signal_id,
                area_id=signal.area_id,
                similarity=similarity,
                pair_confidence=pair_confidence,
                evidence_candidate=_best_evidence_candidate(
                    db, user_a_id, user_b_id, signal, similarity
                ),
            )
        )
    return comparisons


def _area_prompt_counts(db: Session) -> dict[str, int]:
    counts: dict[str, int] = {}
    rows = db.execute(
        select(Prompt.area_id, Prompt.uid).where(Prompt.is_active.is_(True))
    ).all()
    grouped: dict[str, set[int]] = defaultdict(set)
    for area_id, prompt_uid in rows:
        grouped[area_id].add(prompt_uid)
    for area_id, prompt_ids in grouped.items():
        counts[area_id] = len(prompt_ids)
    return counts


def _area_coverage(db: Session, user_a_id: str, user_b_id: str) -> dict[str, float]:
    prompt_counts = _area_prompt_counts(db)
    completion_a = get_profile_completion(db, user_a_id)
    completion_b = get_profile_completion(db, user_b_id)
    a_by_area = {area.area_id: area.answered_prompts for area in completion_a.areas}
    b_by_area = {area.area_id: area.answered_prompts for area in completion_b.areas}
    coverage: dict[str, float] = {}
    for area_id, total in prompt_counts.items():
        answered = min(a_by_area.get(area_id, 0), b_by_area.get(area_id, 0))
        coverage[area_id] = answered / total if total else 0.0
    return coverage


def _weighted_average(items: list[tuple[float, float]]) -> float | None:
    weight_sum = sum(weight for _, weight in items if weight > 0)
    if weight_sum == 0:
        return None
    return sum(value * weight for value, weight in items if weight > 0) / weight_sum


def _select_evidence(comparisons: list[SignalComparison], limit: int = 5) -> list[SignalComparison]:
    sorted_items = sorted(comparisons, key=lambda item: item.similarity, reverse=True)
    meaningful = [item for item in sorted_items if item.similarity >= 0.70]
    return (meaningful or sorted_items)[:limit]


def _prompt_versions_snapshot(db: Session, user_a_id: str, user_b_id: str) -> dict[str, dict[str, int]]:
    snapshot: dict[str, dict[str, int]] = {"user_a": {}, "user_b": {}}
    for label, user_id in [("user_a", user_a_id), ("user_b", user_b_id)]:
        responses = db.scalars(select(Response).where(Response.user_id == user_id)).all()
        snapshot[label] = {
            response.prompt.prompt_id: response.prompt_version for response in responses
        }
    return snapshot


def compare_users(db: Session, user_a_id: str, user_b_id: str) -> SimilarityResultRead:
    if user_a_id == user_b_id:
        raise HTTPException(
            status_code=422,
            detail="A user cannot be compared with themselves.",
        )
    _require_user(db, user_a_id)
    _require_user(db, user_b_id)

    settings = get_settings()
    recalculate_user_signals(db, user_a_id)
    recalculate_user_signals(db, user_b_id)

    areas = db.scalars(select(SimilarityArea).order_by(SimilarityArea.id)).all()
    areas_by_id = {area.id: area for area in areas}
    comparisons = _signal_comparisons(db, user_a_id, user_b_id)
    comparisons_by_area: dict[str, list[SignalComparison]] = defaultdict(list)
    for comparison in comparisons:
        comparisons_by_area[comparison.area_id].append(comparison)

    coverage_by_area = _area_coverage(db, user_a_id, user_b_id)
    area_scores: dict[str, float | None] = {}
    for area in areas:
        area_comparisons = comparisons_by_area.get(area.id, [])
        weighted_items = [
            (comparison.similarity, comparison.pair_confidence)
            for comparison in area_comparisons
        ]
        area_scores[area.id] = _weighted_average(weighted_items)

    overall_items = [
        (score, areas_by_id[area_id].weight)
        for area_id, score in area_scores.items()
        if score is not None
    ]
    overall_score = _weighted_average(overall_items)
    total_area_weight = sum(area.weight for area in areas)
    evidence_coverage = (
        sum(area.weight * coverage_by_area.get(area.id, 0.0) for area in areas)
        / total_area_weight
        if total_area_weight
        else 0.0
    )

    result = SimilarityResult(
        user_a_id=user_a_id,
        user_b_id=user_b_id,
        overall_score=overall_score,
        evidence_coverage=evidence_coverage,
        algorithm_version=settings.algorithm_version,
        ontology_version=settings.ontology_version,
        mapping_version=settings.mapping_version,
        prompt_versions=_prompt_versions_snapshot(db, user_a_id, user_b_id),
        llm_prompt_version=settings.llm_prompt_version,
    )
    db.add(result)
    db.flush()

    for area in areas:
        db.add(
            SimilarityAreaResult(
                result_id=result.id,
                area_id=area.id,
                score=area_scores[area.id],
                coverage=coverage_by_area.get(area.id, 0.0),
                compared_signals=len(comparisons_by_area.get(area.id, [])),
            )
        )

    for comparison in _select_evidence(comparisons):
        candidate = comparison.evidence_candidate
        person_a_response = db.get(Response, candidate.person_a_response_id)
        person_b_response = db.get(Response, candidate.person_b_response_id)
        if person_a_response is None or person_b_response is None:
            raise ValueError("Evidence candidate referenced a missing response.")
        db.add(
            SimilarityEvidence(
                result_id=result.id,
                area_id=candidate.area_id,
                signal_id=candidate.signal_id,
                similarity_score=candidate.signal_similarity,
                person_a_response_id=candidate.person_a_response_id,
                person_b_response_id=candidate.person_b_response_id,
                person_a_prompt_id=person_a_response.prompt.prompt_id,
                person_a_option_key=person_a_response.selected_option.option_key,
                person_a_prompt_version=person_a_response.prompt_version,
                person_b_prompt_id=person_b_response.prompt.prompt_id,
                person_b_option_key=person_b_response.selected_option.option_key,
                person_b_prompt_version=person_b_response.prompt_version,
                strength=_strength(candidate.signal_similarity),
            )
        )

    db.commit()
    return get_similarity_result(db, result.id)


def _response_ref(response: Response, prompt_id: str, option_key: str, prompt_version: int) -> EvidenceResponseRef:
    return EvidenceResponseRef(
        response_id=response.id,
        prompt_id=prompt_id,
        option=option_key,
        prompt_version=prompt_version,
    )


def _serialize_evidence(evidence: SimilarityEvidence) -> SimilarityEvidenceRead:
    return SimilarityEvidenceRead(
        id=evidence.id,
        area_id=evidence.area_id,
        area_name=evidence.area.name,
        signal_id=evidence.signal_id,
        signal_name=evidence.signal.name,
        signal_display_name=evidence.signal.display_name,
        similarity_score=evidence.similarity_score,
        strength=evidence.strength,
        person_a=_response_ref(
            evidence.person_a_response,
            evidence.person_a_prompt_id,
            evidence.person_a_option_key,
            evidence.person_a_prompt_version,
        ),
        person_b=_response_ref(
            evidence.person_b_response,
            evidence.person_b_prompt_id,
            evidence.person_b_option_key,
            evidence.person_b_prompt_version,
        ),
    )


def get_similarity_result(db: Session, result_id: str) -> SimilarityResultRead:
    result = db.get(SimilarityResult, result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Similarity result {result_id} was not found.",
        )
    area_results = [
        SimilarityAreaResultRead(
            area_id=item.area_id,
            area_name=item.area.name,
            score=item.score,
            coverage=item.coverage,
            compared_signals=item.compared_signals,
        )
        for item in sorted(result.area_results, key=lambda item: item.area_id)
    ]
    evidence = [
        _serialize_evidence(item)
        for item in sorted(result.evidence, key=lambda item: item.similarity_score, reverse=True)
    ]
    return SimilarityResultRead(
        id=result.id,
        user_a_id=result.user_a_id,
        user_b_id=result.user_b_id,
        overall_score=result.overall_score,
        overall_score_percent=result.overall_score * 100 if result.overall_score is not None else None,
        evidence_coverage=result.evidence_coverage,
        evidence_coverage_percent=result.evidence_coverage * 100,
        algorithm_version=result.algorithm_version,
        ontology_version=result.ontology_version,
        mapping_version=result.mapping_version,
        prompt_versions=result.prompt_versions,
        llm_prompt_version=result.llm_prompt_version,
        created_at=result.created_at,
        area_results=area_results,
        evidence=evidence,
    )
