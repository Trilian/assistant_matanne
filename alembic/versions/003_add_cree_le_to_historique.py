"""Add cree_le column to historique_recettes table

Revision ID: 003
Revises: 002_add_historique_recettes
Create Date: 2026-01-16 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002_add_historique_recettes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add cree_le column to historique_recettes."""
    op.add_column(
        "historique_recettes",
        sa.Column(
            "cree_le",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    """Remove cree_le column from historique_recettes."""
    op.drop_column("historique_recettes", "cree_le")
