"""
Tests pour les nouveaux services ajoutés.

Services testés:
- OpenFoodFactsService
- CoursesOrganisationService
- Planning exports
"""

import pytest
from unittest.mock import Mock, patch


# ═══════════════════════════════════════════════════════════
# TESTS OPENFOODFACTS SERVICE
# ═══════════════════════════════════════════════════════════


class TestOpenFoodFactsService:
    """Tests pour le service OpenFoodFacts"""
    
    def test_import_service(self):
        """Vérifie que le service peut être importé"""
        from src.services.openfoodfacts import get_openfoodfacts_service
        
        service = get_openfoodfacts_service()
        assert service is not None
    
    @patch('httpx.Client')
    def test_rechercher_produit_mock(self, mock_client_class: Mock):
        """Test recherche produit avec API mockée"""
        from src.services.openfoodfacts import get_openfoodfacts_service
        
        # Configurer le mock pour httpx.Client
        mock_client = Mock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Nutella",
                "brands": "Ferrero",
                "nutriscore_grade": "e",
                "categories": "Pâtes à tartiner",
            }
        }
        mock_client.get.return_value = mock_response
        
        service = get_openfoodfacts_service()
        produit = service.rechercher_produit("3017620422003")
        
        assert produit is not None
        assert produit.nom == "Nutella"
        assert produit.marque == "Ferrero"
    
    @patch('httpx.Client')
    def test_rechercher_produit_non_trouve(self, mock_client_class: Mock):
        """Test recherche produit non trouvé"""
        from src.services.openfoodfacts import get_openfoodfacts_service
        
        # Configurer le mock
        mock_client = Mock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": 0}
        mock_client.get.return_value = mock_response
        
        service = get_openfoodfacts_service()
        produit = service.rechercher_produit("0000000000000")
        
        assert produit is None


# ═══════════════════════════════════════════════════════════
# TESTS COURSES ORGANISATION SERVICE
# ═══════════════════════════════════════════════════════════


class TestCoursesOrganisationService:
    """Tests pour le service d'organisation des courses"""
    
    def test_import_service(self):
        """Vérifie que le service peut être importé"""
        from src.services.courses_organisation import get_courses_organisation_service
        
        service = get_courses_organisation_service()
        assert service is not None
    
    def test_magasins_enum(self):
        """Test que l'enum Magasin contient les valeurs attendues"""
        from src.services.courses_organisation import Magasin
        
        assert Magasin.CARREFOUR_DRIVE is not None
        assert Magasin.BIO_COOP is not None
        assert Magasin.GRAND_FRAIS is not None
        assert Magasin.THIRIET is not None
    
    def test_suggerer_magasin_bio(self):
        """Test suggestion magasin pour produit bio"""
        from src.services.courses_organisation import get_courses_organisation_service, Magasin
        
        service = get_courses_organisation_service()
        
        # Produit bio → Bio Coop
        magasin = service.suggerer_magasin("Yaourt", est_bio=True)
        assert magasin == Magasin.BIO_COOP
    
    def test_suggerer_magasin_surgele(self):
        """Test suggestion magasin pour surgelé"""
        from src.services.courses_organisation import get_courses_organisation_service, Magasin
        
        service = get_courses_organisation_service()
        
        # Surgelé → Thiriet
        magasin = service.suggerer_magasin("Légumes surgelés")
        assert magasin == Magasin.THIRIET
    
    def test_suggerer_magasin_defaut(self):
        """Test suggestion magasin par défaut"""
        from src.services.courses_organisation import get_courses_organisation_service, Magasin
        
        service = get_courses_organisation_service()
        
        # Produit générique → Carrefour
        magasin = service.suggerer_magasin("Pâtes")
        assert magasin == Magasin.CARREFOUR_DRIVE
    
    def test_exporter_bring_format(self):
        """Test export format Bring!"""
        from src.services.courses_organisation import (
            get_courses_organisation_service, 
            Magasin, 
            ListeCoursesMagasin,
            ArticleCourse,
        )
        
        service = get_courses_organisation_service()
        
        # Créer une liste
        liste = ListeCoursesMagasin(magasin=Magasin.CARREFOUR_DRIVE)
        liste.ajouter_article(ArticleCourse(
            nom="Lait",
            quantite=2.0,
            unite="L",
            rayon="produits_laitiers"
        ))
        liste.ajouter_article(ArticleCourse(
            nom="Pain",
            quantite=1.0,
            unite="pièce",
            rayon="boulangerie"
        ))
        
        texte = service.exporter_bring(liste)
        
        assert "Lait" in texte
        assert "Pain" in texte
        assert "2" in texte


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING EXPORTS
# ═══════════════════════════════════════════════════════════


class TestPlanningExports:
    """Tests pour les exports du module planning"""
    
    def test_import_planning_service(self):
        """Test import service planning standard"""
        from src.services import get_planning_service, PlanningService
        
        service = get_planning_service()
        assert isinstance(service, PlanningService)
    
    def test_import_planning_unified_service(self):
        """Test import service planning unifié"""
        from src.services import get_planning_unified_service, PlanningAIService
        
        service = get_planning_unified_service()
        assert isinstance(service, PlanningAIService)
    
    def test_import_schemas_planning(self):
        """Test import des schémas Pydantic"""
        from src.services import JourPlanning, ParametresEquilibre
        
        # Test validation schéma
        jour = JourPlanning(jour="2026-02-02", dejeuner="Pâtes", diner="Soupe")
        assert jour.jour == "2026-02-02"
        
        params = ParametresEquilibre()
        assert params.pates_riz_count == 3


# ═══════════════════════════════════════════════════════════
# TESTS NOUVEAUX MODÈLES
# ═══════════════════════════════════════════════════════════


class TestUserPreferencesModel:
    """Tests pour les nouveaux modèles user_preferences"""
    
    def test_import_models(self):
        """Test import des nouveaux modèles"""
        from src.core.models import (
            UserPreference,
            RecipeFeedback,
            OpenFoodFactsCache,
            ExternalCalendarConfig,
        )
        
        assert UserPreference is not None
        assert RecipeFeedback is not None
        assert OpenFoodFactsCache is not None
        assert ExternalCalendarConfig is not None
    
    def test_feedback_type_enum(self):
        """Test enum FeedbackType"""
        from src.core.models import FeedbackType
        
        assert FeedbackType.LIKE.value == "like"
        assert FeedbackType.DISLIKE.value == "dislike"
        assert FeedbackType.NEUTRAL.value == "neutral"
    
    def test_calendar_provider_enum(self):
        """Test enum CalendarProviderNew"""
        from src.core.models import CalendarProviderNew
        
        assert CalendarProviderNew.GOOGLE.value == "google"
        assert CalendarProviderNew.APPLE.value == "apple"
        assert CalendarProviderNew.OUTLOOK.value == "outlook"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
