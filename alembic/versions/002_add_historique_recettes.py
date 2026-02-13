"""Add HistoriqueRecette table for recipe usage tracking

Revision ID: 002_add_historique_recettes
Revises: 001_add_recettes_columns
Create Date: 2026-01-14 10:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_add_historique_recettes"
down_revision = "001_add_recettes_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create historique_recettes table"""
    op.create_table(
        "historique_recettes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recette_id", sa.Integer(), nullable=False),
        sa.Column("date_cuisson", sa.Date(), nullable=False),
        sa.Column("portions_cuisinees", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("note", sa.Integer(), nullable=True),
        sa.Column("avis", sa.Text(), nullable=True),
        sa.Column("cree_le", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["recette_id"], ["recettes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("note IS NULL OR (note >= 0 AND note <= 5)", name="ck_note_valide"),
        sa.CheckConstraint("portions_cuisinees > 0", name="ck_portions_cuisinees_positive"),
    )

    # Add indexes
    op.create_index("ix_historique_recettes_recette_id", "historique_recettes", ["recette_id"])
    op.create_index("ix_historique_recettes_date_cuisson", "historique_recettes", ["date_cuisson"])


def downgrade() -> None:
    """Drop historique_recettes table"""
    op.drop_index("ix_historique_recettes_date_cuisson", table_name="historique_recettes")
    op.drop_index("ix_historique_recettes_recette_id", table_name="historique_recettes")
    op.drop_table("historique_recettes")
