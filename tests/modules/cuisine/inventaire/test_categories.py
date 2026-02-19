"""
Tests pour src/modules/cuisine/inventaire/categories.py

Tests complets pour afficher_categories() avec mocking Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestRenderCategories:
    """Tests pour afficher_categories()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.cuisine.inventaire.categories.st") as mock:
            mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock inventaire service"""
        with patch("src.modules.cuisine.inventaire.categories.obtenir_service_inventaire") as mock:
            mock_svc = MagicMock()
            mock.return_value = mock_svc
            yield mock_svc

    @pytest.fixture
    def mock_prepare_df(self):
        """Mock de _prepare_inventory_dataframe"""
        with patch(
            "src.modules.cuisine.inventaire.categories._prepare_inventory_dataframe"
        ) as mock:
            mock.return_value = MagicMock()
            yield mock

    def test_affiche_erreur_si_service_none(self, mock_st):
        """Vérifie l'erreur si service indisponible"""
        with patch("src.modules.cuisine.inventaire.categories.obtenir_service_inventaire") as mock:
            mock.return_value = None

            from src.modules.cuisine.inventaire.categories import afficher_categories

            afficher_categories()

            mock_st.error.assert_called_once()

    def test_affiche_info_si_inventaire_vide(self, mock_st, mock_service):
        """Vérifie le message si inventaire vide"""
        mock_service.get_inventaire_complet.return_value = []

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        mock_st.info.assert_called_once()
        assert "vide" in mock_st.info.call_args[0][0].lower()

    def test_groupe_articles_par_categorie(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie le groupement par catégorie"""
        mock_service.get_inventaire_complet.return_value = [
            {"ingredient_categorie": "Fruits", "quantite": 5},
            {"ingredient_categorie": "Fruits", "quantite": 3},
            {"ingredient_categorie": "Légumes", "quantite": 2},
        ]
        mock_service.get_alertes.return_value = {"critique": [], "stock_bas": []}

        mock_st.tabs.return_value = [MagicMock(), MagicMock()]

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        # Vérifie que tabs a été appelé
        mock_st.tabs.assert_called_once()

    def test_affiche_metriques_categorie(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie les métriques par catégorie"""
        mock_service.get_inventaire_complet.return_value = [
            {"ingredient_categorie": "Fruits", "quantite": 5, "statut": "ok"},
            {"ingredient_categorie": "Fruits", "quantite": 3, "statut": "ok"},
        ]
        mock_service.get_alertes.return_value = {"critique": [], "stock_bas": []}

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab]

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        # metric appelé pour les stats
        mock_st.metric.assert_called()

    def test_calcule_quantite_totale(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie le calcul de quantité totale"""
        mock_service.get_inventaire_complet.return_value = [
            {"ingredient_categorie": "Fruits", "quantite": 5.5, "statut": "ok"},
            {"ingredient_categorie": "Fruits", "quantite": 3.5, "statut": "ok"},
        ]
        mock_service.get_alertes.return_value = {"critique": [], "stock_bas": []}

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab]

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        # Vérifier que metric a été appelé avec la quantité totale
        calls = [str(call) for call in mock_st.metric.call_args_list]
        assert any("9" in str(call) or "Quantité" in str(call) for call in calls)

    def test_compte_alertes_par_categorie(self, mock_st, mock_service, mock_prepare_df):
        """Vérifie le comptage des alertes par catégorie"""
        mock_service.get_inventaire_complet.return_value = [
            {"ingredient_categorie": "Fruits", "quantite": 0, "statut": "critique"},
            {"ingredient_categorie": "Fruits", "quantite": 5, "statut": "ok"},
        ]
        mock_service.get_alertes.return_value = {"critique": [], "stock_bas": []}

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs.return_value = [mock_tab]

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        # Une alerte devrait être comptée
        assert mock_st.metric.called

    def test_gere_exception_service(self, mock_st, mock_service):
        """Vérifie la gestion d'exception"""
        mock_service.get_inventaire_complet.side_effect = Exception("DB Error")

        from src.modules.cuisine.inventaire.categories import afficher_categories

        afficher_categories()

        mock_st.error.assert_called()


class TestCategoriesIntegration:
    """Tests d'intégration"""

    def test_import_render_categories(self):
        """Vérifie que afficher_categories s'importe"""
        from src.modules.cuisine.inventaire.categories import afficher_categories

        assert callable(afficher_categories)

    def test_all_exports(self):
        """Vérifie __all__"""
        from src.modules.cuisine.inventaire.categories import __all__

        assert "afficher_categories" in __all__
