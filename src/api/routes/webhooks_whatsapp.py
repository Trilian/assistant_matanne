"""
Webhook WhatsApp — Réception des messages entrants Meta Cloud API.

Endpoints :
- GET  /api/v1/whatsapp/webhook : Vérification Meta (challenge)
- POST /api/v1/whatsapp/webhook : Réception messages et réponses boutons

Machine d'état conversationnelle :
- "planning_valider" → valide le planning proposé
- "planning_modifier" → demande quel repas modifier
- "planning_regenerer" → relance la génération IA
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api
from src.core.config import obtenir_parametres

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp"])


# ═══════════════════════════════════════════════════════════
# VÉRIFICATION WEBHOOK META
# ═══════════════════════════════════════════════════════════


@router.get("/webhook")
async def verifier_webhook_whatsapp(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> int | str:
    """Endpoint de vérification Meta.

    Meta envoie un GET avec hub.mode=subscribe, hub.verify_token et hub.challenge.
    On valide le token et retourne le challenge.
    """
    settings = obtenir_parametres()

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook WhatsApp vérifié par Meta")
        return int(hub_challenge) if hub_challenge else 0

    logger.warning("⚠️ Tentative de vérification webhook invalide")
    raise HTTPException(status_code=403, detail="Token de vérification invalide")


# ═══════════════════════════════════════════════════════════
# RÉCEPTION MESSAGES
# ═══════════════════════════════════════════════════════════


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_message_whatsapp(request: Request) -> MessageResponse:
    """Reçoit les messages WhatsApp entrants (texte ou réponse bouton).

    Traite les interactions du flux planning :
    - Bouton "planning_valider" → valide le planning de la semaine
    - Bouton "planning_modifier" → envoie les options de modification
    - Bouton "planning_regenerer" → relance la suggestion IA
    - Texte libre → interprétation IA basique
    """
    body = await request.json()

    # Extraire le message entrant
    entry = body.get("entry", [])
    if not entry:
        return MessageResponse(message="ok", id=0)

    changes = entry[0].get("changes", [])
    if not changes:
        return MessageResponse(message="ok", id=0)

    value = changes[0].get("value", {})
    messages = value.get("messages", [])
    if not messages:
        return MessageResponse(message="ok", id=0)

    msg = messages[0]
    sender = msg.get("from", "")
    msg_type = msg.get("type", "")

    logger.info(f"📨 Message WhatsApp reçu de {sender[:6]}***, type: {msg_type}")

    # Traiter selon le type
    if msg_type == "interactive":
        button_reply = msg.get("interactive", {}).get("button_reply", {})
        action_id = button_reply.get("id", "")
        await _traiter_action_bouton(sender, action_id)
    elif msg_type == "text":
        texte = msg.get("text", {}).get("body", "")
        await _traiter_message_texte(sender, texte)

    return MessageResponse(message="ok", id=0)


# ═══════════════════════════════════════════════════════════
# MACHINE D'ÉTAT CONVERSATIONNELLE
# ═══════════════════════════════════════════════════════════


async def _traiter_action_bouton(sender: str, action_id: str) -> None:
    """Traite une réponse bouton WhatsApp."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    if action_id == "planning_valider":
        # Valider le planning proposé le plus récent
        await _valider_planning_courant()
        await envoyer_message_whatsapp(sender, "✅ Planning validé ! Bon appétit cette semaine 🍽️")

    elif action_id == "planning_modifier":
        await envoyer_message_whatsapp(
            sender,
            "✏️ Quel repas veux-tu modifier ?\n"
            "Réponds avec le format : *lundi soir* ou *mercredi midi*",
        )

    elif action_id == "planning_regenerer":
        await envoyer_message_whatsapp(
            sender,
            "🔄 Régénération du planning en cours...\n"
            "Je te renvoie les nouvelles suggestions dans quelques instants.",
        )
        # TODO: Intégrer avec le service de génération IA

    else:
        logger.warning(f"Action bouton inconnue : {action_id}")


