"""
Service de calcul du Score Foyer composite.

Indicateur unifié de la santé du foyer :
- Nutrition (40%) — via ScoreBienEtreService
- Budget (25%) — respect du budget mensuel
- Entretien (20%) — taux de réalisation des tâches
- Routines (15%) — régularité des routines actives
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

_NIVEAUX = [
    (80, "excellent"),
    (60, "bon"),
    (40, "vigilance"),
    (0, "critique"),
]


def _niveau_pour_score(score: int) -> str:
    for seuil, niveau in _NIVEAUX:
        if score >= seuil:
            return niveau
    return "critique"


class ScoreFoyerService:
    """Calcule le score foyer composite hebdomadaire."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_score(self, db: Session | None = None) -> dict[str, Any]:
        if db is None:
            return {}

        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        # Semaine précédente pour tendance
        debut_prev = debut_semaine - timedelta(days=7)
        fin_prev = debut_semaine - timedelta(days=1)

        courant = self._calculer_periode(debut_semaine, fin_semaine, aujourd_hui, db)
        precedent = self._calculer_periode(debut_prev, fin_prev, debut_prev + timedelta(days=6), db)

        trend = courant["score_global"] - precedent["score_global"]

        leviers = self._calculer_leviers(courant)

        return {
            "score_global": courant["score_global"],
            "niveau": _niveau_pour_score(courant["score_global"]),
            "trend_semaine_precedente": trend,
            "composantes": {
                "nutrition": courant["score_nutrition"],
                "budget": courant["score_budget"],
                "entretien": courant["score_entretien"],
                "routines": courant["score_routines"],
            },
            "details": courant["details"],
            "leviers_prioritaires": leviers,
            "periode": {
                "debut": debut_semaine.isoformat(),
                "fin": fin_semaine.isoformat(),
            },
        }

    def _calculer_periode(
        self, debut: date, fin: date, ref_date: date, db: Session
    ) -> dict[str, Any]:
        score_nutrition = self._score_nutrition(debut, fin, db)
        score_budget = self._score_budget(ref_date, db)
        score_entretien = self._score_entretien(ref_date, db)
        score_routines = self._score_routines(debut, fin, db)

        score_global = round(
            (score_nutrition * 0.40)
            + (score_budget * 0.25)
            + (score_entretien * 0.20)
            + (score_routines * 0.15)
        )

        return {
            "score_global": score_global,
            "score_nutrition": score_nutrition,
            "score_budget": score_budget,
            "score_entretien": score_entretien,
            "score_routines": score_routines,
            "details": {
                "nutrition_pct": score_nutrition,
                "budget_pct": score_budget,
                "entretien_pct": score_entretien,
                "routines_pct": score_routines,
            },
        }

    def _score_nutrition(self, debut: date, fin: date, db: Session) -> int:
        """Score nutrition via le pattern ScoreBienEtre simplifié."""
        try:
            from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

            service = obtenir_score_bien_etre_service()
            result = service._calculer_periode(debut, fin, db)
            return int(result.get("score_global", 50))
        except Exception:
            return 50

    def _score_budget(self, ref_date: date, db: Session) -> int:
        """Score budget : compare dépenses réelles vs budget moyen 3 mois."""
        try:
            from src.core.models.famille import BudgetFamille

            mois = ref_date.month
            annee = ref_date.year

            depenses_mois = (
                db.query(func.sum(BudgetFamille.montant))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois,
                    func.extract("year", BudgetFamille.date) == annee,
                )
                .scalar()
            ) or 0

            # Moyenne des 3 mois précédents comme référence
            trois_mois_avant = ref_date - timedelta(days=90)
            moyenne_ref = (
                db.query(func.avg(func.sum(BudgetFamille.montant)))
                .filter(
                    BudgetFamille.date >= trois_mois_avant,
                    BudgetFamille.date < ref_date.replace(day=1),
                )
                .scalar()
            )

            if not moyenne_ref or moyenne_ref == 0:
                return 70  # Pas assez de données

            ratio = depenses_mois / float(moyenne_ref)
            if ratio <= 0.9:
                return 100
            if ratio <= 1.0:
                return 85
            if ratio <= 1.1:
                return 70
            if ratio <= 1.3:
                return 50
            return 30
        except Exception:
            return 50

    def _score_entretien(self, ref_date: date, db: Session) -> int:
        """Score entretien : tâches faites / tâches en retard."""
        try:
            from src.core.models.habitat import TacheEntretien

            total = db.query(func.count(TacheEntretien.id)).scalar() or 0
            if total == 0:
                return 80

            en_retard = (
                db.query(func.count(TacheEntretien.id))
                .filter(
                    TacheEntretien.fait == False,  # noqa: E712
                    TacheEntretien.prochaine_fois <= ref_date,
                )
                .scalar()
            ) or 0

            faites = (
                db.query(func.count(TacheEntretien.id))
                .filter(TacheEntretien.fait == True)  # noqa: E712
                .scalar()
            ) or 0

            taux_realisation = faites / total if total > 0 else 0
            penalite_retard = min(en_retard * 5, 40)

            return max(0, min(100, round(taux_realisation * 100) - penalite_retard))
        except Exception:
            return 50

    def _score_routines(self, debut: date, fin: date, db: Session) -> int:
        """Score routines : régularité des routines actives."""
        try:
            from src.core.models.maison import Routine

            routines_actives = (
                db.query(Routine)
                .filter(Routine.actif == True)  # noqa: E712
                .all()
            )

            if not routines_actives:
                return 80

            completees = 0
            for routine in routines_actives:
                if routine.derniere_completion and routine.derniere_completion >= debut:
                    completees += 1

            taux = completees / len(routines_actives)
            return min(100, round(taux * 100))
        except Exception:
            return 50

    def _calculer_leviers(self, scores: dict[str, Any]) -> list[str]:
        """Identifie les 3 leviers d'amélioration prioritaires."""
        composantes = [
            ("nutrition", scores["score_nutrition"], "Diversifier les repas de la semaine"),
            ("budget", scores["score_budget"], "Surveiller les dépenses du mois"),
            ("entretien", scores["score_entretien"], "Réaliser les tâches d'entretien en retard"),
            ("routines", scores["score_routines"], "Compléter les routines actives"),
        ]
        composantes.sort(key=lambda x: x[1])
        return [msg for _, score, msg in composantes[:3] if score < 80]


@service_factory("score_foyer", tags={"dashboard", "famille", "maison"})
def obtenir_score_foyer_service() -> ScoreFoyerService:
    """Factory singleton du service Score foyer."""
    return ScoreFoyerService()
