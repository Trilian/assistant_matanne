"""Add series tracking models for jeux

Revision ID: 017_add_jeux_series
Revises: 016_add_user_preferences_models
Create Date: 2026-02-16

Ajoute les tables pour le tracking des séries (loi des séries):
- jeux_series: Track série actuelle par marché/numéro
- jeux_alertes: Alertes d'opportunités
- jeux_configuration: Configuration des seuils
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "017_add_jeux_series"
down_revision = "016_add_user_preferences_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Table jeux_series
    op.create_table(
        "jeux_series",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type_jeu", sa.String(20), nullable=False),
        sa.Column("championnat", sa.String(50), nullable=True),
        sa.Column("marche", sa.String(50), nullable=False),
        sa.Column("serie_actuelle", sa.Integer(), default=0, nullable=False),
        sa.Column("frequence", sa.Float(), default=0.0, nullable=False),
        sa.Column("nb_occurrences", sa.Integer(), default=0, nullable=False),
        sa.Column("nb_total", sa.Integer(), default=0, nullable=False),
        sa.Column("derniere_occurrence", sa.Date(), nullable=True),
        sa.Column("derniere_mise_a_jour", sa.DateTime(), nullable=True),
        sa.Column("cree_le", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_jeux_series_type_jeu_championnat",
        "jeux_series",
        ["type_jeu", "championnat"],
    )
    op.create_index(
        "ix_jeux_series_type_jeu_marche",
        "jeux_series",
        ["type_jeu", "marche"],
    )

    # Table jeux_alertes
    op.create_table(
        "jeux_alertes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("serie_id", sa.Integer(), nullable=False),
        sa.Column("type_jeu", sa.String(20), nullable=False),
        sa.Column("championnat", sa.String(50), nullable=True),
        sa.Column("marche", sa.String(50), nullable=False),
        sa.Column("value_alerte", sa.Float(), nullable=False),
        sa.Column("serie_alerte", sa.Integer(), nullable=False),
        sa.Column("frequence_alerte", sa.Float(), nullable=False),
        sa.Column("seuil_utilise", sa.Float(), default=2.0, nullable=False),
        sa.Column("notifie", sa.Boolean(), default=False, nullable=False),
        sa.Column("date_notification", sa.DateTime(), nullable=True),
        sa.Column("resultat_verifie", sa.Boolean(), default=False, nullable=False),
        sa.Column("resultat_correct", sa.Boolean(), nullable=True),
        sa.Column("cree_le", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["serie_id"], ["jeux_series.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_jeux_alertes_notifie",
        "jeux_alertes",
        ["notifie"],
    )

    # Table jeux_configuration
    op.create_table(
        "jeux_configuration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cle", sa.String(50), nullable=False, unique=True),
        sa.Column("valeur", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("modifie_le", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Insérer configurations par défaut
    op.execute(
        """
        INSERT INTO jeux_configuration (cle, valeur, description) VALUES
        ('seuil_value_alerte', '2.0', 'Seuil de value minimum pour créer une alerte'),
        ('seuil_value_haute', '2.5', 'Seuil de value pour opportunité haute'),
        ('seuil_series_minimum', '3', 'Série minimum pour considérer comme significatif'),
        ('sync_paris_interval_hours', '6', 'Intervalle de sync paris en heures'),
        ('sync_loto_days', 'mon,wed,sat', 'Jours de sync loto'),
        ('sync_loto_hour', '21:30', 'Heure de sync loto')
    """
    )


def downgrade() -> None:
    op.drop_table("jeux_configuration")
    op.drop_index("ix_jeux_alertes_notifie", table_name="jeux_alertes")
    op.drop_table("jeux_alertes")
    op.drop_index("ix_jeux_series_type_jeu_marche", table_name="jeux_series")
    op.drop_index("ix_jeux_series_type_jeu_championnat", table_name="jeux_series")
    op.drop_table("jeux_series")
