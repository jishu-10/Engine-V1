from __future__ import annotations

from statistics import mean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Prompt,
    PromptOption,
    Response,
    Signal,
    SimilarityAreaResult,
    SimilarityResult,
    User,
    UserSignal,
)
from app.schemas import ValidationMetricsRead


def _distribution(values: list[float | None]) -> dict[str, float | int | None]:
    numeric = [value for value in values if value is not None]
    if not numeric:
        return {"count": 0, "min": None, "max": None, "avg": None}
    return {
        "count": len(numeric),
        "min": min(numeric),
        "max": max(numeric),
        "avg": mean(numeric),
    }


def validation_metrics(db: Session) -> ValidationMetricsRead:
    users = db.scalar(select(func.count(User.id))) or 0
    responses = db.scalar(select(func.count(Response.id))) or 0
    comparisons = db.scalar(select(func.count(SimilarityResult.id))) or 0

    answer_distributions: dict[str, Any] = {}
    prompts = db.scalars(select(Prompt).where(Prompt.is_active.is_(True)).order_by(Prompt.prompt_id)).all()
    for prompt in prompts:
        option_counts: dict[str, int] = {}
        for option in sorted(prompt.options, key=lambda item: item.display_order):
            count = db.scalar(
                select(func.count(Response.id)).where(Response.selected_option_id == option.id)
            )
            option_counts[option.option_key] = int(count or 0)
        answer_distributions[prompt.prompt_id] = option_counts

    prompt_completion = {
        prompt.prompt_id: int(
            db.scalar(
                select(func.count(func.distinct(Response.user_id))).where(
                    Response.prompt_uid == prompt.uid
                )
            )
            or 0
        )
        for prompt in prompts
    }

    signal_distributions: dict[str, Any] = {}
    signals = db.scalars(select(Signal).where(Signal.is_primary.is_(True)).order_by(Signal.id)).all()
    for signal in signals:
        values = [
            row[0]
            for row in db.execute(
                select(UserSignal.value).where(UserSignal.signal_id == signal.id)
            )
        ]
        signal_distributions[signal.id] = {
            "name": signal.name,
            **_distribution(values),
        }

    scores = [row[0] for row in db.execute(select(SimilarityResult.overall_score))]
    coverages = [row[0] for row in db.execute(select(SimilarityResult.evidence_coverage))]
    compared_signal_counts = [
        row[0]
        for row in db.execute(
            select(func.sum(SimilarityAreaResult.compared_signals)).group_by(
                SimilarityAreaResult.result_id
            )
        )
    ]

    score_distribution = _distribution(scores)
    score_distribution["compared_signals"] = _distribution(compared_signal_counts)

    return ValidationMetricsRead(
        users=int(users),
        responses=int(responses),
        comparisons=int(comparisons),
        answer_distributions=answer_distributions,
        prompt_completion=prompt_completion,
        signal_distributions=signal_distributions,
        similarity_score_distribution=score_distribution,
        evidence_coverage_distribution=_distribution(coverages),
    )

