"""Extend zones_jardin with state tracking fields

Revision ID: 019
Revises: 018
Create Date: 2026-02-16 14:30:00.000000

Ajoute les champs de suivi d'état à zones_jardin (migrés depuis GardenZone):
- etat_note: Note de 1 à 5 (état actuel)
- etat_description: Description de l'état
- objectif: Objectif de remise en état
- budget_estime: Budget estimé pour travaux
- prochaine_action: Prochaine action à effectuer
- date_prochaine_action: Date prévue
- photos_url: URLs des photos avant/après (JSON)

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les colonnes de suivi d'état à zones_jardin
    op.add_column(
        "zones_jardin",
        sa.Column("etat_note", sa.Integer(), server_default="3", nullable=False),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("etat_description", sa.Text(), nullable=True),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("objectif", sa.Text(), nullable=True),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("budget_estime", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("prochaine_action", sa.String(200), nullable=True),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("date_prochaine_action", sa.Date(), nullable=True),
    )
    op.add_column(
        "zones_jardin",
        sa.Column("photos_url", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )


def downgrade():
    # Retirer les colonnes ajoutées
    op.drop_column("zones_jardin", "photos_url")
    op.drop_column("zones_jardin", "date_prochaine_action")
    op.drop_column("zones_jardin", "prochaine_action")
    op.drop_column("zones_jardin", "budget_estime")
    op.drop_column("zones_jardin", "objectif")
    op.drop_column("zones_jardin", "etat_description")
    op.drop_column("zones_jardin", "etat_note")
