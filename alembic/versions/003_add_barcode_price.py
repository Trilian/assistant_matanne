"""Add barcode and price fields to article_inventaire

Revision ID: 003_add_barcode_price
Revises:
Create Date: 2026-01-18

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "003_add_barcode_price"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajouter colonnes code_barres et prix_unitaire Ã  la table inventaire
    op.add_column("inventaire", sa.Column("code_barres", sa.String(50), nullable=True))
    op.add_column("inventaire", sa.Column("prix_unitaire", sa.Float(), nullable=True))

    # CrÃ©er index pour code_barres
    op.create_unique_constraint("uq_code_barres", "inventaire", ["code_barres"])
    op.create_index("ix_inventaire_code_barres", "inventaire", ["code_barres"], unique=False)


def downgrade() -> None:
    # Supprimer les colonnes
    op.drop_index("ix_inventaire_code_barres", table_name="inventaire")
    op.drop_constraint("uq_code_barres", "inventaire", type_="unique")
    op.drop_column("inventaire", "prix_unitaire")
    op.drop_column("inventaire", "code_barres")
