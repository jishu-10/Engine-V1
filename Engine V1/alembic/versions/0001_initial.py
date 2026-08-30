"""Initial Similarity Engine V1 schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-31
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("profile_completion", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "similarity_areas",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prompts",
        sa.Column("uid", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prompt_id", sa.String(length=16), nullable=False),
        sa.Column("area_id", sa.String(length=64), nullable=False),
        sa.Column("question_type", sa.String(length=32), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["similarity_areas.id"]),
        sa.PrimaryKeyConstraint("uid"),
        sa.UniqueConstraint("prompt_id", "version", name="uq_prompt_version"),
    )
    op.create_table(
        "signals",
        sa.Column("id", sa.String(length=16), nullable=False),
        sa.Column("area_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("min_value", sa.Float(), nullable=False),
        sa.Column("max_value", sa.Float(), nullable=False),
        sa.Column("version", sa.String(length=16), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["similarity_areas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "prompt_options",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("prompt_uid", sa.Integer(), nullable=False),
        sa.Column("option_key", sa.String(length=8), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["prompt_uid"], ["prompts.uid"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prompt_uid", "option_key", name="uq_option_key"),
    )
    op.create_table(
        "option_signal_mappings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("option_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["option_id"], ["prompt_options.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("option_id", "signal_id", name="uq_option_signal_mapping"),
    )
    op.create_table(
        "responses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("prompt_uid", sa.Integer(), nullable=False),
        sa.Column("selected_option_id", sa.Integer(), nullable=False),
        sa.Column("optional_text", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["prompt_uid"], ["prompts.uid"]),
        sa.ForeignKeyConstraint(["selected_option_id"], ["prompt_options.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "prompt_uid", name="uq_user_prompt_response"),
    )
    op.create_table(
        "similarity_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_a_id", sa.String(length=64), nullable=False),
        sa.Column("user_b_id", sa.String(length=64), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("evidence_coverage", sa.Float(), nullable=False),
        sa.Column("algorithm_version", sa.String(length=32), nullable=False),
        sa.Column("ontology_version", sa.String(length=16), nullable=False),
        sa.Column("mapping_version", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_a_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_b_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "signal_observations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("signal_id", sa.String(length=16), nullable=False),
        sa.Column("response_id", sa.String(length=36), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["response_id"], ["responses.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("response_id", "signal_id", name="uq_response_signal"),
    )
    op.create_table(
        "similarity_area_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("area_id", sa.String(length=64), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("coverage", sa.Float(), nullable=False),
        sa.Column("compared_signals", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["similarity_areas.id"]),
        sa.ForeignKeyConstraint(["result_id"], ["similarity_results.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("result_id", "area_id", name="uq_result_area"),
    )
    op.create_table(
        "user_signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("signal_id", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column("algorithm_version", sa.String(length=32), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "signal_id", name="uq_user_signal"),
    )
    op.create_table(
        "similarity_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("area_id", sa.String(length=64), nullable=False),
        sa.Column("signal_id", sa.String(length=16), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("person_a_response_id", sa.String(length=36), nullable=False),
        sa.Column("person_b_response_id", sa.String(length=36), nullable=False),
        sa.Column("strength", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["similarity_areas.id"]),
        sa.ForeignKeyConstraint(["person_a_response_id"], ["responses.id"]),
        sa.ForeignKeyConstraint(["person_b_response_id"], ["responses.id"]),
        sa.ForeignKeyConstraint(["result_id"], ["similarity_results.id"]),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "similarity_explanations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("result_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("generated_by", sa.String(length=64), nullable=False),
        sa.Column("llm_provider", sa.String(length=64), nullable=False),
        sa.Column("llm_prompt_version", sa.String(length=16), nullable=False),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["result_id"], ["similarity_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("similarity_explanations")
    op.drop_table("similarity_evidence")
    op.drop_table("user_signals")
    op.drop_table("similarity_area_results")
    op.drop_table("signal_observations")
    op.drop_table("similarity_results")
    op.drop_table("responses")
    op.drop_table("option_signal_mappings")
    op.drop_table("prompt_options")
    op.drop_table("signals")
    op.drop_table("prompts")
    op.drop_table("similarity_areas")
    op.drop_table("users")

