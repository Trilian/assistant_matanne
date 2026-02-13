"""
Fonctions utilitaires pures pour les notifications push.

Ces fonctions peuvent être testées sans base de données ni dépendances externes.
Elles représentent la logique métier pure.
"""

import json
from datetime import datetime

from src.services.notifications.types import TypeNotification

# ═══════════════════════════════════════════════════════════
# VÉRIFICATION DES PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


def obtenir_mapping_types_notification() -> dict[TypeNotification, str]:
    """
    Retourne le mapping entre types de notification et préférences utilisateur.

    Returns:
        Dict {TypeNotification: nom_preference}
    """
    return {
        TypeNotification.STOCK_BAS: "alertes_stock",
        TypeNotification.PEREMPTION_ALERTE: "alertes_peremption",
        TypeNotification.PEREMPTION_CRITIQUE: "alertes_peremption",
        TypeNotification.RAPPEL_REPAS: "rappels_repas",
        TypeNotification.RAPPEL_ACTIVITE: "rappels_activites",
        TypeNotification.LISTE_PARTAGEE: "mises_a_jour_courses",
        TypeNotification.LISTE_MISE_A_JOUR: "mises_a_jour_courses",
        TypeNotification.RAPPEL_JALON: "rappels_famille",
        TypeNotification.RAPPEL_SANTE: "rappels_famille",
        TypeNotification.MISE_A_JOUR_SYSTEME: "mises_a_jour_systeme",
        TypeNotification.SYNC_TERMINEE: "mises_a_jour_systeme",
    }


def verifier_type_notification_active(
    type_notification: TypeNotification | str, preferences: dict
) -> bool:
    """
    Vérifie si un type de notification est activé pour l'utilisateur.

    Args:
        type_notification: Type de notification
        preferences: Dict des préférences utilisateur

    Returns:
        True si le type est activé
    """
    if isinstance(type_notification, str):
        try:
            type_notification = TypeNotification(type_notification)
        except ValueError:
            return True  # Type inconnu, activer par défaut

    mapping = obtenir_mapping_types_notification()
    pref_key = mapping.get(type_notification, None)

    if pref_key is None:
        return True  # Type sans préférence, activer par défaut

    return preferences.get(pref_key, True)


# ═══════════════════════════════════════════════════════════
# GESTION DES HEURES SILENCIEUSES
# ═══════════════════════════════════════════════════════════


def est_heures_silencieuses(
    heure_courante: int, heure_debut: int | None, heure_fin: int | None
) -> bool:
    """
    Vérifie si l'heure courante est dans la période silencieuse.

    Gère le cas où la période silencieuse passe par minuit
    (ex: 22h -> 7h).

    Args:
        heure_courante: Heure actuelle (0-23)
        heure_debut: Heure de début de silence (None = pas de silence)
        heure_fin: Heure de fin de silence

    Returns:
        True si dans les heures silencieuses
    """
    if heure_debut is None or heure_fin is None:
        return False

    # Valider l'heure
    if not 0 <= heure_courante <= 23:
        return False

    if heure_debut > heure_fin:
        # Passe par minuit (ex: 22h -> 7h)
        return heure_courante >= heure_debut or heure_courante < heure_fin
    else:
        # Normal (ex: 1h -> 6h)
        return heure_debut <= heure_courante < heure_fin


def peut_envoyer_pendant_silence(type_notification: TypeNotification | str) -> bool:
    """
    Vérifie si un type de notification peut être envoyé pendant les heures silencieuses.

    Certaines notifications critiques sont toujours envoyées.

    Args:
        type_notification: Type de notification

    Returns:
        True si peut être envoyé pendant silence
    """
    if isinstance(type_notification, str):
        try:
            type_notification = TypeNotification(type_notification)
        except ValueError:
            return False

    # Seules les alertes critiques passent
    types_critiques = {
        TypeNotification.PEREMPTION_CRITIQUE,
    }

    return type_notification in types_critiques


