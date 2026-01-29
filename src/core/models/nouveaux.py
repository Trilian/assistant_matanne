"""
Modèles SQLAlchemy pour les nouvelles fonctionnalités.

Contient :
- Depense : Suivi des dépenses (utilisé par budget.py)
- BudgetMensuelDB : Budget mensuel par catégorie
- AlerteMeteo : Alertes météo pour le jardin
- ConfigMeteo : Configuration météo par utilisateur
- Backup : Historique des sauvegardes
- CalendrierExterne : Calendriers synchronisés
- EvenementCalendrier : Événements de calendrier
- PushSubscription : Abonnements notifications push
- NotificationPreference : Préférences de notification

Ces modèles correspondent aux tables SQL créées par migration_new_features_v2.sql
"""

from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class CategorieDepenseDB(str, Enum):
    """Catégories de dépenses (aligné avec contrainte SQL)."""
    ALIMENTATION = "alimentation"
    TRANSPORT = "transport"
    LOGEMENT = "logement"
    SANTE = "sante"
    LOISIRS = "loisirs"
    VETEMENTS = "vetements"
    EDUCATION = "education"
    CADEAUX = "cadeaux"
    ABONNEMENTS = "abonnements"
    RESTAURANT = "restaurant"
    VACANCES = "vacances"
    BEBE = "bebe"
    AUTRE = "autre"


class RecurrenceType(str, Enum):
    """Types de récurrence."""
    PONCTUEL = "ponctuel"
    HEBDOMADAIRE = "hebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"


class NiveauAlerte(str, Enum):
    """Niveaux d'alerte météo."""
    INFO = "info"
    ATTENTION = "attention"
    DANGER = "danger"


class TypeAlerteMeteo(str, Enum):
    """Types d'alertes météo."""
    GEL = "gel"
    CANICULE = "canicule"
    PLUIE_FORTE = "pluie_forte"
    VENT_FORT = "vent_fort"
    GRELE = "grele"
    NEIGE = "neige"


class CalendarProvider(str, Enum):
    """Fournisseurs de calendrier."""
    GOOGLE = "google"
    APPLE = "apple"
    OUTLOOK = "outlook"
    ICAL = "ical"


class SyncDirection(str, Enum):
    """Direction de synchronisation calendrier."""
    IMPORT = "import"
    EXPORT = "export"
    BIDIRECTIONAL = "bidirectional"


# ═══════════════════════════════════════════════════════════
# TABLE DÉPENSES
# ═══════════════════════════════════════════════════════════


class Depense(Base):
    """Dépense familiale.
    
    Table SQL: depenses
    Utilisé par: src/services/budget.py
    
    Attributes:
        montant: Montant de la dépense
        categorie: Catégorie (alimentation, transport, etc.)
        description: Description de la dépense
        date: Date de la dépense
        recurrence: Type de récurrence (ponctuel, mensuel, etc.)
        tags: Tags libres en JSON
        user_id: UUID de l'utilisateur Supabase
    """

    __tablename__ = "depenses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    montant: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, default="autre", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today, index=True)
    recurrence: Mapped[str | None] = mapped_column(String(20))  # 'mensuel', 'hebdomadaire', etc.
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        CheckConstraint(
            "categorie IN ('alimentation', 'transport', 'logement', 'sante', "
            "'loisirs', 'vetements', 'education', 'cadeaux', 'abonnements', "
            "'restaurant', 'vacances', 'bebe', 'autre')",
            name="check_categorie_valide"
        ),
    )

    def __repr__(self) -> str:
        return f"<Depense(id={self.id}, montant={self.montant}, categorie='{self.categorie}')>"

    @property
    def est_recurrente(self) -> bool:
        """Vérifie si la dépense est récurrente."""
        return self.recurrence is not None and self.recurrence != "ponctuel"


# ═══════════════════════════════════════════════════════════
# TABLE BUDGETS MENSUELS
# ═══════════════════════════════════════════════════════════


