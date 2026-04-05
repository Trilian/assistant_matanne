"""Routes Assistant vocal et commandes textuelles."""

from __future__ import annotations

import json
import logging
import re
import os
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])


class CommandeVocaleRequest(BaseModel):
    """Payload texte issu de la reconnaissance vocale."""

    texte: str = Field(..., min_length=2)


class AssistantChatRequest(BaseModel):
    """Payload chat assistant contextuel (IA4)."""

    message: str = Field(..., min_length=1, max_length=2000)
    contexte: str = Field(default="general")
    historique: list[dict[str, str]] = Field(default_factory=list)


class GoogleAssistantIntentRequest(BaseModel):
    """Payload d'exécution d'un intent Google Assistant."""

    intent: str = Field(..., min_length=3, max_length=80)
    slots: dict[str, Any] = Field(default_factory=dict)
    langue: str = Field(default="fr-FR", max_length=10)


INTENTS_GOOGLE_ASSISTANT: dict[str, dict[str, Any]] = {
    "courses_ajouter_article": {
        "description": "Ajouter un article à la liste de courses",
        "slots": ["article"],
        "template": "ajoute du {article} à la liste",
        "action_attendue": "courses.ajout",
    },
    "planning_resume_demain": {
        "description": "Résumer le planning de demain",
        "slots": [],
        "template": "quel est mon planning de demain",
        "action_attendue": "planning.resume",
    },
    "routines_creer_rappel": {
        "description": "Créer un rappel rapide",
        "slots": ["tache", "moment"],
        "template": "rappelle-moi {tache} {moment}",
        "action_attendue": "routine.creation",
    },
    "google_home_bonsoir": {
        "description": "Routine Bonsoir : planning demain + rappel tache",
        "slots": ["tache"],
        "template": "rappelle-moi {tache} demain et quel est mon planning de demain",
        "action_attendue": "routine.bonsoir",
    },
}


def _publier_evenement_assistant(
    type_evenement: str,
    data: dict[str, Any],
    source: str,
) -> None:
    """Publie un événement assistant sans interrompre le flux API."""
    try:
        from src.services.core.events import obtenir_bus

        obtenir_bus().emettre(type_evenement, data, source=source)
    except Exception:
        logger.debug("Échec publication événement assistant %s (non bloquant)", type_evenement)


def _rendre_commande_depuis_intent(intent: str, slots: dict[str, Any]) -> str:
    """Construit une commande textuelle à partir d'un intent Google Assistant."""
    config = INTENTS_GOOGLE_ASSISTANT.get(intent)
    if not config:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Intent Google Assistant non supporté: {intent}",
                "intents_supportes": sorted(INTENTS_GOOGLE_ASSISTANT.keys()),
            },
        )

    valeurs = dict(slots or {})
    if intent == "routines_creer_rappel" and "moment" not in valeurs:
        valeurs["moment"] = "demain"

    manquants = [s for s in config.get("slots", []) if not valeurs.get(s)]
    if manquants:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Slots manquants pour exécuter l'intent",
                "intent": intent,
                "slots_requis": config.get("slots", []),
                "slots_manquants": manquants,
            },
        )

    return str(config["template"]).format(**valeurs)