def doit_envoyer_notification(
    type_notification: TypeNotification | str,
    preferences: dict,
    heure_courante: int | None = None,
    nombre_envoyes_cette_heure: int = 0,
) -> tuple[bool, str]:
    """
    Vérifie si une notification doit être envoyée.

    Prend en compte:
    - Les préférences utilisateur
    - Les heures silencieuses
    - La limite par heure

    Args:
        type_notification: Type de notification
        preferences: Préférences utilisateur
        heure_courante: Heure actuelle (None = auto)
        nombre_envoyes_cette_heure: Nombre de notifications déjà envoyées cette heure

    Returns:
        Tuple (doit_envoyer, raison)
    """
    if heure_courante is None:
        heure_courante = datetime.now().hour

    # 1. Vérifier si le type est activé
    if not verifier_type_notification_active(type_notification, preferences):
        return False, "Type de notification désactivé"

    # 2. Vérifier les heures silencieuses
    heure_debut = preferences.get("heures_silencieuses_debut")
    heure_fin = preferences.get("heures_silencieuses_fin")

    if est_heures_silencieuses(heure_courante, heure_debut, heure_fin):
        if not peut_envoyer_pendant_silence(type_notification):
            return False, "Heures silencieuses actives"

    # 3. Vérifier la limite par heure
    max_par_heure = preferences.get("max_par_heure", 5)
    if nombre_envoyes_cette_heure >= max_par_heure:
        return False, f"Limite par heure atteinte ({max_par_heure})"

    return True, ""


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DE PAYLOADS
# ═══════════════════════════════════════════════════════════


