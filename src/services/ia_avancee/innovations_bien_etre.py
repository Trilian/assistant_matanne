"""Fonctions bien-etre/scores extraites du service innovations."""

from __future__ import annotations

import logging
import re
from datetime import UTC, date, datetime, timedelta
from typing import Any

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_gestion_erreurs

from .innovations_types import (
    DimensionBienEtre,
    DimensionScoreFamille,
    ScoreBienEtreResponse,
)

logger = logging.getLogger(__name__)


def calculer_score_bien_etre(service) -> ScoreBienEtreResponse | None:
    """Calcule le score bien-être familial composite (0-100).

    Combine 4 dimensions :
    - Sport (Garmin) : pas, activités, calories
    - Nutrition : planning équilibré, score nutritionnel
    - Budget : stress financier, dépassements
    - Routines : régularité, accomplissement
    """
    dimensions = []
    scores = []

    # Dimension Sport (poids 30%)
    score_sport = service._calculer_score_sport()
    dimensions.append(DimensionBienEtre(
        nom="Sport & Activité Physique",
        score=score_sport,
        poids=0.30,
        detail=service._detail_sport(score_sport),
        tendance=service._evaluer_tendance("sport"),
    ))
    scores.append(score_sport * 0.30)

    # Dimension Nutrition (poids 25%)
    score_nutrition = service._calculer_score_nutrition()
    dimensions.append(DimensionBienEtre(
        nom="Nutrition & Alimentation",
        score=score_nutrition,
        poids=0.25,
        detail=service._detail_nutrition(score_nutrition),
        tendance=service._evaluer_tendance("nutrition"),
    ))
    scores.append(score_nutrition * 0.25)

    # Dimension Budget (poids 25%)
    score_budget = service._calculer_score_budget()
    dimensions.append(DimensionBienEtre(
        nom="Équilibre Financier",
        score=score_budget,
        poids=0.25,
        detail=service._detail_budget(score_budget),
        tendance=service._evaluer_tendance("budget"),
    ))
    scores.append(score_budget * 0.25)

    # Dimension Routines (poids 20%)
    score_routines = service._calculer_score_routines()
    dimensions.append(DimensionBienEtre(
        nom="Régularité & Routines",
        score=score_routines,
        poids=0.20,
        detail=service._detail_routines(score_routines),
        tendance=service._evaluer_tendance("routines"),
    ))
    scores.append(score_routines * 0.20)

    score_global = round(sum(scores), 1)
    niveau = service._evaluer_niveau(score_global)

    # Conseils basés sur les scores les plus bas
    conseils = service._generer_conseils(dimensions)

    return ScoreBienEtreResponse(
        score_global=score_global,
        niveau=niveau,
        dimensions=dimensions,
        historique_7j=[],
        conseils=conseils,
    )

def _calculer_score_sport(service) -> float:
    """Score sport basé sur Garmin (0-100)."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models.garmin import DonneesGarmin

            semaine = date.today() - timedelta(days=7)
            donnees = (
                session.query(DonneesGarmin)
                .filter(DonneesGarmin.date >= semaine)
                .all()
            )
            if not donnees:
                return 50.0

            pas_moyen = sum(getattr(d, "pas", 0) or 0 for d in donnees) / len(donnees)
            # 10000 pas/jour = 100, 0 = 0
            score = min(100, (pas_moyen / 10000) * 100)
            return round(score, 1)
    except Exception:
        return 50.0

def _calculer_score_nutrition(service) -> float:
    """Score nutrition basé sur le planning repas (0-100)."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models import Repas

            semaine = date.today() - timedelta(days=7)
            nb_repas = (
                session.query(func.count(Repas.id))
                .filter(Repas.date_repas >= semaine)
                .scalar() or 0
            )
            # 21 repas/semaine (3/jour) = 100
            score = min(100, (nb_repas / 21) * 100)
            return round(score, 1)
    except Exception:
        return 50.0

def _calculer_score_budget(service) -> float:
    """Score budget basé sur les dépassements (0-100)."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models import BudgetFamille

            mois_courant = date.today().replace(day=1)
            total = (
                session.query(func.sum(BudgetFamille.montant))
                .filter(BudgetFamille.date >= mois_courant)
                .scalar() or 0
            )
            # Moins de dépenses = meilleur score (heuristique simple)
            score = max(0, 100 - min(100, total / 50))
            return round(score, 1)
    except Exception:
        return 60.0

def _calculer_score_routines(service) -> float:
    """Score routines basé sur l'accomplissement (0-100)."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models.famille import Routine

            routines_actives = (
                session.query(func.count(Routine.id))
                .filter(Routine.actif.is_(True))
                .scalar() or 0
            )
            if routines_actives == 0:
                return 50.0
            # Avoir des routines actives = bon signe
            score = min(100, routines_actives * 15)
            return round(float(score), 1)
    except Exception:
        return 50.0

def _detail_sport(service, score: float) -> str:
    if score >= 80:
        return "Excellent niveau d'activité physique"
    if score >= 60:
        return "Bon niveau d'activité, continuez !"
    if score >= 40:
        return "Activité modérée, essayez de bouger plus"
    return "Activité insuffisante, fixez-vous un objectif de pas quotidien"

def _detail_nutrition(service, score: float) -> str:
    if score >= 80:
        return "Planning repas bien rempli et équilibré"
    if score >= 60:
        return "Bonne planification, quelques repas à ajouter"
    if score >= 40:
        return "Planning repas incomplet, planifiez davantage"
    return "Peu de repas planifiés, utilisez le planificateur IA"

def _detail_budget(service, score: float) -> str:
    if score >= 80:
        return "Budget maîtrisé, bravo !"
    if score >= 60:
        return "Budget correct, attention aux dépenses"
    if score >= 40:
        return "Budget tendu, surveillez vos dépenses"
    return "Budget dépassé, réduisez les dépenses non essentielles"

def _detail_routines(service, score: float) -> str:
    if score >= 80:
        return "Routines régulières et bien suivies"
    if score >= 60:
        return "Bonnes routines, restez constant"
    if score >= 40:
        return "Quelques routines à consolider"
    return "Peu de routines actives, créez-en pour structurer votre quotidien"

def _evaluer_tendance(service, dimension: str) -> str:
    """Évalue la tendance d'une dimension (simplifié)."""
    return "stable"

def _evaluer_niveau(service, score: float) -> str:
    if score >= 80:
        return "excellent"
    if score >= 60:
        return "bon"
    if score >= 40:
        return "moyen"
    return "attention"

def _generer_conseils(service, dimensions: list[DimensionBienEtre]) -> list[str]:
    """Génère des conseils basés sur les dimensions les plus faibles."""
    conseils = []
    sorted_dims = sorted(dimensions, key=lambda d: d.score)
    for dim in sorted_dims[:2]:
        if dim.score < 60:
            conseils.append(f"Améliorez votre {dim.nom.lower()} : {dim.detail}")
    if not conseils:
        conseils.append("Continuez ainsi, votre bien-être familial est excellent !")
    return conseils

def _generer_conseils_score_famille(service, dimensions: list[DimensionScoreFamille]) -> list[str]:
    """Conseils ciblés pour le score famille hebdo."""
    conseils: list[str] = []
    faibles = sorted(dimensions, key=lambda d: d.score)[:2]
    for d in faibles:
        if d.score < 60:
            conseils.append(f"Renforcer le pilier {d.nom.lower()} cette semaine.")
    if not conseils:
        conseils.append("Semaine bien equilibree, gardez ce rythme.")
    return conseils
