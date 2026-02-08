"""
Fonctions utilitaires pures pour le service de notifications push.

Ces fonctions peuvent être testées sans base de données ni dépendances externes.
Elles représentent la logique métier pure extraite de push_notifications.py.
"""

import json
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class NotificationType(str, Enum):
    """Types de notifications push."""
    # Alertes importantes
    STOCK_LOW = "stock_low"
    EXPIRATION_WARNING = "expiration_warning"
    EXPIRATION_CRITICAL = "expiration_critical"
    
    # Planning
    MEAL_REMINDER = "meal_reminder"
    ACTIVITY_REMINDER = "activity_reminder"
    
    # Courses
    SHOPPING_LIST_SHARED = "shopping_list_shared"
    SHOPPING_LIST_UPDATED = "shopping_list_updated"
    
    # Famille
    MILESTONE_REMINDER = "milestone_reminder"
    HEALTH_CHECK_REMINDER = "health_check_reminder"
    
    # Système
    SYSTEM_UPDATE = "system_update"
    SYNC_COMPLETE = "sync_complete"


# ═══════════════════════════════════════════════════════════
# VÉRIFICATION DES PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


def get_notification_type_mapping() -> dict[NotificationType, str]:
    """
    Retourne le mapping entre types de notification et préférences utilisateur.
    
    Returns:
        Dict {NotificationType: nom_preference}
    """
    return {
        NotificationType.STOCK_LOW: "stock_alerts",
        NotificationType.EXPIRATION_WARNING: "expiration_alerts",
        NotificationType.EXPIRATION_CRITICAL: "expiration_alerts",
        NotificationType.MEAL_REMINDER: "meal_reminders",
        NotificationType.ACTIVITY_REMINDER: "activity_reminders",
        NotificationType.SHOPPING_LIST_SHARED: "shopping_updates",
        NotificationType.SHOPPING_LIST_UPDATED: "shopping_updates",
        NotificationType.MILESTONE_REMINDER: "family_reminders",
        NotificationType.HEALTH_CHECK_REMINDER: "family_reminders",
        NotificationType.SYSTEM_UPDATE: "system_updates",
        NotificationType.SYNC_COMPLETE: "system_updates",
    }


def check_notification_type_enabled(
    notification_type: NotificationType | str,
    preferences: dict
) -> bool:
    """
    Vérifie si un type de notification est activé pour l'utilisateur.
    
    Args:
        notification_type: Type de notification
        preferences: Dict des préférences utilisateur
        
    Returns:
        True si le type est activé
        
    Examples:
        >>> prefs = {'stock_alerts': True, 'system_updates': False}
        >>> check_notification_type_enabled(NotificationType.STOCK_LOW, prefs)
        True
        >>> check_notification_type_enabled(NotificationType.SYSTEM_UPDATE, prefs)
        False
    """
    if isinstance(notification_type, str):
        try:
            notification_type = NotificationType(notification_type)
        except ValueError:
            return True  # Type inconnu, activer par défaut
    
    mapping = get_notification_type_mapping()
    pref_key = mapping.get(notification_type, None)
    
    if pref_key is None:
        return True  # Type sans préférence, activer par défaut
    
    return preferences.get(pref_key, True)


# ═══════════════════════════════════════════════════════════
# GESTION DES HEURES SILENCIEUSES
# ═══════════════════════════════════════════════════════════


