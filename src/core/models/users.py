"""
Modèles pour les utilisateurs et intégrations externes (Garmin).

Contient :
- ProfilUtilisateur : Profil utilisateur (Anne, Mathieu)
- GarminToken : Tokens OAuth Garmin
- ActiviteGarmin : Activités synchronisées depuis Garmin
- ResumeQuotidienGarmin : Résumé quotidien Garmin
- ActiviteWeekend : Activités weekend planifiées
- AchatFamille : Achats famille (wishlist)
"""

from datetime import date, datetime
from enum import StrEnum
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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now
from .mixins import CreeLeMixin, TimestampMixin

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class GarminActivityType(StrEnum):
    """Types d'activités Garmin"""

    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WALKING = "walking"
    HIKING = "hiking"
    STRENGTH = "strength"
    YOGA = "yoga"
    CARDIO = "cardio"
    OTHER = "other"


class CategorieAchat(StrEnum):
    """Catégories d'achats famille"""

    JULES_VETEMENTS = "jules_vetements"
    JULES_JOUETS = "jules_jouets"
    JULES_EQUIPEMENT = "jules_equipement"
    NOUS_JEUX = "nous_jeux"
    NOUS_LOISIRS = "nous_loisirs"
    NOUS_EQUIPEMENT = "nous_equipement"
    MAISON = "maison"


class PrioriteAchat(StrEnum):
    """Priorité d'achat"""

    URGENT = "urgent"
    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"
    OPTIONNEL = "optionnel"


# ═══════════════════════════════════════════════════════════
# PROFIL UTILISATEUR
# ═══════════════════════════════════════════════════════════


