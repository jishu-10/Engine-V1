"""Add result version and evidence snapshots.

Revision ID: 0002_version_snapshots
Revises: 0001_initial
Create Date: 2026-08-31
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_version_snapshots"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "option_signal_mappings",
        sa.Column("mapping_version", sa.String(length=16), nullable=False, server_default="1.0"),
    )
    op.add_column("similarity_results", sa.Column("prompt_versions", sa.JSON(), nullable=True))
    op.add_column(
        "similarity_results",
        sa.Column("llm_prompt_version", sa.String(length=16), nullable=False, server_default="1.0"),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_a_prompt_id", sa.String(length=16), nullable=False, server_default=""),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_a_option_key", sa.String(length=8), nullable=False, server_default=""),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_a_prompt_version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_b_prompt_id", sa.String(length=16), nullable=False, server_default=""),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_b_option_key", sa.String(length=8), nullable=False, server_default=""),
    )
    op.add_column(
        "similarity_evidence",
        sa.Column("person_b_prompt_version", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("similarity_evidence", "person_b_prompt_version")
    op.drop_column("similarity_evidence", "person_b_option_key")
    op.drop_column("similarity_evidence", "person_b_prompt_id")
    op.drop_column("similarity_evidence", "person_a_prompt_version")
    op.drop_column("similarity_evidence", "person_a_option_key")
    op.drop_column("similarity_evidence", "person_a_prompt_id")
    op.drop_column("similarity_results", "llm_prompt_version")
    op.drop_column("similarity_results", "prompt_versions")
    op.drop_column("option_signal_mappings", "mapping_version")
