"""
Modèles pour les utilisateurs et intégrations externes (Garmin).

Contient :
- UserProfile : Profil utilisateur (Anne, Mathieu)
- GarminToken : Tokens OAuth Garmin
- GarminActivity : Activités synchronisées depuis Garmin
- GarminDailySummary : Résumé quotidien Garmin
- WeekendActivity : Activités weekend planifiées
- FamilyPurchase : Achats famille (wishlist)
"""

from datetime import date, datetime
from typing import Optional
from enum import Enum as PyEnum

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
    Enum,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GarminActivityType(str, PyEnum):
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


class PurchaseCategory(str, PyEnum):
    """Catégories d'achats famille"""
    JULES_VETEMENTS = "jules_vetements"
    JULES_JOUETS = "jules_jouets"
    JULES_EQUIPEMENT = "jules_equipement"
    NOUS_JEUX = "nous_jeux"
    NOUS_LOISIRS = "nous_loisirs"
    NOUS_EQUIPEMENT = "nous_equipement"
    MAISON = "maison"


class PurchasePriority(str, PyEnum):
    """Priorité d'achat"""
    URGENT = "urgent"
    HAUTE = "haute"
    MOYENNE = "moyenne"
    BASSE = "basse"
    OPTIONNEL = "optionnel"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PROFIL UTILISATEUR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class UserProfile(Base):
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

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200))
    avatar_emoji: Mapped[str] = mapped_column(String(10), default="ðŸ‘¤")
    
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
    
    # Timestamps
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    garmin_token: Mapped[Optional["GarminToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    garmin_activities: Mapped[list["GarminActivity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    daily_summaries: Mapped[list["GarminDailySummary"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    food_logs: Mapped[list["FoodLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserProfile(username='{self.username}', display_name='{self.display_name}')>"
    
    @property
    def streak_jours(self) -> int:
        """Calcule le streak actuel de jours actifs"""
        # TODO: Implémenter le calcul du streak
        return 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GARMIN OAUTH TOKENS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GarminToken(Base):
    """Tokens OAuth Garmin pour synchronisation.
    
    Garmin utilise OAuth 1.0a, donc on stocke:
    - oauth_token
    - oauth_token_secret
    """

    __tablename__ = "garmin_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    
    # OAuth 1.0a tokens
    oauth_token: Mapped[str] = mapped_column(String(500), nullable=False)
    oauth_token_secret: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Métadonnées
    garmin_user_id: Mapped[str | None] = mapped_column(String(100))
    derniere_sync: Mapped[datetime | None] = mapped_column(DateTime)
    sync_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user: Mapped["UserProfile"] = relationship(back_populates="garmin_token")

    def __repr__(self) -> str:
        return f"<GarminToken(user_id={self.user_id}, sync_active={self.sync_active})>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ACTIVITÉS GARMIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GarminActivity(Base):
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

    __tablename__ = "garmin_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
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
    
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["UserProfile"] = relationship(back_populates="garmin_activities")

    __table_args__ = (
        CheckConstraint("duree_secondes > 0", name="ck_garmin_duree_positive"),
    )

    def __repr__(self) -> str:
        return f"<GarminActivity(id={self.id}, type='{self.type_activite}', date={self.date_debut})>"
    
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RÉSUMÉ QUOTIDIEN GARMIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GarminDailySummary(Base):
    """Résumé quotidien des données Garmin.
    
    Données de Daily Summary API:
    - Pas
    - Calories
    - Distance
    - Minutes actives
    - Fréquence cardiaque au repos
    - Sommeil
    """

    __tablename__ = "garmin_daily_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
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
    
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["UserProfile"] = relationship(back_populates="daily_summaries")

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_garmin_daily_user_date"),
    )

    def __repr__(self) -> str:
        return f"<GarminDailySummary(user_id={self.user_id}, date={self.date}, pas={self.pas})>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOG ALIMENTATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class FoodLog(Base):
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

    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=date.today)
    heure: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Repas
    repas: Mapped[str] = mapped_column(String(50), nullable=False)  # petit_dejeuner, dejeuner, diner, snack
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Nutrition (optionnel)
    calories_estimees: Mapped[int | None] = mapped_column(Integer)
    proteines_g: Mapped[float | None] = mapped_column(Float)
    glucides_g: Mapped[float | None] = mapped_column(Float)
    lipides_g: Mapped[float | None] = mapped_column(Float)
    
    # Évaluation
    qualite: Mapped[int | None] = mapped_column(Integer)  # 1-5 étoiles
    notes: Mapped[str | None] = mapped_column(Text)
    
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    user: Mapped["UserProfile"] = relationship(back_populates="food_logs")

    __table_args__ = (
        CheckConstraint("qualite >= 1 AND qualite <= 5", name="ck_food_qualite_range"),
    )

    def __repr__(self) -> str:
        return f"<FoodLog(user_id={self.user_id}, date={self.date}, repas='{self.repas}')>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ACTIVITÉS WEEKEND
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class WeekendActivity(Base):
    """Activité weekend planifiée.
    
    Attributes:
        titre: Titre de l'activité
        type_activite: Type (parc, musée, piscine, restaurant, etc.)
        date_prevue: Date prévue
        heure_debut: Heure de début
        duree_estimee_h: Durée estimée en heures
        lieu: Lieu
        adresse: Adresse complète
        adapte_jules: Si adapté Ã  Jules
        age_min_mois: Ã‚ge minimum en mois
        cout_estime: Coût estimé
        meteo_requise: Météo requise (ensoleillé, couvert, intérieur)
        note_lieu: Note du lieu (1-5)
        commentaire: Commentaire après visite
    """

    __tablename__ = "weekend_activities"

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
    statut: Mapped[str] = mapped_column(String(50), default="planifié", index=True)  # planifié, terminé, annulé
    note_lieu: Mapped[int | None] = mapped_column(Integer)  # 1-5
    commentaire: Mapped[str | None] = mapped_column(Text)
    a_refaire: Mapped[bool | None] = mapped_column(Boolean)
    
    # Participants
    participants: Mapped[list[str] | None] = mapped_column(JSONB)  # ["Anne", "Mathieu", "Jules"]
    
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("note_lieu >= 1 AND note_lieu <= 5", name="ck_weekend_note_range"),
    )

    def __repr__(self) -> str:
        return f"<WeekendActivity(id={self.id}, titre='{self.titre}', date={self.date_prevue})>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ACHATS FAMILLE (WISHLIST)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class FamilyPurchase(Base):
    """Article Ã  acheter pour la famille (wishlist).
    
    Attributes:
        nom: Nom de l'article
        categorie: Catégorie (jules_vetements, jules_jouets, nous_jeux, etc.)
        priorite: Priorité (urgent, haute, moyenne, basse, optionnel)
        prix_estime: Prix estimé
        url: Lien vers l'article
        taille: Taille (pour vêtements)
        age_recommande: Ã‚ge recommandé (pour jouets)
        achete: Si acheté
        date_achat: Date d'achat
        prix_reel: Prix réel
    """

    __tablename__ = "family_purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Infos article
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    priorite: Mapped[str] = mapped_column(String(50), default="moyenne", index=True)
    
    # Prix
    prix_estime: Mapped[float | None] = mapped_column(Float)
    prix_reel: Mapped[float | None] = mapped_column(Float)
    
    # Infos supplémentaires
    url: Mapped[str | None] = mapped_column(String(500))
    image_url: Mapped[str | None] = mapped_column(String(500))
    magasin: Mapped[str | None] = mapped_column(String(200))
    
    # Pour vêtements
    taille: Mapped[str | None] = mapped_column(String(50))
    
    # Pour jouets
    age_recommande_mois: Mapped[int | None] = mapped_column(Integer)
    
    # Statut
    achete: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    date_achat: Mapped[date | None] = mapped_column(Date)
    
    # Qui a suggéré
    suggere_par: Mapped[str | None] = mapped_column(String(50))  # anne, mathieu, ia
    
    notes: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    modifie_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<FamilyPurchase(id={self.id}, nom='{self.nom}', categorie='{self.categorie}')>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

__all__ = [
    # Enums
    "GarminActivityType",
    "PurchaseCategory", 
    "PurchasePriority",
    # Models
    "UserProfile",
    "GarminToken",
    "GarminActivity",
    "GarminDailySummary",
    "FoodLog",
    "WeekendActivity",
    "FamilyPurchase",
]
