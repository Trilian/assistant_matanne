"""Routes Assistant vocal et commandes textuelles."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_CREATION, REPONSES_CRUD_LECTURE
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])


class CommandeVocaleRequest(BaseModel):
    """Payload texte issu de la reconnaissance vocale."""

    texte: str = Field(..., min_length=2)


class AssistantChatRequest(BaseModel):
    """Payload chat assistant contextuel (IA4)."""

    message: str = Field(..., min_length=1, max_length=2000)
    contexte: str = Field(default="general")
    historique: list[dict[str, str]] = Field(default_factory=list)


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
    - Ajouter une mesure de croissance Jules
    - Créer un rappel simple via routine
    - Résumer le planning de demain
    """

    texte = payload.texte.strip()
    if not texte:
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")

    def _action() -> dict[str, Any]:
        from src.core.models import (
            ArticleCourses,
            Ingredient,
            ListeCourses,
            Planning,
            ProfilEnfant,
            Repas,
            Routine,
            TacheRoutine,
        )
        from src.core.models.carnet_sante import MesureCroissance

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
                return {
                    "action": "courses.ajout",
                    "message": f"{nom_article.title()} a été ajouté à la liste {liste.nom}.",
                    "details": {"liste_id": liste.id, "article_id": article.id},
                }

            poids_match = re.search(
                r"jules\s+p[eè]se\s+(?P<poids>\d+(?:[\.,]\d+)?)\s*kg",
                texte_lower,
            )
            if poids_match:
                poids = float(poids_match.group("poids").replace(",", "."))
                enfant = (
                    session.query(ProfilEnfant)
                    .filter(ProfilEnfant.actif.is_(True))
                    .order_by(ProfilEnfant.id.asc())
                    .first()
                )
                if enfant is None:
                    raise HTTPException(status_code=404, detail="Profil Jules introuvable")

                age_mois = None
                if enfant.date_of_birth:
                    age_mois = max(
                        0,
                        (date.today().year - enfant.date_of_birth.year) * 12
                        + date.today().month
                        - enfant.date_of_birth.month,
                    )

                mesure = MesureCroissance(
                    enfant_id=enfant.id,
                    date_mesure=date.today(),
                    poids_kg=poids,
                    age_mois=age_mois,
                    notes="Ajout via assistant vocal",
                )
                session.add(mesure)
                session.commit()
                return {
                    "action": "jules.croissance",
                    "message": f"Mesure enregistrée: Jules pèse {poids:.1f} kg.",
                    "details": {"mesure_id": mesure.id},
                }

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
                return {
                    "action": "routine.creation",
                    "message": f"Rappel créé pour: {tache}.",
                    "details": {"routine_id": routine.id},
                }

            if "planning de demain" in texte_lower or "programme de demain" in texte_lower:
                demain = date.today() + timedelta(days=1)
                planning = (
                    session.query(Planning)
                    .order_by(Planning.cree_le.desc())
                    .first()
                )
                repas = []
                if planning is not None:
                    repas = (
                        session.query(Repas)
                        .filter(Repas.planning_id == planning.id, Repas.date_repas == demain)
                        .order_by(Repas.type_repas.asc())
                        .all()
                    )
                if not repas:
                    return {
                        "action": "planning.resume",
                        "message": "Aucun repas planifié pour demain.",
                        "details": {"date": demain.isoformat()},
                    }

                resume = ", ".join(
                    f"{r.type_repas}: {getattr(getattr(r, 'recette', None), 'nom', 'repas libre')}"
                    for r in repas
                )
                return {
                    "action": "planning.resume",
                    "message": f"Demain, le planning prévoit {resume}.",
                    "details": {"date": demain.isoformat(), "count": len(repas)},
                }

            return {
                "action": "incomprise",
                "message": "Commande comprise mais non exécutable pour l'instant. Essayez avec une liste de courses, le poids de Jules, un rappel, ou le planning de demain.",
                "details": {"texte": texte},
            }

    return await executer_async(_action)


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
        from sqlalchemy import func

        from src.core.models import ActiviteFamille, ArticleInventaire, BudgetFamille, Repas
        from src.core.models.calendrier import EvenementPlanning
        from src.services.dashboard.points_famille import obtenir_points_famille_service
        from src.services.utilitaires.chat_ai import obtenir_chat_ai_service

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

        service = obtenir_chat_ai_service()
        reponse = service.envoyer_message_contextualise(
            message=payload.message,
            contexte_metier=contexte_metier,
            contexte=payload.contexte if payload.contexte else "general",
            historique=payload.historique,
        )

        return {
            "reponse": reponse or "Je n'ai pas pu generer de reponse pour le moment.",
            "contexte": payload.contexte,
            "memoire_utilisee": min(5, len(payload.historique or [])),
            "contexte_metier": contexte_metier,
        }

    return await executer_async(_query)


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