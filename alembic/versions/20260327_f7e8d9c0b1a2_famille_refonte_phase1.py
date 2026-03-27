"""Refonte module Famille — Phase 1 : nouvelles colonnes DB.

Ajoute:
- activites_famille.heure_debut (TIME)
- routines.derniere_completion (DATE)
- achats_famille.pour_qui / a_revendre / prix_revente_estime / vendu_le
- preferences_utilisateurs : 8 colonnes JSONB (tailles, style, loisirs, config_garde)

Revision ID: f7e8d9c0b1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-03-27

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "f7e8d9c0b1a2"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── activites_famille ──────────────────────────────────
    op.add_column(
        "activites_famille",
        sa.Column("heure_debut", sa.Time(), nullable=True),
    )

    # ── routines ───────────────────────────────────────────
    op.add_column(
        "routines",
        sa.Column("derniere_completion", sa.Date(), nullable=True),
    )

    # ── achats_famille ─────────────────────────────────────
    op.add_column(
        "achats_famille",
        sa.Column("pour_qui", sa.String(50), nullable=False, server_default="famille"),
    )
    op.create_index("ix_achats_famille_pour_qui", "achats_famille", ["pour_qui"])

    op.add_column(
        "achats_famille",
        sa.Column("a_revendre", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "achats_famille",
        sa.Column("prix_revente_estime", sa.Float(), nullable=True),
    )
    op.add_column(
        "achats_famille",
        sa.Column("vendu_le", sa.Date(), nullable=True),
    )

    # ── preferences_utilisateurs ───────────────────────────
    _jsonb = postgresql.JSONB(astext_type=sa.Text())

    for col_name, default in [
        ("taille_vetements_anne", "{}"),
        ("taille_vetements_mathieu", "{}"),
        ("style_achats_anne", "{}"),
        ("style_achats_mathieu", "{}"),
        ("interets_gaming", "[]"),
        ("interets_culture", "[]"),
        ("equipement_activites", "{}"),
        ("config_garde", "{}"),
    ]:
        op.add_column(
            "preferences_utilisateurs",
            sa.Column(col_name, _jsonb, nullable=False, server_default=default),
        )


def downgrade() -> None:
    # preferences_utilisateurs
    for col_name in [
        "config_garde",
        "equipement_activites",
        "interets_culture",
        "interets_gaming",
        "style_achats_mathieu",
        "style_achats_anne",
        "taille_vetements_mathieu",
        "taille_vetements_anne",
    ]:
        op.drop_column("preferences_utilisateurs", col_name)

    # achats_famille
    op.drop_index("ix_achats_famille_pour_qui", table_name="achats_famille")
    op.drop_column("achats_famille", "vendu_le")
    op.drop_column("achats_famille", "prix_revente_estime")
    op.drop_column("achats_famille", "a_revendre")
    op.drop_column("achats_famille", "pour_qui")

    # routines
    op.drop_column("routines", "derniere_completion")

    # activites_famille
    op.drop_column("activites_famille", "heure_debut")
