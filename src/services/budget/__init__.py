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
    CategorieDepense,
    FrequenceRecurrence,
    Depense,
    FactureMaison,
    BudgetMensuel,
    ResumeFinancier,
    PrevisionDepense,
)

from .service import (
    BudgetService,
    get_budget_service,
)

from .utils import (
    # Conversion DB → Pydantic
    db_entry_to_depense,
    db_entries_to_depenses,
    # Calculs statistiques
    calculer_moyenne_ponderee,
    calculer_tendance,
    calculer_variance,
    calculer_confiance_prevision,
    generer_prevision_categorie,
    # Calculs de budget
    calculer_pourcentage_budget,
    calculer_reste_disponible,
    est_budget_depasse,
    est_budget_a_risque,
    # Agrégation
    agreger_depenses_par_categorie,
    calculer_total_depenses,
    filtrer_depenses_par_categorie,
    filtrer_depenses_par_periode,
    # Résumés
    construire_resume_financier,
    # Validation
    valider_montant,
    valider_mois,
    valider_annee,
)


def render_budget_dashboard():
    """
    Affiche le tableau de bord budget dans Streamlit.
    
    Déplacé vers src/domains/famille/ui/budget_dashboard.py
    Cette fonction assure la rétrocompatibilité.
    """
    from src.domains.famille.ui.budget_dashboard import render_budget_dashboard as _render
    return _render()


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
    # UI (rétrocompatibilité)
    "render_budget_dashboard",
]
