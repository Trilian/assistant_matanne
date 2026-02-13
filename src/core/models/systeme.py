"""
Modèles SQLAlchemy pour le système et les sauvegardes.

Contient :
- Backup : Historique des sauvegardes
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Backup(id={self.id}, filename='{self.filename}', size={self.size_bytes})>"
