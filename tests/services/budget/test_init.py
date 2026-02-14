"""
Tests pour src/services/budget/__init__.py

Couvre les fonctions wrapper de rétrocompatibilité.
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestRenderBudgetDashboard:
    """Tests pour render_budget_dashboard (rétrocompatibilité)."""

    @patch("src.modules.famille.budget_dashboard.render_budget_dashboard")
    def test_render_budget_dashboard_calls_underlying(self, mock_render):
        """La fonction wrapper appelle la fonction sous-jacente."""
        mock_render.return_value = "dashboard_result"

        # Import APRÈS le patch pour que le lazy import utilise le mock
        from src.services.budget import render_budget_dashboard

        result = render_budget_dashboard()

        mock_render.assert_called_once()
        assert result == "dashboard_result"

    def test_render_budget_dashboard_import(self):
        """Import de render_budget_dashboard fonctionne."""
        from src.services.budget import render_budget_dashboard

        assert callable(render_budget_dashboard)


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