def is_quiet_hours(
    current_hour: int,
    quiet_start: int | None,
    quiet_end: int | None
) -> bool:
    """
    Vérifie si l'heure courante est dans la période silencieuse.
    
    Gère le cas où la période silencieuse passe par minuit
    (ex: 22h -> 7h).
    
    Args:
        current_hour: Heure actuelle (0-23)
        quiet_start: Heure de début de silence (None = pas de silence)
        quiet_end: Heure de fin de silence
        
    Returns:
        True si dans les heures silencieuses
        
    Examples:
        >>> is_quiet_hours(23, 22, 7)  # 23h, silence 22h->7h
        True
        >>> is_quiet_hours(10, 22, 7)  # 10h, silence 22h->7h
        False
        >>> is_quiet_hours(10, None, None)  # Pas de silence
        False
    """
    if quiet_start is None or quiet_end is None:
        return False
    
    # Valider l'heure
    if not 0 <= current_hour <= 23:
        return False
    
    if quiet_start > quiet_end:
        # Passe par minuit (ex: 22h -> 7h)
        # Silence si >= 22 OU < 7
        return current_hour >= quiet_start or current_hour < quiet_end
    else:
        # Normal (ex: 1h -> 6h)
        return quiet_start <= current_hour < quiet_end


def can_send_during_quiet_hours(notification_type: NotificationType | str) -> bool:
    """
    Vérifie si un type de notification peut être envoyé pendant les heures silencieuses.
    
    Certaines notifications critiques sont toujours envoyées.
    
    Args:
        notification_type: Type de notification
        
    Returns:
        True si peut être envoyé pendant silence
        
    Examples:
        >>> can_send_during_quiet_hours(NotificationType.EXPIRATION_CRITICAL)
        True
        >>> can_send_during_quiet_hours(NotificationType.MEAL_REMINDER)
        False
    """
    if isinstance(notification_type, str):
        try:
            notification_type = NotificationType(notification_type)
        except ValueError:
            return False
    
    # Seules les alertes critiques passent
    critical_types = {
        NotificationType.EXPIRATION_CRITICAL,
    }
    
    return notification_type in critical_types


def should_send_notification(
    notification_type: NotificationType | str,
    preferences: dict,
    current_hour: int | None = None,
    sent_count_this_hour: int = 0
) -> tuple[bool, str]:
    """
    Vérifie si une notification doit être envoyée.
    
    Prend en compte:
    - Les préférences utilisateur
    - Les heures silencieuses
    - La limite par heure
    
    Args:
        notification_type: Type de notification
        preferences: Préférences utilisateur
        current_hour: Heure actuelle (None = auto)
        sent_count_this_hour: Nombre de notifications déjà envoyées cette heure
        
    Returns:
        Tuple (should_send, reason)
        
    Examples:
        >>> prefs = {'stock_alerts': True, 'max_per_hour': 5, 'quiet_hours_start': 22, 'quiet_hours_end': 7}
        >>> should_send_notification(NotificationType.STOCK_LOW, prefs, current_hour=10)
        (True, '')
    """
    if current_hour is None:
        current_hour = datetime.now().hour
    
    # 1. Vérifier si le type est activé
    if not check_notification_type_enabled(notification_type, preferences):
        return False, "Type de notification désactivé"
    
    # 2. Vérifier les heures silencieuses
    quiet_start = preferences.get("quiet_hours_start")
    quiet_end = preferences.get("quiet_hours_end")
    
    if is_quiet_hours(current_hour, quiet_start, quiet_end):
        if not can_send_during_quiet_hours(notification_type):
            return False, "Heures silencieuses actives"
    
    # 3. Vérifier la limite par heure
    max_per_hour = preferences.get("max_per_hour", 5)
    if sent_count_this_hour >= max_per_hour:
        return False, f"Limite par heure atteinte ({max_per_hour})"
    
    return True, ""


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DE PAYLOADS
# ═══════════════════════════════════════════════════════════


