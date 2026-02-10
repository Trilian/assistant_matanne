"""
Modèles pour la santé et le bien-être.

Contient :
- HealthRoutine : Routine de santé/sport
- HealthObjective : Objectifs de santé
- HealthEntry : Entrées quotidiennes de suivi
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ═══════════════════════════════════════════════════════════
# ROUTINES SANTÉ
# ═══════════════════════════════════════════════════════════


class HealthRoutine(Base):
    """Routine de santé ou sport.
    
    Attributes:
        nom: Nom de la routine
        description: Description
        type_routine: Type (yoga, course, gym, marche, sport, etc.)
        frequence: Fréquence (3x/semaine, quotidien, etc.)
        duree_minutes: Durée en minutes
        intensite: Intensité (basse, modérée, haute)
        jours_semaine: Jours de la semaine programmés
        calories_brulees_estimees: Calories estimées brûlées
        actif: Si la routine est active
    """

    __tablename__ = "health_routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_routine: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    frequence: Mapped[str] = mapped_column(String(50), nullable=False)
    duree_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensite: Mapped[str] = mapped_column(String(50), nullable=False, default="modérée")
    jours_semaine: Mapped[list[str] | None] = mapped_column(JSONB)
    calories_brulees_estimees: Mapped[int | None] = mapped_column(Integer)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    entries: Mapped[list["HealthEntry"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("duree_minutes > 0", name="ck_routine_duree_positive"),
    )

    def __repr__(self) -> str:
        return f"<HealthRoutine(id={self.id}, nom='{self.nom}', type='{self.type_routine}')>"


class HealthObjective(Base):
    """Objectifs de santé et bien-être.
    
    Attributes:
        titre: Titre de l'objectif
        description: Description
        categorie: Catégorie (poids, endurance, force, flexibilité, alimentation, etc.)
        valeur_cible: Valeur à atteindre
        unite: Unité (kg, km, reps, days, etc.)
        valeur_actuelle: Valeur actuelle
        date_debut: Date de début
        date_cible: Date cible
        priorite: Priorité (haute, moyenne, basse)
        statut: Statut (en_cours, atteint, abandonné)
    """

    __tablename__ = "health_objectives"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    valeur_cible: Mapped[float] = mapped_column(Float, nullable=False)
    unite: Mapped[str] = mapped_column(String(50))
    valeur_actuelle: Mapped[float | None] = mapped_column(Float)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    date_cible: Mapped[date] = mapped_column(Date, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne")
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("valeur_cible > 0", name="ck_objective_valeur_positive"),
        CheckConstraint("date_debut <= date_cible", name="ck_objective_dates"),
    )

    def __repr__(self) -> str:
        return f"<HealthObjective(id={self.id}, titre='{self.titre}', statut='{self.statut}')>"


class HealthEntry(Base):
    """Entrée quotidienne de suivi santé.
    
    Attributes:
        routine_id: ID de la routine (optionnel)
        date: Date de l'entrée
        type_activite: Type d'activité
        duree_minutes: Durée en minutes
        intensite: Intensité
        calories_brulees: Calories brûlées
        note_energie: Note d'énergie (1-10)
        note_moral: Note de moral (1-10)
        ressenti: Ressenti textuel
        notes: Notes supplémentaires
    """

    __tablename__ = "health_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int | None] = mapped_column(
        ForeignKey("health_routines.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    type_activite: Mapped[str] = mapped_column(String(100), nullable=False)
    duree_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensite: Mapped[str] = mapped_column(String(50))
    calories_brulees: Mapped[int | None] = mapped_column(Integer)
    note_energie: Mapped[int | None] = mapped_column(Integer)
    note_moral: Mapped[int | None] = mapped_column(Integer)
    ressenti: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    routine: Mapped[Optional["HealthRoutine"]] = relationship(back_populates="entries")

    __table_args__ = (
        CheckConstraint("duree_minutes > 0", name="ck_entry_duree_positive"),
        CheckConstraint("note_energie >= 1 AND note_energie <= 10", name="ck_entry_energie"),
        CheckConstraint("note_moral >= 1 AND note_moral <= 10", name="ck_entry_moral"),
    )

    def __repr__(self) -> str:
        return f"<HealthEntry(id={self.id}, date={self.date}, type='{self.type_activite}')>"