class BudgetMensuelDB(Base):
    """Budget mensuel par utilisateur.
    
    Table SQL: budgets_mensuels
    
    Attributes:
        mois: Premier jour du mois
        budget_total: Budget total du mois
        budgets_par_categorie: JSON avec budgets par catégorie
        notes: Notes libres
        user_id: UUID de l'utilisateur Supabase
    """

    __tablename__ = "budgets_mensuels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mois: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    budget_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    budgets_par_categorie: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("mois", "user_id", name="uq_budget_mois_user"),
    )

    def __repr__(self) -> str:
        return f"<BudgetMensuelDB(id={self.id}, mois={self.mois}, total={self.budget_total})>"


# ═══════════════════════════════════════════════════════════
# TABLE ALERTES MÉTÉO
# ═══════════════════════════════════════════════════════════


class AlerteMeteo(Base):
    """Alerte météo pour le jardin.
    
    Table SQL: alertes_meteo
    Utilisé par: src/services/weather.py
    
    Attributes:
        type_alerte: Type d'alerte (gel, canicule, etc.)
        niveau: Niveau (info, attention, danger)
        titre: Titre de l'alerte
        message: Message détaillé
        conseil_jardin: Conseil pour le jardin
        date_debut: Date de début de l'alerte
        date_fin: Date de fin
        temperature: Température associée
        lu: Si l'alerte a été lue
    """

    __tablename__ = "alertes_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type_alerte: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    niveau: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    conseil_jardin: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_fin: Mapped[date | None] = mapped_column(Date)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lu: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AlerteMeteo(id={self.id}, type='{self.type_alerte}', niveau='{self.niveau}')>"


# ═══════════════════════════════════════════════════════════
# TABLE CONFIGURATION MÉTÉO
# ═══════════════════════════════════════════════════════════


class ConfigMeteo(Base):
    """Configuration météo par utilisateur.
    
    Table SQL: config_meteo
    
    Attributes:
        latitude: Latitude (par défaut Paris)
        longitude: Longitude (par défaut Paris)
        ville: Nom de la ville
        surface_jardin_m2: Surface du jardin en m²
        notifications_*: Préférences de notifications
    """

    __tablename__ = "config_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("48.8566"))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("2.3522"))
    ville: Mapped[str] = mapped_column(String(100), default="Paris")
    surface_jardin_m2: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("50"))
    
    # Préférences notifications
    notifications_gel: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_canicule: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_pluie: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Supabase user (unique)
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<ConfigMeteo(id={self.id}, ville='{self.ville}')>"


# ═══════════════════════════════════════════════════════════
# TABLE BACKUPS
# ═══════════════════════════════════════════════════════════


class Backup(Base):
    """Historique des sauvegardes.
    
    Table SQL: backups
    Utilisé par: src/services/backup.py
    
    Attributes:
        filename: Nom du fichier de backup
        tables_included: Liste des tables sauvegardées
        row_counts: Compteurs de lignes par table
        size_bytes: Taille en octets
        compressed: Si le backup est compressé
        storage_path: Chemin Supabase Storage
        version: Version du format de backup
    """

    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    tables_included: Mapped[list | None] = mapped_column(JSONB, default=list)
    row_counts: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0)
    compressed: Mapped[bool] = mapped_column(Boolean, default=True)
    storage_path: Mapped[str | None] = mapped_column(String(500))
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<Backup(id={self.id}, filename='{self.filename}', size={self.size_bytes})>"


# ═══════════════════════════════════════════════════════════
# TABLE CALENDRIERS EXTERNES
# ═══════════════════════════════════════════════════════════


