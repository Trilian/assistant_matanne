"""Modèles Sprint 10 pour gamification et automations.

Contient:
- PointsUtilisateur: points hebdo sport/nutrition/anti-gaspi
- BadgeUtilisateur: badges gagnés par utilisateur
- AutomationRegle: règles "si -> alors" exécutables
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now


class PointsUtilisateur(Base):
    """Points hebdomadaires de gamification pour un utilisateur."""

    __tablename__ = "points_utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    semaine_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    points_sport: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_alimentation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    points_anti_gaspi: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    details: Mapped[dict | None] = mapped_column(JSONB)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("ProfilUtilisateur")

    __table_args__ = (
        UniqueConstraint("user_id", "semaine_debut", name="uq_points_user_semaine"),
    )


class BadgeUtilisateur(Base):
    """Badge gagné par un utilisateur, avec date d'obtention."""

    __tablename__ = "badges_utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    badge_label: Mapped[str] = mapped_column(String(150), nullable=False)
    acquis_le: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, index=True)

    meta: Mapped[dict | None] = mapped_column(JSONB)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    user = relationship("ProfilUtilisateur")

    __table_args__ = (
        UniqueConstraint("user_id", "badge_type", "acquis_le", name="uq_badge_user_type_date"),
    )


class AutomationRegle(Base):
    """Règle d'automation exécutable périodiquement (LT-04)."""

    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    declencheur: Mapped[dict] = mapped_column(JSONB, nullable=False)
    action: Mapped[dict] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)

    derniere_execution: Mapped[datetime | None] = mapped_column(DateTime)
    execution_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("ProfilUtilisateur")
