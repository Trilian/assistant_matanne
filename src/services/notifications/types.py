"""
Types et modèles pour le package notifications.

Centralise toutes les enums et modèles Pydantic pour les services de notifications.
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class TypeAlerte(str, Enum):
    """Types d'alertes pour l'inventaire (notifications locales)."""

    STOCK_CRITIQUE = "stock_critique"
    STOCK_BAS = "stock_bas"
    PEREMPTION_PROCHE = "peremption_proche"
    PEREMPTION_DEPASSEE = "peremption_depassee"
    ARTICLE_AJOUTE = "article_ajoute"
    ARTICLE_MODIFIE = "article_modifie"


class TypeNotification(str, Enum):
    """Types de notifications push (Web Push et ntfy)."""

    # Alertes importantes
    STOCK_BAS = "stock_low"
    STOCK_LOW = "stock_low"  # Alias rétrocompat
    PEREMPTION_ALERTE = "expiration_warning"
    EXPIRATION_WARNING = "expiration_warning"  # Alias rétrocompat
    PEREMPTION_CRITIQUE = "expiration_critical"
    EXPIRATION_CRITICAL = "expiration_critical"  # Alias rétrocompat

    # Planning
    RAPPEL_REPAS = "meal_reminder"
    MEAL_REMINDER = "meal_reminder"  # Alias rétrocompat
    RAPPEL_ACTIVITE = "activity_reminder"
    ACTIVITY_REMINDER = "activity_reminder"  # Alias rétrocompat

    # Courses
    LISTE_PARTAGEE = "shopping_list_shared"
    SHOPPING_LIST_SHARED = "shopping_list_shared"  # Alias rétrocompat
    LISTE_MISE_A_JOUR = "shopping_list_updated"
    SHOPPING_LIST_UPDATED = "shopping_list_updated"  # Alias rétrocompat

    # Famille
    RAPPEL_JALON = "milestone_reminder"
    MILESTONE_REMINDER = "milestone_reminder"  # Alias rétrocompat
    RAPPEL_SANTE = "health_check_reminder"
    HEALTH_CHECK_REMINDER = "health_check_reminder"  # Alias rétrocompat

    # Système
    MISE_A_JOUR_SYSTEME = "system_update"
    SYSTEM_UPDATE = "system_update"  # Alias rétrocompat
    SYNC_TERMINEE = "sync_complete"
    SYNC_COMPLETE = "sync_complete"  # Alias rétrocompat


# ═══════════════════════════════════════════════════════════
# MODÈLES - NOTIFICATIONS INVENTAIRE (locales)
# ═══════════════════════════════════════════════════════════


class NotificationInventaire(BaseModel):
    """Notification locale pour l'inventaire."""

    id: int | None = None
    type_alerte: TypeAlerte
    article_id: int
    ingredient_id: int
    titre: str = Field(..., min_length=5)
    message: str = Field(..., min_length=10)
    icone: str = "ℹ️"
    date_creation: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lue: bool = False
    priorite: Literal["haute", "moyenne", "basse"] = "moyenne"
    email: str | None = None
    push_envoyee: bool = False


# ═══════════════════════════════════════════════════════════
# MODÈLES - NOTIFICATIONS NTFY.SH
# ═══════════════════════════════════════════════════════════


class ConfigurationNtfy(BaseModel):
    """Configuration des notifications push ntfy.sh pour un utilisateur."""

    topic: str = Field(default="matanne-famille")
    actif: bool = Field(default=True)
    rappels_taches: bool = Field(default=True)
    rappels_courses: bool = Field(default=False)
    heure_digest: int = Field(default=8, ge=0, le=23)
    jours_digest: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])


class NotificationNtfy(BaseModel):
    """Une notification à envoyer via ntfy.sh."""

    titre: str
    message: str
    priorite: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
    click_url: str | None = None
    actions: list[dict] = Field(default_factory=list)


class ResultatEnvoiNtfy(BaseModel):
    """Résultat d'envoi de notification ntfy.sh."""

    succes: bool
    message: str
    notification_id: str | None = None


# ═══════════════════════════════════════════════════════════
# MODÈLES - NOTIFICATIONS WEB PUSH
# ═══════════════════════════════════════════════════════════


