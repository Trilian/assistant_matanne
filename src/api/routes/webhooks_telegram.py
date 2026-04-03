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

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])


class EnvoyerPlanningTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'un planning via Telegram."""

    planning_id: int
    contenu: str | None = None


class EnvoyerCoursesTelegramRequest(BaseModel):
    """Payload pour l'envoi manuel d'une liste de courses via Telegram."""

    liste_id: int
    nom_liste: str | None = None


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


def _extraire_id_depuis_callback(callback_data: str, prefix: str) -> int | None:
    """Extrait l'ID depuis le callback_data (format: 'prefix:ID').
    
    Args:
        callback_data: Données du callback (ex: 'planning_valider:123')
        prefix: Préfixe attendu (ex: 'planning_valider')
    
    Returns:
        ID extrait ou None si format invalide
    """
    if not callback_data.startswith(f"{prefix}:"):
        return None
    try:
        return int(callback_data.split(":", 1)[1])
    except (ValueError, IndexError):
        return None


async def _traiter_callback_planning(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Traite les callbacks de planning: valider, modifier, régénérer.
    
    Phase 5.2: Webhook callbacks → endpoints de validation
    """
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query, modifier_message
    
    # Parse callback_data: "planning_valider:ID" ou "planning_valider" (backward compat)
    if ":" in callback_data:
        action, id_str = callback_data.split(":", 1)
        try:
            planning_id = int(id_str)
        except ValueError:
            await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide")
            logger.error(f"Invalid planning ID in callback: {callback_data}")
            return
    else:
        # Backward compat: prendre le planning de la semaine actuelle
        action = callback_data
        planning_id = None

    logger.info(f"Callback planning reçu: action={action}, planning_id={planning_id}")

    if action == "planning_valider":
        # Trigger: POST /api/v1/planning/{planning_id}/valider
        try:
            def _valider():
                from src.core.db import obtenir_contexte_db
                from src.core.models.planning import Planning

                with executer_avec_session() as session:
                    if planning_id:
                        planning = session.query(Planning).filter(Planning.id == planning_id).first()
                    else:
                        planning = session.query(Planning).order_by(Planning.semaine_debut.desc()).first()

                    if not planning:
                        return {"error": "Planning non trouvé", "status": 404}

                    if planning.etat != "brouillon":
                        return {"error": f"Planning déjà {planning.etat}", "status": 409}

                    planning.etat = "valide"
                    session.commit()
                    return {"message": "Planning validé", "id": planning.id, "status": 200}

            result = await executer_async(_valider)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "✅ Planning validé!",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "✅ <b>Planning validé</b>\n\nVotre planning a été validé et les courses sont générées.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback planning_valider: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "planning_modifier":
        # Instruction pour modifier via web
        web_url = "https://matanne.vercel.app/app/cuisine/planning"
        await repondre_callback_query(
            callback_query_id,
            f"Ouvrez ce lien pour modifier: {web_url}",
            show_alert=False,
        )

    elif action == "planning_regenerer":
        # Trigger: POST /api/v1/planning/{planning_id}/regenerer
        try:
            def _regenerer():
                from src.core.db import obtenir_contexte_db
                from src.core.models.planning import Planning

                with executer_avec_session() as session:
                    if planning_id:
                        old_planning = session.query(Planning).filter(Planning.id == planning_id).first()
                    else:
                        old_planning = session.query(Planning).order_by(Planning.semaine_debut.desc()).first()

                    if not old_planning:
                        return {"error": "Planning non trouvé", "status": 404}

                    if old_planning.etat == "archive":
                        return {"error": "Planning archivé ne peut pas être régénéré", "status": 409}

                    # Archive old planning
                    old_planning.etat = "archive"
                    session.flush()

                    # Create new planning (brouillon)
                    # This would normally be done by a service
                    new_planning = Planning(
                        nom=f"{old_planning.nom} (refait)",
                        semaine_debut=old_planning.semaine_debut,
                        semaine_fin=old_planning.semaine_fin,
                        etat="brouillon",
                    )
                    session.add(new_planning)
                    session.commit()
                    return {"message": "Planning régénéré", "id": new_planning.id, "status": 200}

            result = await executer_async(_regenerer)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "🔄 Planning en cours de régénération...",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "🔄 <b>Planning régénéré</b>\n\nLe nouveau planning en brouillon est prêt.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback planning_regenerer: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)


async def _traiter_callback_courses(
    callback_data: str,
    callback_query_id: str,
    chat_id: str,
) -> None:
    """Traite les callbacks de courses: confirmer, ajouter, refaire.
    
    Phase 5.2: Webhook callbacks → endpoints de confirmation
    """
    from src.api.utils import executer_async, executer_avec_session
    from src.services.integrations.telegram import repondre_callback_query, modifier_message
    
    # Parse callback_data: "courses_confirmer:ID" ou "courses_confirmer" (backward compat)
    if ":" in callback_data:
        action, id_str = callback_data.split(":", 1)
        try:
            liste_id = int(id_str)
        except ValueError:
            await repondre_callback_query(callback_query_id, "❌ Erreur: ID invalide")
            logger.error(f"Invalid courses list ID in callback: {callback_data}")
            return
    else:
        action = callback_data
        liste_id = None

    logger.info(f"Callback courses reçu: action={action}, liste_id={liste_id}")

    if action == "courses_confirmer":
        # Trigger: POST /api/v1/courses/{liste_id}/confirmer
        try:
            def _confirmer():
                from src.core.db import obtenir_contexte_db
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                    else:
                        liste = session.query(ListeCourses).filter(
                            ListeCourses.etat == "brouillon"
                        ).order_by(ListeCourses.cree_le.desc()).first()

                    if not liste:
                        return {"error": "Liste non trouvée", "status": 404}

                    if liste.etat != "brouillon":
                        return {"error": f"Liste déjà {liste.etat}", "status": 409}

                    liste.etat = "active"
                    session.commit()
                    return {"message": "Liste confirmée", "id": liste.id, "status": 200}

            result = await executer_async(_confirmer)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "✅ Liste confirmée!",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "✅ <b>Liste de courses confirmée</b>\n\nVous pouvez maintenant faire les courses!",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_confirmer: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)

    elif action == "courses_ajouter":
        # Instruction pour ajouter via web
        web_url = "https://matanne.vercel.app/app/cuisine/courses"
        await repondre_callback_query(
            callback_query_id,
            f"Ouvrez ce lien pour ajouter: {web_url}",
            show_alert=False,
        )

    elif action == "courses_refaire":
        # Archive current list and create new brouillon
        try:
            def _refaire():
                from src.core.db import obtenir_contexte_db
                from src.core.models.courses import ListeCourses

                with executer_avec_session() as session:
                    if liste_id:
                        old_liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                    else:
                        old_liste = session.query(ListeCourses).filter(
                            ListeCourses.etat == "brouillon"
                        ).order_by(ListeCourses.cree_le.desc()).first()

                    if not old_liste:
                        return {"error": "Liste non trouvée", "status": 404}

                    # Archive old list
                    old_liste.archivee = True
                    session.flush()

                    # Create new list (brouillon)
                    new_liste = ListeCourses(nom=f"{old_liste.nom} (refait)", etat="brouillon")
                    session.add(new_liste)
                    session.commit()
                    return {"message": "Liste refaite", "id": new_liste.id, "status": 200}

            result = await executer_async(_refaire)
            if result.get("status") == 200:
                await repondre_callback_query(
                    callback_query_id,
                    "🔄 Liste en cours de refonte...",
                    show_alert=False,
                )
                await modifier_message(
                    chat_id,
                    (await _obtenir_message_id(callback_query_id)) or 0,
                    "🔄 <b>Liste refaite</b>\n\nUne nouvelle liste brouillon a été créée.",
                    boutons=None,
                )
            else:
                await repondre_callback_query(
                    callback_query_id,
                    f"❌ {result.get('error', 'Erreur')}",
                    show_alert=True,
                )
        except Exception as e:
            logger.error(f"❌ Erreur traitement callback courses_refaire: {e}", exc_info=True)
            await repondre_callback_query(callback_query_id, "❌ Erreur serveur", show_alert=True)


async def _obtenir_message_id(callback_query_id: str) -> int | None:
    """Stub pour obtenir le message_id depuis callback_query_id (normally in payload)."""
    # Note: This would normally come from the webhook payload
    # For now, return None to indicate we can't modify the message
    return None


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
            .order_by(ListeCourses.cree_le.desc())
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


@router.post("/envoyer-planning", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_planning_telegram(payload: EnvoyerPlanningTelegramRequest) -> MessageResponse:
    """Envoie un planning existant sur Telegram avec boutons interactifs."""
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.planning import Planning
    from src.services.integrations.telegram import envoyer_planning_semaine

    def _charger_planning() -> dict[str, object]:
        with executer_avec_session() as session:
            planning = session.query(Planning).filter(Planning.id == payload.planning_id).first()
            if not planning:
                raise HTTPException(status_code=404, detail="Planning non trouvé")

            lignes = []
            repas_tries = sorted(planning.repas, key=lambda item: (item.date_repas, item.type_repas))
            for repas in repas_tries:
                nom_recette = None
                if getattr(repas, "recette", None) is not None:
                    nom_recette = getattr(repas.recette, "nom", None)
                lignes.append(
                    f"• {repas.date_repas.strftime('%d/%m')} {repas.type_repas} : {nom_recette or 'Repas à préciser'}"
                )

            return {
                "planning_id": planning.id,
                "contenu": payload.contenu
                or "\n".join(lignes)
                or f"Planning {planning.nom} du {planning.semaine_debut.strftime('%d/%m')} au {planning.semaine_fin.strftime('%d/%m')}",
            }

    resultat = await executer_async(_charger_planning)
    succes = await envoyer_planning_semaine(
        str(resultat["contenu"]),
        planning_id=int(resultat["planning_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="planning_envoye", id=int(resultat["planning_id"]))


@router.post("/envoyer-courses", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_courses_telegram(payload: EnvoyerCoursesTelegramRequest) -> MessageResponse:
    """Envoie une liste de courses existante sur Telegram avec boutons interactifs."""
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.courses import ListeCourses
    from src.services.integrations.telegram import envoyer_liste_courses_partagee

    def _charger_liste() -> dict[str, object]:
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == payload.liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste de courses non trouvée")

            articles = []
            for article in liste.articles:
                ingredient = getattr(article, "ingredient", None)
                nom_article = getattr(ingredient, "nom", None) or f"Article #{article.id}"
                articles.append(nom_article)

            if not articles:
                raise HTTPException(status_code=400, detail="La liste ne contient aucun article")

            return {
                "liste_id": liste.id,
                "nom_liste": payload.nom_liste or liste.nom,
                "articles": articles,
            }

    resultat = await executer_async(_charger_liste)
    succes = await envoyer_liste_courses_partagee(
        list(resultat["articles"]),
        nom_liste=str(resultat["nom_liste"]),
        liste_id=int(resultat["liste_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="courses_envoyees", id=int(resultat["liste_id"]))


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_update_telegram(request: Request) -> MessageResponse:
    """Recoit un update Telegram et traite les commandes principales et callbacks.
    
    Gère:
    - callback_query (Phase 5.2: planning/courses workflow buttons)
    - message texte (commandes naturelles)
    """
    payload = await request.json()

    # Phase 5.2: Traitement des callbacks (boutons interactifs)
    callback_query = payload.get("callback_query") or {}
    if callback_query:
        data = str(callback_query.get("data") or "").strip()
        message_info = callback_query.get("message") or {}
        chat_id = str((message_info.get("chat") or {}).get("id") or "")
        callback_query_id = callback_query.get("id") or ""
        message_id = message_info.get("message_id")

        if not chat_id or not data or not callback_query_id:
            logger.warning(f"Callback incomplet: chat_id={chat_id}, data={data}, id={callback_query_id}")
            return MessageResponse(message="invalid_callback", id=0)

        logger.info(f"Callback Telegram reçu: {data} (msg_id={message_id})")

        # Dispatch aux handlers Phase 5.2
        if data.startswith("planning_"):
            await _traiter_callback_planning(data, callback_query_id, chat_id)
        elif data.startswith("courses_"):
            await _traiter_callback_courses(data, callback_query_id, chat_id)
        else:
            # Backward compat: anciennes commandes
            if data == "cmd_ce_soir":
                await _envoyer_repas_du_soir(chat_id)
            elif data == "cmd_courses":
                await _ajouter_article_liste(chat_id, "lait")
            elif data == "cmd_samedi":
                await _envoyer_activites_samedi(chat_id)

        return MessageResponse(message="ok", id=0)

    # Traitement des messages texte (commandes naturelles, backward compat)
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
