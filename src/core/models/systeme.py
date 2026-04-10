"""
Modèles SQLAlchemy pour le système et les sauvegardes.

Contient :
- Backup : Historique des sauvegardes
- HistoriqueAction : Historique des actions utilisateur (audit)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import CreeLeMixin

# ═══════════════════════════════════════════════════════════
# TABLE BACKUPS
# ═══════════════════════════════════════════════════════════


class Backup(CreeLeMixin, Base):
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

    __tablename__ = "sauvegardes"

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

    __table_args__ = (Index("ix_backups_cree_le", "cree_le"),)

    def __repr__(self) -> str:
        return f"<Backup(id={self.id}, filename='{self.filename}', size={self.size_bytes})>"


# ═══════════════════════════════════════════════════════════
# TABLE ACTION_HISTORY
# ═══════════════════════════════════════════════════════════


class HistoriqueAction(CreeLeMixin, Base):
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

    __tablename__ = "historique_actions"

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

    __table_args__ = (Index("ix_action_history_cree_le", "cree_le"),)

    def __repr__(self) -> str:
        return f"<HistoriqueAction(id={self.id}, user='{self.user_name}', action='{self.action_type}')>"


class LogSecurite(CreeLeMixin, Base):
    """Journal dédié des événements sécurité (auth/rate-limit/admin).

    Table SQL: logs_securite
    """

    __tablename__ = "logs_securite"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(255), index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    details: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_logs_securite_created_at", "created_at"),
        Index("ix_logs_securite_event_type_created_at", "event_type", "created_at"),
        Index("ix_logs_securite_user_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<LogSecurite(id={self.id}, event_type='{self.event_type}', user_id='{self.user_id}')>"
        )


# ═══════════════════════════════════════════════════════════
# TABLE IA_SUGGESTIONS_HISTORIQUE
# ═══════════════════════════════════════════════════════════


class IASuggestionsHistorique(CreeLeMixin, Base):
    """Historique des suggestions IA pour traçabilité et feedback.

    Table SQL: ia_suggestions_historique
    Stocke toutes les suggestions IA avec feedback utilisateur.

    Attributes:
        user_id: ID de l'utilisateur
        type_suggestion: Type de suggestion (achats, planning_adaptatif, etc.)
        module: Module source (cuisine, maison, famille, etc.)
        contenu: Contenu JSON de la suggestion IA
        acceptee: Si l'utilisateur a accepté la suggestion
        raison_rejet: Raison du rejet (optionnel)
        tokens_utilises: Nombre de tokens consommés
        duree_generation_ms: Durée de génération en millisecondes
        modele_ia: Modèle IA utilisé
    """

    __tablename__ = "ia_suggestions_historique"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type_suggestion: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contenu: Mapped[dict | None] = mapped_column(JSONB)
    acceptee: Mapped[bool | None] = mapped_column(Boolean, index=True)
    raison_rejet: Mapped[str | None] = mapped_column(Text)
    tokens_utilises: Mapped[int | None] = mapped_column(Integer)
    duree_generation_ms: Mapped[int | None] = mapped_column(Integer)
    modele_ia: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        Index("ix_ia_hist_user_type_cree", "user_id", "type_suggestion", "cree_le"),
        Index("ix_ia_hist_module_cree", "module", "cree_le"),
    )

    def __repr__(self) -> str:
        return f"<IASuggestionsHistorique(id={self.id}, type='{self.type_suggestion}', module='{self.module}')>"
