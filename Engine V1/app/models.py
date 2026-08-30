from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    profile_completion = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    responses = relationship("Response", back_populates="user", cascade="all, delete-orphan")


class SimilarityArea(Base):
    __tablename__ = "similarity_areas"

    id = Column(String(64), primary_key=True)
    name = Column(String(120), nullable=False)
    weight = Column(Float, nullable=False)
    description = Column(Text, nullable=False)

    signals = relationship("Signal", back_populates="area")
    prompts = relationship("Prompt", back_populates="area")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String(16), primary_key=True)
    area_id = Column(String(64), ForeignKey("similarity_areas.id"), nullable=False)
    name = Column(String(80), unique=True, nullable=False)
    display_name = Column(String(160), nullable=False)
    description = Column(Text, nullable=False)
    min_value = Column(Float, default=-1.0, nullable=False)
    max_value = Column(Float, default=1.0, nullable=False)
    version = Column(String(16), default="1.0", nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)

    area = relationship("SimilarityArea", back_populates="signals")
    mappings = relationship("OptionSignalMapping", back_populates="signal")


class Prompt(Base):
    __tablename__ = "prompts"
    __table_args__ = (UniqueConstraint("prompt_id", "version", name="uq_prompt_version"),)

    uid = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(String(16), nullable=False)
    area_id = Column(String(64), ForeignKey("similarity_areas.id"), nullable=False)
    question_type = Column(String(32), nullable=False)
    question_text = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    area = relationship("SimilarityArea", back_populates="prompts")
    options = relationship(
        "PromptOption",
        back_populates="prompt",
        order_by="PromptOption.display_order",
        cascade="all, delete-orphan",
    )


class PromptOption(Base):
    __tablename__ = "prompt_options"
    __table_args__ = (UniqueConstraint("prompt_uid", "option_key", name="uq_option_key"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_uid = Column(Integer, ForeignKey("prompts.uid"), nullable=False)
    option_key = Column(String(8), nullable=False)
    option_text = Column(Text, nullable=False)
    display_order = Column(Integer, nullable=False)

    prompt = relationship("Prompt", back_populates="options")
    mappings = relationship(
        "OptionSignalMapping",
        back_populates="option",
        cascade="all, delete-orphan",
    )


class OptionSignalMapping(Base):
    __tablename__ = "option_signal_mappings"
    __table_args__ = (
        UniqueConstraint("option_id", "signal_id", name="uq_option_signal_mapping"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    option_id = Column(Integer, ForeignKey("prompt_options.id"), nullable=False)
    signal_id = Column(String(16), ForeignKey("signals.id"), nullable=False)
    value = Column(Float, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    mapping_version = Column(String(16), default="1.0", nullable=False)

    option = relationship("PromptOption", back_populates="mappings")
    signal = relationship("Signal", back_populates="mappings")


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        UniqueConstraint("user_id", "prompt_uid", name="uq_user_prompt_response"),
    )

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    prompt_uid = Column(Integer, ForeignKey("prompts.uid"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("prompt_options.id"), nullable=False)
    optional_text = Column(Text, nullable=True)
    prompt_version = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    user = relationship("User", back_populates="responses")
    prompt = relationship("Prompt")
    selected_option = relationship("PromptOption")
    observations = relationship(
        "SignalObservation",
        back_populates="response",
        cascade="all, delete-orphan",
    )


class SignalObservation(Base):
    __tablename__ = "signal_observations"
    __table_args__ = (
        UniqueConstraint("response_id", "signal_id", name="uq_response_signal"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    signal_id = Column(String(16), ForeignKey("signals.id"), nullable=False)
    response_id = Column(String(36), ForeignKey("responses.id"), nullable=False)
    value = Column(Float, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    signal = relationship("Signal")
    response = relationship("Response", back_populates="observations")


class UserSignal(Base):
    __tablename__ = "user_signals"
    __table_args__ = (UniqueConstraint("user_id", "signal_id", name="uq_user_signal"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    signal_id = Column(String(16), ForeignKey("signals.id"), nullable=False)
    value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence_count = Column(Integer, nullable=False)
    algorithm_version = Column(String(32), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    signal = relationship("Signal")


class SimilarityResult(Base):
    __tablename__ = "similarity_results"

    id = Column(String(36), primary_key=True, default=new_uuid)
    user_a_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    user_b_id = Column(String(64), ForeignKey("users.id"), nullable=False)
    overall_score = Column(Float, nullable=True)
    evidence_coverage = Column(Float, nullable=False)
    algorithm_version = Column(String(32), nullable=False)
    ontology_version = Column(String(16), nullable=False)
    mapping_version = Column(String(16), nullable=False)
    prompt_versions = Column(JSON, nullable=True)
    llm_prompt_version = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    area_results = relationship(
        "SimilarityAreaResult",
        back_populates="result",
        cascade="all, delete-orphan",
    )
    evidence = relationship(
        "SimilarityEvidence",
        back_populates="result",
        cascade="all, delete-orphan",
    )
    explanations = relationship(
        "SimilarityExplanation",
        back_populates="result",
        cascade="all, delete-orphan",
    )


class SimilarityAreaResult(Base):
    __tablename__ = "similarity_area_results"
    __table_args__ = (UniqueConstraint("result_id", "area_id", name="uq_result_area"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(String(36), ForeignKey("similarity_results.id"), nullable=False)
    area_id = Column(String(64), ForeignKey("similarity_areas.id"), nullable=False)
    score = Column(Float, nullable=True)
    coverage = Column(Float, nullable=False)
    compared_signals = Column(Integer, default=0, nullable=False)

    result = relationship("SimilarityResult", back_populates="area_results")
    area = relationship("SimilarityArea")


class SimilarityEvidence(Base):
    __tablename__ = "similarity_evidence"

    id = Column(String(36), primary_key=True, default=new_uuid)
    result_id = Column(String(36), ForeignKey("similarity_results.id"), nullable=False)
    area_id = Column(String(64), ForeignKey("similarity_areas.id"), nullable=False)
    signal_id = Column(String(16), ForeignKey("signals.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    person_a_response_id = Column(String(36), ForeignKey("responses.id"), nullable=False)
    person_b_response_id = Column(String(36), ForeignKey("responses.id"), nullable=False)
    person_a_prompt_id = Column(String(16), nullable=False)
    person_a_option_key = Column(String(8), nullable=False)
    person_a_prompt_version = Column(Integer, nullable=False)
    person_b_prompt_id = Column(String(16), nullable=False)
    person_b_option_key = Column(String(8), nullable=False)
    person_b_prompt_version = Column(Integer, nullable=False)
    strength = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    result = relationship("SimilarityResult", back_populates="evidence")
    area = relationship("SimilarityArea")
    signal = relationship("Signal")
    person_a_response = relationship("Response", foreign_keys=[person_a_response_id])
    person_b_response = relationship("Response", foreign_keys=[person_b_response_id])


class SimilarityExplanation(Base):
    __tablename__ = "similarity_explanations"

    id = Column(String(36), primary_key=True, default=new_uuid)
    result_id = Column(String(36), ForeignKey("similarity_results.id"), nullable=False)
    title = Column(String(240), nullable=False)
    explanation = Column(Text, nullable=False)
    evidence_ids = Column(JSON, nullable=False)
    generated_by = Column(String(64), nullable=False)
    llm_provider = Column(String(64), nullable=False)
    llm_prompt_version = Column(String(16), nullable=False)
    raw_output = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    result = relationship("SimilarityResult", back_populates="explanations")
