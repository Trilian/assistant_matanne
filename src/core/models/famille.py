"""
Modèles pour la famille et le bien-être.

Contient :
- ProfilEnfant : Profil d'enfant (Jules)
- EntreeBienEtre : Entrée de bien-être
- Jalon : Jalon de développement (enrichi premières fois)
- ActiviteFamille : Activité familiale
- BudgetFamille : Dépenses familiales
- ArticleAchat : Article shopping familial
- AnniversaireFamille : Anniversaires et rappels
- EvenementFamilial : Événements familiaux récurrents
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

from .base import Base, utc_now
from .mixins import CreeLeMixin

# ═══════════════════════════════════════════════════════════
# PROFIL ENFANT
# ═══════════════════════════════════════════════════════════


class ProfilEnfant(CreeLeMixin, Base):
    """Profil d'un enfant suivi.

    Attributes:
        name: Prénom de l'enfant
        date_of_birth: Date de naissance
        gender: Genre
        notes: Notes diverses
        actif: Si le profil est actif
    """

    __tablename__ = "profils_enfants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relations
    wellbeing_entries: Mapped[list["EntreeBienEtre"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["Jalon"]] = relationship(
        back_populates="child", cascade="all, delete-orphan"
    )
    # Use fully-qualified target names for relationships defined in other modules
    vaccins: Mapped[list["src.core.models.carnet_sante.Vaccin"]] = relationship(  # noqa: F821
        "src.core.models.carnet_sante.Vaccin", back_populates="enfant", cascade="all, delete-orphan"
    )
    rendez_vous: Mapped[list["src.core.models.carnet_sante.RendezVousMedical"]] = relationship(  # noqa: F821
        "src.core.models.carnet_sante.RendezVousMedical",
        back_populates="enfant",
        cascade="all, delete-orphan",
    )
    mesures_croissance: Mapped[list["src.core.models.carnet_sante.MesureCroissance"]] = (
        relationship(  # noqa: F821
            "src.core.models.carnet_sante.MesureCroissance",
            back_populates="enfant",
            cascade="all, delete-orphan",
        )
    )

    def __repr__(self) -> str:
        return f"<ProfilEnfant(name='{self.name}', id={self.id})>"


class EntreeBienEtre(CreeLeMixin, Base):
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

    __tablename__ = "entrees_bien_etre"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int | None] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE"), index=True
    )
    username: Mapped[str | None] = mapped_column(String(200), index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    mood: Mapped[str | None] = mapped_column(String(100))
    sleep_hours: Mapped[float | None] = mapped_column(Float)
    activity: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    child: Mapped[Optional["ProfilEnfant"]] = relationship(back_populates="wellbeing_entries")

    def __repr__(self) -> str:
        return f"<EntreeBienEtre(id={self.id}, date={self.date}, mood='{self.mood}')>"


# ═══════════════════════════════════════════════════════════
# JALONS DE DÉVELOPPEMENT
# ═══════════════════════════════════════════════════════════


class Jalon(CreeLeMixin, Base):
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

    __tablename__ = "jalons"

    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_atteint: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

    # Enrichissement jalons (premières fois)
    contexte_narratif: Mapped[str | None] = mapped_column(Text)  # "Il a dit papa au parc"
    lieu: Mapped[str | None] = mapped_column(String(200))
    emotion_parents: Mapped[str | None] = mapped_column(String(50))  # joie, fierté, émotion
    age_mois_atteint: Mapped[int | None] = mapped_column(Integer)  # calculé automatiquement

    # Relations
    child: Mapped["ProfilEnfant"] = relationship(back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Jalon(id={self.id}, titre='{self.titre}', date={self.date_atteint})>"


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS FAMILIALES
# ═══════════════════════════════════════════════════════════


class ActiviteFamille(CreeLeMixin, Base):
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

    __tablename__ = "activites_famille"

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

    __table_args__ = (
        CheckConstraint("duree_heures > 0", name="ck_activite_duree_positive"),
        CheckConstraint("age_minimal_recommande >= 0", name="ck_activite_age_positif"),
    )

    def __repr__(self) -> str:
        return f"<ActiviteFamille(id={self.id}, titre='{self.titre}', date={self.date_prevue})>"


# ═══════════════════════════════════════════════════════════
# BUDGET FAMILIAL
# ═══════════════════════════════════════════════════════════


class BudgetFamille(CreeLeMixin, Base):
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

    __tablename__ = "budgets_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(200))
    montant: Mapped[float] = mapped_column(Float, nullable=False)
    magasin: Mapped[str | None] = mapped_column(String(200))
    est_recurrent: Mapped[bool] = mapped_column(Boolean, default=False)
    frequence_recurrence: Mapped[str | None] = mapped_column(
        String(50)
    )  # mensuel, hebdomadaire, etc.
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (CheckConstraint("montant > 0", name="ck_budget_montant_positive"),)

    def __repr__(self) -> str:
        return (
            f"<BudgetFamille(id={self.id}, categorie='{self.categorie}', montant={self.montant})>"
        )


# ═══════════════════════════════════════════════════════════
# SHOPPING FAMILIAL
# ═══════════════════════════════════════════════════════════


class ArticleAchat(Base):
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

    __tablename__ = "articles_achats_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quantite: Mapped[float] = mapped_column(Float, default=1.0)
    prix_estime: Mapped[float] = mapped_column(Float, default=0.0)
    liste: Mapped[str] = mapped_column(String(50), default="Nous", index=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Timestamps
    date_ajout: Mapped[datetime] = mapped_column(DateTime, default=utc_now, index=True)
    date_achat: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ArticleAchat(titre={self.titre}, categorie={self.categorie}, actif={self.actif})>"


# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES ET ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════


class AnniversaireFamille(CreeLeMixin, Base):
    """Anniversaire d'un membre de la famille ou proche.

    Attributes:
        nom_personne: Nom de la personne
        date_naissance: Date de naissance
        relation: Relation (parent, enfant, grand_parent, oncle_tante, cousin, ami, collègue)
        rappel_jours_avant: Jours avant pour rappel (JSONB array: [7, 1, 0])
        idees_cadeaux: Idées de cadeaux (texte libre)
        historique_cadeaux: Historique des cadeaux offerts (JSONB)
        notes: Notes
        actif: Si actif
    """

    __tablename__ = "anniversaires_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom_personne: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    date_naissance: Mapped[date] = mapped_column(Date, nullable=False)
    relation: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # parent, enfant, grand_parent, oncle_tante, cousin, ami, collègue
    rappel_jours_avant: Mapped[list[int] | None] = mapped_column(
        JSONB, default=[7, 1, 0]
    )  # [7, 1, 0] = J-7, J-1, Jour J
    idees_cadeaux: Mapped[str | None] = mapped_column(Text)
    historique_cadeaux: Mapped[list[dict] | None] = mapped_column(
        JSONB
    )  # [{"annee": 2025, "cadeau": "Livre", "budget": 30}]
    notes: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    @property
    def age(self) -> int:
        """Calcule l'âge actuel de la personne."""
        today = date.today()
        return (
            today.year
            - self.date_naissance.year
            - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
        )

    @property
    def prochain_anniversaire(self) -> date:
        """Retourne la date du prochain anniversaire."""
        today = date.today()
        anniv_cette_annee = self.date_naissance.replace(year=today.year)
        if anniv_cette_annee < today:
            return self.date_naissance.replace(year=today.year + 1)
        return anniv_cette_annee

    @property
    def jours_restants(self) -> int:
        """Nombre de jours avant le prochain anniversaire."""
        return (self.prochain_anniversaire - date.today()).days

    def __repr__(self) -> str:
        return (
            f"<AnniversaireFamille(id={self.id}, nom='{self.nom_personne}', "
            f"relation='{self.relation}', age={self.age})>"
        )


class EvenementFamilial(CreeLeMixin, Base):
    """Événement familial récurrent ou ponctuel.

    Attributes:
        titre: Titre de l'événement
        date_evenement: Date de l'événement
        type_evenement: Type (anniversaire, fete, vacances, rentree, tradition)
        recurrence: Récurrence (annuelle, mensuelle, unique)
        rappel_jours_avant: Jours avant pour rappel
        notes: Notes
        participants: Liste des participants (JSONB)
        actif: Si actif
    """

    __tablename__ = "evenements_familiaux"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    date_evenement: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type_evenement: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # anniversaire, fete, vacances, rentree, tradition
    recurrence: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unique"
    )  # annuelle, mensuelle, unique
    rappel_jours_avant: Mapped[int] = mapped_column(Integer, default=7)
    notes: Mapped[str | None] = mapped_column(Text)
    participants: Mapped[list[str] | None] = mapped_column(JSONB)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    def __repr__(self) -> str:
        return (
            f"<EvenementFamilial(id={self.id}, titre='{self.titre}', "
            f"date={self.date_evenement}, type='{self.type_evenement}')>"
        )
