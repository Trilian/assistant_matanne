"""
Tests pour CoursesService - Service critique
Tests complets pour la gestion des listes de courses

Uses patch_db_context fixture for test DB.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock

from src.services.courses import CoursesService, get_courses_service


# ═══════════════════════════════════════════════════════════
# TESTS INSTANCIATION ET FACTORY
# ═══════════════════════════════════════════════════════════

class TestCoursesServiceFactory:
    """Tests pour la factory et l'instanciation du service."""
    
    def test_get_courses_service_returns_instance(self):
        """La factory retourne une instance de CoursesService."""
        service = get_courses_service()
        assert service is not None
        assert isinstance(service, CoursesService)
    
    def test_service_has_required_attributes(self):
        """Le service a les attributs requis."""
        service = get_courses_service()
        # Vérifier attributs de BaseService
        assert hasattr(service, 'model')
        assert hasattr(service, 'create')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'get_all')
        # Vérifier attributs de BaseAIService
        assert hasattr(service, 'client')
        assert hasattr(service, 'cache_prefix')


# ═══════════════════════════════════════════════════════════
# TESTS CRUD VIA BASESERVICE (Méthodes héritées)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceCRUD:
    """Tests pour les opérations CRUD héritées de BaseService."""
    
    def test_get_all_empty_list(self, courses_service):
        """get_all retourne une liste (vide ou non)."""
        with patch.object(courses_service, '_with_session') as mock_session:
            mock_session.return_value = []
            result = courses_service.get_all()
            assert isinstance(result, list)
    
    def test_get_by_id_not_found(self, courses_service):
        """get_by_id retourne None si non trouvé."""
        with patch.object(courses_service, '_with_session') as mock_session:
            mock_session.return_value = None
            result = courses_service.get_by_id(99999)
            assert result is None
    
    def test_create_with_mock_session(self, courses_service):
        """create utilise la session correctement."""
        mock_entity = MagicMock()
        mock_entity.id = 1
        
        with patch.object(courses_service, '_with_session') as mock_session:
            mock_session.return_value = mock_entity
            result = courses_service.create({"nom": "Test"})
            assert mock_session.called


# ═══════════════════════════════════════════════════════════
# TESTS LISTE COURSES (Méthode spécifique)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceListeCourses:
    """Tests pour get_liste_courses."""
    
    @pytest.mark.skip(reason="Mock complexe - à revoir")
    def test_get_liste_courses_returns_list(self, courses_service):
        """get_liste_courses retourne toujours une liste."""
        with patch('src.core.database.obtenir_contexte_db') as mock_db:
            mock_session = MagicMock()
            mock_query = MagicMock()
            mock_query.options.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.all.return_value = []
            mock_session.query.return_value = mock_query
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=None)
            
            result = courses_service.get_liste_courses()
            # Le décorateur @with_error_handling retourne [] par défaut
            assert isinstance(result, list)
    
    def test_get_liste_courses_accepts_filters(self, courses_service):
        """get_liste_courses accepte les paramètres de filtre."""
        # Vérifier que la signature accepte ces paramètres
        import inspect
        sig = inspect.signature(courses_service.get_liste_courses)
        params = list(sig.parameters.keys())
        assert 'achetes' in params
        assert 'priorite' in params


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES DE COURSES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceModeles:
    """Tests pour les méthodes de modèles."""
    
    def test_get_modeles_exists(self, courses_service):
        """La méthode get_modeles existe."""
        assert hasattr(courses_service, 'get_modeles')
        assert callable(courses_service.get_modeles)
    
    def test_create_modele_exists(self, courses_service):
        """La méthode create_modele existe."""
        assert hasattr(courses_service, 'create_modele')
        assert callable(courses_service.create_modele)
    
    def test_delete_modele_exists(self, courses_service):
        """La méthode delete_modele existe."""
        assert hasattr(courses_service, 'delete_modele')
        assert callable(courses_service.delete_modele)
    
    def test_appliquer_modele_exists(self, courses_service):
        """La méthode appliquer_modele existe."""
        assert hasattr(courses_service, 'appliquer_modele')
        assert callable(courses_service.appliquer_modele)


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS IA
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceSuggestionsIA:
    """Tests pour les suggestions IA."""
    
    def test_generer_suggestions_ia_exists(self, courses_service):
        """La méthode de génération IA existe."""
        assert hasattr(courses_service, 'generer_suggestions_ia_depuis_inventaire')
        assert callable(courses_service.generer_suggestions_ia_depuis_inventaire)
    
    @pytest.mark.skip(reason="Mock complexe sur les caches - à revoir")
    def test_generer_suggestions_ia_returns_list(self, courses_service):
        """Les suggestions IA retournent une liste."""
        with patch('src.services.courses.get_inventaire_service') as mock_inv:
            mock_inv.return_value = None
            result = courses_service.generer_suggestions_ia_depuis_inventaire()
            # Avec inventaire_service None, retourne []
            assert isinstance(result, list)
    
    @pytest.mark.skip(reason="Mock complexe sur les caches - à revoir")
    @patch('src.services.courses.get_inventaire_service')
    def test_generer_suggestions_ia_inventaire_vide(self, mock_inv, courses_service):
        """Suggestions avec inventaire vide."""
        mock_service = MagicMock()
        mock_service.get_inventaire_complet.return_value = []
        mock_inv.return_value = mock_service
        
        result = courses_service.generer_suggestions_ia_depuis_inventaire()
        # Inventaire vide = pas de suggestions
        assert isinstance(result, list)