def build_push_payload(notification: dict) -> str:
    """
    Construit le payload JSON pour Web Push.
    
    Args:
        notification: Dict avec title, body, icon, etc.
        
    Returns:
        Chaîne JSON du payload
        
    Examples:
        >>> notif = {'title': 'Test', 'body': 'Message'}
        >>> payload = build_push_payload(notif)
        >>> 'Test' in payload
        True
    """
    payload = {
        "title": notification.get("title", "Notification"),
        "body": notification.get("body", ""),
        "icon": notification.get("icon", "/static/icons/icon-192x192.png"),
        "badge": notification.get("badge", "/static/icons/badge-72x72.png"),
        "tag": notification.get("tag"),
        "data": {
            "url": notification.get("url", "/"),
            "type": notification.get("notification_type", "system_update"),
            **(notification.get("data", {}))
        },
        "actions": notification.get("actions", []),
        "vibrate": notification.get("vibrate", [100, 50, 100]),
        "requireInteraction": notification.get("require_interaction", False),
        "silent": notification.get("silent", False),
    }
    
    # Ajouter timestamp si fourni
    timestamp = notification.get("timestamp")
    if timestamp:
        if isinstance(timestamp, datetime):
            payload["timestamp"] = timestamp.isoformat()
        else:
            payload["timestamp"] = str(timestamp)
    
    return json.dumps(payload, ensure_ascii=False)


def build_subscription_info(subscription: dict) -> dict:
    """
    Construit l'info d'abonnement pour pywebpush.
    
    Args:
        subscription: Dict avec endpoint, p256dh_key, auth_key
        
    Returns:
        Dict formaté pour pywebpush
        
    Examples:
        >>> sub = {'endpoint': 'https://...', 'p256dh_key': 'abc', 'auth_key': 'xyz'}
        >>> info = build_subscription_info(sub)
        >>> 'keys' in info
        True
    """
    return {
        "endpoint": subscription.get("endpoint", ""),
        "keys": {
            "p256dh": subscription.get("p256dh_key", ""),
            "auth": subscription.get("auth_key", ""),
        }
    }


# ═══════════════════════════════════════════════════════════
# CRÉATION DE NOTIFICATIONS PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


def create_stock_notification(
    item_name: str,
    quantity: float,
    unit: str = ""
) -> dict:
    """
    Crée une notification de stock bas.
    
    Args:
        item_name: Nom de l'article
        quantity: Quantité restante
        unit: Unité (optionnel)
        
    Returns:
        Dict notification prêt à envoyer
        
    Examples:
        >>> notif = create_stock_notification('Lait', 0.5, 'L')
        >>> notif['title']
        '📦 Stock bas'
        >>> 'Lait' in notif['body']
        True
    """
    quantity_str = f"{quantity} {unit}".strip() if unit else str(quantity)
    
    return {
        "title": "📦 Stock bas",
        "body": f"{item_name} est presque épuisé ({quantity_str} restant)",
        "notification_type": NotificationType.STOCK_LOW.value,
        "url": "/?module=cuisine.inventaire",
        "tag": f"stock_{item_name.lower().replace(' ', '_')}",
        "actions": [
            {"action": "add_to_cart", "title": "Ajouter aux courses"},
            {"action": "dismiss", "title": "Ignorer"}
        ],
        "require_interaction": False,
    }


def create_expiration_notification(
    item_name: str,
    days_left: int,
    critical: bool = False
) -> dict:
    """
    Crée une notification de péremption proche.
    
    Args:
        item_name: Nom de l'article
        days_left: Jours avant péremption (0 = aujourd'hui, <0 = périmé)
        critical: Forcer le mode critique
        
    Returns:
        Dict notification prêt à envoyer
        
    Examples:
        >>> notif = create_expiration_notification('Yaourt', 1)
        >>> notif['title']
        '🔴 Péremption demain'
        >>> notif = create_expiration_notification('Lait', -1)
        >>> 'périmé' in notif['body'].lower()
        True
    """
    if days_left <= 0:
        title = "⚠️ Produit périmé!"
        body = f"{item_name} a expiré!"
        notif_type = NotificationType.EXPIRATION_CRITICAL.value
        require_interaction = True
    elif days_left == 1:
        title = "🔴 Péremption demain"
        body = f"{item_name} expire demain"
        notif_type = NotificationType.EXPIRATION_CRITICAL.value if critical else NotificationType.EXPIRATION_WARNING.value
        require_interaction = critical
    else:
        title = "🟡 Péremption proche"
        body = f"{item_name} expire dans {days_left} jours"
        notif_type = NotificationType.EXPIRATION_WARNING.value
        require_interaction = False
    
    return {
        "title": title,
        "body": body,
        "notification_type": notif_type,
        "url": "/?module=cuisine.inventaire&filter=expiring",
        "tag": f"expiry_{item_name.lower().replace(' ', '_')}",
        "require_interaction": require_interaction,
    }


