"""Routes FastAPI Telegram (webhook + endpoints d'envoi)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.dependencies import require_auth
from src.api.schemas import MessageResponse
from src.api.utils import gerer_exception_api

from ._callbacks import (
    _obtenir_message_id,
    _traiter_callback_action_article,
    _traiter_callback_courses,
    _traiter_callback_menu,
    _traiter_callback_planning,
    _traiter_callback_sondage_repas,
    _traiter_callback_tache,
    _traiter_callback_toggle_article,
    _traiter_reponse_rapide_ok,
)
from ._cuisine import (
    _ajouter_article_liste,
    _envoyer_courses_commande,
    _envoyer_repas_du_soir,
)
from ._dispatcher import _dispatcher_commande_telegram
from ._famille import _envoyer_activites_samedi
from ._helpers import (
    _construire_message_aide,
    _extraire_article_depuis_commande,
    _extraire_commande_telegram,
    _normaliser_texte,
)
from ._outils import _traiter_photo_frigo_telegram
from ._schemas import (
    LIBELLES_MAGASINS,
    EnvoyerCoursesMagasinRequest,
    EnvoyerCoursesTelegramRequest,
    EnvoyerPlanningTelegramRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["Telegram"])


async def _enregistrer_webhook_telegram(base_url: str) -> dict[str, Any]:
    """Enregistre le webhook Telegram avec l'URL publique de l'API."""
    import httpx

    from src.core.config import obtenir_parametres

    settings = obtenir_parametres()
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN non configuré"}

    webhook_url = f"{base_url.rstrip('/')}/api/v1/telegram/webhook"
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(api_url, json={"url": webhook_url, "drop_pending_updates": False})
            data = resp.json()
            if data.get("ok"):
                logger.info("✅ Webhook Telegram enregistré : %s", webhook_url)
            else:
                logger.warning("⚠️ Échec enregistrement webhook : %s", data.get("description"))
            return data
    except Exception as exc:
        logger.error("❌ Erreur enregistrement webhook Telegram : %s", exc)
        return {"ok": False, "error": str(exc)}


async def _obtenir_info_webhook() -> dict[str, Any]:
    """Retourne les informations du webhook Telegram enregistré."""
    import httpx

    from src.core.config import obtenir_parametres

    settings = obtenir_parametres()
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN non configuré"}

    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(api_url)
            return resp.json()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@router.post("/setup-webhook", response_model=MessageResponse)
@gerer_exception_api
async def setup_webhook(
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Enregistre ou met à jour le webhook Telegram.

    Utilise APP_BASE_URL depuis les paramètres. Appeler une fois après chaque
    nouveau déploiement Railway pour activer les callbacks des boutons.
    """
    from src.core.config import obtenir_parametres

    settings = obtenir_parametres()
    base_url = settings.APP_BASE_URL
    if not base_url:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="APP_BASE_URL non configuré. Ajoutez cette variable dans Railway.",
        )

    result = await _enregistrer_webhook_telegram(base_url)
    if not result.get("ok"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=502,
            detail=f"Échec Telegram : {result.get('description') or result.get('error')}",
        )
    return MessageResponse(message="webhook_enregistre", id=0)


@router.get("/webhook-info")
@gerer_exception_api
async def webhook_info(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne les informations du webhook Telegram actuellement configuré."""
    return await _obtenir_info_webhook()


@router.post("/envoyer-planning", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_planning_telegram(
    payload: EnvoyerPlanningTelegramRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
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
            repas_tries = sorted(
                planning.repas, key=lambda item: (item.date_repas, item.type_repas)
            )
            from src.api.routes.telegram._helpers import _formater_planning_html

            noms_recettes: list[str] = []
            for repas in repas_tries:
                nom_recette = None
                if getattr(repas, "recette", None) is not None:
                    nom_recette = getattr(repas.recette, "nom", None)
                nom_affiche = nom_recette or "Repas à préciser"
                noms_recettes.append(str(nom_affiche))
                lignes.append(nom_affiche)  # conservé pour le résumé IA uniquement
            contenu_formate = _formater_planning_html(repas_tries)

            noms_uniques = {nom.lower() for nom in noms_recettes if nom}
            mots_reconfort = ("soupe", "gratin", "curry", "mijot", "potage", "parmentier")
            resume_parts: list[str] = []
            if any(any(mot in nom.lower() for mot in mots_reconfort) for nom in noms_recettes):
                resume_parts.append("semaine plutôt réconfortante, adaptée au temps frais")
            if noms_recettes and len(noms_uniques) == len(noms_recettes):
                resume_parts.append("bonne variété de repas sans doublon direct")
            elif noms_recettes:
                resume_parts.append("quelques répétitions utiles pour simplifier les courses")

            return {
                "planning_id": planning.id,
                "contenu": payload.contenu
                or contenu_formate
                or f"Planning {planning.nom} du {planning.semaine_debut.strftime('%d/%m')} au {planning.semaine_fin.strftime('%d/%m')}",
                "resume_ia": " • ".join(resume_parts[:2]),
            }

    resultat = await executer_async(_charger_planning)
    kwargs_envoi: dict[str, object] = {
        "planning_id": int(resultat["planning_id"]),
        "resume_ia": str(resultat.get("resume_ia") or ""),
    }

    succes = await envoyer_planning_semaine(
        str(resultat["contenu"]),
        **kwargs_envoi,
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


@router.post("/envoyer-courses-magasin", response_model=MessageResponse)
@gerer_exception_api
async def envoyer_courses_par_magasin(payload: EnvoyerCoursesMagasinRequest) -> MessageResponse:
    """Envoie sur Telegram les articles d'une liste filtrés par magasin cible."""
    from src.api.utils import executer_async, executer_avec_session
    from src.core.models.courses import ArticleCourses, ListeCourses
    from src.services.integrations.telegram import envoyer_liste_courses_partagee

    def _charger_articles() -> dict[str, object]:
        with executer_avec_session() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == payload.liste_id).first()
            if not liste:
                raise HTTPException(status_code=404, detail="Liste de courses non trouvée")

            articles_db = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.magasin_cible == payload.magasin,
                    ArticleCourses.achete.is_(False),
                )
                .order_by(ArticleCourses.rayon_magasin, ArticleCourses.id)
                .all()
            )

            articles = []
            for article in articles_db:
                ingredient = getattr(article, "ingredient", None)
                nom = getattr(ingredient, "nom", None) or f"Article #{article.id}"
                qte = article.quantite_necessaire
                unite = getattr(ingredient, "unite", "") or ""
                ligne = f"{nom} ({qte} {unite})".strip() if qte != 1 else nom
                articles.append(ligne)

            if not articles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Aucun article non acheté pour le magasin '{payload.magasin}'",
                )

            libelle = LIBELLES_MAGASINS.get(payload.magasin, payload.magasin)
            nom_liste = payload.nom_liste or f"{libelle} — {liste.nom}"

            return {
                "liste_id": liste.id,
                "nom_liste": nom_liste,
                "articles": articles,
            }

    resultat = await executer_async(_charger_articles)
    succes = await envoyer_liste_courses_partagee(
        list(resultat["articles"]),
        nom_liste=str(resultat["nom_liste"]),
        liste_id=int(resultat["liste_id"]),
    )
    if not succes:
        raise HTTPException(status_code=502, detail="Envoi Telegram impossible")

    return MessageResponse(message="courses_magasin_envoyees", id=int(resultat["liste_id"]))


