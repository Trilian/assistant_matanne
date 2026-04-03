"""
Modèles pour l'historique des notifications enrichies.

Contient :
- HistoriqueNotification : Historique centralisé des notifications (E.5)
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TimestampMixin


class HistoriqueNotification(TimestampMixin, Base):
    """Historique centralisé des notifications envoyées (E.5).

    Table SQL: historique_notifications

    Utilisé par: Centre de notifications frontend (E.5)

    Attributes:
        user_id: Utilisateur destinataire
        canal: Canal utilisé (ntfy, push, email, telegram)
        titre: Titre de la notification
        message: Contenu
        type_evenement: Type événement métier
        categorie: Catégorie (rappels, alertes, resumes)
        lu: Si l'utilisateur a lu
        action_effectuee: Bouton cliqué si applicable
    """

    __tablename__ = "historique_notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Destinataire
    user_id: Mapped[str] = mapped_column(String(255), index=True)

    # Contenu
    canal: Mapped[str] = mapped_column(String(20))  # ntfy, push, email, telegram
    titre: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text)
    type_evenement: Mapped[str | None] = mapped_column(String(100), nullable=True)
    categorie: Mapped[str] = mapped_column(String(50), default="autres")  # rappels, alertes, resumes

    # Métadonnées de suivi
    lu: Mapped[bool] = mapped_column(Boolean, default=False)
    action_effectuee: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Extra data (JSON). Nom d'attribut Python != 'metadata' (réservé SQLAlchemy).
    metadata_payload: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    def __repr__(self) -> str:
        return f"<HistoriqueNotification(id={self.id}, user_id={self.user_id}, canal={self.canal})>"
