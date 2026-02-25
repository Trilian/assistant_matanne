"""
Modèle pour le stockage d'état persistant PersistentState → DB.

Permet la synchronisation automatique session_state ↔ base de données
pour les configurations et préférences utilisateur.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TimestampMixin


class EtatPersistantDB(TimestampMixin, Base):
    """
    Stockage persistant d'état applicatif.

    Permet de sauvegarder les données de session_state
    en base de données pour persistance entre sessions.

    Attributes:
        namespace: Nom de l'espace de stockage (ex: "foyer_config")
        user_id: Identifiant utilisateur
        data: Données JSON sérialisées
        created_at: Date de création (cree_le)
        updated_at: Date de dernière modification (modifie_le)
    """

    __tablename__ = "etats_persistants"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identifiants
    namespace: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, default="default", index=True)

    # Données
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    # Contraintes
    __table_args__ = (UniqueConstraint("namespace", "user_id", name="uq_pstate_namespace_user"),)

    def __repr__(self) -> str:
        return f"<EtatPersistantDB(namespace='{self.namespace}', user='{self.user_id}')>"


__all__ = ["EtatPersistantDB"]