def _extraire_payload_google_assistant(payload: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    """Extrait intent, slots et langue depuis un payload fulfillment Google Assistant."""
    intent = (
        payload.get("intent", {}).get("displayName")
        or payload.get("intent", {}).get("name")
        or payload.get("queryResult", {}).get("intent", {}).get("displayName")
        or payload.get("intent")
    )

    session_info = payload.get("sessionInfo") or {}
    query_result = payload.get("queryResult") or {}
    slots = (
        session_info.get("parameters")
        or query_result.get("parameters")
        or payload.get("slots")
        or {}
    )

    langue = (
        payload.get("languageCode")
        or query_result.get("languageCode")
        or "fr-FR"
    )

    if not isinstance(intent, str) or not intent.strip():
        raise HTTPException(status_code=400, detail="Intent manquant dans le payload Google Assistant")

    if not isinstance(slots, dict):
        slots = {}

    return intent.strip(), slots, str(langue)


def _normaliser_historique_chat(historique: list[dict[str, str]] | None) -> list[dict[str, str]]:
    """Normalise l'historique pour accepter `content` et `contenu`."""
    normalise: list[dict[str, str]] = []
    for message in historique or []:
        role = str(message.get("role") or "user")
        contenu = str(message.get("contenu") or message.get("content") or "")
        normalise.append({"role": role, "contenu": contenu})
    return normalise


def _collecter_contexte_metier_chat() -> dict[str, Any]:
    """Construit le contexte métier injecté dans le chat IA."""
    from sqlalchemy import func

    from src.core.models import (
        ActiviteFamille,
        ArticleInventaire,
        BudgetFamille,
        EvenementPlanning,
        Repas,
    )
    from src.services.dashboard.points_famille import obtenir_points_famille_service

    today = date.today()
    horizon = today + timedelta(days=7)
    debut_mois = today.replace(day=1)

    with executer_avec_session() as session:
        contexte_metier = {
            "planning": {
                "repas_7j": int(
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= today, Repas.date_repas <= horizon)
                    .scalar()
                    or 0
                ),
                "activites_7j": int(
                    session.query(func.count(ActiviteFamille.id))
                    .filter(
                        ActiviteFamille.date_prevue >= today,
                        ActiviteFamille.date_prevue <= horizon,
                    )
                    .scalar()
                    or 0
                ),
                "evenements_7j": int(
                    session.query(func.count(EvenementPlanning.id))
                    .filter(
                        EvenementPlanning.date_debut >= today,
                        EvenementPlanning.date_debut <= horizon,
                    )
                    .scalar()
                    or 0
                ),
            },
            "inventaire": {
                "stock_bas": int(
                    session.query(func.count(ArticleInventaire.id))
                    .filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)
                    .scalar()
                    or 0
                ),
                "peremptions_7j": int(
                    session.query(func.count(ArticleInventaire.id))
                    .filter(
                        ArticleInventaire.date_peremption.isnot(None),
                        ArticleInventaire.date_peremption >= today,
                        ArticleInventaire.date_peremption <= horizon,
                    )
                    .scalar()
                    or 0
                ),
            },
            "budget": {
                "depenses_mois": float(
                    session.query(func.sum(BudgetFamille.montant))
                    .filter(BudgetFamille.date >= debut_mois)
                    .scalar()
                    or 0.0
                )
            },
            "score_jules": {},
        }

    points = obtenir_points_famille_service().calculer_points() or {}
    contexte_metier["score_jules"] = {
        "total_points": int(points.get("total_points", 0)),
        "badges": points.get("badges", []),
    }
    return contexte_metier


def _executer_commande_assistant(texte: str, source: str = "assistant_api") -> dict[str, Any]:
    """Exécute une commande assistant (voix/Google Assistant) et retourne le résultat."""
    from src.core.models import (
        ArticleCourses,
        Ingredient,
        ListeCourses,
        Planning,
        Repas,
        Routine,
        TacheRoutine,
    )

    texte_lower = texte.lower()
    with executer_avec_session() as session:
        course_match = re.search(
            r"(?:ajoute|ajouter)\s+(?:du|de la|de l'|des)?\s*(?P<article>[\w\s\-éèêàùç']+)\s+(?:à|dans)\s+la\s+liste",
            texte_lower,
        )
        if course_match:
            from src.core.validation import SanitiseurDonnees

            nom_article = SanitiseurDonnees.nettoyer_texte(
                course_match.group("article").strip(" .,!?")
            )
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.archivee.is_(False))
                .order_by(ListeCourses.id.desc())
                .first()
            )
            if not liste:
                liste = ListeCourses(nom="Liste principale", archivee=False)
                session.add(liste)
                session.flush()

            ingredient = session.query(Ingredient).filter(Ingredient.nom == nom_article).first()
            if ingredient is None:
                ingredient = Ingredient(nom=nom_article, unite="pcs")
                session.add(ingredient)
                session.flush()

            article = ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1.0,
            )
            session.add(article)
            session.commit()
            resultat = {
                "action": "courses.ajout",
                "message": f"{nom_article.title()} a été ajouté à la liste {liste.nom}.",
                "details": {"liste_id": liste.id, "article_id": article.id},
            }
            _publier_evenement_assistant(
                "assistant.commande_executee",
                {"texte": texte, "action": resultat["action"]},
                source=source,
            )
            return resultat

        rappel_match = re.search(
            r"rappelle[- ]moi\s+(?P<tache>.+?)\s+(?:demain|ce soir|ce matin)",
            texte_lower,
        )
        if rappel_match:
            tache = rappel_match.group("tache").strip(" .,!?")
            routine = Routine(nom=f"Rappel: {tache}", categorie="assistant", actif=True)
            session.add(routine)
            session.flush()
            session.add(TacheRoutine(routine_id=routine.id, nom=tache, ordre=1))
            session.commit()
            resultat = {
                "action": "routine.creation",
                "message": f"Rappel créé pour: {tache}.",
                "details": {"routine_id": routine.id},
            }
            _publier_evenement_assistant(
                "assistant.commande_executee",
                {"texte": texte, "action": resultat["action"]},
                source=source,
            )
            return resultat

        if "planning de demain" in texte_lower or "programme de demain" in texte_lower:
            demain = date.today() + timedelta(days=1)
            planning = session.query(Planning).order_by(Planning.cree_le.desc()).first()
            repas = []
            if planning is not None:
                repas = (
                    session.query(Repas)
                    .filter(Repas.planning_id == planning.id, Repas.date_repas == demain)
                    .order_by(Repas.type_repas.asc())
                    .all()
                )
            if not repas:
                resultat = {
                    "action": "planning.resume",
                    "message": "Aucun repas planifié pour demain.",
                    "details": {"date": demain.isoformat()},
                }
                _publier_evenement_assistant(
                    "assistant.commande_executee",
                    {"texte": texte, "action": resultat["action"]},
                    source=source,
                )
                return resultat

            resume = ", ".join(
                f"{r.type_repas}: {getattr(getattr(r, 'recette', None), 'nom', 'repas libre')}"
                for r in repas
            )
            resultat = {
                "action": "planning.resume",
                "message": f"Demain, le planning prévoit {resume}.",
                "details": {"date": demain.isoformat(), "count": len(repas)},
            }
            _publier_evenement_assistant(
                "assistant.commande_executee",
                {"texte": texte, "action": resultat["action"]},
                source=source,
            )
            return resultat

        return {
            "action": "incomprise",
            "message": "Commande comprise mais non exécutable pour l'instant. Essayez avec une liste de courses, un rappel, ou le planning de demain.",
            "details": {"texte": texte},
        }


