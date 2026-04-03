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
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


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
        args = [debut, fin, db]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_orig'), object.__getattribute__(self, 'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_mutants'), args, kwargs, self)

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_orig(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_1(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_2(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(None, Repas.date_repas <= fin)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_3(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_4(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas <= fin)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_5(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_6(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_7(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas > debut, Repas.date_repas <= fin)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_8(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, Repas.date_repas < fin)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_9(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
            .all()
        )

        categories: set[str] = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_10(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
        from src.core.models import ActiviteFamille, Repas
        from src.core.models.users import ActiviteGarmin, ResumeQuotidienGarmin

        # Diversite alimentaire = nombre de categories distinctes sur 7 jours
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
            .all()
        )

        categories: set[str] = set()
        nutri_points: list[int] = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_11(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_12(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(None, "recette", None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_13(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(r, None, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_14(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr("recette", None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_15(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(r, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_16(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(r, "recette", )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_17(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(r, "XXrecetteXX", None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_18(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            recette = getattr(r, "RECETTE", None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_19(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette or getattr(recette, "type_proteines", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_20(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(None, "type_proteines", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_21(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(recette, None, None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_22(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr("type_proteines", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_23(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(recette, None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_24(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(recette, "type_proteines", ):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_25(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(recette, "XXtype_proteinesXX", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_26(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            if recette and getattr(recette, "TYPE_PROTEINES", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_27(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_28(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(str(recette.type_proteines).upper())
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_29(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(str(None).lower())
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_30(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette or getattr(recette, "categorie", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_31(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(None, "categorie", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_32(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(recette, None, None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_33(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr("categorie", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_34(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(recette, None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_35(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(recette, "categorie", ):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_36(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(recette, "XXcategorieXX", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_37(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            elif recette and getattr(recette, "CATEGORIE", None):
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_38(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(None)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_39(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(str(recette.categorie).upper())

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_40(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                categories.add(str(None).lower())

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_41(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_42(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, "calories", None) and 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_43(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(None, "calories", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_44(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, None, None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_45(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr("calories", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_46(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_47(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, "calories", ) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_48(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, "XXcaloriesXX", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_49(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, "CALORIES", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_50(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                calories = getattr(recette, "calories", None) or 1
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_51(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_52(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, "lipides", None) and 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_53(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(None, "lipides", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_54(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, None, None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_55(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr("lipides", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_56(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_57(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, "lipides", ) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_58(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, "XXlipidesXX", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_59(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, "LIPIDES", None) or 0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_60(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                lipides = getattr(recette, "lipides", None) or 1
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_61(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                if calories <= 350 or lipides <= 12:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_62(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                if calories < 350 and lipides <= 12:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_63(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                if calories <= 351 and lipides <= 12:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_64(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                if calories <= 350 and lipides < 12:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_65(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                if calories <= 350 and lipides <= 13:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_66(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_67(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["XXAXX"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_68(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["a"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_69(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 500 or lipides <= 18:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_70(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories < 500 and lipides <= 18:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_71(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 501 and lipides <= 18:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_72(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 500 and lipides < 18:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_73(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 500 and lipides <= 19:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_74(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_75(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["XXBXX"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_76(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["b"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_77(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories < 650:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_78(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 651:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_79(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_80(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["XXCXX"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_81(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["c"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_82(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories < 800:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_83(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                elif calories <= 801:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_84(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_85(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["XXDXX"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_86(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["d"])
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_87(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(None)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_88(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["XXEXX"])

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_89(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                    nutri_points.append(_NUTRI_POINTS["e"])

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_90(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_91(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(None, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_92(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(len(categories) / 7.0, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_93(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_94(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(len(categories) / 7.0, )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_95(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(len(categories) * 7.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_96(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(len(categories) / 8.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_97(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        diversite_ratio = min(len(categories) / 7.0, 2.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_98(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_diversite = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_99(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_diversite = round(None)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_100(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_diversite = round(diversite_ratio / 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_101(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_diversite = round(diversite_ratio * 101)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_102(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        nutri_moy = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_103(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        nutri_moy = (sum(nutri_points) * len(nutri_points)) if nutri_points else 3.0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_104(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        nutri_moy = (sum(None) / len(nutri_points)) if nutri_points else 3.0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_105(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        nutri_moy = (sum(nutri_points) / len(nutri_points)) if nutri_points else 4.0
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_106(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_107(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = round(None)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_108(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = round((nutri_moy / 5.0) / 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_109(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = round((nutri_moy * 5.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_110(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = round((nutri_moy / 6.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_111(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_nutri = round((nutri_moy / 5.0) * 101)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_112(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        activites = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_113(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_114(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_115(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_116(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_117(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            db.query(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_118(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ActiviteFamille.date_prevue > debut,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_119(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ActiviteFamille.date_prevue < fin,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_120(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        sports = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_121(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_122(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                k not in (a.type_activite or "").lower()
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_123(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                k in (a.type_activite or "").upper()
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_124(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                k in (a.type_activite and "").lower()
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_125(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                k in (a.type_activite or "XXXX").lower()
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_126(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("XXsportXX", "plein-air", "piscine", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_127(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("SPORT", "plein-air", "piscine", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_128(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "XXplein-airXX", "piscine", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_129(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "PLEIN-AIR", "piscine", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_130(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "XXpiscineXX", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_131(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "PISCINE", "velo", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_132(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "piscine", "XXveloXX", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_133(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "piscine", "VELO", "randonnee")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_134(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "piscine", "velo", "XXrandonneeXX")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_135(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                for k in ("sport", "plein-air", "piscine", "velo", "RANDONNEE")
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_136(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        garmin_activites = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_137(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_138(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_139(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_140(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_141(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            db.query(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_142(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ActiviteGarmin.date_debut > debut,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_143(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ActiviteGarmin.date_debut < fin,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_144(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        garmin_summaries = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_145(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_146(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                None,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_147(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_148(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_149(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            db.query(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_150(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ResumeQuotidienGarmin.date > debut,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_151(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                ResumeQuotidienGarmin.date < fin,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_152(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_153(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(None, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_154(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(len(sports) / 5.0, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_155(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_156(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(len(sports) / 5.0, )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_157(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(len(sports) * 5.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_158(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(len(sports) / 6.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_159(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        base_sport = min(len(sports) / 5.0, 2.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_160(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_161(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(None, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_162(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(len(garmin_activites) / 6.0, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_163(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_164(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(len(garmin_activites) / 6.0, )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_165(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(len(garmin_activites) * 6.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_166(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(len(garmin_activites) / 7.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_167(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_activites = min(len(garmin_activites) / 6.0, 2.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_168(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        total_calories = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_169(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        total_calories = sum(None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_170(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        total_calories = sum(int(None) for s in garmin_summaries)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_171(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        total_calories = sum(int(s.calories_actives and 0) for s in garmin_summaries)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_172(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        total_calories = sum(int(s.calories_actives or 1) for s in garmin_summaries)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_173(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_174(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(None, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_175(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(total_calories / 2500.0, None)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_176(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_177(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(total_calories / 2500.0, )
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_178(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(total_calories * 2500.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_179(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(total_calories / 2501.0, 1.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_180(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        bonus_calories = min(total_calories / 2500.0, 2.0)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_181(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_182(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(None)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_183(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) / 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_184(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min(None, 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_185(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), None) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_186(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min(1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_187(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), ) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_188(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) - (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_189(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) - (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_190(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport / 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_191(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 1.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_192(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites / 0.25) + (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_193(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 1.25) + (bonus_calories * 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_194(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories / 0.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_195(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 1.25), 1.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_196(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 2.0) * 100)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_197(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
        score_activites = round(min((base_sport * 0.5) + (bonus_activites * 0.25) + (bonus_calories * 0.25), 1.0) * 101)

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_198(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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

        score_global = None

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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_199(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            None
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_200(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            + (score_nutri * 0.30) - (score_activites * 0.30)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_201(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            (score_diversite * 0.40) - (score_nutri * 0.30)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_202(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            (score_diversite / 0.40)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_203(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            (score_diversite * 1.4)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_204(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            + (score_nutri / 0.30)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_205(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            + (score_nutri * 1.3)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_206(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            + (score_activites / 0.30)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_207(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            + (score_activites * 1.3)
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_208(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "XXscore_globalXX": score_global,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_209(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "SCORE_GLOBAL": score_global,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_210(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "XXdiversite_alimentaire_scoreXX": score_diversite,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_211(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "DIVERSITE_ALIMENTAIRE_SCORE": score_diversite,
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

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_212(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "XXnutriscore_moyen_scoreXX": score_nutri,
            "activites_sportives_score": score_activites,
            "details": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_213(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "NUTRISCORE_MOYEN_SCORE": score_nutri,
            "activites_sportives_score": score_activites,
            "details": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_214(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "XXactivites_sportives_scoreXX": score_activites,
            "details": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_215(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "ACTIVITES_SPORTIVES_SCORE": score_activites,
            "details": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_216(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "XXdetailsXX": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_217(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
            "DETAILS": {
                "categories_alimentaires_distinctes": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_218(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "XXcategories_alimentaires_distinctesXX": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_219(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "CATEGORIES_ALIMENTAIRES_DISTINCTES": sorted(categories),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_220(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "categories_alimentaires_distinctes": sorted(None),
                "nb_activites_sportives": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_221(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "XXnb_activites_sportivesXX": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_222(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "NB_ACTIVITES_SPORTIVES": len(sports),
                "nb_activites_garmin": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_223(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "XXnb_activites_garminXX": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_224(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "NB_ACTIVITES_GARMIN": len(garmin_activites),
                "calories_actives_garmin": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_225(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "XXcalories_actives_garminXX": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_226(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "CALORIES_ACTIVES_GARMIN": total_calories,
                "nb_repas_analyses": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_227(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "XXnb_repas_analysesXX": len(repas),
            },
        }

    def xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_228(self, debut: date, fin: date, db: Session) -> dict[str, Any]:
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
                "NB_REPAS_ANALYSES": len(repas),
            },
        }
    
    xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_1': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_1, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_2': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_2, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_3': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_3, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_4': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_4, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_5': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_5, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_6': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_6, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_7': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_7, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_8': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_8, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_9': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_9, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_10': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_10, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_11': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_11, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_12': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_12, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_13': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_13, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_14': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_14, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_15': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_15, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_16': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_16, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_17': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_17, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_18': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_18, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_19': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_19, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_20': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_20, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_21': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_21, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_22': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_22, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_23': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_23, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_24': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_24, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_25': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_25, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_26': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_26, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_27': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_27, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_28': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_28, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_29': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_29, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_30': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_30, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_31': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_31, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_32': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_32, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_33': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_33, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_34': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_34, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_35': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_35, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_36': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_36, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_37': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_37, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_38': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_38, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_39': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_39, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_40': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_40, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_41': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_41, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_42': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_42, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_43': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_43, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_44': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_44, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_45': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_45, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_46': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_46, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_47': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_47, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_48': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_48, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_49': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_49, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_50': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_50, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_51': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_51, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_52': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_52, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_53': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_53, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_54': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_54, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_55': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_55, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_56': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_56, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_57': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_57, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_58': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_58, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_59': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_59, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_60': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_60, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_61': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_61, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_62': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_62, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_63': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_63, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_64': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_64, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_65': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_65, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_66': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_66, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_67': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_67, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_68': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_68, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_69': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_69, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_70': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_70, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_71': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_71, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_72': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_72, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_73': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_73, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_74': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_74, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_75': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_75, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_76': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_76, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_77': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_77, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_78': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_78, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_79': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_79, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_80': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_80, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_81': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_81, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_82': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_82, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_83': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_83, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_84': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_84, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_85': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_85, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_86': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_86, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_87': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_87, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_88': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_88, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_89': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_89, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_90': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_90, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_91': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_91, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_92': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_92, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_93': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_93, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_94': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_94, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_95': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_95, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_96': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_96, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_97': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_97, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_98': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_98, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_99': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_99, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_100': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_100, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_101': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_101, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_102': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_102, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_103': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_103, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_104': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_104, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_105': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_105, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_106': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_106, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_107': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_107, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_108': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_108, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_109': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_109, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_110': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_110, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_111': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_111, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_112': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_112, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_113': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_113, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_114': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_114, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_115': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_115, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_116': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_116, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_117': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_117, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_118': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_118, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_119': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_119, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_120': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_120, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_121': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_121, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_122': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_122, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_123': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_123, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_124': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_124, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_125': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_125, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_126': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_126, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_127': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_127, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_128': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_128, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_129': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_129, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_130': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_130, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_131': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_131, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_132': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_132, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_133': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_133, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_134': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_134, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_135': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_135, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_136': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_136, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_137': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_137, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_138': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_138, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_139': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_139, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_140': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_140, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_141': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_141, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_142': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_142, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_143': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_143, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_144': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_144, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_145': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_145, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_146': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_146, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_147': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_147, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_148': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_148, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_149': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_149, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_150': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_150, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_151': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_151, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_152': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_152, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_153': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_153, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_154': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_154, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_155': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_155, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_156': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_156, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_157': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_157, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_158': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_158, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_159': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_159, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_160': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_160, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_161': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_161, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_162': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_162, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_163': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_163, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_164': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_164, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_165': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_165, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_166': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_166, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_167': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_167, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_168': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_168, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_169': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_169, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_170': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_170, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_171': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_171, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_172': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_172, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_173': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_173, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_174': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_174, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_175': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_175, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_176': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_176, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_177': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_177, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_178': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_178, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_179': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_179, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_180': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_180, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_181': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_181, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_182': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_182, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_183': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_183, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_184': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_184, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_185': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_185, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_186': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_186, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_187': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_187, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_188': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_188, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_189': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_189, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_190': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_190, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_191': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_191, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_192': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_192, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_193': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_193, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_194': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_194, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_195': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_195, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_196': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_196, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_197': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_197, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_198': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_198, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_199': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_199, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_200': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_200, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_201': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_201, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_202': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_202, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_203': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_203, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_204': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_204, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_205': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_205, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_206': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_206, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_207': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_207, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_208': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_208, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_209': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_209, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_210': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_210, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_211': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_211, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_212': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_212, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_213': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_213, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_214': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_214, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_215': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_215, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_216': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_216, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_217': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_217, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_218': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_218, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_219': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_219, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_220': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_220, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_221': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_221, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_222': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_222, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_223': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_223, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_224': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_224, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_225': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_225, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_226': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_226, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_227': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_227, 
        'xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_228': xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_228
    }
    xǁScoreBienEtreServiceǁ_calculer_periode__mutmut_orig.__name__ = 'xǁScoreBienEtreServiceǁ_calculer_periode'


@service_factory("score_bien_etre", tags={"dashboard", "famille", "cuisine"})
def obtenir_score_bien_etre_service() -> ScoreBienEtreService:
    """Factory singleton du service de score bien-etre."""
    return ScoreBienEtreService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_score_bien_etre_service = obtenir_score_bien_etre_service  # alias rétrocompatibilité 
