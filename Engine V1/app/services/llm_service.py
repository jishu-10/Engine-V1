from __future__ import annotations

import re
from typing import Protocol

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import SimilarityEvidence, SimilarityExplanation, SimilarityResult
from app.schemas import ExplanationRead


class LLMProvider(Protocol):
    def generate_similarity_explanation(
        self, evidence_payload: list[dict[str, object]]
    ) -> dict[str, object]:
        raise NotImplementedError


class ExplanationPayload(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    explanation: str = Field(min_length=1, max_length=2000)
    evidence_ids: list[str] = Field(default_factory=list)


UNSUPPORTED_TERMS = {
    "compatible",
    "compatibility",
    "relationship success",
    "mbti",
    "big five",
    "attachment style",
    "diagnose",
    "diagnosis",
    "personality type",
    "emotionally intelligent",
}


class LLMValidationError(Exception):
    """Raised when LLM output cannot be trusted for a comparison."""


class AnthropicLLMProvider:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate_similarity_explanation(
        self, evidence_payload: list[dict[str, object]]
    ) -> dict[str, object]:
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("The optional anthropic package is not installed.") from exc

        client = anthropic.Anthropic(api_key=self.api_key)
        prompt = (
            "You explain deterministic people-to-people similarity. "
            "Use only the supplied evidence. Do not calculate scores, infer traits, "
            "claim compatibility, diagnose personality, or reveal raw private answers. "
            "Return JSON with title, explanation, evidence_ids."
        )
        response = client.messages.create(
            model=self.model,
            max_tokens=500,
            system=prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Evidence: {evidence_payload}",
                }
            ],
        )
        text = response.content[0].text
        import json

        return json.loads(text)


def _configured_provider() -> LLMProvider | None:
    settings = get_settings()
    if settings.llm_provider.lower() == "anthropic" and settings.anthropic_api_key:
        return AnthropicLLMProvider(settings.anthropic_api_key, settings.anthropic_model)
    return None


def _evidence_payload(evidence: list[SimilarityEvidence]) -> list[dict[str, object]]:
    payload = []
    for item in evidence:
        payload.append(
            {
                "evidence_id": item.id,
                "area": item.area_id,
                "signal": item.signal.name,
                "signal_display_name": item.signal.display_name,
                "similarity": item.similarity_score,
                "strength": item.strength,
                "person_a_evidence": {
                    "response_id": item.person_a_response_id,
                    "prompt_id": item.person_a_prompt_id,
                    "option": item.person_a_option_key,
                    "prompt_version": item.person_a_prompt_version,
                },
                "person_b_evidence": {
                    "response_id": item.person_b_response_id,
                    "prompt_id": item.person_b_prompt_id,
                    "option": item.person_b_option_key,
                    "prompt_version": item.person_b_prompt_version,
                },
            }
        )
    return payload


def _normalized_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if len(word) >= 4:
            terms.add(word)
        if word.endswith("ness") and len(word) > 6:
            terms.add(word[:-4])
        if word.endswith("ity") and len(word) > 5:
            terms.add(word[:-3])
    return terms


def _allowed_evidence_terms(evidence: list[SimilarityEvidence]) -> set[str]:
    terms: set[str] = set()
    for item in evidence:
        terms.update(_normalized_terms(item.area_id))
        terms.update(_normalized_terms(item.area.name))
        terms.update(_normalized_terms(item.signal.name))
        terms.update(_normalized_terms(item.signal.display_name))
    return terms


def _validate_llm_output(
    raw: dict[str, object],
    evidence_ids: set[str],
    allowed_terms: set[str],
) -> ExplanationPayload:
    try:
        payload = ExplanationPayload.model_validate(raw)
    except ValidationError as exc:
        raise LLMValidationError("LLM output did not match the required schema.") from exc

    if not payload.evidence_ids:
        raise LLMValidationError("LLM output did not include evidence references.")

    if not set(payload.evidence_ids).issubset(evidence_ids):
        raise LLMValidationError("LLM output referenced evidence outside this comparison.")

    combined_text = f"{payload.title} {payload.explanation}".lower()
    if any(term in combined_text for term in UNSUPPORTED_TERMS):
        raise LLMValidationError("LLM output introduced unsupported claims.")

    if allowed_terms and not (_normalized_terms(combined_text) & allowed_terms):
        raise LLMValidationError("LLM output was not grounded in supplied evidence terms.")

    return payload


def _fallback_payload(evidence: list[SimilarityEvidence]) -> ExplanationPayload:
    if not evidence:
        return ExplanationPayload(
            title="Not enough shared evidence yet",
            explanation=(
                "There is not enough verified similarity evidence to generate a useful "
                "explanation yet. More answered prompts will improve the result."
            ),
            evidence_ids=[],
        )
    top = max(evidence, key=lambda item: item.similarity_score)
    area_name = top.area.name
    signal_name = top.signal.display_name
    return ExplanationPayload(
        title=f"Similar {signal_name.lower()}",
        explanation=(
            f"The strongest verified overlap is in {signal_name} within {area_name}. "
            "This explanation is based only on stored questionnaire evidence and does "
            "not change the deterministic similarity score."
        ),
        evidence_ids=[top.id],
    )


def generate_explanation_for_result(
    db: Session,
    result_id: str,
    *,
    use_llm: bool = False,
    provider: LLMProvider | None = None,
) -> ExplanationRead:
    result = db.get(SimilarityResult, result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Similarity result {result_id} was not found.",
        )

    settings = get_settings()
    evidence = sorted(result.evidence, key=lambda item: item.similarity_score, reverse=True)
    valid_evidence_ids = {item.id for item in evidence}
    generated_by = "fallback"
    raw_output = None
    llm_provider = "disabled"

    if use_llm:
        llm = provider or _configured_provider()
        if llm is not None and evidence:
            try:
                raw_output = llm.generate_similarity_explanation(_evidence_payload(evidence))
                payload = _validate_llm_output(
                    raw_output,
                    valid_evidence_ids,
                    _allowed_evidence_terms(evidence),
                )
                generated_by = "llm"
                llm_provider = settings.llm_provider
            except Exception:
                payload = _fallback_payload(evidence)
        else:
            payload = _fallback_payload(evidence)
    else:
        payload = _fallback_payload(evidence)

    explanation = SimilarityExplanation(
        result_id=result.id,
        title=payload.title,
        explanation=payload.explanation,
        evidence_ids=payload.evidence_ids,
        generated_by=generated_by,
        llm_provider=llm_provider,
        llm_prompt_version=settings.llm_prompt_version,
        raw_output=raw_output,
    )
    db.add(explanation)
    db.commit()
    db.refresh(explanation)
    return ExplanationRead(
        id=explanation.id,
        result_id=explanation.result_id,
        title=explanation.title,
        explanation=explanation.explanation,
        evidence_ids=list(explanation.evidence_ids),
        generated_by=explanation.generated_by,
        llm_provider=explanation.llm_provider,
        llm_prompt_version=explanation.llm_prompt_version,
        created_at=explanation.created_at,
    )