def construire_payload_push(notification: dict) -> str:
    """
    Construit le payload JSON pour Web Push.

    Args:
        notification: Dict avec title, body, icon, etc.

    Returns:
        Chaîne JSON du payload
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
            **(notification.get("data", {})),
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


def construire_info_abonnement(subscription: dict) -> dict:
    """
    Construit l'info d'abonnement pour pywebpush.

    Args:
        subscription: Dict avec endpoint, p256dh_key, auth_key

    Returns:
        Dict formaté pour pywebpush
    """
    return {
        "endpoint": subscription.get("endpoint", ""),
        "keys": {
            "p256dh": subscription.get("p256dh_key", ""),
            "auth": subscription.get("auth_key", ""),
        },
    }


# ═══════════════════════════════════════════════════════════
# CRÉATION DE NOTIFICATIONS PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


def creer_notification_stock(nom_article: str, quantite: float, unite: str = "") -> dict:
    """
    Crée une notification de stock bas.

    Args:
        nom_article: Nom de l'article
        quantite: Quantité restante
        unite: Unité (optionnel)

    Returns:
        Dict notification prêt à envoyer
    """
    quantite_str = f"{quantite} {unite}".strip() if unite else str(quantite)

    return {
        "title": "📦 Stock bas",
        "body": f"{nom_article} est presque épuisé ({quantite_str} restant)",
        "notification_type": TypeNotification.STOCK_BAS.value,
        "url": "/?module=cuisine.inventaire",
        "tag": f"stock_{nom_article.lower().replace(' ', '_')}",
        "actions": [
            {"action": "add_to_cart", "title": "Ajouter aux courses"},
            {"action": "dismiss", "title": "Ignorer"},
        ],
        "require_interaction": False,
    }


def creer_notification_peremption(
    nom_article: str, jours_restants: int, critique: bool = False
) -> dict:
    """
    Crée une notification de péremption proche.

    Args:
        nom_article: Nom de l'article
        jours_restants: Jours avant péremption (0 = aujourd'hui, <0 = périmé)
        critique: Forcer le mode critique

    Returns:
        Dict notification prêt à envoyer
    """
    if jours_restants <= 0:
        title = "⚠️ Produit périmé!"
        body = f"{nom_article} a expiré!"
        notif_type = TypeNotification.PEREMPTION_CRITIQUE.value
        require_interaction = True
    elif jours_restants == 1:
        title = "🔴 Péremption demain"
        body = f"{nom_article} expire demain"
        notif_type = (
            TypeNotification.PEREMPTION_CRITIQUE.value
            if critique
            else TypeNotification.PEREMPTION_ALERTE.value
        )
        require_interaction = critique
    else:
        title = "🟡 Péremption proche"
        body = f"{nom_article} expire dans {jours_restants} jours"
        notif_type = TypeNotification.PEREMPTION_ALERTE.value
        require_interaction = False

    return {
        "title": title,
        "body": body,
        "notification_type": notif_type,
        "url": "/?module=cuisine.inventaire&filter=expiring",
        "tag": f"expiry_{nom_article.lower().replace(' ', '_')}",
        "require_interaction": require_interaction,
    }


def creer_notification_rappel_repas(type_repas: str, nom_recette: str, temps_restant: str) -> dict:
    """
    Crée une notification de rappel de repas.

    Args:
        type_repas: Type de repas (déjeuner, dîner)
        nom_recette: Nom de la recette
        temps_restant: Temps restant (ex: "30 min")

    Returns:
        Dict notification prêt à envoyer
    """
    return {
        "title": f"🍽️ {type_repas.title()} dans {temps_restant}",
        "body": f"Au menu: {nom_recette}",
        "notification_type": TypeNotification.RAPPEL_REPAS.value,
        "url": "/?module=planning",
        "tag": f"meal_{type_repas.lower()}",
        "actions": [
            {"action": "view_recipe", "title": "Voir la recette"},
            {"action": "dismiss", "title": "OK"},
        ],
        "require_interaction": False,
    }


def creer_notification_liste_partagee(partage_par: str, nom_liste: str) -> dict:
    """
    Crée une notification de partage de liste de courses.

    Args:
        partage_par: Nom de la personne qui partage
        nom_liste: Nom de la liste

    Returns:
        Dict notification prêt à envoyer
    """
    return {
        "title": "🛒 Liste partagée",
        "body": f"{partage_par} a partagé la liste '{nom_liste}'",
        "notification_type": TypeNotification.LISTE_PARTAGEE.value,
        "url": "/?module=cuisine.courses",
        "actions": [
            {"action": "view", "title": "Voir"},
            {"action": "dismiss", "title": "Plus tard"},
        ],
        "require_interaction": False,
    }


def creer_notification_rappel_activite(
    nom_activite: str, temps_restant: str, lieu: str | None = None
) -> dict:
    """
    Crée une notification de rappel d'activité.

    Args:
        nom_activite: Nom de l'activité
        temps_restant: Temps restant
        lieu: Lieu (optionnel)

    Returns:
        Dict notification prêt à envoyer
    """
    body = f"{nom_activite} dans {temps_restant}"
    if lieu:
        body += f" - {lieu}"

    return {
        "title": "📝… Rappel d'activité",
        "body": body,
        "notification_type": TypeNotification.RAPPEL_ACTIVITE.value,
        "url": "/?module=planning",
        "tag": f"activity_{nom_activite.lower().replace(' ', '_')}",
        "require_interaction": False,
    }


def creer_notification_rappel_jalon(prenom_enfant: str, type_jalon: str, nom_jalon: str) -> dict:
    """
    Crée une notification de rappel de jalon enfant.

    Args:
        prenom_enfant: Prénom de l'enfant
        type_jalon: Type du jalon
        nom_jalon: Nom du jalon

    Returns:
        Dict notification prêt à envoyer
    """
    return {
        "title": f"👶 Jalon pour {prenom_enfant}",
        "body": f"{type_jalon}: {nom_jalon}",
        "notification_type": TypeNotification.RAPPEL_JALON.value,
        "url": "/?module=famille.jules",
        "require_interaction": False,
    }


# ═══════════════════════════════════════════════════════════
# COMPTEUR DE NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


def generer_cle_compteur(user_id: str, dt: datetime | None = None) -> str:
    """
    Génère une clé pour le compteur de notifications par heure.

    Args:
        user_id: ID de l'utilisateur
        dt: Date/heure (défaut: maintenant)

    Returns:
        Clé au format user_id_YYYYMMDDHH
    """
    if dt is None:
        dt = datetime.now()
    return f"{user_id}_{dt.strftime('%Y%m%d%H')}"


def parser_cle_compteur(key: str) -> tuple[str, datetime | None]:
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


def doit_reinitialiser_compteur(derniere_cle: str, cle_courante: str) -> bool:
    """
    Vérifie si le compteur doit être remis à zéro (nouvelle heure).

    Args:
        derniere_cle: Dernière clé utilisée
        cle_courante: Clé actuelle

    Returns:
        True si les clés sont différentes (nouvelle heure)
    """
    return derniere_cle != cle_courante


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_abonnement(subscription: dict) -> tuple[bool, str]:
    """
    Valide un abonnement push.

    Args:
        subscription: Dict avec endpoint, keys

    Returns:
        Tuple (is_valid, error_message)
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


def valider_preferences(preferences: dict) -> tuple[bool, list[str]]:
    """
    Valide les préférences de notification.

    Args:
        preferences: Dict des préférences

    Returns:
        Tuple (is_valid, list_of_warnings)
    """
    warnings = []

    # Vérifier les heures silencieuses
    heure_debut = preferences.get("heures_silencieuses_debut")
    heure_fin = preferences.get("heures_silencieuses_fin")

    if heure_debut is not None and not 0 <= heure_debut <= 23:
        warnings.append("heures_silencieuses_debut doit être entre 0 et 23")

    if heure_fin is not None and not 0 <= heure_fin <= 23:
        warnings.append("heures_silencieuses_fin doit être entre 0 et 23")

    # Vérifier max_par_heure
    max_par_heure = preferences.get("max_par_heure", 5)
    if max_par_heure < 1:
        warnings.append("max_par_heure doit être >= 1")
    elif max_par_heure > 100:
        warnings.append("max_par_heure semble élevé (>100)")

    return len(warnings) == 0, warnings


# ═══════════════════════════════════════════════════════════
# ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════

# Enum alias (pour anciens imports)
NotificationType = TypeNotification

# Fonctions alias
get_notification_type_mapping = obtenir_mapping_types_notification
check_notification_type_enabled = verifier_type_notification_active
is_quiet_hours = est_heures_silencieuses
can_send_during_quiet_hours = peut_envoyer_pendant_silence
should_send_notification = doit_envoyer_notification
build_push_payload = construire_payload_push
build_subscription_info = construire_info_abonnement
create_stock_notification = creer_notification_stock
create_expiration_notification = creer_notification_peremption
create_meal_reminder_notification = creer_notification_rappel_repas
create_shopping_shared_notification = creer_notification_liste_partagee
create_activity_reminder_notification = creer_notification_rappel_activite
create_milestone_reminder_notification = creer_notification_rappel_jalon
generate_count_key = generer_cle_compteur
parse_count_key = parser_cle_compteur
should_reset_counter = doit_reinitialiser_compteur
validate_subscription = valider_abonnement
validate_preferences = valider_preferences


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Types (français)
    "TypeNotification",
    # Préférences (français)
    "obtenir_mapping_types_notification",
    "verifier_type_notification_active",
    # Heures silencieuses (français)
    "est_heures_silencieuses",
    "peut_envoyer_pendant_silence",
    "doit_envoyer_notification",
    # Payloads (français)
    "construire_payload_push",
    "construire_info_abonnement",
    # Notifications prédéfinies (français)
    "creer_notification_stock",
    "creer_notification_peremption",
    "creer_notification_rappel_repas",
    "creer_notification_liste_partagee",
    "creer_notification_rappel_activite",
    "creer_notification_rappel_jalon",
    # Compteur (français)
    "generer_cle_compteur",
    "parser_cle_compteur",
    "doit_reinitialiser_compteur",
    # Validation (français)
    "valider_abonnement",
    "valider_preferences",
    # Alias rétrocompatibilité (anglais)
    "NotificationType",
    "get_notification_type_mapping",
    "check_notification_type_enabled",
    "is_quiet_hours",
    "can_send_during_quiet_hours",
    "should_send_notification",
    "build_push_payload",
    "build_subscription_info",
    "create_stock_notification",
    "create_expiration_notification",
    "create_meal_reminder_notification",
    "create_shopping_shared_notification",
    "create_activity_reminder_notification",
    "create_milestone_reminder_notification",
    "generate_count_key",
    "parse_count_key",
    "should_reset_counter",
    "validate_subscription",
    "validate_preferences",
]