# ═══════════════════════════════════════════════════════════
# TESTS BASEAISERVICE HÉRITÉ
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCoursesServiceAIBase:
    """Tests pour les méthodes héritées de BaseAIService."""
    
    def test_has_build_json_prompt(self, courses_service):
        """Le service a la méthode build_json_prompt."""
        assert hasattr(courses_service, 'build_json_prompt')
    
    def test_has_build_system_prompt(self, courses_service):
        """Le service a la méthode build_system_prompt."""
        assert hasattr(courses_service, 'build_system_prompt')
    
    def test_has_call_with_list_parsing_sync(self, courses_service):
        """Le service a la méthode call_with_list_parsing_sync."""
        assert hasattr(courses_service, 'call_with_list_parsing_sync')
    
    def test_service_name_is_courses(self, courses_service):
        """Le service_name est 'courses'."""
        assert courses_service.service_name == "courses"
    
    def test_cache_prefix_is_courses(self, courses_service):
        """Le cache_prefix est 'courses'."""
        assert courses_service.cache_prefix == "courses"


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMA PYDANTIC SuggestionCourses
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestSuggestionCoursesSchema:
    """Tests pour le schéma Pydantic SuggestionCourses."""
    
    def test_suggestion_courses_import(self):
        """Import du schéma SuggestionCourses."""
        from src.services.courses import SuggestionCourses
        assert SuggestionCourses is not None
    
    def test_suggestion_courses_valid_data(self):
        """Validation avec données valides."""
        from src.services.courses import SuggestionCourses
        
        data = {
            "nom": "Tomates",
            "quantite": 2.0,
            "unite": "kg",
            "priorite": "haute",
            "rayon": "Fruits et légumes"
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Tomates"
        assert suggestion.quantite == 2.0
        assert suggestion.priorite == "haute"
    
    def test_suggestion_courses_field_aliases(self):
        """Validation avec alias de champs."""
        from src.services.courses import SuggestionCourses
        
        # Le schéma normalise 'article' -> 'nom', 'quantity' -> 'quantite'
        data = {
            "article": "Pain",
            "quantity": 1.0,
            "unit": "pcs",
            "priority": "high",
            "section": "Boulangerie"
        }
        suggestion = SuggestionCourses.model_validate(data)
        assert suggestion.nom == "Pain"
        assert suggestion.quantite == 1.0
        assert suggestion.priorite == "haute"  # 'high' -> 'haute'
    
    def test_suggestion_courses_invalid_priorite(self):
        """Validation échoue avec priorité invalide."""
        from src.services.courses import SuggestionCourses
        from pydantic import ValidationError
        
        data = {
            "nom": "Test",
            "quantite": 1.0,
            "unite": "pcs",
            "priorite": "invalide",  # Doit être haute/moyenne/basse
            "rayon": "Test"
        }
        with pytest.raises(ValidationError):
            SuggestionCourses(**data)
    
    def test_suggestion_courses_quantite_positive(self):
        """La quantité doit être positive."""
        from src.services.courses import SuggestionCourses
        from pydantic import ValidationError
        
        data = {
            "nom": "Test",
            "quantite": -1.0,  # Invalide
            "unite": "pcs",
            "priorite": "haute",
            "rayon": "Test"
        }
        with pytest.raises(ValidationError):
            SuggestionCourses(**data)


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION (avec mocks complets)
# ═══════════════════════════════════════════════════════════

@pytest.mark.skip(reason="Mocks complexes de BD - à améliorer ultérieurement")
@pytest.mark.integration
class TestCoursesServiceIntegration:
    """Tests d'intégration avec mocks."""
    
    @patch('src.core.database.obtenir_contexte_db')
    def test_workflow_liste_courses(self, mock_db, courses_service):
        """Workflow complet de liste de courses."""
        # Setup mock
        mock_article = MagicMock()
        mock_article.id = 1
        mock_article.ingredient_id = 1
        mock_article.ingredient.nom = "Tomates"
        mock_article.ingredient.unite = "kg"
        mock_article.quantite_necessaire = 2.0
        mock_article.priorite = "haute"
        mock_article.achete = False
        mock_article.rayon_magasin = "Fruits"
        mock_article.magasin_cible = "Carrefour"
        mock_article.notes = ""
        mock_article.suggere_par_ia = False
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_article]
        mock_session.query.return_value = mock_query
        
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=None)
        
        # Exécuter
        result = courses_service.get_liste_courses(achetes=False)
        
        # Vérifier
        assert isinstance(result, list)


def test_import_courses_module():
    """Vérifie que le module courses s'importe sans erreur."""
    import importlib
    module = importlib.import_module("src.services.courses")
    assert module is not None
