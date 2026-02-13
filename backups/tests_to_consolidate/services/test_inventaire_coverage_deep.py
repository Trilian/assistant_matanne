"""
Tests complets pour src/services/inventaire.py

Couverture cible: >80%
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SCHÃ‰MAS PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggestionCourses:
    """Tests schÃ©ma SuggestionCourses."""

    def test_import_schema(self):
        from src.services.inventaire import SuggestionCourses

        assert SuggestionCourses is not None

    def test_creation_valide(self):
        from src.services.inventaire import SuggestionCourses

        suggestion = SuggestionCourses(
            nom="Lait", quantite=2.0, unite="L", priorite="haute", rayon="Laitier"
        )

        assert suggestion.nom == "Lait"
        assert suggestion.quantite == 2.0
        assert suggestion.priorite == "haute"

    def test_priorite_validation(self):
        from pydantic import ValidationError

        from src.services.inventaire import SuggestionCourses

        # PrioritÃ© valide
        s = SuggestionCourses(nom="Test", quantite=1, unite="u", priorite="moyenne", rayon="Test")
        assert s.priorite == "moyenne"

        # PrioritÃ© invalide
        with pytest.raises(ValidationError):
            SuggestionCourses(nom="Test", quantite=1, unite="u", priorite="invalid", rayon="Test")

    def test_quantite_positive(self):
        from pydantic import ValidationError

        from src.services.inventaire import SuggestionCourses

        with pytest.raises(ValidationError):
            SuggestionCourses(nom="Test", quantite=0, unite="u", priorite="haute", rayon="Test")


class TestArticleImport:
    """Tests schÃ©ma ArticleImport."""

    def test_creation_basique(self):
        from src.services.inventaire import ArticleImport

        article = ArticleImport(nom="Tomates", quantite=5.0, quantite_min=2.0, unite="kg")

        assert article.nom == "Tomates"
        assert article.quantite == 5.0

    def test_champs_optionnels(self):
        from src.services.inventaire import ArticleImport

        article = ArticleImport(
            nom="Pommes",
            quantite=3.0,
            quantite_min=1.0,
            unite="kg",
            categorie="Fruits",
            emplacement="Frigo",
            date_peremption="2026-03-15",
        )

        assert article.categorie == "Fruits"
        assert article.emplacement == "Frigo"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInventaireConstants:
    """Tests constantes du module."""

    def test_categories_defined(self):
        from src.services.inventaire import CATEGORIES

        assert len(CATEGORIES) > 0
        assert "LÃ©gumes" in CATEGORIES
        assert "Fruits" in CATEGORIES
        assert "ProtÃ©ines" in CATEGORIES

    def test_emplacements_defined(self):
        from src.services.inventaire import EMPLACEMENTS

        assert len(EMPLACEMENTS) > 0
        assert "Frigo" in EMPLACEMENTS
        assert "CongÃ©lateur" in EMPLACEMENTS
        assert "Placard" in EMPLACEMENTS


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE INVENTAIRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInventaireServiceInit:
    """Tests initialisation du service."""

    def test_import_service(self):
        from src.services.inventaire import InventaireService

        assert InventaireService is not None

    def test_init_service(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # VÃ©rifier que le service est bien crÃ©Ã©
        assert service is not None

    def test_heritage_multiple(self):
        from src.services.base_ai_service import BaseAIService
        from src.services.inventaire import InventaireService
        from src.services.types import BaseService

        service = InventaireService()

        assert isinstance(service, BaseService)
        assert isinstance(service, BaseAIService)


class TestInventaireServiceCalculerStatut:
    """Tests _calculer_statut."""

    def test_statut_ok(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # Mock article avec stock OK
        article = Mock()
        article.quantite = 10.0
        article.quantite_min = 5.0
        article.date_peremption = None

        statut = service._calculer_statut(article, date.today())

        assert statut == "ok"

    def test_statut_stock_bas(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # Stock < quantite_min mais >= 50% de quantite_min
        article = Mock()
        article.quantite = 3.0
        article.quantite_min = 5.0
        article.date_peremption = None

        statut = service._calculer_statut(article, date.today())

        assert statut == "stock_bas"

    def test_statut_critique(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # Stock < 50% de quantite_min
        article = Mock()
        article.quantite = 1.0
        article.quantite_min = 5.0
        article.date_peremption = None

        statut = service._calculer_statut(article, date.today())

        assert statut == "critique"

    def test_statut_peremption_proche(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # PÃ©remption dans 5 jours (< 7)
        article = Mock()
        article.quantite = 10.0
        article.quantite_min = 5.0
        article.date_peremption = date.today() + timedelta(days=5)

        statut = service._calculer_statut(article, date.today())

        assert statut == "peremption_proche"


class TestInventaireServiceJoursAvantPeremption:
    """Tests _jours_avant_peremption."""

    def test_sans_date_peremption(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.date_peremption = None

        result = service._jours_avant_peremption(article, date.today())

        assert result is None

    def test_avec_date_peremption(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.date_peremption = date.today() + timedelta(days=10)

        result = service._jours_avant_peremption(article, date.today())

        assert result == 10

    def test_perime(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.date_peremption = date.today() - timedelta(days=3)

        result = service._jours_avant_peremption(article, date.today())

        assert result == -3


class TestInventaireServiceGetAlertes:
    """Tests get_alertes."""

    def test_get_alertes_structure(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # Mock get_inventaire_complet
        with patch.object(service, "get_inventaire_complet", return_value=[]):
            alertes = service.get_alertes()

        assert "stock_bas" in alertes
        assert "critique" in alertes
        assert "peremption_proche" in alertes

    def test_get_alertes_avec_articles(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        mock_inventaire = [
            {"id": 1, "statut": "stock_bas", "ingredient_nom": "Lait"},
            {"id": 2, "statut": "critique", "ingredient_nom": "Oeufs"},
            {"id": 3, "statut": "peremption_proche", "ingredient_nom": "Yaourt"},
            {"id": 4, "statut": "ok", "ingredient_nom": "Riz"},  # Pas inclus
        ]

        with patch.object(service, "get_inventaire_complet", return_value=mock_inventaire):
            alertes = service.get_alertes()

        assert len(alertes["stock_bas"]) == 1
        assert len(alertes["critique"]) == 1
        assert len(alertes["peremption_proche"]) == 1


class TestInventaireServiceGetInventaireComplet:
    """Tests get_inventaire_complet."""

    def test_methode_existe(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # VÃ©rifier que la mÃ©thode existe
        assert hasattr(service, "get_inventaire_complet") or hasattr(service, "get_all")


class TestInventaireServiceSuggererCoursesIA:
    """Tests suggerer_courses_ia."""

    def test_methode_existe(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert hasattr(service, "suggerer_courses_ia")
        assert callable(service.suggerer_courses_ia)


class TestInventaireServiceEnregistrerModification:
    """Tests _enregistrer_modification."""

    def test_methode_existe(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert hasattr(service, "_enregistrer_modification")


class TestInventaireServiceGetHistorique:
    """Tests get_historique."""

    def test_methode_existe(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        assert hasattr(service, "get_historique")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInventaireEdgeCases:
    """Tests cas limites."""

    def test_quantite_zero(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.quantite = 0.0
        article.quantite_min = 5.0
        article.date_peremption = None

        statut = service._calculer_statut(article, date.today())

        assert statut == "critique"

    def test_quantite_min_zero(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.quantite = 5.0
        article.quantite_min = 0.0
        article.date_peremption = None

        # Ne devrait pas diviser par zÃ©ro
        statut = service._calculer_statut(article, date.today())

        assert statut == "ok"

    def test_peremption_aujourdhui(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.quantite = 10.0
        article.quantite_min = 5.0
        article.date_peremption = date.today()  # Expire aujourd'hui

        jours = service._jours_avant_peremption(article, date.today())

        assert jours == 0

    def test_peremption_exactement_7_jours(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        article = Mock()
        article.quantite = 10.0
        article.quantite_min = 5.0
        article.date_peremption = date.today() + timedelta(days=7)

        statut = service._calculer_statut(article, date.today())

        # 7 jours = still peremption_proche (<=7)
        assert statut == "peremption_proche"


class TestInventaireIntegration:
    """Tests d'intÃ©gration."""

    def test_workflow_alertes(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # Simuler diffÃ©rents articles
        mock_articles = [
            {"id": 1, "statut": "critique", "ingredient_nom": "A"},
            {"id": 2, "statut": "stock_bas", "ingredient_nom": "B"},
            {"id": 3, "statut": "peremption_proche", "ingredient_nom": "C"},
        ]

        with patch.object(service, "get_inventaire_complet", return_value=mock_articles):
            alertes = service.get_alertes()

        total_alertes = sum(len(v) for v in alertes.values())
        assert total_alertes == 3

    def test_service_has_ai_methods(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # MÃ©thodes hÃ©ritÃ©es de BaseAIService
        assert hasattr(service, "call_with_list_parsing_sync")

        # MÃ©thodes hÃ©ritÃ©es de InventoryAIMixin
        assert hasattr(service, "build_inventory_summary")


class TestInventaireBaseServiceMethods:
    """Tests mÃ©thodes hÃ©ritÃ©es de BaseService."""

    def test_has_crud_methods(self):
        from src.services.inventaire import InventaireService

        service = InventaireService()

        # BaseService fournit ces mÃ©thodes
        assert hasattr(service, "get_all")
        assert hasattr(service, "get_by_id")
        assert hasattr(service, "create")
        assert hasattr(service, "update")
        assert hasattr(service, "delete")
