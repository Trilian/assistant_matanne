"""
Client WhatsApp via Meta Cloud API (WhatsApp Business).

Plan gratuit : 1000 conversations/mois (messages initiés par l'entreprise).
Messages de réponse aux utilisateurs : illimités.

Utilisé pour :
- Envoyer le planning de la semaine (dimanche soir)
- Recevoir la validation "OK" / "Changer lundi soir" par message
- Alertes péremption
- Rappels de repas du jour
"""

import logging

import httpx

from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

META_API_BASE = "https://graph.facebook.com/v21.0"


async def envoyer_message_whatsapp(
    destinataire: str,
    texte: str,
) -> bool:
    """Envoie un message texte WhatsApp via Meta Cloud API.

    Args:
        destinataire: Numéro de téléphone au format international (ex: "33612345678")
        texte: Message à envoyer

    Returns:
        True si envoyé avec succès
    """
    settings = obtenir_parametres()

    if not settings.META_WHATSAPP_TOKEN or not settings.META_PHONE_NUMBER_ID:
        logger.debug("WhatsApp non configuré — message ignoré")
        return False

    url = f"{META_API_BASE}/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinataire,
        "type": "text",
        "text": {"body": texte},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            import hashlib
            hash_dest = hashlib.sha256(destinataire.encode()).hexdigest()[:8]
            logger.info(f"✅ Message WhatsApp envoyé à [hash:{hash_dest}]")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Erreur WhatsApp HTTP {e.response.status_code}: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur WhatsApp : {e}")
        return False


async def envoyer_message_interactif(
    destinataire: str,
    corps: str,
    boutons: list[dict[str, str]],
) -> bool:
    """Envoie un message interactif avec boutons de réponse rapide.

    Args:
        destinataire: Numéro au format international
        corps: Texte principal du message
        boutons: Liste de {"id": "action_id", "title": "Texte bouton"} (max 3)
    """
    settings = obtenir_parametres()

    if not settings.META_WHATSAPP_TOKEN or not settings.META_PHONE_NUMBER_ID:
        return False

    url = f"{META_API_BASE}/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    # WhatsApp limite à 3 boutons
    boutons_wa = [
        {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
        for b in boutons[:3]
    ]

    payload = {
        "messaging_product": "whatsapp",
        "to": destinataire,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": corps},
            "action": {"buttons": boutons_wa},
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"❌ Erreur WhatsApp interactif : {e}")
        return False


async def envoyer_planning_semaine(planning_texte: str) -> bool:
    """Envoie le résumé du planning de la semaine via WhatsApp.

    Appelé par le cron job du dimanche soir avec le planning formaté.
    """
    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire:
        logger.debug("WHATSAPP_USER_NUMBER non configuré")
        return False

    message = f"🍽️ *Planning repas de la semaine*\n\n{planning_texte}\n\n✅ Valider | ✏️ Modifier"

    return await envoyer_message_interactif(
        destinataire=destinataire,
        corps=message,
        boutons=[
            {"id": "planning_valider", "title": "✅ Valider"},
            {"id": "planning_modifier", "title": "✏️ Modifier"},
            {"id": "planning_regenerer", "title": "🔄 Régénérer"},
        ],
    )


async def envoyer_alerte_peremption(articles: list[dict]) -> bool:
    """Envoie une alerte pour les articles proches de la péremption."""
    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire or not articles:
        return False

    lignes = [f"• {a['nom']} — expire le {a['date']}" for a in articles[:10]]
    message = f"⚠️ *Alerte péremption*\n\n{chr(10).join(lignes)}\n\nPense à les utiliser !"

    return await envoyer_message_whatsapp(destinataire, message)


async def envoyer_rappel_creche(message_creche: str) -> bool:
    """Envoie un rappel lié à la crèche (fermeture, jours sans crèche, rappel RDV).

    Args:
        message_creche: Texte du rappel (ex: «Crèche fermée lundi — prévenir la famille»)
    """
    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire:
        return False

    message = f"👶 *Rappel crèche*\n\n{message_creche}"
    return await envoyer_message_whatsapp(destinataire, message)


async def envoyer_liste_courses_partagee(articles: list[str], nom_liste: str = "Courses") -> bool:
    """Envoie la liste de courses active via WhatsApp.

    Args:
        articles: Liste des noms d'articles à acheter
        nom_liste: Nom de la liste de courses
    """
    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire or not articles:
        return False

    lignes = "\n".join(f"☐ {a}" for a in articles[:30])
    message = f"🛒 *{nom_liste}*\n\n{lignes}"
    return await envoyer_message_whatsapp(destinataire, message)


async def envoyer_rapport_hebdo_whatsapp(texte_resume: str) -> bool:
    """Envoie le rapport hebdomadaire compact via WhatsApp.

    Complément du canal email/ntfy — version courte pour WhatsApp.
    """
    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire:
        return False

    message = f"📋 *Résumé de la semaine*\n\n{texte_resume}"
    return await envoyer_message_interactif(
        destinataire=destinataire,
        corps=message,
        boutons=[
            {"id": "resume_vu", "title": "👍 Vu !"},
            {"id": "resume_detail", "title": "📊 Détail"},
        ],
    )