class CalendrierExterne(Base):
    """Calendrier externe synchronisé.
    
    Table SQL: calendriers_externes
    Utilisé par: src/services/calendar_sync.py
    
    Attributes:
        provider: Fournisseur (google, apple, outlook, ical)
        nom: Nom du calendrier
        url: URL du calendrier (pour iCal)
        credentials: Tokens OAuth chiffrés
        enabled: Si la synchronisation est active
        sync_interval_minutes: Intervalle de synchro en minutes
        last_sync: Dernière synchronisation
        sync_direction: Direction de synchro
    """

    __tablename__ = "calendriers_externes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    provider: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    credentials: Mapped[dict | None] = mapped_column(JSONB)  # Tokens OAuth
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_sync: Mapped[datetime | None] = mapped_column(DateTime)
    sync_direction: Mapped[str] = mapped_column(String(20), default="bidirectional")
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relations
    evenements: Mapped[list["EvenementCalendrier"]] = relationship(
        back_populates="calendrier_source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<CalendrierExterne(id={self.id}, provider='{self.provider}', nom='{self.nom}')>"


# ═══════════════════════════════════════════════════════════
# TABLE ÉVÉNEMENTS CALENDRIER
# ═══════════════════════════════════════════════════════════


class EvenementCalendrier(Base):
    """Événement de calendrier synchronisé.
    
    Table SQL: evenements_calendrier
    
    Attributes:
        uid: UID iCal unique
        titre: Titre de l'événement
        description: Description
        date_debut: Date/heure de début
        date_fin: Date/heure de fin
        lieu: Lieu
        all_day: Si c'est un événement sur toute la journée
        recurrence_rule: Règle de récurrence RRULE
        rappel_minutes: Rappel avant l'événement
        source_calendrier_id: ID du calendrier source
    """

    __tablename__ = "evenements_calendrier"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uid: Mapped[str] = mapped_column(String(255), nullable=False)
    titre: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    date_fin: Mapped[datetime | None] = mapped_column(DateTime)
    lieu: Mapped[str | None] = mapped_column(String(300))
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(Text)  # RRULE iCal
    rappel_minutes: Mapped[int | None] = mapped_column(Integer)
    
    # Relation calendrier source
    source_calendrier_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("calendriers_externes.id", ondelete="SET NULL")
    )
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint("uid", "user_id", name="uq_event_uid_user"),
    )

    # Relations
    calendrier_source: Mapped[Optional["CalendrierExterne"]] = relationship(
        back_populates="evenements"
    )

    def __repr__(self) -> str:
        return f"<EvenementCalendrier(id={self.id}, titre='{self.titre}', date={self.date_debut})>"


# ═══════════════════════════════════════════════════════════
# TABLE ABONNEMENTS PUSH
# ═══════════════════════════════════════════════════════════


class PushSubscription(Base):
    """Abonnement push notification.
    
    Table SQL: push_subscriptions
    Utilisé par: src/services/push_notifications.py
    
    Attributes:
        endpoint: URL de l'endpoint push
        p256dh_key: Clé p256dh pour le chiffrement
        auth_key: Clé d'authentification
        device_info: Informations sur l'appareil
    """

    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh_key: Mapped[str] = mapped_column(Text, nullable=False)
    auth_key: Mapped[str] = mapped_column(Text, nullable=False)
    device_info: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PushSubscription(id={self.id}, user_id={self.user_id})>"


# ═══════════════════════════════════════════════════════════
# TABLE PRÉFÉRENCES NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class NotificationPreference(Base):
    """Préférences de notification par utilisateur.
    
    Table SQL: notification_preferences
    
    Attributes:
        courses_rappel: Rappel courses
        repas_suggestion: Suggestions de repas
        stock_alerte: Alertes de stock
        meteo_alerte: Alertes météo
        budget_alerte: Alertes budget
        quiet_hours_start: Début des heures silencieuses
        quiet_hours_end: Fin des heures silencieuses
    """

    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    
    # Préférences
    courses_rappel: Mapped[bool] = mapped_column(Boolean, default=True)
    repas_suggestion: Mapped[bool] = mapped_column(Boolean, default=True)
    stock_alerte: Mapped[bool] = mapped_column(Boolean, default=True)
    meteo_alerte: Mapped[bool] = mapped_column(Boolean, default=True)
    budget_alerte: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Heures silencieuses
    quiet_hours_start: Mapped[time | None] = mapped_column(Time, default=time(22, 0))
    quiet_hours_end: Mapped[time | None] = mapped_column(Time, default=time(7, 0))
    
    # Supabase user (unique)
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<NotificationPreference(id={self.id}, user_id={self.user_id})>"
