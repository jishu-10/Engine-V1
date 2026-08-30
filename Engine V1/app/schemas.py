from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    id: str | None = Field(default=None, max_length=64)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_completion: float
    created_at: datetime
    updated_at: datetime


class PromptOptionRead(BaseModel):
    key: str
    text: str
    display_order: int


class PromptRead(BaseModel):
    prompt_id: str
    version: int
    area_id: str
    area_name: str
    question_type: str
    question_text: str
    options: list[PromptOptionRead]


class NextPromptRead(BaseModel):
    prompt: PromptRead | None


class ResponseCreate(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    prompt_id: str = Field(min_length=1, max_length=16)
    selected_option: str = Field(min_length=1, max_length=8)
    optional_text: str | None = Field(default=None, max_length=2000)


class ResponseRead(BaseModel):
    id: str
    user_id: str
    prompt_id: str
    selected_option: str
    prompt_version: int
    optional_text: str | None
    created_at: datetime
    updated_at: datetime


class SignalRead(BaseModel):
    signal_id: str
    name: str
    display_name: str
    value: float
    confidence: float
    evidence_count: int


class AreaProfileRead(BaseModel):
    area_id: str
    area_name: str
    signals: list[SignalRead]


class CompletionAreaRead(BaseModel):
    area_id: str
    area_name: str
    answered_prompts: int
    total_prompts: int
    completion: float


class ProfileCompletionRead(BaseModel):
    user_id: str
    answered_prompts: int
    total_prompts: int
    completion: float
    areas: list[CompletionAreaRead]


class ProfileRead(BaseModel):
    user_id: str
    profile_completion: float
    areas: list[AreaProfileRead]


class SimilarityCompareRequest(BaseModel):
    user_a_id: str = Field(min_length=1, max_length=64)
    user_b_id: str = Field(min_length=1, max_length=64)


class EvidenceResponseRef(BaseModel):
    response_id: str
    prompt_id: str
    option: str
    prompt_version: int


class SimilarityEvidenceRead(BaseModel):
    id: str
    area_id: str
    area_name: str
    signal_id: str
    signal_name: str
    signal_display_name: str
    similarity_score: float
    strength: str
    person_a: EvidenceResponseRef
    person_b: EvidenceResponseRef


class SimilarityAreaResultRead(BaseModel):
    area_id: str
    area_name: str
    score: float | None
    coverage: float
    compared_signals: int


class SimilarityResultRead(BaseModel):
    id: str
    user_a_id: str
    user_b_id: str
    overall_score: float | None
    overall_score_percent: float | None
    evidence_coverage: float
    evidence_coverage_percent: float
    algorithm_version: str
    ontology_version: str
    mapping_version: str
    prompt_versions: dict[str, dict[str, int]] | None
    llm_prompt_version: str
    created_at: datetime
    area_results: list[SimilarityAreaResultRead]
    evidence: list[SimilarityEvidenceRead]


class ExplanationRequest(BaseModel):
    use_llm: bool = False


class ExplanationRead(BaseModel):
    id: str
    result_id: str
    title: str
    explanation: str
    evidence_ids: list[str]
    generated_by: str
    llm_provider: str
    llm_prompt_version: str
    created_at: datetime


class ValidationMetricsRead(BaseModel):
    users: int
    responses: int
    comparisons: int
    answer_distributions: dict[str, Any]
    prompt_completion: dict[str, Any]
    signal_distributions: dict[str, Any]
    similarity_score_distribution: dict[str, Any]
    evidence_coverage_distribution: dict[str, Any]
