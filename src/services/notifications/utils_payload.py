"""
Fonctions utilitaires pour la construction de payloads et notifications prédéfinies.

Construction des payloads JSON pour Web Push et factories
de notifications typées (stock, péremption, repas, etc.).
"""

import json
from datetime import datetime

from src.services.notifications.types import TypeNotification

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
        "title": "📅 Rappel d'activité",
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
