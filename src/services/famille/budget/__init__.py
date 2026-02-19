"""
Package de gestion du budget familial.

Exports:
- BudgetService: Service principal
- get_budget_service: Factory
- Schémas: CategorieDepense, Depense, BudgetMensuel, etc.
- Utils: Fonctions utilitaires pures
"""

from .schemas import (
    DEFAULT_USER_ID,
    BudgetMensuel,
    CategorieDepense,
    Depense,
    FactureMaison,
    FrequenceRecurrence,
    PrevisionDepense,
    ResumeFinancier,
)
from .service import (
    BudgetService,
    get_budget_service,
    obtenir_service_budget,
)
from .utils import (
    # Agrégation
    agreger_depenses_par_categorie,
    calculer_confiance_prevision,
    # Calculs statistiques
    calculer_moyenne_ponderee,
    # Calculs de budget
    calculer_pourcentage_budget,
    calculer_reste_disponible,
    calculer_tendance,
    calculer_total_depenses,
    calculer_variance,
    # Résumés
    construire_resume_financier,
    db_entries_to_depenses,
    # Conversion DB → Pydantic
    db_entry_to_depense,
    est_budget_a_risque,
    est_budget_depasse,
    filtrer_depenses_par_categorie,
    filtrer_depenses_par_periode,
    generer_prevision_categorie,
    valider_annee,
    valider_mois,
    # Validation
    valider_montant,
)

# NOTE: afficher_budget_dashboard déplacé vers src/modules/famille/budget_dashboard.py
# Ne plus importer l'UI depuis ce package services


__all__ = [
    # Constantes
    "DEFAULT_USER_ID",
    # Schémas
    "CategorieDepense",
    "FrequenceRecurrence",
    "Depense",
    "FactureMaison",
    "BudgetMensuel",
    "ResumeFinancier",
    "PrevisionDepense",
    # Service
    "BudgetService",
    "get_budget_service",
    "obtenir_service_budget",
    # Utils - Conversion
    "db_entry_to_depense",
    "db_entries_to_depenses",
    # Utils - Calculs statistiques
    "calculer_moyenne_ponderee",
    "calculer_tendance",
    "calculer_variance",
    "calculer_confiance_prevision",
    "generer_prevision_categorie",
    # Utils - Calculs de budget
    "calculer_pourcentage_budget",
    "calculer_reste_disponible",
    "est_budget_depasse",
    "est_budget_a_risque",
    # Utils - Agrégation
    "agreger_depenses_par_categorie",
    "calculer_total_depenses",
    "filtrer_depenses_par_categorie",
    "filtrer_depenses_par_periode",
    # Utils - Résumés
    "construire_resume_financier",
    # Utils - Validation
    "valider_montant",
    "valider_mois",
    "valider_annee",
]
