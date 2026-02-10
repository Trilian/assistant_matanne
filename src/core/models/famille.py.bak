"""
Modèles pour la famille et le bien-être.

Contient :
- ChildProfile : Profil d'enfant (Jules)
- WellbeingEntry : Entrée de bien-être
- Milestone : Jalon de développement
- FamilyActivity : Activité familiale
- FamilyBudget : Dépenses familiales
- ShoppingItem : Article shopping familial
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
# PROFIL ENFANT
# ═══════════════════════════════════════════════════════════


class ChildProfile(Base):
    """Profil d'un enfant suivi.
    
    Attributes:
        name: Prénom de l'enfant
        date_of_birth: Date de naissance
        gender: Genre
        notes: Notes diverses
        actif: Si le profil est actif
    """

    __tablename__ = "child_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    wellbeing_entries: Mapped[list["WellbeingEntry"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChildProfile(name='{self.name}', id={self.id})>"


class WellbeingEntry(Base):
    """Entrée de bien-être familial.
    
    Attributes:
        child_id: ID de l'enfant (optionnel)
        username: Nom de l'utilisateur adulte
        date: Date de l'entrée
        mood: Humeur
        sleep_hours: Heures de sommeil
        activity: Activité principale
        notes: Notes
    """

    __tablename__ = "wellbeing_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int | None] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE"), index=True
    )
    username: Mapped[str | None] = mapped_column(String(200), index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    mood: Mapped[str | None] = mapped_column(String(100))
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    activity: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped[Optional["ChildProfile"]] = relationship(back_populates="wellbeing_entries")

    def __repr__(self) -> str:
        return f"<WellbeingEntry(id={self.id}, date={self.date}, mood='{self.mood}')>"


# ═══════════════════════════════════════════════════════════
# JALONS DE DÉVELOPPEMENT
# ═══════════════════════════════════════════════════════════


class Milestone(Base):
    """Jalons et apprentissages de l'enfant.
    
    Attributes:
        child_id: ID de l'enfant
        titre: Titre du jalon
        description: Description détaillée
        categorie: Catégorie (langage, motricité, social, cognitif, etc.)
        date_atteint: Date d'acquisition
        photo_url: URL de la photo souvenir
        notes: Notes
    """

    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(
        ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_atteint: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    child: Mapped["ChildProfile"] = relationship(back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Milestone(id={self.id}, titre='{self.titre}', date={self.date_atteint})>"


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS FAMILIALES
# ═══════════════════════════════════════════════════════════


class FamilyActivity(Base):
    """Activités et sorties familiales.
    
    Attributes:
        titre: Titre de l'activité
        description: Description
        type_activite: Type (parc, musée, piscine, jeu_maison, sport, etc.)
        date_prevue: Date prévue
        duree_heures: Durée en heures
        lieu: Lieu de l'activité
        qui_participe: Liste des participants
        age_minimal_recommande: Âge minimum en mois
        cout_estime: Coût estimé
        cout_reel: Coût réel
        statut: Statut (planifié, terminé, annulé)
    """

    __tablename__ = "family_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_activite: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_prevue: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    duree_heures: Mapped[float | None] = mapped_column(Float)
    lieu: Mapped[str | None] = mapped_column(String(200))
    qui_participe: Mapped[list[str] | None] = mapped_column(JSONB)
    age_minimal_recommande: Mapped[int | None] = mapped_column(Integer)
    cout_estime: Mapped[float | None] = mapped_column(Float)
    cout_reel: Mapped[float | None] = mapped_column(Float)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="planifié", index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("duree_heures > 0", name="ck_activite_duree_positive"),
        CheckConstraint("age_minimal_recommande >= 0", name="ck_activite_age_positif"),
    )

    def __repr__(self) -> str:
        return f"<FamilyActivity(id={self.id}, titre='{self.titre}', date={self.date_prevue})>"


# ═══════════════════════════════════════════════════════════
# BUDGET FAMILIAL
# ═══════════════════════════════════════════════════════════


class FamilyBudget(Base):
    """Dépenses familiales par catégorie.
    
    Attributes:
        date: Date de la dépense
        categorie: Catégorie (Jules_jouets, Jules_vetements, Nous_sport, etc.)
        description: Description de la dépense
        montant: Montant dépensé
        magasin: Magasin où l'achat a été fait
        est_recurrent: Si c'est une dépense récurrente
        frequence_recurrence: Fréquence de récurrence (mensuel, hebdomadaire, etc.)
        notes: Notes
    """

    __tablename__ = "family_budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(200))
    montant: Mapped[float] = mapped_column(Float, nullable=False)
    magasin: Mapped[str | None] = mapped_column(String(200))
    est_recurrent: Mapped[bool] = mapped_column(Boolean, default=False)
    frequence_recurrence: Mapped[str | None] = mapped_column(String(50))  # mensuel, hebdomadaire, etc.
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("montant > 0", name="ck_budget_montant_positive"),
    )

    def __repr__(self) -> str:
        return f"<FamilyBudget(id={self.id}, categorie='{self.categorie}', montant={self.montant})>"


# ═══════════════════════════════════════════════════════════
# SHOPPING FAMILIAL
# ═══════════════════════════════════════════════════════════


class ShoppingItem(Base):
    """Article dans une liste de shopping familial.
    
    Attributes:
        titre: Titre de l'article
        categorie: Catégorie
        quantite: Quantité
        prix_estime: Prix estimé
        liste: Liste d'appartenance (Jules, Nous, etc.)
        actif: Si l'article est actif (non acheté)
        date_ajout: Date d'ajout
        date_achat: Date d'achat
    """

    __tablename__ = "shopping_items_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quantite: Mapped[float] = mapped_column(Float, default=1.0)
    prix_estime: Mapped[float] = mapped_column(Float, default=0.0)
    liste: Mapped[str] = mapped_column(String(50), default="Nous", index=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Timestamps
    date_ajout: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    date_achat: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ShoppingItem(titre={self.titre}, categorie={self.categorie}, actif={self.actif})>"
