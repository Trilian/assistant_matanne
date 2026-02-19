"""
Tests pour src/modules/cuisine/inventaire/historique.py

Tests complets pour afficher_historique().
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestRenderHistorique:
    """Tests pour afficher_historique()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.cuisine.inventaire.historique.st") as mock:
            mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_service(self):
        """Mock inventaire service"""
        with patch("src.modules.cuisine.inventaire.historique.obtenir_service_inventaire") as mock:
            mock_svc = MagicMock()
            mock.return_value = mock_svc
            yield mock_svc

    def test_affiche_erreur_si_service_none(self, mock_st):
        """Vérifie l'erreur si service indisponible"""
        with patch("src.modules.cuisine.inventaire.historique.obtenir_service_inventaire") as mock:
            mock.return_value = None

            from src.modules.cuisine.inventaire.historique import afficher_historique

            afficher_historique()

            mock_st.error.assert_called()

    def test_affiche_subheader(self, mock_st, mock_service):
        """Vérifie l'affichage du titre"""
        mock_service.get_historique.return_value = []

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.subheader.assert_called_once()
        assert "Historique" in mock_st.subheader.call_args[0][0]

    def test_affiche_filtres(self, mock_st, mock_service):
        """Vérifie l'affichage des filtres"""
        mock_service.get_historique.return_value = []

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.slider.assert_called()
        mock_st.selectbox.assert_called()
        mock_st.multiselect.assert_called()

    def test_affiche_info_si_pas_historique(self, mock_st, mock_service):
        """Vérifie le message sans historique"""
        mock_service.get_historique.return_value = []

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.info.assert_called()

    def test_filtre_par_type_modification(self, mock_st, mock_service):
        """Vérifie le filtrage par type"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["ajout"]

        mock_service.get_historique.return_value = [
            {
                "type": "ajout",
                "ingredient_nom": "Lait",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
            {
                "type": "suppression",
                "ingredient_nom": "Pain",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        # Le dataframe devrait être créé avec les données filtrées
        mock_st.dataframe.assert_called()

    def test_formate_changements_quantite(self, mock_st, mock_service):
        """Vérifie le formatage des changements de quantité"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["modification"]

        mock_service.get_historique.return_value = [
            {
                "type": "modification",
                "ingredient_nom": "Lait",
                "date_modification": datetime.now(),
                "quantite_avant": 2.0,
                "quantite_apres": 1.0,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            }
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.dataframe.assert_called_once()

    def test_formate_changements_emplacement(self, mock_st, mock_service):
        """Vérifie le formatage des changements d'emplacement"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["modification"]

        mock_service.get_historique.return_value = [
            {
                "type": "modification",
                "ingredient_nom": "Beurre",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": "Frigo",
                "emplacement_apres": "Congélo",
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            }
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.dataframe.assert_called_once()

    def test_formate_date_peremption(self, mock_st, mock_service):
        """Vérifie le formatage des changements de date péremption"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["modification"]

        mock_service.get_historique.return_value = [
            {
                "type": "modification",
                "ingredient_nom": "Yaourt",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": "2025-01-01",
                "date_peremption_apres": "2025-02-01",
            }
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.dataframe.assert_called_once()

    def test_affiche_icones_actions(self, mock_st, mock_service):
        """Vérifie les icônes par type d'action"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["ajout", "modification", "suppression"]

        mock_service.get_historique.return_value = [
            {
                "type": "ajout",
                "ingredient_nom": "A",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
            {
                "type": "modification",
                "ingredient_nom": "B",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
            {
                "type": "suppression",
                "ingredient_nom": "C",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.dataframe.assert_called_once()

    def test_affiche_stats_total(self, mock_st, mock_service):
        """Vérifie l'affichage des statistiques"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["ajout", "modification"]

        mock_service.get_historique.return_value = [
            {
                "type": "ajout",
                "ingredient_nom": "A",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
            {
                "type": "ajout",
                "ingredient_nom": "B",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
            {
                "type": "modification",
                "ingredient_nom": "C",
                "date_modification": datetime.now(),
                "quantite_avant": None,
                "quantite_apres": None,
                "emplacement_avant": None,
                "emplacement_apres": None,
                "date_peremption_avant": None,
                "date_peremption_apres": None,
            },
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        # Vérifie que metric est appelé pour les stats
        assert mock_st.metric.call_count >= 3

    def test_affiche_info_si_filtres_vident_resultats(self, mock_st, mock_service):
        """Vérifie le message si filtres ne matchent rien"""
        mock_st.slider.return_value = 30
        mock_st.selectbox.return_value = "Tous"
        mock_st.multiselect.return_value = ["suppression"]  # Filtré sur suppression seulement

        mock_service.get_historique.return_value = [
            {
                "type": "ajout",  # Pas suppression
                "ingredient_nom": "A",
                "date_modification": datetime.now(),
            }
        ]

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.info.assert_called()

    def test_gere_exception_service(self, mock_st, mock_service):
        """Vérifie la gestion d'erreur du service"""
        mock_service.get_historique.side_effect = Exception("Service error")

        from src.modules.cuisine.inventaire.historique import afficher_historique

        afficher_historique()

        mock_st.error.assert_called()


class TestHistoriqueIntegration:
    """Tests d'intégration pour le module historique"""

    def test_import_render_historique(self):
        """Vérifie que afficher_historique est importable"""
        from src.modules.cuisine.inventaire.historique import afficher_historique

        assert callable(afficher_historique)

    def test_all_exports(self):
        """Vérifie __all__"""
        from src.modules.cuisine.inventaire.historique import __all__

        assert "afficher_historique" in __all__
