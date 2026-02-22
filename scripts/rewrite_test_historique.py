"""Rewrite test_historique.py to mock service instead of DB."""

import os

new_content = '''"""
Tests pour src/modules/cuisine/courses/historique.py

Couverture complete des fonctions UI historique courses.
Refactored: mocks service.obtenir_historique_achats() au lieu de obtenir_contexte_db.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch


class TestRenderHistorique:
    """Tests pour afficher_historique()."""

    def test_import(self):
        """Test import reussi."""
        from src.modules.cuisine.courses.historique import afficher_historique

        assert afficher_historique is not None

    @patch("src.modules.cuisine.courses.historique.etat_vide")
    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_no_articles(self, mock_st, mock_get_service, mock_etat_vide):
        """Test avec aucun article achete."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = []
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_st.subheader.assert_called()
        mock_etat_vide.assert_called_with("Aucun achat pendant cette p\\u00e9riode", "\\U0001f6d2")

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.pd")
    def test_render_historique_with_articles(self, mock_pd, mock_st, mock_get_service):
        """Test avec articles achetes."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],  # date inputs
            [MagicMock(), MagicMock(), MagicMock()],  # metrics
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = [
            {
                "id": 1,
                "ingredient_nom": "Tomates",
                "quantite_necessaire": 2.0,
                "unite": "kg",
                "priorite": "haute",
                "rayon_magasin": "Fruits et l\\u00e9gumes",
                "achete_le": datetime.now(),
                "suggere_par_ia": False,
            }
        ]
        mock_get_service.return_value = mock_service

        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.to_csv.return_value = "test,csv"
        mock_pd.DataFrame.return_value = mock_df

        afficher_historique()

        mock_st.metric.assert_called()
        mock_st.dataframe.assert_called()
        mock_st.download_button.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_with_multiple_rayons(self, mock_st, mock_get_service):
        """Test statistiques multiples rayons."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock(), MagicMock()],
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = [
            {"id": 1, "ingredient_nom": "Lait", "quantite_necessaire": 1.0, "unite": "l",
             "priorite": "haute", "rayon_magasin": "Cr\\u00e8merie", "achete_le": datetime.now(), "suggere_par_ia": True},
            {"id": 2, "ingredient_nom": "Pain", "quantite_necessaire": 1.0, "unite": "pi\\u00e8ce",
             "priorite": "moyenne", "rayon_magasin": "Boulangerie", "achete_le": datetime.now(), "suggere_par_ia": False},
            {"id": 3, "ingredient_nom": "Beurre", "quantite_necessaire": 1.0, "unite": "pi\\u00e8ce",
             "priorite": "moyenne", "rayon_magasin": "Cr\\u00e8merie", "achete_le": datetime.now(), "suggere_par_ia": False},
        ]
        mock_get_service.return_value = mock_service

        afficher_historique()

        assert mock_st.metric.call_count >= 3

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    @patch("src.modules.cuisine.courses.historique.logger")
    def test_render_historique_exception(self, mock_logger, mock_st, mock_get_service):
        """Test gestion erreur."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.side_effect = Exception("DB error")
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_st.error.assert_called()
        mock_logger.error.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_ia_badge(self, mock_st, mock_get_service):
        """Test badge IA pour suggestions."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock(), MagicMock()],
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=7),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = [
            {"id": 1, "ingredient_nom": "Pommes", "quantite_necessaire": 1.5, "unite": "kg",
             "priorite": "basse", "rayon_magasin": "Fruits", "achete_le": datetime.now(), "suggere_par_ia": True},
        ]
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_st.dataframe.assert_called()

    @patch("src.modules.cuisine.courses.historique.etat_vide")
    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_empty_df(self, mock_st, mock_get_service, mock_etat_vide):
        """Test avec DataFrame vide (cas edge)."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=1),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = []
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_etat_vide.assert_called_with("Aucun achat pendant cette p\\u00e9riode", "\\U0001f6d2")

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_null_ingredient(self, mock_st, mock_get_service):
        """Test avec ingredient null (donnees dict)."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock(), MagicMock()],
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = [
            {"id": 1, "ingredient_nom": "N/A", "quantite_necessaire": 1.0, "unite": "",
             "priorite": "moyenne", "rayon_magasin": None, "achete_le": None, "suggere_par_ia": False},
        ]
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_st.dataframe.assert_called()

    @patch("src.modules.cuisine.courses.historique.obtenir_service_courses")
    @patch("src.modules.cuisine.courses.historique.st")
    def test_render_historique_unknown_priority(self, mock_st, mock_get_service):
        """Test avec priorite inconnue."""
        from src.modules.cuisine.courses.historique import afficher_historique

        mock_st.columns.side_effect = [
            [MagicMock(), MagicMock()],
            [MagicMock(), MagicMock(), MagicMock()],
        ]
        mock_st.date_input.side_effect = [
            datetime.now().date() - timedelta(days=30),
            datetime.now().date(),
        ]

        mock_service = MagicMock()
        mock_service.obtenir_historique_achats.return_value = [
            {"id": 1, "ingredient_nom": "Test", "quantite_necessaire": 1.0, "unite": "kg",
             "priorite": "inconnu", "rayon_magasin": "Autre", "achete_le": datetime.now(), "suggere_par_ia": False},
        ]
        mock_get_service.return_value = mock_service

        afficher_historique()

        mock_st.dataframe.assert_called()


class TestHistoriqueModule:
    """Tests module-level."""

    def test_all_exports(self):
        """Test __all__ exports."""
        from src.modules.cuisine.courses import historique

        assert "afficher_historique" in historique.__all__
'''

filepath = os.path.join("tests", "modules", "cuisine", "courses", "test_historique.py")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"Rewrote {filepath}")
