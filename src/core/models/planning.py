"""
Modèles pour le planning et le calendrier.

Contient :
- Planning : Planning hebdomadaire de repas
- Repas : Repas planifié
- CalendarEvent : Événement du calendrier
"""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .recettes import Recette


# ═══════════════════════════════════════════════════════════
# PLANNING REPAS
# ═══════════════════════════════════════════════════════════


class Planning(Base):
    """Planning hebdomadaire de repas.

    Attributes:
        nom: Nom du planning
        semaine_debut: Date de début de semaine
        semaine_fin: Date de fin de semaine
        actif: Si le planning est actif
        genere_par_ia: Si généré par l'IA
        notes: Notes supplémentaires
    """

    __tablename__ = "plannings"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    semaine_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    semaine_fin: Mapped[date] = mapped_column(Date, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    repas: Mapped[list["Repas"]] = relationship(
        back_populates="planning", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Planning(id={self.id}, nom='{self.nom}')>"


class Repas(Base):
    """Repas planifié dans un planning.

    Attributes:
        planning_id: ID du planning parent
        recette_id: ID de la recette (optionnel)
        date_repas: Date du repas
        type_repas: Type (petit_déjeuner, déjeuner, dîner, goûter)
        portion_ajustee: Portions ajustées
        prepare: Si le repas a été préparé
        notes: Notes supplémentaires
    """

    __tablename__ = "repas"

    id: Mapped[int] = mapped_column(primary_key=True)
    planning_id: Mapped[int] = mapped_column(
        ForeignKey("plannings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )
    date_repas: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type_repas: Mapped[str] = mapped_column(String(50), nullable=False, default="dîner", index=True)
    portion_ajustee: Mapped[int | None] = mapped_column(Integer)
    prepare: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    planning: Mapped["Planning"] = relationship(back_populates="repas")
    recette: Mapped[Optional["Recette"]] = relationship()

    def __repr__(self) -> str:
        return f"<Repas(id={self.id}, date={self.date_repas}, type='{self.type_repas}')>"


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS CALENDRIER
# ═══════════════════════════════════════════════════════════


class CalendarEvent(Base):
    """Événement du calendrier familial.

    Attributes:
        titre: Titre de l'événement
        description: Description
        date_debut: Date et heure de début
        date_fin: Date et heure de fin
        lieu: Lieu de l'événement
        type_event: Type (rdv, activité, fête, autre)
        couleur: Couleur d'affichage
        rappel_avant_minutes: Minutes avant pour le rappel
    """

    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    date_fin: Mapped[datetime | None] = mapped_column(DateTime)
    lieu: Mapped[str | None] = mapped_column(String(200))
    type_event: Mapped[str] = mapped_column(String(50), nullable=False, default="autre", index=True)
    couleur: Mapped[str | None] = mapped_column(String(20))
    rappel_avant_minutes: Mapped[int | None] = mapped_column(Integer)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_date_type", "date_debut", "type_event"),
        Index("idx_date_range", "date_debut", "date_fin"),
    )

    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, titre='{self.titre}', date={self.date_debut})>"