def create_meal_reminder_notification(
    meal_type: str,
    recipe_name: str,
    time_until: str
) -> dict:
    """
    Crée une notification de rappel de repas.
    
    Args:
        meal_type: Type de repas (déjeuner, dîner)
        recipe_name: Nom de la recette
        time_until: Temps restant (ex: "30 min")
        
    Returns:
        Dict notification prêt à envoyer
        
    Examples:
        >>> notif = create_meal_reminder_notification('déjeuner', 'Pâtes carbonara', '30 min')
        >>> 'Pâtes carbonara' in notif['body']
        True
    """
    return {
        "title": f"🍽️ {meal_type.title()} dans {time_until}",
        "body": f"Au menu: {recipe_name}",
        "notification_type": NotificationType.MEAL_REMINDER.value,
        "url": "/?module=planning",
        "tag": f"meal_{meal_type.lower()}",
        "actions": [
            {"action": "view_recipe", "title": "Voir la recette"},
            {"action": "dismiss", "title": "OK"}
        ],
        "require_interaction": False,
    }


def create_shopping_shared_notification(
    shared_by: str,
    list_name: str
) -> dict:
    """
    Crée une notification de partage de liste de courses.
    
    Args:
        shared_by: Nom de la personne qui partage
        list_name: Nom de la liste
        
    Returns:
        Dict notification prêt à envoyer
        
    Examples:
        >>> notif = create_shopping_shared_notification('Marie', 'Courses hebdo')
        >>> 'Marie' in notif['body']
        True
    """
    return {
        "title": "🛒 Liste partagée",
        "body": f"{shared_by} a partagé la liste '{list_name}'",
        "notification_type": NotificationType.SHOPPING_LIST_SHARED.value,
        "url": "/?module=cuisine.courses",
        "actions": [
            {"action": "view", "title": "Voir"},
            {"action": "dismiss", "title": "Plus tard"}
        ],
        "require_interaction": False,
    }


def create_activity_reminder_notification(
    activity_name: str,
    time_until: str,
    location: str | None = None
) -> dict:
    """
    Crée une notification de rappel d'activité.
    
    Args:
        activity_name: Nom de l'activité
        time_until: Temps restant
        location: Lieu (optionnel)
        
    Returns:
        Dict notification prêt à envoyer
    """
    body = f"{activity_name} dans {time_until}"
    if location:
        body += f" - {location}"
    
    return {
        "title": "📅 Rappel d'activité",
        "body": body,
        "notification_type": NotificationType.ACTIVITY_REMINDER.value,
        "url": "/?module=planning",
        "tag": f"activity_{activity_name.lower().replace(' ', '_')}",
        "require_interaction": False,
    }


def create_milestone_reminder_notification(
    child_name: str,
    milestone_type: str,
    milestone_name: str
) -> dict:
    """
    Crée une notification de rappel de jalon enfant.
    
    Args:
        child_name: Prénom de l'enfant
        milestone_type: Type du jalon
        milestone_name: Nom du jalon
        
    Returns:
        Dict notification prêt à envoyer
    """
    return {
        "title": f"👶 Jalon pour {child_name}",
        "body": f"{milestone_type}: {milestone_name}",
        "notification_type": NotificationType.MILESTONE_REMINDER.value,
        "url": "/?module=famille.jules",
        "require_interaction": False,
    }


# ═══════════════════════════════════════════════════════════
# COMPTEUR DE NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


