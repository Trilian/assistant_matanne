"""
Client WhatsApp via Meta Cloud API (WhatsApp Business).

Plan gratuit : 1000 conversations/mois (messages initiés par l'entreprise).
Messages de réponse aux utilisateurs : illimités.

Utilisé pour :
- Envoyer le planning de la semaine (dimanche soir)
- Recevoir la validation "OK" / "Changer lundi soir" par message
- Alertes péremption
- Rappels de repas du jour

Rate limiting intégré :
- 10 messages/heure par destinataire
- 100 messages/jour global
- Respect des quotas Meta (1000 conversations/mois)
"""

import logging
import re
import time
from collections import defaultdict

import httpx

from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

META_API_BASE = "https://graph.facebook.com/v21.0"


# ═══════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════

_LIMITE_PAR_HEURE = 10
_LIMITE_PAR_JOUR = 100

_compteurs_heure: dict[str, list[float]] = defaultdict(list)
_compteurs_jour: list[float] = []


def _nettoyer_compteur_heure(dest: str) -> None:
    """Supprime les entrées de plus d'une heure."""
    seuil = time.monotonic() - 3600
    _compteurs_heure[dest] = [t for t in _compteurs_heure[dest] if t > seuil]


def _nettoyer_compteur_jour() -> None:
    """Supprime les entrées de plus de 24h."""
    global _compteurs_jour
    seuil = time.monotonic() - 86400
    _compteurs_jour = [t for t in _compteurs_jour if t > seuil]


def _verifier_rate_limit(destinataire: str) -> tuple[bool, str]:
    """Vérifie si l'envoi est autorisé.

    Returns:
        (autorisé, raison si refusé)
    """
    _nettoyer_compteur_heure(destinataire)
    if len(_compteurs_heure[destinataire]) >= _LIMITE_PAR_HEURE:
        return False, f"Limite horaire atteinte ({_LIMITE_PAR_HEURE}/h) pour ce destinataire"

    _nettoyer_compteur_jour()
    if len(_compteurs_jour) >= _LIMITE_PAR_JOUR:
        return False, f"Limite journalière atteinte ({_LIMITE_PAR_JOUR}/jour)"

    return True, ""


def _enregistrer_envoi(destinataire: str) -> None:
    """Enregistre un envoi réussi pour le rate limiting."""
    now = time.monotonic()
    _compteurs_heure[destinataire].append(now)
    _compteurs_jour.append(now)


# ═══════════════════════════════════════════════════════════
# VALIDATION NUMÉRO DE TÉLÉPHONE
# ═══════════════════════════════════════════════════════════

_REGEX_E164 = re.compile(r"^\d{10,15}$")


def valider_numero_telephone(numero: str) -> tuple[bool, str]:
    """Valide un numéro de téléphone au format international E.164 (sans le +).

    Exemples valides : "33612345678", "14155552671"
    Exemples invalides : "+33612345678", "06 12 34 56 78", ""

    Returns:
        (valide, numéro nettoyé ou message d'erreur)
    """
    if not numero:
        return False, "Numéro vide"

    # Nettoyer : supprimer espaces, tirets, parenthèses, +
    propre = numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if propre.startswith("+"):
        propre = propre[1:]

    # Convertir le format français 06/07 → international
    if propre.startswith("0") and len(propre) == 10:
        propre = "33" + propre[1:]

    if not _REGEX_E164.match(propre):
        return False, f"Format invalide : '{numero}' → attendu 10-15 chiffres (format E.164)"

    return True, propre


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

    # Validation du numéro
    valide, resultat = valider_numero_telephone(destinataire)
    if not valide:
        logger.warning("WhatsApp : numéro invalide — %s", resultat)
        return False
    destinataire = resultat

    # Rate limiting
    autorise, raison = _verifier_rate_limit(destinataire)
    if not autorise:
        logger.warning("WhatsApp rate limit : %s", raison)
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
            _enregistrer_envoi(destinataire)
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

    # Validation du numéro
    valide, resultat = valider_numero_telephone(destinataire)
    if not valide:
        logger.warning("WhatsApp interactif : numéro invalide — %s", resultat)
        return False
    destinataire = resultat

    # Rate limiting
    autorise, raison = _verifier_rate_limit(destinataire)
    if not autorise:
        logger.warning("WhatsApp interactif rate limit : %s", raison)
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
            _enregistrer_envoi(destinataire)
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


