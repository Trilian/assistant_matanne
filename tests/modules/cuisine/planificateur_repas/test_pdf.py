"""
Tests pour src/modules/cuisine/planificateur_repas/pdf.py

Tests pour la generation de PDF du planning repas.
"""

from datetime import date, timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest


class TestGenererPdfPlanningSession:
    """Tests pour generer_pdf_planning_session"""

    def test_import(self):
        """Test import de la fonction"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        assert callable(generer_pdf_planning_session)

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_simple(self, mock_logger):
        """Test generation PDF avec donnees simples"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {
            "Lundi": {"midi": "Pates bolognaise", "soir": "Soupe legumes"},
            "Mardi": {"midi": "Poulet roti", "soir": "Omelette"},
        }
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None
        assert isinstance(result, BytesIO)
        result.seek(0)
        data = result.read()
        assert len(data) > 0
        assert data[:4] == b"%PDF"

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_avec_gouter(self, mock_logger):
        """Test generation PDF avec gouter inclus"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {"Mercredi": {"midi": "Steak", "soir": "Pizza", "gouter": "Fruits"}}
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None
        assert isinstance(result, BytesIO)

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_avec_conseils(self, mock_logger):
        """Test generation PDF avec conseils batch cooking"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {"Lundi": {"midi": "Riz curry"}}
        conseils = "Preparez le riz en grande quantite."
        result = generer_pdf_planning_session(planning_data, date.today(), conseils=conseils)
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_avec_suggestions_bio(self, mock_logger):
        """Test generation PDF avec suggestions bio/local"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {"Jeudi": {"midi": "Salade composee"}}
        suggestions_bio = ["Legumes de saison", "Fromage fermier local"]
        result = generer_pdf_planning_session(
            planning_data, date.today(), suggestions_bio=suggestions_bio
        )
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_complet(self, mock_logger):
        """Test generation PDF avec toutes les options"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {
            "Lundi": {"midi": "Pates", "soir": "Soupe", "gouter": "Pomme"},
            "Mardi": {"midi": "Poulet", "soir": "Salade"},
            "Mercredi": {"midi": "Poisson", "soir": "Pizza"},
        }
        conseils = "Batch cooking dimanche matin."
        suggestions_bio = ["Legumes bio", "Viande locale"]
        result = generer_pdf_planning_session(
            planning_data, date.today(), conseils=conseils, suggestions_bio=suggestions_bio
        )
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_repas_dict(self, mock_logger):
        """Test generation PDF avec repas au format dict"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {
            "Lundi": {
                "midi": {"nom": "Pates carbonara", "id": 1},
                "soir": {"nom": "Soupe maison", "id": 2},
            },
        }
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_vide(self, mock_logger):
        """Test generation PDF avec planning vide"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {}
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_repas_partiels(self, mock_logger):
        """Test generation PDF avec repas partiellement remplis"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {
            "Lundi": {"midi": "Pates"},
            "Mardi": {"soir": "Soupe"},
        }
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_nom_long(self, mock_logger):
        """Test generation PDF avec noms de recettes longs"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {
            "Lundi": {"midi": "Une recette avec un nom tres tres tres tres long"},
        }
        result = generer_pdf_planning_session(planning_data, date.today())
        assert result is not None

    @patch("src.modules.cuisine.planificateur_repas.pdf.logger")
    def test_generer_pdf_planning_date_future(self, mock_logger):
        """Test generation PDF avec date future"""
        from src.modules.cuisine.planificateur_repas.pdf import generer_pdf_planning_session

        planning_data = {"Lundi": {"midi": "Test"}}
        date_future = date.today() + timedelta(days=30)
        result = generer_pdf_planning_session(planning_data, date_future)
        assert result is not None
