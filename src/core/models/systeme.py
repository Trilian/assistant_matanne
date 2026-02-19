"""
Modèles SQLAlchemy pour le système et les sauvegardes.

Contient :
- Backup : Historique des sauvegardes
- ActionHistory : Historique des actions utilisateur (audit)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, utc_now

# ═══════════════════════════════════════════════════════════
# TABLE BACKUPS
# ═══════════════════════════════════════════════════════════


class Backup(Base):
    """Historique des sauvegardes.

    Table SQL: backups
    Utilisé par: src/services/backup.py

    Attributes:
        filename: Nom du fichier de backup
        tables_included: Liste des tables sauvegardées
        row_counts: Compteurs de lignes par table
        size_bytes: Taille en octets
        compressed: Si le backup est compressé
        storage_path: Chemin Supabase Storage
        version: Version du format de backup
    """

    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    tables_included: Mapped[list | None] = mapped_column(JSONB, default=list)
    row_counts: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    compressed: Mapped[bool] = mapped_column(Boolean, default=True)
    storage_path: Mapped[str | None] = mapped_column(String(500))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")

    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    def __repr__(self) -> str:
        return f"<Backup(id={self.id}, filename='{self.filename}', size={self.size_bytes})>"


# ═══════════════════════════════════════════════════════════
# TABLE ACTION_HISTORY
# ═══════════════════════════════════════════════════════════


class ActionHistory(Base):
    """Historique des actions utilisateur pour audit.

    Table SQL: action_history
    Utilisé par: src/services/core/utilisateur/historique.py

    Attributes:
        user_id: ID de l'utilisateur
        user_name: Nom de l'utilisateur
        action_type: Type d'action (recette.created, etc.)
        entity_type: Type d'entité (recette, inventaire, etc.)
        entity_id: ID de l'entité concernée
        entity_name: Nom de l'entité
        description: Description lisible de l'action
        details: Détails additionnels (JSON)
        old_value: Valeur avant modification (pour undo)
        new_value: Valeur après modification
        ip_address: Adresse IP
        user_agent: User agent du navigateur
    """

    __tablename__ = "action_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(BigInteger)
    entity_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    old_value: Mapped[dict | None] = mapped_column(JSONB)
    new_value: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)

    def __repr__(self) -> str:
        return (
            f"<ActionHistory(id={self.id}, user='{self.user_name}', action='{self.action_type}')>"
        )
