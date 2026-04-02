"""
Service IA — Prévision budget mensuel.

Analyse les tendances de dépenses pour prédire le montant en fin de mois
et détecter les anomalies budgétaires (B1.3 / B5.2 / B4.9).
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PrevisionBudgetService(BaseAIService):
    """Service de prévision et analyse budgétaire IA."""

    def __init__(self):
        super().__init__(
            cache_prefix="prevision_budget",
            default_ttl=7200,
            service_name="prevision_budget",
        )

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def prevision_fin_de_mois(
        self, mois: int | None = None, annee: int | None = None,
        db: Session | None = None
    ) -> dict:
        """Prédit les dépenses totales en fin de mois.

        Algorithme :
        1. Calcule les dépenses actuelles du mois en cours
        2. Calcule la moyenne journalière
        3. Extrapole au nombre de jours restants
        4. Compare avec les mois précédents

        Returns:
            Dict avec depenses_actuelles, prevision, tendance, anomalies
        """
        from src.core.models import BudgetFamille
        import calendar

        aujourd_hui = date.today()
        mois = mois or aujourd_hui.month
        annee = annee or aujourd_hui.year

        # Dépenses du mois en cours
        depenses_mois = (
            db.query(func.sum(BudgetFamille.montant))
            .filter(
                func.extract("month", BudgetFamille.date) == mois,
                func.extract("year", BudgetFamille.date) == annee,
            )
            .scalar() or 0
        )

        # Dépenses par catégorie
        depenses_par_cat = (
            db.query(
                BudgetFamille.categorie,
                func.sum(BudgetFamille.montant).label("total"),
            )
            .filter(
                func.extract("month", BudgetFamille.date) == mois,
                func.extract("year", BudgetFamille.date) == annee,
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        # Jours écoulés et total
        jour_courant = min(aujourd_hui.day, calendar.monthrange(annee, mois)[1])
        jours_total = calendar.monthrange(annee, mois)[1]

        # Extrapolation
        if jour_courant > 0:
            moyenne_jour = float(depenses_mois) / jour_courant
            prevision = moyenne_jour * jours_total
        else:
            moyenne_jour = 0
            prevision = 0

        # Comparaison avec mois précédent
        mois_prec = mois - 1 if mois > 1 else 12
        annee_prec = annee if mois > 1 else annee - 1
        depenses_mois_prec = (
            db.query(func.sum(BudgetFamille.montant))
            .filter(
                func.extract("month", BudgetFamille.date) == mois_prec,
                func.extract("year", BudgetFamille.date) == annee_prec,
            )
            .scalar() or 0
        )

        # Tendance
        if float(depenses_mois_prec) > 0:
            tendance_pct = ((prevision - float(depenses_mois_prec)) / float(depenses_mois_prec)) * 100
        else:
            tendance_pct = 0

        # Détection anomalies (catégorie > 30% en plus vs mois précédent)
        anomalies = []
        for cat, total in depenses_par_cat:
            cat_prec = (
                db.query(func.sum(BudgetFamille.montant))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois_prec,
                    func.extract("year", BudgetFamille.date) == annee_prec,
                    BudgetFamille.categorie == cat,
                )
                .scalar() or 0
            )
            if float(cat_prec) > 0:
                variation = ((float(total) - float(cat_prec)) / float(cat_prec)) * 100
                if variation > 30:
                    anomalies.append({
                        "categorie": cat,
                        "montant_actuel": float(total),
                        "montant_precedent": float(cat_prec),
                        "variation_pct": round(variation, 1),
                    })

        return {
            "mois": f"{mois:02d}/{annee}",
            "jours_ecoules": jour_courant,
            "jours_total": jours_total,
            "depenses_actuelles": float(depenses_mois),
            "moyenne_jour": round(moyenne_jour, 2),
            "prevision_fin_mois": round(prevision, 2),
            "depenses_mois_precedent": float(depenses_mois_prec),
            "tendance_pct": round(tendance_pct, 1),
            "par_categorie": [
                {"categorie": cat, "montant": float(total)} for cat, total in depenses_par_cat
            ],
            "anomalies": anomalies,
        }

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def detecter_anomalies_budget(self, seuil_pct: float = 80, db: Session | None = None) -> list[dict]:
        """Détecte les catégories qui dépassent un seuil de leur budget mensuel.

        Args:
            seuil_pct: Pourcentage de seuil d'alerte (80% par défaut)

        Returns:
            Liste de dicts {categorie, depense, budget, pourcentage}
        """
        from src.core.models import BudgetFamille

        aujourd_hui = date.today()
        mois = aujourd_hui.month
        annee = aujourd_hui.year

        # Regrouper dépenses par catégorie
        depenses = (
            db.query(
                BudgetFamille.categorie,
                func.sum(BudgetFamille.montant).label("total"),
            )
            .filter(
                func.extract("month", BudgetFamille.date) == mois,
                func.extract("year", BudgetFamille.date) == annee,
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        alertes = []
        for cat, total in depenses:
            # Budget défini par catégorie (on utilise le budget du mois précédent comme référence)
            mois_prec = mois - 1 if mois > 1 else 12
            annee_prec = annee if mois > 1 else annee - 1
            budget_ref = (
                db.query(func.sum(BudgetFamille.montant))
                .filter(
                    func.extract("month", BudgetFamille.date) == mois_prec,
                    func.extract("year", BudgetFamille.date) == annee_prec,
                    BudgetFamille.categorie == cat,
                )
                .scalar() or 0
            )

            if float(budget_ref) > 0:
                pct = (float(total) / float(budget_ref)) * 100
                if pct >= seuil_pct:
                    alertes.append({
                        "categorie": cat,
                        "depense": float(total),
                        "budget_ref": float(budget_ref),
                        "pourcentage": round(pct, 1),
                        "niveau": "critique" if pct >= 100 else "attention",
                    })

        alertes.sort(key=lambda x: -x["pourcentage"])
        return alertes

    def auto_categoriser_depense(self, description: str) -> dict:
        """Catégorise automatiquement une dépense basée sur la description (B4.9).

        Args:
            description: Description/nom du commerçant

        Returns:
            Dict avec categorie, confiance
        """
        # Mapping statique pour les cas communs
        MAPPING_CATEGORIES = {
            "carrefour": "alimentation", "leclerc": "alimentation", "auchan": "alimentation",
            "lidl": "alimentation", "monoprix": "alimentation", "picard": "alimentation",
            "boulangerie": "alimentation", "boucherie": "alimentation",
            "restaurant": "resto", "mcdo": "resto", "uber eats": "resto", "deliveroo": "resto",
            "edf": "energie", "engie": "energie", "total": "energie",
            "orange": "telecom", "sfr": "telecom", "free": "telecom", "bouygues": "telecom",
            "amazon": "shopping", "fnac": "shopping", "darty": "shopping",
            "ikea": "maison", "leroy merlin": "maison", "castorama": "maison",
            "decathlon": "loisirs", "cinema": "loisirs",
            "pharmacie": "sante", "doctolib": "sante",
            "essence": "transport", "sncf": "transport", "ratp": "transport",
        }

        desc_lower = description.lower()
        for mot_cle, categorie in MAPPING_CATEGORIES.items():
            if mot_cle in desc_lower:
                return {"categorie": categorie, "confiance": 0.9, "source": "mapping"}

        # Fallback IA
        try:
            prompt = f"""Catégorise cette dépense en une seule catégorie.
Description: "{description}"

Catégories possibles: alimentation, resto, energie, telecom, shopping, maison, loisirs, sante, transport, education, autre

Réponds en JSON: {{"categorie": "...", "confiance": 0.8}}"""

            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu catégorises des dépenses. Réponds en JSON valide uniquement.",
            )
            if isinstance(result, dict) and "categorie" in result:
                result["source"] = "ia"
                return result
        except Exception as e:
            logger.warning(f"Erreur IA catégorisation: {e}")

        return {"categorie": "autre", "confiance": 0.3, "source": "defaut"}


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("prevision_budget", tags={"famille", "ia", "budget"})
def obtenir_service_prevision_budget() -> PrevisionBudgetService:
    """Factory singleton pour le service de prévision budget."""
    return PrevisionBudgetService()


get_prevision_budget_service = obtenir_service_prevision_budget