@router.post(
    "/commande-vocale",
    responses=REPONSES_CRUD_CREATION,
    summary="Interpréter une commande vocale",
)
@gerer_exception_api
async def interpreter_commande_vocale(
    payload: CommandeVocaleRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Interprète une commande vocale et exécute une action simple.

    Intentions actuellement gérées:
    - Ajouter un article à la liste de courses
    - Créer un rappel simple via routine
    - Résumer le planning de demain
    """

    texte = payload.texte.strip()
    if not texte:
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")

    def _action() -> dict[str, Any]:
        return _executer_commande_assistant(texte=texte, source="assistant_vocal")

    return await executer_async(_action)


@router.get(
    "/google-assistant/intents",
    summary="Lister les intents Google Assistant supportés",
)
@gerer_exception_api
async def lister_intents_google_assistant(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Expose le mapping intents/actions pour les raccourcis Google Assistant (I.10)."""
    return {
        "intents": [
            {
                "intent": intent,
                "description": cfg["description"],
                "slots": cfg["slots"],
                "action_attendue": cfg["action_attendue"],
            }
            for intent, cfg in sorted(INTENTS_GOOGLE_ASSISTANT.items())
        ]
    }


@router.post(
    "/google-assistant/executer",
    summary="Exécuter un intent Google Assistant",
)
@gerer_exception_api
async def executer_intent_google_assistant(
    payload: GoogleAssistantIntentRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Convertit un intent en commande puis exécute l'action backend associée."""

    commande = _rendre_commande_depuis_intent(payload.intent, payload.slots)

    def _action() -> dict[str, Any]:
        resultat = _executer_commande_assistant(
            texte=commande,
            source=f"google_assistant:{payload.intent}",
        )
        return {
            "intent": payload.intent,
            "langue": payload.langue,
            "commande": commande,
            "resultat": resultat,
        }

    return await executer_async(_action)


@router.post(
    "/google-assistant/webhook",
    summary="Webhook fulfillment Google Assistant",
)
@gerer_exception_api
async def webhook_google_assistant(
    request: Request,
    x_assistant_secret: str | None = Header(default=None),
) -> dict[str, Any]:
    """Endpoint fulfillment direct pour Google Assistant (Dialogflow/Actions)."""

    secret_attendu = os.getenv("GOOGLE_ASSISTANT_WEBHOOK_SECRET", "").strip()
    if secret_attendu and x_assistant_secret != secret_attendu:
        raise HTTPException(status_code=401, detail="Webhook Google Assistant non autorisé")

    payload = await request.json()
    intent, slots, langue = _extraire_payload_google_assistant(payload)

    def _action() -> dict[str, Any]:
        try:
            commande = _rendre_commande_depuis_intent(intent, slots)
            resultat = _executer_commande_assistant(
                texte=commande,
                source=f"google_assistant_webhook:{intent}",
            )
            message = str(resultat.get("message") or "Action exécutée.")
            action = str(resultat.get("action") or "incomprise")
        except HTTPException as e:
            message = f"Je n'ai pas pu exécuter cette action: {e.detail}"
            action = "erreur"
            commande = ""

        return {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [message],
                        }
                    }
                ]
            },
            "sessionInfo": {
                "parameters": {
                    "intent": intent,
                    "langue": langue,
                    "action": action,
                    "commande": commande,
                }
            },
        }

    return await executer_async(_action)