async def _traiter_message_texte(sender: str, texte: str) -> None:
    """Traite un message texte libre."""
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    texte_lower = texte.lower().strip()

    # Commandes simples
    if texte_lower in ("menu", "planning", "semaine"):
        await _envoyer_planning_courant(sender)
    elif texte_lower in ("courses", "liste"):
        await _envoyer_liste_courses(sender)
    elif texte_lower in ("frigo", "stock", "inventaire"):
        await _envoyer_alerte_stocks(sender)
    else:
        await envoyer_message_whatsapp(
            sender,
            "🤖 Commandes disponibles :\n"
            "• *menu* — Planning de la semaine\n"
            "• *courses* — Liste de courses en cours\n"
            "• *frigo* — État des stocks",
        )


async def _valider_planning_courant() -> None:
    """Valide le planning proposé le plus récent."""
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Planning

    with obtenir_contexte_db() as session:
        planning = (
            session.query(Planning)
            .filter(Planning.statut == "propose")
            .order_by(Planning.date_creation.desc())
            .first()
        )
        if planning:
            planning.statut = "actif"
            session.commit()
            logger.info(f"✅ Planning #{planning.id} validé via WhatsApp")


async def _envoyer_planning_courant(sender: str) -> None:
    """Envoie le planning actif de la semaine."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Planning, Repas
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        repas = (
            session.query(Repas)
            .join(Planning)
            .filter(
                Planning.statut == "actif",
                Repas.date_repas >= debut_semaine,
                Repas.date_repas <= fin_semaine,
            )
            .order_by(Repas.date_repas, Repas.type_repas)
            .all()
        )

        if not repas:
            await envoyer_message_whatsapp(sender, "📅 Aucun planning actif cette semaine.")
            return

        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        lignes = []
        for r in repas:
            jour = jours[r.date_repas.weekday()]
            nom = r.recette.nom if r.recette else r.notes or "?"
            emoji = "🌙" if r.type_repas == "diner" else "☀️"
            lignes.append(f"{emoji} {jour} {r.type_repas} : {nom}")

        await envoyer_message_whatsapp(
            sender, f"🍽️ *Planning de la semaine*\n\n{''.join(chr(10) + l for l in lignes)}"
        )


async def _envoyer_liste_courses(sender: str) -> None:
    """Envoie la liste de courses active."""
    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        liste = (
            session.query(ListeCourses)
            .filter(ListeCourses.archivee == False)  # noqa: E712
            .order_by(ListeCourses.date_creation.desc())
            .first()
        )

        if not liste:
            await envoyer_message_whatsapp(sender, "🛒 Aucune liste de courses en cours.")
            return

        articles = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste.id,
                ArticleCourses.achete == False,  # noqa: E712
            )
            .all()
        )

        lignes = [f"• {a.ingredient.nom if a.ingredient else '?'}" for a in articles[:20]]
        msg = f"🛒 *Liste de courses* ({len(articles)} articles)\n\n{''.join(chr(10) + l for l in lignes)}"

        if len(articles) > 20:
            msg += f"\n\n... et {len(articles) - 20} autres"

        await envoyer_message_whatsapp(sender, msg)


async def _envoyer_alerte_stocks(sender: str) -> None:
    """Envoie l'état des stocks bas + péremptions proches."""
    from datetime import date, timedelta

    from src.core.db import obtenir_contexte_db
    from src.core.models import ArticleInventaire
    from src.services.integrations.whatsapp import envoyer_message_whatsapp

    with obtenir_contexte_db() as session:
        aujourd_hui = date.today()
        seuil = aujourd_hui + timedelta(days=3)

        stocks_bas = (
            session.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite <= ArticleInventaire.quantite_min)
            .all()
        )

        peremptions = (
            session.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= seuil,
            )
            .all()
        )

        lignes = []
        if stocks_bas:
            lignes.append("📉 *Stocks bas :*")
            for a in stocks_bas[:10]:
                lignes.append(f"  • {a.nom} ({a.quantite}/{a.quantite_min})")
        if peremptions:
            lignes.append("\n⚠️ *Péremption proche :*")
            for a in peremptions[:10]:
                lignes.append(f"  • {a.nom} — {a.date_peremption}")

        if not lignes:
            await envoyer_message_whatsapp(sender, "✅ Tous les stocks sont OK !")
        else:
            await envoyer_message_whatsapp(sender, "\n".join(lignes))
