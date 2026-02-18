"""
Tests pour src/services/budget/__init__.py

Couvre les exports du module budget.
"""

import pytest


@pytest.mark.unit
class TestBudgetModuleExports:
    """Tests pour les exports du module budget."""

    def test_exports_budget_service(self):
        """Export BudgetService."""
        from src.services.budget import BudgetService

        assert BudgetService is not None

    def test_exports_get_budget_service(self):
        """Export get_budget_service."""
        from src.services.budget import get_budget_service

        assert callable(get_budget_service)

    def test_exports_schemas(self):
        """Export des schémas."""
        from src.services.budget import (
            CategorieDepense,
            Depense,
        )

        assert CategorieDepense is not None
        assert Depense is not None

    def test_exports_utils(self):
        """Export des fonctions utilitaires."""
        from src.services.budget import (
            calculer_moyenne_ponderee,
            valider_montant,
        )

        assert callable(calculer_moyenne_ponderee)
        assert callable(valider_montant)
