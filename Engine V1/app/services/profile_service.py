from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import (
    OptionSignalMapping,
    Prompt,
    Response,
    Signal,
    SignalObservation,
    SimilarityArea,
    User,
    UserSignal,
)
from app.schemas import (
    AreaProfileRead,
    CompletionAreaRead,
    ProfileCompletionRead,
    ProfileRead,
    SignalRead,
)


@dataclass(frozen=True)
class AggregatedSignal:
    signal_id: str
    value: float
    confidence: float
    evidence_count: int


def _signal_expected_observation_counts(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(OptionSignalMapping.signal_id, func.count(func.distinct(Prompt.uid)))
        .join(OptionSignalMapping.option)
        .join(Prompt)
        .join(Signal)
        .where(Prompt.is_active.is_(True), Signal.is_primary.is_(True))
        .group_by(OptionSignalMapping.signal_id)
    )
    return {signal_id: int(count) for signal_id, count in rows}


def _consistency(values: list[float]) -> float:
    if len(values) <= 1:
        return 1.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return max(0.0, min(1.0, 1.0 - variance))


def aggregate_user_signals(db: Session, user_id: str) -> list[AggregatedSignal]:
    expected_counts = _signal_expected_observation_counts(db)
    observations = db.scalars(
        select(SignalObservation)
        .join(Signal)
        .where(SignalObservation.user_id == user_id, Signal.is_primary.is_(True))
    ).all()

    grouped: dict[str, list[SignalObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.signal_id].append(observation)

    aggregated: list[AggregatedSignal] = []
    for signal_id, signal_observations in grouped.items():
        weight_sum = sum(item.weight for item in signal_observations)
        if weight_sum == 0:
            continue
        value = sum(item.value * item.weight for item in signal_observations) / weight_sum
        values = [item.value for item in signal_observations]
        evidence_count = len(signal_observations)
        max_count = max(1, expected_counts.get(signal_id, evidence_count))
        coverage = min(1.0, evidence_count / max_count)
        confidence = max(0.0, min(1.0, coverage * _consistency(values)))
        aggregated.append(
            AggregatedSignal(
                signal_id=signal_id,
                value=value,
                confidence=confidence,
                evidence_count=evidence_count,
            )
        )
    return aggregated


def recalculate_user_signals(db: Session, user_id: str) -> list[AggregatedSignal]:
    settings = get_settings()
    aggregated = aggregate_user_signals(db, user_id)
    db.execute(delete(UserSignal).where(UserSignal.user_id == user_id))
    for item in aggregated:
        db.add(
            UserSignal(
                user_id=user_id,
                signal_id=item.signal_id,
                value=item.value,
                confidence=item.confidence,
                evidence_count=item.evidence_count,
                algorithm_version=settings.algorithm_version,
            )
        )

    user = db.get(User, user_id)
    if user is not None:
        user.profile_completion = get_profile_completion(db, user_id).completion
    db.flush()
    return aggregated


def get_profile_completion(db: Session, user_id: str) -> ProfileCompletionRead:
    areas = db.scalars(select(SimilarityArea).order_by(SimilarityArea.id)).all()
    active_prompts = db.scalars(
        select(Prompt).where(Prompt.is_active.is_(True)).order_by(Prompt.prompt_id)
    ).all()
    responses = db.scalars(select(Response).where(Response.user_id == user_id)).all()
    answered_prompt_uids = {response.prompt_uid for response in responses}

    total_prompts = len(active_prompts)
    answered_prompts = len(
        {prompt.uid for prompt in active_prompts if prompt.uid in answered_prompt_uids}
    )
    area_reads: list[CompletionAreaRead] = []
    for area in areas:
        area_prompts = [prompt for prompt in active_prompts if prompt.area_id == area.id]
        area_total = len(area_prompts)
        area_answered = len(
            {prompt.uid for prompt in area_prompts if prompt.uid in answered_prompt_uids}
        )
        area_reads.append(
            CompletionAreaRead(
                area_id=area.id,
                area_name=area.name,
                answered_prompts=area_answered,
                total_prompts=area_total,
                completion=area_answered / area_total if area_total else 0.0,
            )
        )

    return ProfileCompletionRead(
        user_id=user_id,
        answered_prompts=answered_prompts,
        total_prompts=total_prompts,
        completion=answered_prompts / total_prompts if total_prompts else 0.0,
        areas=area_reads,
    )


def get_profile(db: Session, user_id: str) -> ProfileRead:
    recalculate_user_signals(db, user_id)
    completion = get_profile_completion(db, user_id)
    areas = db.scalars(select(SimilarityArea).order_by(SimilarityArea.id)).all()
    user_signals = db.scalars(
        select(UserSignal).join(Signal).where(UserSignal.user_id == user_id)
    ).all()

    by_area: dict[str, list[SignalRead]] = defaultdict(list)
    for user_signal in user_signals:
        signal = user_signal.signal
        by_area[signal.area_id].append(
            SignalRead(
                signal_id=signal.id,
                name=signal.name,
                display_name=signal.display_name,
                value=user_signal.value,
                confidence=user_signal.confidence,
                evidence_count=user_signal.evidence_count,
            )
        )

    return ProfileRead(
        user_id=user_id,
        profile_completion=completion.completion,
        areas=[
            AreaProfileRead(
                area_id=area.id,
                area_name=area.name,
                signals=sorted(by_area[area.id], key=lambda item: item.signal_id),
            )
            for area in areas
        ],
    )