def generate_count_key(user_id: str, dt: datetime | None = None) -> str:
    """
    Génère une clé pour le compteur de notifications par heure.
    
    Args:
        user_id: ID de l'utilisateur
        dt: Date/heure (défaut: maintenant)
        
    Returns:
        Clé au format user_id_YYYYMMDDHH
        
    Examples:
        >>> generate_count_key('user123', datetime(2024, 1, 15, 14, 30))
        'user123_2024011514'
    """
    if dt is None:
        dt = datetime.now()
    return f"{user_id}_{dt.strftime('%Y%m%d%H')}"


def parse_count_key(key: str) -> tuple[str, datetime | None]:
    """
    Parse une clé de compteur pour extraire user_id et heure.
    
    Args:
        key: Clé au format user_id_YYYYMMDDHH
        
    Returns:
        Tuple (user_id, datetime)
    """
    if "_" not in key:
        return key, None
    
    parts = key.rsplit("_", 1)
    user_id = parts[0]
    
    try:
        dt = datetime.strptime(parts[1], "%Y%m%d%H")
        return user_id, dt
    except ValueError:
        return user_id, None


def should_reset_counter(last_key: str, current_key: str) -> bool:
    """
    Vérifie si le compteur doit être remis à zéro (nouvelle heure).
    
    Args:
        last_key: Dernière clé utilisée
        current_key: Clé actuelle
        
    Returns:
        True si les clés sont différentes (nouvelle heure)
    """
    return last_key != current_key


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def validate_subscription(subscription: dict) -> tuple[bool, str]:
    """
    Valide un abonnement push.
    
    Args:
        subscription: Dict avec endpoint, keys
        
    Returns:
        Tuple (is_valid, error_message)
        
    Examples:
        >>> validate_subscription({'endpoint': 'https://...', 'keys': {'p256dh': 'a', 'auth': 'b'}})
        (True, '')
    """
    if not subscription.get("endpoint"):
        return False, "Endpoint manquant"
    
    if not subscription["endpoint"].startswith("https://"):
        return False, "Endpoint doit être HTTPS"
    
    keys = subscription.get("keys", {})
    if not keys.get("p256dh"):
        return False, "Clé p256dh manquante"
    
    if not keys.get("auth"):
        return False, "Clé auth manquante"
    
    return True, ""


def validate_preferences(preferences: dict) -> tuple[bool, list[str]]:
    """
    Valide les préférences de notification.
    
    Args:
        preferences: Dict des préférences
        
    Returns:
        Tuple (is_valid, list_of_warnings)
    """
    warnings = []
    
    # Vérifier les heures silencieuses
    quiet_start = preferences.get("quiet_hours_start")
    quiet_end = preferences.get("quiet_hours_end")
    
    if quiet_start is not None and not 0 <= quiet_start <= 23:
        warnings.append("quiet_hours_start doit être entre 0 et 23")
    
    if quiet_end is not None and not 0 <= quiet_end <= 23:
        warnings.append("quiet_hours_end doit être entre 0 et 23")
    
    # Vérifier max_per_hour
    max_per_hour = preferences.get("max_per_hour", 5)
    if max_per_hour < 1:
        warnings.append("max_per_hour doit être >= 1")
    elif max_per_hour > 100:
        warnings.append("max_per_hour semble élevé (>100)")
    
    return len(warnings) == 0, warnings


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Types
    "NotificationType",
    # Préférences
    "get_notification_type_mapping",
    "check_notification_type_enabled",
    # Heures silencieuses
    "is_quiet_hours",
    "can_send_during_quiet_hours",
    "should_send_notification",
    # Payloads
    "build_push_payload",
    "build_subscription_info",
    # Notifications prédéfinies
    "create_stock_notification",
    "create_expiration_notification",
    "create_meal_reminder_notification",
    "create_shopping_shared_notification",
    "create_activity_reminder_notification",
    "create_milestone_reminder_notification",
    # Compteur
    "generate_count_key",
    "parse_count_key",
    "should_reset_counter",
    # Validation
    "validate_subscription",
    "validate_preferences",
]
