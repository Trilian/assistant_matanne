"""Add magasin column to family_budgets table.

Revision ID: 011
Revises: 010
Create Date: 2026-01-31 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne magasin si elle n'existe pas
    try:
        op.add_column('family_budgets', 
            sa.Column('magasin', sa.String(200), nullable=True)
        )
    except Exception:
        # La colonne existe déjà, on ignore
        pass


def downgrade():
    try:
        op.drop_column('family_budgets', 'magasin')
    except Exception:
        pass
