"""
Modèles pour la maison (projets, routines, jardin).

Contient :
- Project : Projet domestique
- ProjectTask : Tâche de projet
- Routine : Routine quotidienne
- RoutineTask : Tâche de routine
- GardenItem : Élément du jardin
- GardenLog : Journal d'entretien du jardin
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ═══════════════════════════════════════════════════════════
# PROJETS DOMESTIQUES
# ═══════════════════════════════════════════════════════════


class Project(Base):
    """Projet domestique.
    
    Attributes:
        nom: Nom du projet
        description: Description
        statut: Statut (en_cours, terminé, annulé)
        priorite: Priorité (haute, moyenne, basse)
        date_debut: Date de début
        date_fin_prevue: Date de fin prévue
        date_fin_reelle: Date de fin réelle
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne", index=True)
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin_prevue: Mapped[date | None] = mapped_column(Date)
    date_fin_reelle: Mapped[date | None] = mapped_column(Date)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tasks: Mapped[list["ProjectTask"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, nom='{self.nom}', statut='{self.statut}')>"


class ProjectTask(Base):
    """Tâche d'un projet.
    
    Attributes:
        project_id: ID du projet parent
        nom: Nom de la tâche
        description: Description
        statut: Statut (à_faire, en_cours, terminé)
        priorite: Priorité
        date_echéance: Date limite
        assigné_à: Personne assignée
    """

    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="à_faire", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne")
    date_echéance: Mapped[date | None] = mapped_column(Date)
    assigné_à: Mapped[str | None] = mapped_column(String(200))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    project: Mapped["Project"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ProjectTask(id={self.id}, project={self.project_id}, statut='{self.statut}')>"


# ═══════════════════════════════════════════════════════════
# ROUTINES
# ═══════════════════════════════════════════════════════════


class Routine(Base):
    """Routine ou habitude quotidienne.
    
    Attributes:
        nom: Nom de la routine
        description: Description
        categorie: Catégorie (ménage, enfant, etc.)
        frequence: Fréquence (quotidien, hebdomadaire, etc.)
        actif: Si la routine est active
    """

    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str | None] = mapped_column(String(100), index=True)
    frequence: Mapped[str] = mapped_column(String(50), nullable=False, default="quotidien")
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    tasks: Mapped[list["RoutineTask"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Routine(id={self.id}, nom='{self.nom}')>"


class RoutineTask(Base):
    """Tâche d'une routine.
    
    Attributes:
        routine_id: ID de la routine parent
        nom: Nom de la tâche
        description: Description
        ordre: Ordre d'exécution
        heure_prevue: Heure prévue (format HH:MM)
        fait_le: Date de dernière exécution
        notes: Notes
    """

    __tablename__ = "routine_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(
        ForeignKey("routines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    heure_prevue: Mapped[str | None] = mapped_column(String(5))  # Format: HH:MM
    fait_le: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    routine: Mapped["Routine"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<RoutineTask(id={self.id}, routine={self.routine_id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class GardenItem(Base):
    """Élément du jardin (plante, légume, fleur, etc.).
    
    Attributes:
        nom: Nom de la plante
        type: Type (plante, légume, fleur, arbre, etc.)
        location: Emplacement dans le jardin
        statut: Statut (actif, inactif, mort)
        date_plantation: Date de plantation
        date_recolte_prevue: Date de récolte prévue
        notes: Notes
    """

    __tablename__ = "garden_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(200))
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="actif", index=True)
    date_plantation: Mapped[date | None] = mapped_column(Date)
    date_recolte_prevue: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    logs: Mapped[list["GardenLog"]] = relationship(
        back_populates="garden_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<GardenItem(id={self.id}, nom='{self.nom}', type='{self.type}')>"


class GardenLog(Base):
    """Journal d'entretien du jardin.
    
    Attributes:
        garden_item_id: ID de l'élément (optionnel)
        date: Date de l'action
        action: Action effectuée (arrosage, désherbage, taille, récolte, etc.)
        notes: Notes
    """

    __tablename__ = "garden_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    garden_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("garden_items.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    garden_item: Mapped[Optional["GardenItem"]] = relationship(back_populates="logs")

    def __repr__(self) -> str:
        return f"<GardenLog(id={self.id}, action='{self.action}', date={self.date})>"
