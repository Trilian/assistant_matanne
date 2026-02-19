"""
Mixin d'analyses et prévisions budgétaires.

Méthodes d'analyse statistique, tendances et prévisions
extraites de BudgetService.
"""

import logging
from datetime import date as date_type

from sqlalchemy.orm import Session

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache, avec_session_db

from .schemas import (
    BudgetMensuel,
    CategorieDepense,
    PrevisionDepense,
    ResumeFinancier,
)

logger = logging.getLogger(__name__)


class BudgetAnalysesMixin:
    """Mixin pour les analyses, tendances et prévisions budgétaires."""

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES ET ANALYSES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=600)
    @avec_session_db
    def get_resume_mensuel(
        self,
        mois: int | None = None,
        annee: int | None = None,
        db: Session = None,
    ) -> ResumeFinancier:
        """
        Génère un résumé financier du mois.

        Args:
            mois: Mois (défaut = mois courant)
            annee: Année (défaut = année courante)
            db: Session DB

        Returns:
            Résumé financier complet
        """
        mois = mois or date_type.today().month
        annee = annee or date_type.today().year

        resume = ResumeFinancier(mois=mois, annee=annee)

        # Récupérer les dépenses du mois
        depenses = self.get_depenses_mois(mois, annee, db=db)

        # Total et par catégorie
        for dep in depenses:
            resume.total_depenses += dep.montant
            cat_key = dep.categorie.value
            resume.depenses_par_categorie[cat_key] = (
                resume.depenses_par_categorie.get(cat_key, 0) + dep.montant
            )

        # Budgets
        budgets = self.get_tous_budgets(mois, annee, db=db)
        for cat, budget_montant in budgets.items():
            depense_cat = resume.depenses_par_categorie.get(cat.value, 0)

            budget = BudgetMensuel(
                mois=mois,
                annee=annee,
                categorie=cat,
                budget_prevu=budget_montant,
                depense_reelle=depense_cat,
            )

            resume.budgets_par_categorie[cat.value] = budget
            resume.total_budget += budget_montant

            # Alertes
            if budget.est_depasse:
                resume.categories_depassees.append(cat.value)
            elif budget.pourcentage_utilise > 80:
                resume.categories_a_risque.append(cat.value)

        # Variation vs mois précédent
        mois_prec = mois - 1 if mois > 1 else 12
        annee_prec = annee if mois > 1 else annee - 1
        depenses_prec = self.get_depenses_mois(mois_prec, annee_prec, db=db)
        total_prec = sum(d.montant for d in depenses_prec)

        if total_prec > 0:
            resume.variation_vs_mois_precedent = (
                (resume.total_depenses - total_prec) / total_prec
            ) * 100

        # Moyenne 6 mois
        totaux_6_mois = []
        for i in range(6):
            m = mois - i if mois - i > 0 else 12 + (mois - i)
            a = annee if mois - i > 0 else annee - 1
            deps = self.get_depenses_mois(m, a, db=db)
            totaux_6_mois.append(sum(d.montant for d in deps))

        resume.moyenne_6_mois = sum(totaux_6_mois) / len(totaux_6_mois) if totaux_6_mois else 0

        return resume

    @avec_session_db
    def get_tendances(
        self,
        nb_mois: int = 6,
        db: Session = None,
    ) -> dict[str, list[float]]:
        """
        Récupère les tendances de dépenses sur plusieurs mois.

        Args:
            nb_mois: Nombre de mois à analyser
            db: Session DB

        Returns:
            Dict avec les tendances par catégorie
        """
        tendances = {cat.value: [] for cat in CategorieDepense}
        tendances["total"] = []
        tendances["mois"] = []

        aujourd_hui = date_type.today()

        for i in range(nb_mois - 1, -1, -1):
            # Calculer le mois
            mois_delta = aujourd_hui.month - i
            if mois_delta <= 0:
                mois = 12 + mois_delta
                annee = aujourd_hui.year - 1
            else:
                mois = mois_delta
                annee = aujourd_hui.year

            tendances["mois"].append(f"{mois:02d}/{annee}")

            # Récupérer les dépenses
            depenses = self.get_depenses_mois(mois, annee, db=db)

            # Totaux par catégorie
            totaux_cat = {cat.value: 0.0 for cat in CategorieDepense}
            total_mois = 0.0

            for dep in depenses:
                totaux_cat[dep.categorie.value] += dep.montant
                total_mois += dep.montant

            for cat in CategorieDepense:
                tendances[cat.value].append(totaux_cat[cat.value])

            tendances["total"].append(total_mois)

        return tendances

    def prevoir_depenses(
        self,
        mois_cible: int,
        annee_cible: int,
    ) -> list[PrevisionDepense]:
        """
        Prédit les dépenses pour un mois futur.

        Args:
            mois_cible: Mois cible
            annee_cible: Année cible

        Returns:
            Liste des prévisions par catégorie
        """
        previsions = []

        # Récupérer l'historique
        with obtenir_contexte_db() as db:
            tendances = self.get_tendances(nb_mois=6, db=db)

        for cat in CategorieDepense:
            valeurs = tendances.get(cat.value, [])

            if not valeurs or all(v == 0 for v in valeurs):
                continue

            # Moyenne simple pondérée (plus récent = plus de poids)
            poids = [1, 1.2, 1.4, 1.6, 1.8, 2.0][: len(valeurs)]
            moyenne_ponderee = sum(v * p for v, p in zip(valeurs, poids, strict=False)) / sum(poids)

            # Tendance (croissance ou décroissance)
            if len(valeurs) >= 3:
                tendance = (valeurs[-1] - valeurs[0]) / len(valeurs)
            else:
                tendance = 0

            montant_prevu = max(0, moyenne_ponderee + tendance)

            # Score de confiance basé sur la variance
            if len(valeurs) >= 3:
                variance = sum((v - moyenne_ponderee) ** 2 for v in valeurs) / len(valeurs)
                confiance = max(0, 1 - (variance / (moyenne_ponderee**2 + 1)))
            else:
                confiance = 0.5

            previsions.append(
                PrevisionDepense(
                    categorie=cat,
                    montant_prevu=round(montant_prevu, 2),
                    confiance=round(confiance, 2),
                    base_calcul=f"Moyenne pondérée sur {len(valeurs)} mois",
                )
            )

        return sorted(previsions, key=lambda p: p.montant_prevu, reverse=True)
