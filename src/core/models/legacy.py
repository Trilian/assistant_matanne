"""
Models Legacy - Modèles Famille, Maison, Planning (non refactorisés).

Ces modèles ne sont pas encore refactorisés et sont importés tels quels
depuis l'ancien fichier models.py pour maintenir la compatibilité.

⚠️ À refactoriser dans une prochaine phase.
"""
from datetime import datetime, date
from typing import Optional, List, Dict
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Float,
    Boolean,
    ForeignKey,
    Text,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from .base import Base


# ═══════════════════════════════════════════════════════════
# PLANNING HEBDOMADAIRE
# ═══════════════════════════════════════════════════════════

class PlanningHebdomadaire(Base):
    """Planning d'une semaine (non refactorisé)."""

    __tablename__ = "plannings_hebdomadaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    semaine_debut: Mapped[date] = mapped_column(Date, nullable=False)
    nom: Mapped[Optional[str]] = mapped_column(String(200))
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)
    statut: Mapped[str] = mapped_column(String(50), default="brouillon")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    repas: Mapped[List["RepasPlanning"]] = relationship(
        "RepasPlanning",
        back_populates="planning",
        cascade="all, delete-orphan",
        order_by="RepasPlanning.jour_semaine, RepasPlanning.ordre",
    )


class RepasPlanning(Base):
    """Repas individuel dans un planning (non refactorisé)."""

    __tablename__ = "repas_planning"

    id: Mapped[int] = mapped_column(primary_key=True)
    planning_id: Mapped[int] = mapped_column(
        ForeignKey("plannings_hebdomadaires.id", ondelete="CASCADE")
    )
    jour_semaine: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    type_repas: Mapped[str] = mapped_column(String(50), nullable=False)
    recette_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL")
    )
    portions: Mapped[int] = mapped_column(Integer, default=4)
    est_adapte_bebe: Mapped[bool] = mapped_column(Boolean, default=False)
    est_batch_cooking: Mapped[bool] = mapped_column(Boolean, default=False)
    recettes_batch: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    ordre: Mapped[int] = mapped_column(Integer, default=0)
    statut: Mapped[str] = mapped_column(String(50), default="planifié")
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    planning: Mapped["PlanningHebdomadaire"] = relationship(back_populates="repas")

    # Import dynamique pour éviter circular import
    @property
    def recette(self):
        from .cuisine import Recette
        if self.recette_id:
            from src.core.database import get_db_context
            with get_db_context() as db:
                return db.query(Recette).get(self.recette_id)
        return None


class ConfigPlanningUtilisateur(Base):
    """Configuration utilisateur pour le planning (non refactorisé)."""

    __tablename__ = "config_planning_utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE")
    )
    repas_actifs: Mapped[Dict] = mapped_column(
        JSONB,
        default={
            "petit_déjeuner": False,
            "déjeuner": True,
            "dîner": True,
            "goûter": False,
            "bébé": False,
            "batch_cooking": False,
        },
    )
    nb_adultes: Mapped[int] = mapped_column(Integer, default=2)
    nb_enfants: Mapped[int] = mapped_column(Integer, default=0)
    a_bebe: Mapped[bool] = mapped_column(Boolean, default=False)
    batch_cooking_actif: Mapped[bool] = mapped_column(Boolean, default=False)
    jours_batch: Mapped[List[int]] = mapped_column(ARRAY(Integer), default=[])
    preferences: Mapped[Dict] = mapped_column(JSONB, default={})
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# FAMILLE
# ═══════════════════════════════════════════════════════════

class ProfilEnfant(Base):
    """Profil d'un enfant (non refactorisé)."""

    __tablename__ = "profils_enfants"

    id: Mapped[int] = mapped_column(primary_key=True)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    date_naissance: Mapped[date] = mapped_column(Date, nullable=False)
    url_photo: Mapped[Optional[str]] = mapped_column(String(500))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entrees_bien_etre: Mapped[List["EntreeBienEtre"]] = relationship(
        back_populates="enfant", cascade="all, delete-orphan"
    )
    routines: Mapped[List["Routine"]] = relationship(back_populates="enfant")


class EntreeBienEtre(Base):
    """Entrée de suivi bien-être (non refactorisé)."""

    __tablename__ = "entrees_bien_etre"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    humeur: Mapped[str] = mapped_column(String(50), nullable=False)
    heures_sommeil: Mapped[Optional[float]] = mapped_column(Float)
    activite: Mapped[Optional[str]] = mapped_column(String(200))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    nom_utilisateur: Mapped[Optional[str]] = mapped_column(String(100))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(back_populates="entrees_bien_etre")


