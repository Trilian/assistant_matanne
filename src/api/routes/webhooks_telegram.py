"""Webhook Telegram pour les commandes en langage naturel.

Endpoints:
- POST /api/v1/telegram/webhook : reception des updates Telegram

Commandes bot Telegram :
- "Qu'est-ce qu'on mange ce soir ?"
- "Ajoute lait a la liste"
- "Activite samedi ?"
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date, timedelta

from fastapi import APIRouter, Request

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])


def _normaliser_texte(texte: str) -> str:
    valeur = " ".join((texte or "").lower().strip().split())
    return unicodedata.normalize("NFKD", valeur).encode("ascii", "ignore").decode("ascii")


def _extraire_article_depuis_commande(texte: str) -> str:
    """Extrait l'article cible depuis "ajoute ... a la liste".

    Fallback: texte apres le premier mot de commande.
    """
    nettoye = (texte or "").strip()
    motif = re.compile(r"^(?:ajoute|ajouter)\s+(.+?)\s+(?:a|à)\s+la\s+liste\s*$", re.IGNORECASE)
    match = motif.match(nettoye)
    if match:
        return match.group(1).strip()

    morceaux = nettoye.split(" ", 1)
    if len(morceaux) == 2:
        return morceaux[1].strip()
    return ""


async def _envoyer_repas_du_soir(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.planning import Repas
    from src.services.integrations.telegram import envoyer_message_telegram

    with obtenir_contexte_db() as session:
        repas = (
            session.query(Repas)
            .filter(Repas.date_repas == date.today(), Repas.type_repas == "diner")
            .first()
        )

    if repas:
        nom = repas.recette.nom if getattr(repas, "recette", None) else (repas.notes or "Repas du soir")
        await envoyer_message_telegram(chat_id, f"🍽️ Ce soir: <b>{nom}</b>.")
        return

    await envoyer_message_telegram(
        chat_id,
        "🍽️ Rien de planifie pour ce soir. Suggestion rapide: omelette + salade + fruit.",
    )


async def _ajouter_article_liste(chat_id: str, article: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.core.models.recettes import Ingredient
    from src.services.integrations.telegram import envoyer_message_telegram

    nom_article = (article or "").strip()
    if not nom_article:
        await envoyer_message_telegram(chat_id, "🛒 Quel article veux-tu ajouter exactement ?")
        return

    with obtenir_contexte_db() as session:
        liste = (
            session.query(ListeCourses)
            .filter(ListeCourses.archivee.is_(False))
            .order_by(ListeCourses.date_creation.desc())
            .first()
        )
        if not liste:
            liste = ListeCourses(nom="Courses Telegram")
            session.add(liste)
            session.flush()

        ingredient = session.query(Ingredient).filter(Ingredient.nom.ilike(nom_article)).first()
        if not ingredient:
            ingredient = Ingredient(nom=nom_article.capitalize())
            session.add(ingredient)
            session.flush()

        existant = (
            session.query(ArticleCourses)
            .filter(
                ArticleCourses.liste_id == liste.id,
                ArticleCourses.ingredient_id == ingredient.id,
                ArticleCourses.achete.is_(False),
            )
            .first()
        )
        if existant:
            await envoyer_message_telegram(chat_id, f"🛒 '{nom_article}' est deja sur la liste.")
            return

        session.add(
            ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1,
                achete=False,
            )
        )
        session.commit()

    await envoyer_message_telegram(chat_id, f"✅ '{nom_article}' ajoute a la liste.")


async def _envoyer_activites_samedi(chat_id: str) -> None:
    from src.core.db import obtenir_contexte_db
    from src.core.models.famille import ActiviteFamille
    from src.services.integrations.telegram import envoyer_message_telegram

    aujourd_hui = date.today()
    jours_jusqua_samedi = (5 - aujourd_hui.weekday()) % 7
    prochain_samedi = aujourd_hui + timedelta(days=jours_jusqua_samedi)

    with obtenir_contexte_db() as session:
        activites = (
            session.query(ActiviteFamille)
            .filter(
                ActiviteFamille.date_prevue == prochain_samedi,
                ActiviteFamille.statut.in_(["planifié", "planifie", "à venir", "a venir"]),
            )
            .order_by(ActiviteFamille.heure_debut.asc())
            .limit(3)
            .all()
        )

    if not activites:
        await envoyer_message_telegram(
            chat_id,
            "🎯 Rien de planifie samedi pour le moment. Suggestion: parc le matin, activite calme l'apres-midi.",
        )
        return

    lignes: list[str] = []
    for activite in activites:
        heure = activite.heure_debut.strftime("%H:%M") if activite.heure_debut else "horaire libre"
        lieu = f" - {activite.lieu}" if activite.lieu else ""
        lignes.append(f"- {heure} : {activite.titre}{lieu}")

    await envoyer_message_telegram(
        chat_id,
        "🎯 <b>Activites prevues samedi</b>\n\n" + "\n".join(lignes),
    )


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_update_telegram(request: Request) -> MessageResponse:
    """Recoit un update Telegram et traite les commandes principales."""
    payload = await request.json()

    callback_query = payload.get("callback_query") or {}
    if callback_query:
        data = str(callback_query.get("data") or "").strip()
        chat_id = str(((callback_query.get("message") or {}).get("chat") or {}).get("id") or "")
        if chat_id and data:
            if data == "cmd_ce_soir":
                await _envoyer_repas_du_soir(chat_id)
            elif data == "cmd_courses":
                await _ajouter_article_liste(chat_id, "lait")
            elif data == "cmd_samedi":
                await _envoyer_activites_samedi(chat_id)
        return MessageResponse(message="ok", id=0)

    message = payload.get("message") or {}
    if not message:
        return MessageResponse(message="ok", id=0)

    chat_id = str((message.get("chat") or {}).get("id") or "")
    texte = str(message.get("text") or "").strip()
    if not chat_id or not texte:
        return MessageResponse(message="ok", id=0)

    normalise = _normaliser_texte(texte)
    logger.info("Message Telegram recu (%s): %s", chat_id[:6], normalise)

    if "ce soir" in normalise or "qu'est-ce qu'on mange" in normalise or "quest ce quon mange" in normalise:
        await _envoyer_repas_du_soir(chat_id)
    elif normalise.startswith("ajoute ") or normalise.startswith("ajouter "):
        await _ajouter_article_liste(chat_id, _extraire_article_depuis_commande(texte))
    elif "activite samedi" in normalise or "activite pour samedi" in normalise:
        await _envoyer_activites_samedi(chat_id)
    else:
        from src.services.integrations.telegram import envoyer_message_interactif

        await envoyer_message_interactif(
            destinataire=chat_id,
            corps=(
                "🤖 Commandes Telegram disponibles:\n"
                "- Qu'est-ce qu'on mange ce soir ?\n"
                "- Ajoute lait a la liste\n"
                "- Activite samedi ?"
            ),
            boutons=[
                {"id": "cmd_ce_soir", "title": "Ce soir"},
                {"id": "cmd_courses", "title": "Courses"},
                {"id": "cmd_samedi", "title": "Samedi"},
            ],
        )

    return MessageResponse(message="ok", id=0)
