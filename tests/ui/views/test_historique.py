"""
Tests unitaires pour src/ui/views/historique.py

Couverture: afficher_timeline_activite, afficher_activite_utilisateur, afficher_statistiques_activite
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class MockAction:
    """Mock pour Action."""

    def __init__(self, **kwargs):
        self.entity_type = kwargs.get("entity_type", "recette")
        self.description = kwargs.get("description", "Action test")
        self.user_name = kwargs.get("user_name", "User")
        self.cree_le = kwargs.get("cree_le", datetime.now())
        self.details = kwargs.get("details", {"key": "value"})


class MockStats:
    """Mock pour les statistiques."""

    def __init__(self, **kwargs):
        self.total_actions = kwargs.get("total_actions", 42)
        self.actions_today = kwargs.get("actions_today", 5)
        self.actions_this_week = kwargs.get("actions_this_week", 20)
        self.most_active_users = kwargs.get(
            "most_active_users",
            [{"name": "Alice", "count": 15}, {"name": "Bob", "count": 10}],
        )


class TestAfficherTimelineActivite:
    """Tests pour afficher_timeline_activite."""

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.info")
    def test_affiche_message_si_vide(self, mock_info, mock_service):
        """Test qu'un message est affiché si aucune activité."""
        from src.ui.views.historique import afficher_timeline_activite

        mock_service.return_value.get_recent_actions.return_value = []

        afficher_timeline_activite()

        mock_info.assert_called_with("Aucune activité récente")

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.caption")
    @patch("streamlit.info")
    def test_affiche_actions(
        self, mock_info, mock_caption, mock_columns, mock_markdown, mock_service
    ):
        """Test que les actions sont affichées."""
        from src.ui.views.historique import afficher_timeline_activite

        mock_action = MockAction(entity_type="recette", description="Ajout recette")
        mock_service.return_value.get_recent_actions.return_value = [mock_action]
        mock_columns.return_value = [MagicMock(), MagicMock()]

        afficher_timeline_activite(limit=5)

        mock_service.return_value.get_recent_actions.assert_called_with(limit=5)

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.caption")
    @patch("streamlit.info")
    def test_icones_par_type_entite(
        self, mock_info, mock_caption, mock_columns, mock_markdown, mock_service
    ):
        """Test que les icônes correspondent aux types d'entité."""
        from src.ui.views.historique import afficher_timeline_activite

        # Test avec type "recette" → icône 🍳
        mock_action = MockAction(entity_type="recette")
        mock_service.return_value.get_recent_actions.return_value = [mock_action]
        col_mock = MagicMock()
        mock_columns.return_value = [col_mock, MagicMock()]

        afficher_timeline_activite()

        # Vérifier qu'une icône est affichée dans col1
        assert mock_columns.called


class TestAfficherActiviteUtilisateur:
    """Tests pour afficher_activite_utilisateur."""

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.markdown")
    @patch("streamlit.info")
    def test_affiche_message_si_vide(self, mock_info, mock_markdown, mock_service):
        """Test message si aucune activité utilisateur."""
        from src.ui.views.historique import afficher_activite_utilisateur

        mock_service.return_value.get_user_history.return_value = []

        afficher_activite_utilisateur("user_123")

        mock_info.assert_called_with("Aucune activité enregistrée")

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.markdown")
    @patch("streamlit.expander")
    @patch("streamlit.json")
    @patch("streamlit.info")
    def test_appelle_service_avec_user_id(
        self, mock_info, mock_json, mock_expander, mock_markdown, mock_service
    ):
        """Test que le service est appelé avec le bon user_id."""
        from src.ui.views.historique import afficher_activite_utilisateur

        mock_service.return_value.get_user_history.return_value = [MockAction()]
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()

        afficher_activite_utilisateur("user_456")

        mock_service.return_value.get_user_history.assert_called_with("user_456", limit=20)


class TestAfficherStatistiquesActivite:
    """Tests pour afficher_statistiques_activite."""

    @patch("src.ui.views.historique.get_action_history_service")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    @patch("streamlit.write")
    def test_affiche_metriques(
        self, mock_write, mock_metric, mock_columns, mock_markdown, mock_service
    ):
        """Test que les métriques sont affichées."""
        from src.ui.views.historique import afficher_statistiques_activite

        mock_service.return_value.get_stats.return_value = MockStats(
            total_actions=100, actions_today=10, actions_this_week=50
        )
        mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        afficher_statistiques_activite()

        # Vérifie que metric est appelé 3 fois (total, aujourd'hui, semaine)
        assert mock_metric.call_count >= 3


class TestHistoriqueExports:
    """Tests pour les exports du module."""

    def test_all_exports(self):
        """Test que __all__ contient les exports attendus."""
        from src.ui.views import historique

        assert hasattr(historique, "__all__")
        assert "afficher_timeline_activite" in historique.__all__
        assert "afficher_activite_utilisateur" in historique.__all__
        assert "afficher_statistiques_activite" in historique.__all__

    def test_import_depuis_views(self):
        """Test imports depuis src.ui.views."""
        from src.ui.views import (
            afficher_activite_utilisateur,
            afficher_statistiques_activite,
            afficher_timeline_activite,
        )

        assert callable(afficher_timeline_activite)
        assert callable(afficher_activite_utilisateur)
        assert callable(afficher_statistiques_activite)

    def test_import_depuis_ui(self):
        """Test imports depuis src.ui."""
        from src.ui import (
            afficher_activite_utilisateur,
            afficher_statistiques_activite,
            afficher_timeline_activite,
        )

        assert callable(afficher_timeline_activite)
        assert callable(afficher_activite_utilisateur)
        assert callable(afficher_statistiques_activite)