class Routine(Base):
    """Routine pour un enfant (non refactorisé)."""

    __tablename__ = "routines"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE")
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    frequence: Mapped[str] = mapped_column(String(50), default="quotidien")
    est_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(back_populates="routines")
    taches: Mapped[List["TacheRoutine"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )


class TacheRoutine(Base):
    """Tâche d'une routine (non refactorisé)."""

    __tablename__ = "taches_routine"

    id: Mapped[int] = mapped_column(primary_key=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id", ondelete="CASCADE"))
    nom_tache: Mapped[str] = mapped_column(String(200), nullable=False)
    heure_prevue: Mapped[Optional[str]] = mapped_column(String(10))
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    termine_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    routine: Mapped["Routine"] = relationship(back_populates="taches")


# ═══════════════════════════════════════════════════════════
# MAISON
# ═══════════════════════════════════════════════════════════

class Projet(Base):
    """Projet maison (non refactorisé)."""

    __tablename__ = "projets"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    categorie: Mapped[Optional[str]] = mapped_column(String(100))
    date_debut: Mapped[Optional[date]] = mapped_column(Date)
    date_fin: Mapped[Optional[date]] = mapped_column(Date)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne")
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    progression: Mapped[int] = mapped_column(Integer, default=0)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    taches: Mapped[List["TacheProjet"]] = relationship(
        back_populates="projet", cascade="all, delete-orphan"
    )


class TacheProjet(Base):
    """Tâche d'un projet (non refactorisé)."""

    __tablename__ = "taches_projet"

    id: Mapped[int] = mapped_column(primary_key=True)
    projet_id: Mapped[int] = mapped_column(ForeignKey("projets.id", ondelete="CASCADE"))
    nom_tache: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(String(50), default="à faire")
    date_echeance: Mapped[Optional[date]] = mapped_column(Date)
    termine_le: Mapped[Optional[datetime]] = mapped_column(DateTime)

    projet: Mapped["Projet"] = relationship(back_populates="taches")


class ElementJardin(Base):
    """Élément du jardin (non refactorisé)."""

    __tablename__ = "elements_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(100))
    date_plantation: Mapped[Optional[date]] = mapped_column(Date)
    date_recolte: Mapped[Optional[date]] = mapped_column(Date)
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    emplacement: Mapped[Optional[str]] = mapped_column(String(200))
    frequence_arrosage_jours: Mapped[int] = mapped_column(Integer, default=2)
    dernier_arrosage: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    logs: Mapped[List["LogJardin"]] = relationship(
        back_populates="element", cascade="all, delete-orphan"
    )


class LogJardin(Base):
    """Log d'activité jardin (non refactorisé)."""

    __tablename__ = "logs_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)
    element_id: Mapped[int] = mapped_column(ForeignKey("elements_jardin.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    element: Mapped["ElementJardin"] = relationship(back_populates="logs")


# ═══════════════════════════════════════════════════════════
# CALENDRIER
# ═══════════════════════════════════════════════════════════

class EvenementCalendrier(Base):
    """Événement dans le calendrier (non refactorisé)."""

    __tablename__ = "evenements_calendrier"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_fin: Mapped[Optional[datetime]] = mapped_column(DateTime)
    lieu: Mapped[Optional[str]] = mapped_column(String(200))
    categorie: Mapped[Optional[str]] = mapped_column(String(100))
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ═══════════════════════════════════════════════════════════
# UTILISATEURS
# ═══════════════════════════════════════════════════════════

class Utilisateur(Base):
    """Utilisateur de l'application (non refactorisé)."""

    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_utilisateur: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    parametres: Mapped[dict] = mapped_column(JSON, default=dict)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    profils: Mapped[List["ProfilUtilisateur"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="utilisateur", cascade="all, delete-orphan"
    )


class ProfilUtilisateur(Base):
    """Profil d'un utilisateur (non refactorisé)."""

    __tablename__ = "profils_utilisateur"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    nom_profil: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50))
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    est_actif: Mapped[bool] = mapped_column(Boolean, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="profils")


class Notification(Base):
    """Notification utilisateur (non refactorisé)."""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id", ondelete="CASCADE"))
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne")
    lu: Mapped[bool] = mapped_column(Boolean, default=False)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    utilisateur: Mapped["Utilisateur"] = relationship(back_populates="notifications")