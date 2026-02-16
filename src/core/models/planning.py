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
        recurrence_type: Type de récurrence (none, daily, weekly, monthly, yearly)
        recurrence_interval: Intervalle de récurrence (tous les N jours/semaines/mois/années)
        recurrence_jours: Jours de la semaine pour weekly (ex: "0,1,4" = lun,mar,ven)
        recurrence_fin: Date de fin de la récurrence
        parent_event_id: ID de l'événement parent (pour les occurrences)
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

    # Récurrence
    recurrence_type: Mapped[str | None] = mapped_column(String(20))  # none, daily, weekly, monthly, yearly
    recurrence_interval: Mapped[int | None] = mapped_column(Integer, default=1)  # Tous les N jours/semaines/mois/années
    recurrence_jours: Mapped[str | None] = mapped_column(String(20))  # Pour weekly: "0,1,4" = lun,mar,ven
    recurrence_fin: Mapped[date | None] = mapped_column(Date)  # Date de fin de la récurrence
    parent_event_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("calendar_events.id"))

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_date_type", "date_debut", "type_event"),
        Index("idx_date_range", "date_debut", "date_fin"),
    )

    def __repr__(self) -> str:
        return f"<CalendarEvent(id={self.id}, titre='{self.titre}', date={self.date_debut})>"


# ═══════════════════════════════════════════════════════════
# TEMPLATES DE SEMAINE
# ═══════════════════════════════════════════════════════════


class TemplateSemaine(Base):
    """Modèle de semaine type réutilisable.

    Permet de sauvegarder une organisation de semaine
    et de l'appliquer à n'importe quelle semaine.

    Attributes:
        nom: Nom du template
        description: Description du template
        actif: Si le template est actif
    """

    __tablename__ = "templates_semaine"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    items: Mapped[list["TemplateItem"]] = relationship(
        "TemplateItem",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateItem.jour_semaine, TemplateItem.heure_debut",
    )

    def __repr__(self) -> str:
        return f"<TemplateSemaine(id={self.id}, nom='{self.nom}')>"


class TemplateItem(Base):
    """Élément d'un template de semaine.

    Représente un événement type dans le template,
    positionné sur un jour et une heure.

    Attributes:
        template_id: ID du template parent
        jour_semaine: Jour (0=Lundi à 6=Dimanche)
        heure_debut: Heure de début (ex: "09:00")
        heure_fin: Heure de fin (ex: "10:30")
        titre: Titre de l'événement
        type_event: Type d'événement
        lieu: Lieu optionnel
        couleur: Couleur d'affichage
    """

    __tablename__ = "template_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates_semaine.id"), nullable=False)
    jour_semaine: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-6
    heure_debut: Mapped[str] = mapped_column(String(5), nullable=False)  # "HH:MM"
    heure_fin: Mapped[str | None] = mapped_column(String(5))
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    type_event: Mapped[str] = mapped_column(String(50), default="autre")
    lieu: Mapped[str | None] = mapped_column(String(200))
    couleur: Mapped[str | None] = mapped_column(String(20))

    # Relations
    template: Mapped["TemplateSemaine"] = relationship("TemplateSemaine", back_populates="items")

    __table_args__ = (
        Index("idx_template_jour", "template_id", "jour_semaine"),
    )

    def __repr__(self) -> str:
        return f"<TemplateItem(jour={self.jour_semaine}, heure={self.heure_debut}, titre='{self.titre}')>"
