"""Anniversaires checklists: tables checklist + items.

Revision ID: c8d1e2f3a4b5
Revises: f7e8d9c0b1a2
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision: str = "c8d1e2f3a4b5"
down_revision: Union[str, None] = "f7e8d9c0b1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checklists_anniversaire",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("anniversaire_id", sa.Integer(), nullable=False),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("budget_total", sa.Float(), nullable=True),
        sa.Column("date_limite", sa.Date(), nullable=True),
        sa.Column("completee", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("maj_auto_le", sa.DateTime(), nullable=True),
        sa.Column("cree_le", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["anniversaire_id"], ["anniversaires_famille.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_checklists_anniversaire_anniversaire_id",
        "checklists_anniversaire",
        ["anniversaire_id"],
    )
    op.create_index(
        "ix_checklists_anniversaire_completee",
        "checklists_anniversaire",
        ["completee"],
    )

    op.create_table(
        "items_checklist_anniversaire",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("categorie", sa.String(length=50), nullable=False),
        sa.Column("libelle", sa.String(length=300), nullable=False),
        sa.Column("budget_estime", sa.Float(), nullable=True),
        sa.Column("budget_reel", sa.Float(), nullable=True),
        sa.Column("fait", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("priorite", sa.String(length=20), nullable=False, server_default="moyenne"),
        sa.Column("responsable", sa.String(length=50), nullable=True),
        sa.Column("quand", sa.String(length=20), nullable=True),
        sa.Column("source", sa.String(length=20), nullable=False, server_default="manuel"),
        sa.Column("score_pertinence", sa.Float(), nullable=True),
        sa.Column("raison_suggestion", sa.Text(), nullable=True),
        sa.Column("ordre", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cree_le", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["checklist_id"], ["checklists_anniversaire.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_items_checklist_anniversaire_checklist_id",
        "items_checklist_anniversaire",
        ["checklist_id"],
    )
    op.create_index(
        "ix_items_checklist_anniversaire_categorie",
        "items_checklist_anniversaire",
        ["categorie"],
    )
    op.create_index(
        "ix_items_checklist_anniversaire_fait",
        "items_checklist_anniversaire",
        ["fait"],
    )
    op.create_index(
        "ix_items_checklist_anniversaire_source",
        "items_checklist_anniversaire",
        ["source"],
    )


def downgrade() -> None:
    op.drop_index("ix_items_checklist_anniversaire_source", table_name="items_checklist_anniversaire")
    op.drop_index("ix_items_checklist_anniversaire_fait", table_name="items_checklist_anniversaire")
    op.drop_index("ix_items_checklist_anniversaire_categorie", table_name="items_checklist_anniversaire")
    op.drop_index("ix_items_checklist_anniversaire_checklist_id", table_name="items_checklist_anniversaire")
    op.drop_table("items_checklist_anniversaire")

    op.drop_index("ix_checklists_anniversaire_completee", table_name="checklists_anniversaire")
    op.drop_index("ix_checklists_anniversaire_anniversaire_id", table_name="checklists_anniversaire")
    op.drop_table("checklists_anniversaire")
