"""Fonctions score famille extraites du service innovations."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from src.core.db import obtenir_contexte_db

from .innovations_types import DimensionScoreFamille, ScoreFamilleHebdoResponse

logger = logging.getLogger(__name__)


def calculer_score_famille_hebdo(service: Any) -> ScoreFamilleHebdoResponse | None:
    """Score famille hebdo composite (nutrition, depenses, activites, entretien)."""
    score_nutrition = service._calculer_score_nutrition()
    score_budget = service._calculer_score_budget()

    score_activites = 50.0
    score_entretien = 50.0
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import func
            from src.core.models.famille import ActiviteFamille
            from src.core.models.maison import TacheEntretien

            debut = date.today() - timedelta(days=7)
            nb_activites = int(
                session.query(func.count(ActiviteFamille.id))
                .filter(ActiviteFamille.date_prevue >= debut)
                .scalar()
                or 0
            )
            score_activites = min(100.0, nb_activites * 18.0)

            nb_taches_faites = int(
                session.query(func.count(TacheEntretien.id))
                .filter(TacheEntretien.fait.is_(True), TacheEntretien.date_prevue >= debut)
                .scalar()
                or 0
            )
            score_entretien = min(100.0, nb_taches_faites * 12.5)
    except Exception:
        logger.warning("Score famille hebdo partiel", exc_info=True)

    dimensions = [
        DimensionScoreFamille(nom="Nutrition", score=round(score_nutrition, 1), poids=0.30),
        DimensionScoreFamille(nom="Depenses", score=round(score_budget, 1), poids=0.25),
        DimensionScoreFamille(nom="Activites", score=round(score_activites, 1), poids=0.25),
        DimensionScoreFamille(nom="Entretien", score=round(score_entretien, 1), poids=0.20),
    ]
    global_score = round(sum(d.score * d.poids for d in dimensions), 1)
    return ScoreFamilleHebdoResponse(
        semaine_reference=date.today().isoformat(),
        score_global=global_score,
        dimensions=dimensions,
        recommandations=service._generer_conseils_score_famille(dimensions),
    )
