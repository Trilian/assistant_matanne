"""Baseline initiale — état du schéma au moment de l'introduction d'Alembic.

Cette migration représente la baseline à partir de laquelle Alembic gère
les évolutions incrémentales. Le schéma réel est défini dans
``sql/INIT_COMPLET.sql`` et a été appliqué directement sur Supabase.

NE PAS ré-exécuter cette migration sur une DB existante.
Utiliser à la place : ``alembic stamp head``

Revision ID: a1b2c3d4e5f6
Revises: (aucune — première migration)
Create Date: 2026-03-27 00:00:00

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline : schéma déjà appliqué via sql/INIT_COMPLET.sql + GestionnaireMigrations.

    Aucune opération DDL ici — la DB est déjà au bon état.
    Marquer manuellement : ``alembic stamp head``
    """
    pass


def downgrade() -> None:
    """Ne pas rétrograder la baseline — le schéma complet est dans sql/INIT_COMPLET.sql."""
    pass
