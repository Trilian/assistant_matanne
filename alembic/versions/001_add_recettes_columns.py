"""Add bio local robots nutrition columns to recettes

Revision ID: 001_add_recettes_columns
Revises:
Create Date: 2026-01-12 21:30:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_add_recettes_columns"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add bio/local columns
    op.add_column(
        "recettes", sa.Column("est_bio", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "recettes", sa.Column("est_local", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "recettes", sa.Column("score_bio", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "recettes", sa.Column("score_local", sa.Integer(), nullable=False, server_default="0")
    )

    # Add robot compatibility columns
    op.add_column(
        "recettes",
        sa.Column("compatible_cookeo", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "recettes",
        sa.Column(
            "compatible_monsieur_cuisine", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "recettes",
        sa.Column("compatible_airfryer", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "recettes",
        sa.Column("compatible_multicooker", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Add nutrition columns
    op.add_column(
        "recettes", sa.Column("calories", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "recettes", sa.Column("proteines", sa.Float(), nullable=False, server_default="0.0")
    )
    op.add_column(
        "recettes", sa.Column("lipides", sa.Float(), nullable=False, server_default="0.0")
    )
    op.add_column(
        "recettes", sa.Column("glucides", sa.Float(), nullable=False, server_default="0.0")
    )

    # Add IA and image columns
    op.add_column(
        "recettes", sa.Column("genere_par_ia", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column("recettes", sa.Column("score_ia", sa.Float(), nullable=True))
    op.add_column("recettes", sa.Column("url_image", sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column("recettes", "url_image")
    op.drop_column("recettes", "score_ia")
    op.drop_column("recettes", "genere_par_ia")
    op.drop_column("recettes", "glucides")
    op.drop_column("recettes", "lipides")
    op.drop_column("recettes", "proteines")
    op.drop_column("recettes", "calories")
    op.drop_column("recettes", "compatible_multicooker")
    op.drop_column("recettes", "compatible_airfryer")
    op.drop_column("recettes", "compatible_monsieur_cuisine")
    op.drop_column("recettes", "compatible_cookeo")
    op.drop_column("recettes", "score_local")
    op.drop_column("recettes", "score_bio")
    op.drop_column("recettes", "est_local")
    op.drop_column("recettes", "est_bio")