@router.get(
    "/proactif/dernieres-suggestions",
    summary="Dernières suggestions proactives issues de l'EventBus",
)
@gerer_exception_api
async def obtenir_dernieres_suggestions_proactives(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Expose les suggestions proactives les plus récentes produites par I.15."""

    def _query() -> dict[str, Any]:
        from src.services.utilitaires.chat.assistant_proactif import (
            obtenir_service_assistant_proactif,
        )

        return obtenir_service_assistant_proactif().obtenir_derniere_suggestion()

    return await executer_async(_query)


@router.post(
    "/chat",
    responses=REPONSES_CRUD_LECTURE,
    summary="Chat IA contextuel enrichi",
)
@gerer_exception_api
async def chat_assistant_contextuel(
    payload: AssistantChatRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Chat IA avec contexte cross-module (planning, inventaire, budget, score Jules, evenements)."""

    def _query() -> dict[str, Any]:
        from src.services.utilitaires.chat.chat_ai import obtenir_chat_ai_service

        contexte_metier = _collecter_contexte_metier_chat()
        historique = _normaliser_historique_chat(payload.historique)

        service = obtenir_chat_ai_service()
        reponse = service.envoyer_message_contextualise(
            message=payload.message,
            contexte_metier=contexte_metier,
            contexte=payload.contexte if payload.contexte else "general",
            historique=historique,
        )

        _publier_evenement_assistant(
            "chat.contexte.mis_a_jour",
            {
                "contexte": payload.contexte or "general",
                "memoire_utilisee": min(5, len(historique)),
            },
            source="chat_assistant",
        )

        return {
            "reponse": reponse or "Je n'ai pas pu generer de reponse pour le moment.",
            "contexte": payload.contexte,
            "memoire_utilisee": min(5, len(historique)),
            "contexte_metier": contexte_metier,
        }

    return await executer_async(_query)


@router.post(
    "/chat/stream",
    summary="Chat IA contextuel en streaming SSE",
)
@gerer_exception_api
async def chat_assistant_contextuel_stream(
    payload: AssistantChatRequest,
    user: dict[str, Any] = Depends(require_auth),
) -> StreamingResponse:
    """Diffuse la réponse IA au fil de l'eau via Server-Sent Events."""
    from src.services.utilitaires.chat.chat_ai import obtenir_chat_ai_service

    contexte_metier = _collecter_contexte_metier_chat()
    historique = _normaliser_historique_chat(payload.historique)
    service = obtenir_chat_ai_service()

    _publier_evenement_assistant(
        "chat.streaming.demarre",
        {
            "contexte": payload.contexte or "general",
            "memoire_utilisee": min(5, len(historique)),
        },
        source="chat_assistant_stream",
    )

    def _stream() -> Any:
        yield (
            "event: context\n"
            f"data: {json.dumps({'contexte': payload.contexte or 'general', 'memoire_utilisee': min(5, len(historique))}, ensure_ascii=False)}\n\n"
        )

        a_emit_un_token = False
        try:
            for chunk in service.streamer_message(
                message=payload.message,
                contexte=payload.contexte if payload.contexte else "general",
                historique=historique,
            ):
                texte = str(chunk or "")
                if not texte.strip():
                    continue
                a_emit_un_token = True
                yield f"event: token\ndata: {texte}\n\n"
        except Exception as exc:
            logger.warning("Streaming chat assistant interrompu: %s", exc)
            yield "event: error\ndata: Le streaming IA a été interrompu.\n\n"

        if not a_emit_un_token:
            yield "event: token\ndata: Je n'ai pas pu generer de reponse pour le moment.\n\n"

        yield f"event: done\ndata: {json.dumps({'status': 'completed'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        _stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get(
    "/commande-vocale/exemples",
    responses=REPONSES_CRUD_LECTURE,
    summary="Exemples de commandes vocales",
)
async def exemples_commandes_vocales() -> dict[str, list[str]]:
    return {
        "exemples": [
            "Ajoute du lait à la liste",
            "Jules pèse 11,4 kg",
            "Rappelle-moi appeler le plombier demain",
            "Quel est mon planning de demain ?",
        ]
    }