class ProfilUtilisateur(TimestampMixin, Base):
    """Profil utilisateur (Anne ou Mathieu).

    Attributes:
        username: Identifiant unique (anne, mathieu)
        display_name: Nom affiché
        email: Email (optionnel)
        avatar_emoji: Emoji avatar
        date_naissance: Date de naissance (pour calculs santé)
        taille_cm: Taille en cm
        poids_kg: Poids actuel en kg
        objectif_poids_kg: Objectif de poids
        objectif_pas_quotidien: Objectif de pas par jour
        objectif_calories_brulees: Objectif calories brûlées/jour
        garmin_connected: Si Garmin est connecté
    """

    __tablename__ = "profils_utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200))
    avatar_emoji: Mapped[str] = mapped_column(String(10), default="👤")

    # Infos santé
    date_naissance: Mapped[date | None] = mapped_column(Date)
    taille_cm: Mapped[int | None] = mapped_column(Integer)
    poids_kg: Mapped[float | None] = mapped_column(Float)
    objectif_poids_kg: Mapped[float | None] = mapped_column(Float)

    # Objectifs fitness
    objectif_pas_quotidien: Mapped[int] = mapped_column(Integer, default=10000)
    objectif_calories_brulees: Mapped[int] = mapped_column(Integer, default=500)
    objectif_minutes_actives: Mapped[int] = mapped_column(Integer, default=30)

    # Garmin
    garmin_connected: Mapped[bool] = mapped_column(Boolean, default=False)

    # Sécurité
    pin_hash: Mapped[str | None] = mapped_column(String(255))
    sections_protegees: Mapped[list | None] = mapped_column(JSONB)

    # 2FA (TOTP)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(255))
    backup_codes: Mapped[list | None] = mapped_column(JSONB)

    # Préférences avancées
    preferences_modules: Mapped[dict | None] = mapped_column(JSONB)
    theme_prefere: Mapped[str] = mapped_column(String(20), default="auto")

    # Relations
    garmin_token: Mapped[Optional["GarminToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    garmin_activities: Mapped[list["ActiviteGarmin"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_summaries: Mapped[list["ResumeQuotidienGarmin"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    food_logs: Mapped[list["JournalAlimentaire"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ProfilUtilisateur(username='{self.username}', display_name='{self.display_name}')>"
        )

    @property
    def streak_jours(self) -> int:
        """Calcule le streak actuel de jours actifs consécutifs.

        Compte le nombre de jours consécutifs (en remontant depuis aujourd'hui)
        où l'utilisateur a au moins un JournalAlimentaire enregistré.
        """
        if not self.food_logs:
            return 0

        from datetime import timedelta

        dates_actives: set[date] = {log.date for log in self.food_logs}
        streak = 0
        jour = date.today()

        # Inclure aujourd'hui s'il y a un log
        if jour in dates_actives:
            streak += 1
            jour -= timedelta(days=1)
        else:
            # Commencer depuis hier
            jour -= timedelta(days=1)

        while jour in dates_actives:
            streak += 1
            jour -= timedelta(days=1)

        return streak


# ═══════════════════════════════════════════════════════════
# GARMIN OAUTH TOKENS
# ═══════════════════════════════════════════════════════════


class GarminToken(TimestampMixin, Base):
    """Tokens OAuth Garmin pour synchronisation.

    Garmin utilise OAuth 1.0a, donc on stocke:
    - oauth_token
    - oauth_token_secret
    """

    __tablename__ = "garmin_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # OAuth 1.0a tokens
    oauth_token: Mapped[str] = mapped_column(String(500), nullable=False)
    oauth_token_secret: Mapped[str] = mapped_column(String(500), nullable=False)

    # Métadonnées
    garmin_user_id: Mapped[str | None] = mapped_column(String(100))
    derniere_sync: Mapped[datetime | None] = mapped_column(DateTime)
    sync_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relations
    user: Mapped["ProfilUtilisateur"] = relationship(back_populates="garmin_token")

    def __repr__(self) -> str:
        return f"<GarminToken(user_id={self.user_id}, sync_active={self.sync_active})>"


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS GARMIN
# ═══════════════════════════════════════════════════════════


class ActiviteGarmin(CreeLeMixin, Base):
    """Activité sportive synchronisée depuis Garmin.

    Attributes:
        garmin_activity_id: ID unique Garmin
        type_activite: Type (running, cycling, etc.)
        nom: Nom de l'activité
        date_debut: Date/heure de début
        duree_secondes: Durée en secondes
        distance_metres: Distance en mètres
        calories: Calories brûlées
        fc_moyenne: Fréquence cardiaque moyenne
        fc_max: Fréquence cardiaque max
        vitesse_moyenne: Vitesse moyenne (m/s)
        elevation_gain: Dénivelé positif (m)
    """

    __tablename__ = "activites_garmin"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    garmin_activity_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Infos activité
    type_activite: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Timing
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duree_secondes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Métriques
    distance_metres: Mapped[float | None] = mapped_column(Float)
    calories: Mapped[int | None] = mapped_column(Integer)
    fc_moyenne: Mapped[int | None] = mapped_column(Integer)
    fc_max: Mapped[int | None] = mapped_column(Integer)
    vitesse_moyenne: Mapped[float | None] = mapped_column(Float)
    allure_moyenne: Mapped[float | None] = mapped_column(Float)  # min/km
    elevation_gain: Mapped[int | None] = mapped_column(Integer)

    # Données brutes Garmin (JSON)
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    cree_le: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Relations
    user: Mapped["ProfilUtilisateur"] = relationship(back_populates="garmin_activities")

    __table_args__ = (CheckConstraint("duree_secondes > 0", name="ck_garmin_duree_positive"),)

    def __repr__(self) -> str:
        return (
            f"<ActiviteGarmin(id={self.id}, type='{self.type_activite}', date={self.date_debut})>"
        )

    @property
    def duree_formatted(self) -> str:
        """Durée formatée HH:MM:SS"""
        h = self.duree_secondes // 3600
        m = (self.duree_secondes % 3600) // 60
        s = self.duree_secondes % 60
        if h > 0:
            return f"{h}h{m:02d}m{s:02d}s"
        return f"{m}m{s:02d}s"

    @property
    def distance_km(self) -> float:
        """Distance en km"""
        return (self.distance_metres or 0) / 1000


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ QUOTIDIEN GARMIN
# ═══════════════════════════════════════════════════════════


class ResumeQuotidienGarmin(CreeLeMixin, Base):
    """Résumé quotidien des données Garmin.

    Données de Daily Summary API:
    - Pas
    - Calories
    - Distance
    - Minutes actives
    - Fréquence cardiaque au repos
    - Sommeil
    """

    __tablename__ = "resumes_quotidiens_garmin"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Activité
    pas: Mapped[int] = mapped_column(Integer, default=0)
    distance_metres: Mapped[int] = mapped_column(Integer, default=0)
    calories_totales: Mapped[int] = mapped_column(Integer, default=0)
    calories_actives: Mapped[int] = mapped_column(Integer, default=0)
    minutes_actives: Mapped[int] = mapped_column(Integer, default=0)
    minutes_tres_actives: Mapped[int] = mapped_column(Integer, default=0)

    # CÅ“ur
    fc_repos: Mapped[int | None] = mapped_column(Integer)
    fc_min: Mapped[int | None] = mapped_column(Integer)
    fc_max: Mapped[int | None] = mapped_column(Integer)

    # Sommeil
    sommeil_total_minutes: Mapped[int | None] = mapped_column(Integer)
    sommeil_profond_minutes: Mapped[int | None] = mapped_column(Integer)
    sommeil_leger_minutes: Mapped[int | None] = mapped_column(Integer)
    sommeil_rem_minutes: Mapped[int | None] = mapped_column(Integer)

    # Stress & Body Battery
    stress_moyen: Mapped[int | None] = mapped_column(Integer)
    body_battery_max: Mapped[int | None] = mapped_column(Integer)
    body_battery_min: Mapped[int | None] = mapped_column(Integer)

    # Données brutes
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    # Relations
    user: Mapped["ProfilUtilisateur"] = relationship(back_populates="daily_summaries")

    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_garmin_daily_user_date"),)

    def __repr__(self) -> str:
        return f"<ResumeQuotidienGarmin(user_id={self.user_id}, date={self.date}, pas={self.pas})>"


# ═══════════════════════════════════════════════════════════
# LOG ALIMENTATION
# ═══════════════════════════════════════════════════════════


class JournalAlimentaire(CreeLeMixin, Base):
    """Log d'alimentation quotidien.

    Attributes:
        repas: Type de repas (petit_dejeuner, dejeuner, diner, snack)
        description: Description du repas
        calories_estimees: Calories estimées
        proteines_g: Protéines en grammes
        glucides_g: Glucides en grammes
        lipides_g: Lipides en grammes
        qualite: Note qualité (1-5)
    """

    __tablename__ = "journaux_alimentaires"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("profils_utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    heure: Mapped[datetime | None] = mapped_column(DateTime)

    # Repas
    repas: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # petit_dejeuner, dejeuner, diner, snack
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Nutrition (optionnel)
    calories_estimees: Mapped[int | None] = mapped_column(Integer)
    proteines_g: Mapped[float | None] = mapped_column(Float)
    glucides_g: Mapped[float | None] = mapped_column(Float)
    lipides_g: Mapped[float | None] = mapped_column(Float)

    # Évaluation
    qualite: Mapped[int | None] = mapped_column(Integer)  # 1-5 étoiles
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    user: Mapped["ProfilUtilisateur"] = relationship(back_populates="food_logs")

    __table_args__ = (
        CheckConstraint(
            "qualite IS NULL OR (qualite >= 1 AND qualite <= 5)",
            name="ck_food_qualite_range",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<JournalAlimentaire(user_id={self.user_id}, date={self.date}, repas='{self.repas}')>"
        )


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS WEEKEND
# ═══════════════════════════════════════════════════════════


class ActiviteWeekend(TimestampMixin, Base):
    """Activité weekend planifiée.

    Attributes:
        titre: Titre de l'activité
        type_activite: Type (parc, musée, piscine, restaurant, etc.)
        date_prevue: Date prévue
        heure_debut: Heure de début
        duree_estimee_h: Durée estimée en heures
        lieu: Lieu
        adresse: Adresse complète
        adapte_jules: Si adapté à Jules
        age_min_mois: Âge minimum en mois
        cout_estime: Coût estimé
        meteo_requise: Météo requise (ensoleillé, couvert, intérieur)
        note_lieu: Note du lieu (1-5)
        commentaire: Commentaire après visite
    """

    __tablename__ = "activites_weekend"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Infos de base
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_activite: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Planning
    date_prevue: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[str | None] = mapped_column(String(10))  # "14:00"
    duree_estimee_h: Mapped[float | None] = mapped_column(Float)

    # Lieu
    lieu: Mapped[str | None] = mapped_column(String(200))
    adresse: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    # Adapté enfant
    adapte_jules: Mapped[bool] = mapped_column(Boolean, default=True)
    age_min_mois: Mapped[int | None] = mapped_column(Integer)

    # Budget
    cout_estime: Mapped[float | None] = mapped_column(Float)
    cout_reel: Mapped[float | None] = mapped_column(Float)

    # Météo
    meteo_requise: Mapped[str | None] = mapped_column(String(50))  # ensoleillé, couvert, intérieur

    # Feedback
    statut: Mapped[str] = mapped_column(
        String(50), default="planifié", index=True
    )  # planifié, terminé, annulé
    note_lieu: Mapped[int | None] = mapped_column(Integer)  # 1-5
    commentaire: Mapped[str | None] = mapped_column(Text)
    a_refaire: Mapped[bool | None] = mapped_column(Boolean)

    # Participants
    participants: Mapped[list[str] | None] = mapped_column(JSONB)  # ["Anne", "Mathieu", "Jules"]

    __table_args__ = (
        CheckConstraint(
            "note_lieu IS NULL OR (note_lieu >= 1 AND note_lieu <= 5)",
            name="ck_weekend_note_range",
        ),
    )

    def __repr__(self) -> str:
        return f"<ActiviteWeekend(id={self.id}, titre='{self.titre}', date={self.date_prevue})>"


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "GarminActivityType",
    "CategorieAchat",
    "PrioriteAchat",
    # Models
    "ProfilUtilisateur",
    "GarminToken",
    "ActiviteGarmin",
    "ResumeQuotidienGarmin",
    "JournalAlimentaire",
    "ActiviteWeekend",
    # AchatFamille is defined in famille.py (canonical Phase P version)
]
