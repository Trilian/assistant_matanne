"""
Tests pour src/modules/cuisine/inventaire/alertes.py

Tests complets pour afficher_alertes() avec mocking Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestRenderAlertes:
    """Tests pour afficher_alertes()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.cuisine.inventaire.alertes.st") as mock:
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock inventaire service"""
        with patch("src.modules.cuisine.inventaire.alertes.obtenir_service_inventaire") as mock:
            mock_svc = MagicMock()
            mock.return_value = mock_svc
            yield mock_svc

    @pytest.fixture
    def mock_prepare_df(self):
        """Mock de _prepare_alert_dataframe"""
        with patch("src.modules.cuisine.inventaire.alertes._prepare_alert_dataframe") as mock:
            mock.return_value = MagicMock()
            yield mock

    def test_affiche_erreur_si_service_none(self, mock_st):
        """Vérifie l'erreur si service indisponible"""
        with patch("src.modules.cuisine.inventaire.alertes.obtenir_service_inventaire") as mock:
            mock.return_value = None

            from src.modules.cuisine.inventaire.alertes import afficher_alertes

            afficher_alertes()

            mock_st.error.assert_called_once()

    def test_affiche_success_si_pas_alertes(self, mock_st, mock_service):
        """Vérifie le message sans alertes"""
        mock_service.get_alertes.return_value = {
            "critique": [],
            "stock_bas": [],
            "peremption_proche": [],
        }

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        mock_st.success.assert_called_once()
        assert "Aucune alerte" in mock_st.success.call_args[0][0]

    def test_affiche_alertes_critiques(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie l'affichage des alertes critiques"""
        mock_service.get_alertes.return_value = {
            "critique": [{"nom": "Lait", "quantite": 0}],
            "stock_bas": [],
            "peremption_proche": [],
        }

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        mock_st.error.assert_called()
        mock_st.dataframe.assert_called()

    def test_affiche_alertes_stock_bas(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie l'affichage des alertes stock bas"""
        mock_service.get_alertes.return_value = {
            "critique": [],
            "stock_bas": [{"nom": "Riz", "quantite": 1}],
            "peremption_proche": [],
        }

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        mock_st.warning.assert_called()

    def test_affiche_alertes_peremption(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie l'affichage des alertes péremption"""
        mock_service.get_alertes.return_value = {
            "critique": [],
            "stock_bas": [],
            "peremption_proche": [{"nom": "Yaourt", "date_peremption": "2025-01-15"}],
        }

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        mock_st.warning.assert_called()
        assert "péremption" in mock_st.warning.call_args[0][0].lower()

    def test_affiche_dividers(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie l'affichage des dividers"""
        mock_service.get_alertes.return_value = {
            "critique": [{"nom": "Lait"}],
            "stock_bas": [{"nom": "Riz"}],
            "peremption_proche": [],
        }

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        assert mock_st.divider.call_count >= 1

    def test_gere_exception_service(self, mock_st, mock_service):
        """Vérifie la gestion d'exception"""
        mock_service.get_alertes.side_effect = Exception("DB Error")

        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        afficher_alertes()

        mock_st.error.assert_called()


class TestAlertesIntegration:
    """Tests d'intégration"""

    def test_import_render_alertes(self):
        """Vérifie que afficher_alertes s'importe"""
        from src.modules.cuisine.inventaire.alertes import afficher_alertes

        assert callable(afficher_alertes)

    def test_all_exports(self):
        """Vérifie __all__"""
        from src.modules.cuisine.inventaire.alertes import __all__

        assert "afficher_alertes" in __all__