class AbonnementPush(BaseModel):
    """Abonnement push d'un utilisateur (Web Push API)."""

    id: int | None = None
    user_id: str
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: datetime | None = None
    is_active: bool = True


class NotificationPush(BaseModel):
    """Notification push à envoyer via Web Push API."""

    id: int | None = None
    title: str
    body: str
    icon: str = "/static/icons/icon-192x192.png"
    badge: str = "/static/icons/badge-72x72.png"
    tag: str | None = None
    notification_type: TypeNotification = TypeNotification.MISE_A_JOUR_SYSTEME
    url: str = "/"
    data: dict = Field(default_factory=dict)
    actions: list[dict] = Field(default_factory=list)
    vibrate: list[int] = Field(default_factory=lambda: [100, 50, 100])
    require_interaction: bool = False
    silent: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class PreferencesNotification(BaseModel):
    """Préférences de notification d'un utilisateur."""

    user_id: str

    # Catégories activées (avec alias anglais pour rétrocompatibilité)
    alertes_stock: bool = Field(default=True, alias="stock_alerts")
    alertes_peremption: bool = Field(default=True, alias="expiration_alerts")
    rappels_repas: bool = Field(default=True, alias="meal_reminders")
    rappels_activites: bool = Field(default=True, alias="activity_reminders")
    mises_a_jour_courses: bool = Field(default=True, alias="shopping_updates")
    rappels_famille: bool = Field(default=True, alias="family_reminders")
    mises_a_jour_systeme: bool = Field(default=False, alias="system_updates")

    # Horaires de silence (avec alias anglais)
    heures_silencieuses_debut: int | None = Field(default=22, alias="quiet_hours_start")
    heures_silencieuses_fin: int | None = Field(default=7, alias="quiet_hours_end")

    # Fréquence
    max_par_heure: int = Field(default=5, alias="max_per_hour")
    mode_digest: bool = Field(default=False, alias="digest_mode")

    # Permettre à la fois les noms français et anglais lors de l'initialisation
    model_config = {"populate_by_name": True}

    # Propriétés d'accès avec les noms anglais pour rétrocompatibilité
    @property
    def stock_alerts(self) -> bool:
        return self.alertes_stock

    @property
    def expiration_alerts(self) -> bool:
        return self.alertes_peremption

    @property
    def meal_reminders(self) -> bool:
        return self.rappels_repas

    @property
    def activity_reminders(self) -> bool:
        return self.rappels_activites

    @property
    def shopping_updates(self) -> bool:
        return self.mises_a_jour_courses

    @property
    def family_reminders(self) -> bool:
        return self.rappels_famille

    @property
    def system_updates(self) -> bool:
        return self.mises_a_jour_systeme

    @property
    def quiet_hours_start(self) -> int | None:
        return self.heures_silencieuses_debut

    @property
    def quiet_hours_end(self) -> int | None:
        return self.heures_silencieuses_fin

    @property
    def max_per_hour(self) -> int:
        return self.max_par_heure

    @property
    def digest_mode(self) -> bool:
        return self.mode_digest


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

NTFY_BASE_URL = "https://ntfy.sh"
DEFAULT_TOPIC = "matanne-famille"

PRIORITY_MAPPING = {"urgente": 5, "haute": 4, "normale": 3, "basse": 2, "min": 1}

# Clés VAPID pour Web Push
VAPID_PUBLIC_KEY = (
    "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U"
)
VAPID_PRIVATE_KEY = ""  # À configurer via variable d'environnement
VAPID_EMAIL = "mailto:contact@assistant-matanne.fr"


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "TypeAlerte",
    "TypeNotification",
    # Modèles inventaire
    "NotificationInventaire",
    # Modèles ntfy
    "ConfigurationNtfy",
    "NotificationNtfy",
    "ResultatEnvoiNtfy",
    # Modèles Web Push
    "AbonnementPush",
    "NotificationPush",
    "PreferencesNotification",
    # Constantes
    "NTFY_BASE_URL",
    "DEFAULT_TOPIC",
    "PRIORITY_MAPPING",
    "VAPID_PUBLIC_KEY",
    "VAPID_PRIVATE_KEY",
    "VAPID_EMAIL",
]
