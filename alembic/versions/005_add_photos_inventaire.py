"""Add photos support to inventory articles

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajoute les colonnes photo à la table inventaire
    op.add_column(
        "inventaire",
        sa.Column("photo_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "inventaire",
        sa.Column("photo_filename", sa.String(200), nullable=True),
    )
    op.add_column(
        "inventaire",
        sa.Column("photo_uploaded_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    # Supprime les colonnes photo
    op.drop_column("inventaire", "photo_uploaded_at")
    op.drop_column("inventaire", "photo_filename")
    op.drop_column("inventaire", "photo_url")
