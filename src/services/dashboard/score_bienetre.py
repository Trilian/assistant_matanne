"""
Service de calcul du score bien-etre global (MT-03).

Formule:
- Diversite alimentaire (40%)
- Nutri-score moyen (30%)
- Activites sportives (30%)
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

_NUTRI_POINTS = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}


class ScoreBienEtreService:
    """Calcule le score bien-etre hebdomadaire."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def calculer_score(self, db: Session | None = None) -> dict[str, Any]:
        """Calcule le score de la semaine courante et la tendance."""
        if db is None:
            return {}
        aujourd_hui = date.today()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)

        debut_prev = debut_semaine - timedelta(days=7)
        fin_prev = debut_semaine - timedelta(days=1)

        courant = self._calculer_periode(debut_semaine, fin_semaine, db)
        precedent = self._calculer_periode(debut_prev, fin_prev, db)

        trend = courant["score_global"] - precedent["score_global"]
        courant["trend_semaine_precedente"] = trend
        courant["periode"] = {
            "debut": debut_semaine.isoformat(),
            "fin": fin_semaine.isoformat(),
        }
        return courant

    def _calculer_periode(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
            .all()
        )

        categories: set[str] = set()
        nutri_points: list[int] = []
        for r in repas:
            recette = getattr(r, "recette", None)
            if recette and getattr(recette, "type_proteines", None):
                categories.add(str(recette.type_proteines).lower())
            elif recette and getattr(recette, "categorie", None):
                categories.add(str(recette.categorie).lower())

            # Approximation Nutri-score depuis la charge nutritionnelle
            if recette:
                calories = getattr(recette, "calories", None) or 0
                lipides = getattr(recette, "lipides", None) or 0
                if calories <= 350 and lipides <= 12:
                    nutri_points.append(_NUTRI_POINTS["A"])
                elif calories <= 500 and lipides <= 18:
                    nutri_points.append(_NUTRI_POINTS["B"])
                elif calories <= 650:
                    nutri_points.append(_NUTRI_POINTS["C"])
                elif calories <= 800:
                    nutri_points.append(_NUTRI_POINTS["D"])
                else:
                    nutri_points.append(_NUTRI_POINTS["E"])

        diversite_ratio = min(len(categories) / 7.0, 1.0)
        score_diversite = round(diversite_ratio * 100)

        nutri_moy = (sum(nutri_points) / len(nutri_points)) if nutri_points else 3.0
        score_nutri = round((nutri_moy / 5.0) * 100)

        # Activites sportives
        activites = (
            db.query(ActiviteFamille)
            .filter(
                ActiviteFamille.date_prevue >= debut,
                ActiviteFamille.date_prevue <= fin,
            )
            .all()
        )
        sports = [
            a for a in activites
            if any(
                k in (a.type_activite or "").lower()
                for k in ("sport", "plein-air", "piscine", "velo", "randonnee")
            )
        ]

        garmin_activites = (
            db.query(ActiviteGarmin)
            .filter(
                ActiviteGarmin.date_debut >= debut,
                ActiviteGarmin.date_debut <= fin,
            )
            .all()
        )
        garmin_summaries = (
            db.query(ResumeQuotidienGarmin)
            .filter(
                ResumeQuotidienGarmin.date >= debut,
                ResumeQuotidienGarmin.date <= fin,
            )
            .all()
        )

        base_sport = min(len(sports) / 5.0, 1.0)
        bonus_activites = min(len(garmin_activites) / 6.0, 1.0)
        total_calories = sum(int(s.calories_actives or 0) for s in garmin_summaries)
        bonus_calories = min(total_calories / 2500.0, 1.0)
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) * 100)

        score_global = round(
            (score_diversite * 0.40)
            + (score_nutri * 0.30)
            + (score_activites * 0.30)
        )

        return {
            "score_global": score_global,
            "diversite_alimentaire_score": score_diversite,
            "nutriscore_moyen_score": score_nutri,
            "activites_sportives_score": score_activites,
            "details": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }


@service_factory("score_bien_etre", tags={"dashboard", "famille", "cuisine"})
def obtenir_score_bien_etre_service() -> ScoreBienEtreService:
    """Factory singleton du service de score bien-etre."""
    return ScoreBienEtreService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
obtenir_score_bien_etre_service = obtenir_score_bien_etre_service  # alias rétrocompatibilité 