@router.post("/webhook", response_model=MessageResponse)
@gerer_exception_api
async def recevoir_update_telegram(request: Request) -> MessageResponse:
    """Recoit un update Telegram et traite les commandes principales et callbacks."""
    payload = await request.json()

    # Traitement des callbacks issus des boutons interactifs.
    callback_query = payload.get("callback_query") or {}
    if callback_query:
        data = str(callback_query.get("data") or "").strip()
        message_info = callback_query.get("message") or {}
        chat_id = str((message_info.get("chat") or {}).get("id") or "")
        callback_query_id = callback_query.get("id") or ""
        message_id = message_info.get("message_id")

        if not chat_id or not data or not callback_query_id:
            logger.warning(
                f"Callback incomplet: chat_id={chat_id}, data={data}, id={callback_query_id}"
            )
            return MessageResponse(message="invalid_callback", id=0)

        logger.info(f"Callback Telegram reçu: {data} (msg_id={message_id})")

        # Accusé de réception immédiat (< 10 s deadline Telegram).
        # Appelé en premier avant tout traitement lourd pour éviter le timeout
        # en cas de cold-start Railway (15-30 s de démarrage).
        from src.services.integrations.telegram import repondre_callback_query as _ack
        await _ack(callback_query_id)

        # Dispatch vers le handler correspondant.
        if data.startswith("courses_toggle_article:"):
            await _traiter_callback_toggle_article(data, callback_query_id, chat_id)
        elif data.startswith("courses_action:"):
            await _traiter_callback_action_article(data, callback_query_id, chat_id)
        elif data.startswith("repas_sondage:"):
            await _traiter_callback_sondage_repas(data, callback_query_id, chat_id)
        elif data.startswith("planning_"):
            await _traiter_callback_planning(data, callback_query_id, chat_id, message_id)
        elif data.startswith("tache_"):
            await _traiter_callback_tache(data, callback_query_id, chat_id)
        elif data.startswith("courses_"):
            await _traiter_callback_courses(data, callback_query_id, chat_id, message_id)
        elif data.startswith("menu_") or data.startswith("action_"):
            await _traiter_callback_menu(data, callback_query_id, chat_id)
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
    photos = message.get("photo") or []
    texte = str(message.get("text") or "").strip()

    if chat_id and photos:
        await _traiter_photo_frigo_telegram(chat_id, list(photos))
        return MessageResponse(message="ok", id=0)

    if not chat_id or not texte:
        return MessageResponse(message="ok", id=0)

    normalise = _normaliser_texte(texte)
    logger.info("Message Telegram recu (%s): %s", chat_id[:6], normalise)

    if normalise in {"ok", "oui", "vas-y", "go", "valide"}:
        if await _traiter_reponse_rapide_ok(chat_id):
            return MessageResponse(message="ok", id=0)

    commande = _extraire_commande_telegram(texte)
    if commande.startswith("/") or commande in {"menu", "aide", "help"}:
        if await _dispatcher_commande_telegram(chat_id, texte, commande):
            return MessageResponse(message="ok", id=0)

    if (
        "ce soir" in normalise
        or "qu'est-ce qu'on mange" in normalise
        or "quest ce quon mange" in normalise
    ):
        await _envoyer_repas_du_soir(chat_id)
    elif normalise.startswith("ajoute ") or normalise.startswith("ajouter "):
        await _ajouter_article_liste(chat_id, _extraire_article_depuis_commande(texte))
    elif "activite samedi" in normalise or "activite pour samedi" in normalise:
        await _envoyer_activites_samedi(chat_id)
    else:
        from src.services.integrations.telegram import envoyer_message_interactif

        await envoyer_message_interactif(
            destinataire=chat_id,
            corps=_construire_message_aide(),
            boutons=[
                {"id": "menu_principal", "title": "🏠 Menu principal"},
                {"id": "action_planning", "title": "🍽️ Planning"},
                {"id": "action_courses", "title": "🛒 Courses"},
            ],
        )

    return MessageResponse(message="ok", id=0)
