"""
Modèles pour la maison (projets, routines, jardin).

Contient :
- Projet : Projet domestique
- TacheProjet : Tâche de projet
- Routine : Routine quotidienne
- TacheRoutine : Tâche de routine
- ElementJardin : Élément du jardin
- JournalJardin : Journal d'entretien du jardin
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
from .mixins import CreeLeMixin

# ═══════════════════════════════════════════════════════════
# PROJETS DOMESTIQUES
# ═══════════════════════════════════════════════════════════


class Projet(CreeLeMixin, Base):
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

    __tablename__ = "projets"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="en_cours", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne", index=True)
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin_prevue: Mapped[date | None] = mapped_column(Date)
    date_fin_reelle: Mapped[date | None] = mapped_column(Date)

    # Relations
    tasks: Mapped[list["TacheProjet"]] = relationship(
        back_populates="projet", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Projet(id={self.id}, nom='{self.nom}', statut='{self.statut}')>"


# Alias rétrocompatibilité
Project = Projet


class TacheProjet(CreeLeMixin, Base):
    """Tâche d'un projet.

    Attributes:
        project_id: ID du projet parent
        nom: Nom de la tâche
        description: Description
        statut: Statut (à_faire, en_cours, terminé)
        priorite: Priorité
        date_echeance: Date limite
        assigne_a: Personne assignée
    """

    __tablename__ = "taches_projets"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="à_faire", index=True)
    priorite: Mapped[str] = mapped_column(String(50), nullable=False, default="moyenne")
    date_echeance: Mapped[date | None] = mapped_column(Date)
    assigne_a: Mapped[str | None] = mapped_column(String(200))

    # Relations
    projet: Mapped["Projet"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<TacheProjet(id={self.id}, projet={self.project_id}, statut='{self.statut}')>"


# ═══════════════════════════════════════════════════════════
# ROUTINES
# ═══════════════════════════════════════════════════════════


class Routine(CreeLeMixin, Base):
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

    # Relations
    tasks: Mapped[list["TacheRoutine"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Routine(id={self.id}, nom='{self.nom}')>"


class TacheRoutine(CreeLeMixin, Base):
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

    __tablename__ = "taches_routines"

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

    # Relations
    routine: Mapped["Routine"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"<TacheRoutine(id={self.id}, routine={self.routine_id}, nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class ElementJardin(CreeLeMixin, Base):
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

    __tablename__ = "elements_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(200))
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="actif", index=True)
    date_plantation: Mapped[date | None] = mapped_column(Date)
    date_recolte_prevue: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    logs: Mapped[list["JournalJardin"]] = relationship(
        back_populates="garden_item", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ElementJardin(id={self.id}, nom='{self.nom}', type='{self.type}')>"


class JournalJardin(CreeLeMixin, Base):
    """Journal d'entretien du jardin.

    Attributes:
        garden_item_id: ID de l'élément (optionnel)
        date: Date de l'action
        action: Action effectuée (arrosage, désherbage, taille, récolte, etc.)
        notes: Notes
    """

    __tablename__ = "journaux_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    garden_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("elements_jardin.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    garden_item: Mapped[Optional["ElementJardin"]] = relationship(back_populates="logs")

    def __repr__(self) -> str:
        return f"<JournalJardin(id={self.id}, action='{self.action}', date={self.date})>"