async def envoyer_digest_matinal() -> bool:
    """Envoie le digest matinal WhatsApp : résumé de la journée à venir.

    Contenu :
    - Repas prévus aujourd'hui
    - Tâches/rendez-vous du jour
    - Alertes péremption imminentes
    - Météo (si configurée)

    Appelé par le CRON job matinal (7h-8h).
    """
    from datetime import date, timedelta

    settings = obtenir_parametres()
    destinataire = settings.WHATSAPP_USER_NUMBER

    if not destinataire:
        return False

    aujourd_hui = date.today()
    sections: list[str] = []

    # 1. Repas du jour
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.planning import Repas

        with obtenir_contexte_db() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas == aujourd_hui)
                .order_by(Repas.type_repas)
                .all()
            )
            if repas:
                lignes = []
                for r in repas:
                    nom = r.recette.nom if getattr(r, "recette", None) else (r.notes or "?")
                    emoji = "🌙" if r.type_repas == "diner" else "☀️"
                    lignes.append(f"  {emoji} {r.type_repas.capitalize()} : {nom}")
                sections.append("🍽️ *Repas du jour :*\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : repas indisponibles")

    # 2. Alertes péremption (J0-J2)
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleInventaire

        with obtenir_contexte_db() as session:
            seuil = aujourd_hui + timedelta(days=2)
            peremptions = (
                session.query(ArticleInventaire)
                .filter(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption <= seuil,
                )
                .limit(5)
                .all()
            )
            if peremptions:
                lignes = [f"  • {a.nom} — {a.date_peremption}" for a in peremptions]
                sections.append("⚠️ *Péremptions proches :*\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : péremptions indisponibles")

    # 3. Tâches du jour (entretien/maison)
    try:
        from src.core.db import obtenir_contexte_db

        with obtenir_contexte_db() as session:
            from sqlalchemy import text

            rows = session.execute(
                text(
                    "SELECT titre FROM taches_maison"
                    " WHERE statut NOT IN ('termine', 'annule')"
                    " AND date_echeance = :today"
                    " LIMIT 5"
                ),
                {"today": aujourd_hui},
            ).fetchall()
            if rows:
                lignes = [f"  • {titre}" for (titre,) in rows]
                sections.append("📋 *Tâches du jour :*\n" + "\n".join(lignes))
    except Exception:
        logger.debug("Digest matinal : tâches indisponibles")

    if not sections:
        message = f"☀️ *Bonjour !* — {aujourd_hui.strftime('%A %d %B')}\n\nRien de spécial prévu aujourd'hui. Bonne journée !"
    else:
        message = f"☀️ *Bonjour !* — {aujourd_hui.strftime('%A %d %B')}\n\n" + "\n\n".join(sections)

    return await envoyer_message_interactif(
        destinataire=destinataire,
        corps=message,
        boutons=[
            {"id": "digest_courses", "title": "🛒 Courses"},
            {"id": "digest_detail", "title": "📊 Détail"},
        ],
    )


async def envoyer_message_liste(
    destinataire: str,
    corps: str,
    bouton_texte: str,
    sections: list[dict],
) -> bool:
    """Envoie un message avec une liste interactive WhatsApp.

    Args:
        destinataire: Numéro au format international
        corps: Texte principal du message
        bouton_texte: Texte du bouton pour ouvrir la liste (max 20 chars)
        sections: Liste de sections, chaque section = {
            "title": "Titre section",
            "rows": [{"id": "action_id", "title": "Texte", "description": "Desc optionnelle"}]
        }
    """
    settings = obtenir_parametres()

    if not settings.META_WHATSAPP_TOKEN or not settings.META_PHONE_NUMBER_ID:
        return False

    valide, resultat = valider_numero_telephone(destinataire)
    if not valide:
        return False
    destinataire = resultat

    autorise, raison = _verifier_rate_limit(destinataire)
    if not autorise:
        logger.warning("WhatsApp liste rate limit : %s", raison)
        return False

    url = f"{META_API_BASE}/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }

    # Formater les sections pour Meta API
    sections_wa = []
    for section in sections[:10]:
        rows_wa = []
        for row in section.get("rows", [])[:10]:
            row_wa = {
                "id": row["id"][:200],
                "title": row["title"][:24],
            }
            if row.get("description"):
                row_wa["description"] = row["description"][:72]
            rows_wa.append(row_wa)
        sections_wa.append({"title": section.get("title", "")[:24], "rows": rows_wa})

    payload = {
        "messaging_product": "whatsapp",
        "to": destinataire,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": corps},
            "action": {
                "button": bouton_texte[:20],
                "sections": sections_wa,
            },
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            _enregistrer_envoi(destinataire)
            return True
    except Exception as e:
        logger.error("❌ Erreur WhatsApp liste : %s", e)
        return False
