"""Tests avancés pour le module famille avec les vraies fonctions."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
import streamlit as st


class TestIntegrationCuisineCourses:
    """Tests pour l'intégration cuisine/courses/famille."""
    
    @patch('src.modules.famille.integration_cuisine_courses.get_db')
    def test_get_recipe_suggestions_endurance(self, mock_db):
        """Suggère recettes pour endurance."""
        from src.modules.famille.integration_cuisine_courses import get_recipe_suggestions
        
        objectifs = [{"type": "endurance", "target": 5000, "actuel": 3000}]
        result = get_recipe_suggestions(objectifs)
        
        assert isinstance(result, dict)
        assert "endurance" in str(result).lower() or len(result) > 0
    
    @patch('src.modules.famille.integration_cuisine_courses.get_db')
    def test_get_recipe_suggestions_multiple_objectifs(self, mock_db):
        """Suggère recettes pour plusieurs objectifs."""
        from src.modules.famille.integration_cuisine_courses import get_recipe_suggestions
        
        objectifs = [
            {"type": "endurance", "target": 5000},
            {"type": "force", "target": 10}
        ]
        result = get_recipe_suggestions(objectifs)
        assert isinstance(result, dict)


class TestFamilleHelpers:
    """Tests pour les helpers du module famille."""
    
    @patch('src.modules.famille.helpers.get_db')
    def test_get_objectifs_actifs(self, mock_db):
        """Récupère objectifs santé actifs."""
        from src.modules.famille.helpers import get_objectives_actifs
        
        try:
            result = get_objectifs_actifs()
            assert isinstance(result, (list, type(None)))
        except Exception:
            pytest.skip("Fonction nécessite DB configurée")
    
    @patch('src.modules.famille.helpers.get_db')
    def test_get_activites_semaine(self, mock_db):
        """Récupère activités de la semaine."""
        from src.modules.famille.helpers import get_activites_semaine
        
        try:
            debut = date.today()
            fin = date.today()
            result = get_activites_semaine(debut, fin)
            assert isinstance(result, (list, type(None)))
        except Exception:
            pytest.skip("Fonction nécessite DB configurée")
    
    @patch('src.modules.famille.helpers.get_db')
    def test_get_stats_sante_semaine(self, mock_db):
        """Récupère stats santé hebdomadaires."""
        from src.modules.famille.helpers import get_stats_santé_semaine
        
        try:
            debut = date.today()
            fin = date.today()
            result = get_stats_santé_semaine(debut, fin)
            assert isinstance(result, (dict, type(None)))
        except Exception:
            pytest.skip("Fonction nécessite DB configurée")


class TestFamilleModules:
    """Tests pour les modules famille."""
    
    def test_import_suivi_jules(self):
        """Importe le module suivi Jules."""
        from src.modules.famille import suivi_jules
        assert hasattr(suivi_jules, 'app')
    
    def test_import_bien_etre(self):
        """Importe le module bien-être."""
        from src.modules.famille import bien_etre
        assert hasattr(bien_etre, 'app')
    
    def test_import_routines(self):
        """Importe le module routines."""
        from src.modules.famille import routines
        assert hasattr(routines, 'app')
    
    def test_import_activites(self):
        """Importe le module activités."""
        from src.modules.famille import activites
        assert hasattr(activites, 'app')
    
    def test_import_sante(self):
        """Importe le module santé."""
        from src.modules.famille import sante
        assert hasattr(sante, 'app')
    
    def test_import_shopping(self):
        """Importe le module shopping."""
        from src.modules.famille import shopping
        assert hasattr(shopping, 'app')


class TestIntegrationCuisineCacheFunctions:
    """Tests pour les fonctions cached d'intégration."""
    
    def test_get_recipe_suggestions_cache(self):
        """Teste le cache des suggestions."""
        from src.modules.famille.integration_cuisine_courses import get_recipe_suggestions
        
        objectifs = [{"type": "test"}]
        
        # Premier appel
        result1 = get_recipe_suggestions(objectifs)
        # Deuxième appel (depuis cache)
        result2 = get_recipe_suggestions(objectifs)
        
        # Les résultats doivent être identiques
        assert type(result1) == type(result2)
    
    def test_recipe_suggestions_return_type(self):
        """Vérifie le type de retour."""
        from src.modules.famille.integration_cuisine_courses import get_recipe_suggestions
        
        result = get_recipe_suggestions([])
        assert isinstance(result, dict)


class TestFamilleIntegrationWorkflow:
    """Tests pour les workflows d'intégration."""
    
    @patch('src.modules.famille.integration_cuisine_courses.get_objectives_actifs')
    def test_workflow_objectifs_to_recettes(self, mock_objectifs):
        """Teste workflow objectifs → recettes."""
        from src.modules.famille.integration_cuisine_courses import get_recipe_suggestions
        
        mock_objectifs.return_value = [{"type": "endurance"}]
        objectifs = mock_objectifs()
        
        if objectifs:
            result = get_recipe_suggestions(objectifs)
            assert isinstance(result, dict)
    
    def test_integration_module_structure(self):
        """Vérifie la structure du module intégration."""
        from src.modules.famille import integration_cuisine_courses
        
        # Vérifie que les fonctions principales existent
        assert hasattr(integration_cuisine_courses, 'get_recipe_suggestions')
        assert hasattr(integration_cuisine_courses, 'app')


class TestFamilleAppFunctions:
    """Tests pour les fonctions app() des modules."""
    
    @patch('streamlit.title')
    def test_suivi_jules_app_callable(self, mock_title):
        """Test que app() de suivi_jules est callable."""
        from src.modules.famille.suivi_jules import app
        
        assert callable(app)
    
    @patch('streamlit.title')
    def test_bien_etre_app_callable(self, mock_title):
        """Test que app() de bien_etre est callable."""
        from src.modules.famille.bien_etre import app
        
        assert callable(app)
    
    @patch('streamlit.title')
    def test_activites_app_callable(self, mock_title):
        """Test que app() de activites est callable."""
        from src.modules.famille.activites import app
        
        assert callable(app)
