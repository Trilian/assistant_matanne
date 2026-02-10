"""
Package de gestion du budget familial.

Exports:
- BudgetService: Service principal
- get_budget_service: Factory
- Schémas: CategorieDepense, Depense, BudgetMensuel, etc.
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
    # UI (rétrocompatibilité)
    "render_budget_dashboard",
]
