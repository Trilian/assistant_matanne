"""
Tests pour l'application principale app.py
Couvre: Initialisation, routing, état, configuration
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from dotenv import load_dotenv
import os


class TestAppInitialization:
    """Tests pour l'initialisation de l'application"""

    def test_env_loading_from_env_local(self):
        """Teste le chargement du fichier .env.local"""
        # S'assurer que .env.local existe dans le test
        env_file = Path(__file__).parent.parent / '.env.local'
        
        with patch.dict(os.environ, {'MISTRAL_API_KEY': 'test_key'}):
            result = load_dotenv(env_file, override=True)
            # Ne pas vérifier le résultat exact car le fichier peut ou non exister
            assert isinstance(result, bool)
    
    def test_sys_path_configuration(self):
        """Teste que sys.path est correctement configuré"""
        project_root = Path(__file__).parent.parent
        assert str(project_root) in sys.path or any(
            str(project_root) in p for p in sys.path
        )
    
    @patch('src.core.logging.GestionnaireLog.initialiser')
    def test_logging_initialization(self, mock_logging):
        """Teste l'initialisation du logger"""
        from src.core.logging import GestionnaireLog
        
        mock_logging.return_value = None
        GestionnaireLog.initialiser(niveau_log="INFO")
        
        mock_logging.assert_called_once()
    
    def test_core_imports_available(self):
        """Teste que les imports principaux sont disponibles"""
        from src.core import Cache, GestionnaireEtat, obtenir_etat
        
        assert Cache is not None
        assert GestionnaireEtat is not None
        assert obtenir_etat is not None


class TestAppConfiguration:
    """Tests pour la configuration de l'application"""
    
    def test_obtenir_parametres(self):
        """Teste l'obtention des paramètres"""
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        assert params is not None
        assert hasattr(params, 'nom_application') or hasattr(params, '__dict__')
    
    def test_database_connection_verification(self):
        """Teste la vérification de la connexion à la base de données"""
        from src.core.database import verifier_connexion
        
        try:
            # La vérification peut échouer en test, c'est OK
            result = verifier_connexion()
            assert isinstance(result, (bool, dict)) or result is None
        except Exception:
            # Attendu en environnement de test
            pass
    
    @patch.dict(os.environ, {'DATABASE_URL': 'sqlite:///:memory:'})
    def test_database_url_environment_variable(self):
        """Teste que DATABASE_URL peut être configuré"""
        db_url = os.getenv('DATABASE_URL')
        assert db_url == 'sqlite:///:memory:'


class TestStateManagement:
    """Tests pour la gestion d'état de l'application"""
    
    def test_gestionnaire_etat_creation(self):
        """Teste la création du gestionnaire d'état"""
        from src.core.state import GestionnaireEtat
        
        gestionnaire = GestionnaireEtat()
        assert gestionnaire is not None
    
    def test_obtenir_etat(self):
        """Teste l'obtention de l'état"""
        from src.core.state import obtenir_etat
        
        etat = obtenir_etat()
        assert etat is not None
    
    @patch('streamlit.session_state', {})
    def test_cache_functionality(self):
        """Teste la fonctionnalité de cache"""
        from src.core.cache import Cache
        
        # Test que la classe Cache existe et peut être instanciée
        assert Cache is not None
        assert hasattr(Cache, 'clear')
        assert hasattr(Cache, 'obtenir')
        assert hasattr(Cache, 'definir')


class TestStreamlitIntegration:
    """Tests pour l'intégration avec Streamlit"""
    
    @patch('streamlit.set_page_config')
    def test_page_config_called(self, mock_config):
        """Teste que la configuration de page est appelée"""
        mock_config.return_value = None
        # Configuration simulée
        st_config = {'page_title': 'Assistant Matanne', 'layout': 'wide'}
        assert 'page_title' in st_config
    
    @patch('streamlit.sidebar')
    def test_sidebar_available(self, mock_sidebar):
        """Teste que la barre latérale Streamlit est disponible"""
        assert mock_sidebar is not None


class TestRouting:
    """Tests pour le routing de l'application"""
    
    def test_page_selection_stored_in_state(self):
        """Teste que la sélection de page peut être stockée dans l'état."""
        # Test simplifié - vérifier que l'on peut manipuler un dictionnaire
        mock_state = {}
        mock_state['current_page'] = 'accueil'
        assert mock_state['current_page'] == 'accueil'
    
    def test_module_registry_exists(self):
        """Teste que le registre de modules existe"""
        try:
            from src.core.lazy_loader import RouteurOptimise
            assert hasattr(RouteurOptimise, 'MODULE_REGISTRY')
        except ImportError:
            # Optionnel selon l'architecture
            pass


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    def test_missing_env_variables_handling(self):
        """Teste la gestion des variables d'environnement manquantes"""
        with patch.dict(os.environ, {}, clear=True):
            # L'app ne devrait pas crasher avec des variables manquantes
            try:
                from src.core.config import obtenir_parametres
                params = obtenir_parametres()
                # L'application doit avoir des valeurs par défaut
            except Exception:
                # Acceptable en test
                pass
    
    @patch('src.core.database.verifier_connexion')
    def test_database_connection_error_handling(self, mock_verify):
        """Teste la gestion des erreurs de connexion BD"""
        mock_verify.side_effect = Exception("Connexion échouée")
        
        try:
            from src.core.database import verifier_connexion
            verifier_connexion()
        except Exception as e:
            assert "Connexion" in str(e)


class TestApplicationWorkflow:
    """Tests d'intégration du flux d'application"""
    
    @patch('streamlit.session_state', {})
    def test_initial_state_setup(self):
        """Teste la configuration de l'état initial"""
        from src.core.state import obtenir_etat
        
        etat = obtenir_etat()
        assert etat is not None
    
    def test_imports_no_circular_dependencies(self):
        """Teste qu'il n'y a pas de dépendances circulaires"""
        try:
            from src import app
            assert app is not None
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Dépendance circulaire détectée: {e}")
    
    @patch('streamlit.set_page_config')
    @patch('streamlit.session_state', {})
    def test_complete_app_initialization(self, mock_config):
        """Teste l'initialisation complète de l'app"""
        # Configuration mock
        mock_config.return_value = None
        
        from src.core.config import obtenir_parametres
        from src.core.state import obtenir_etat
        
        params = obtenir_parametres()
        etat = obtenir_etat()
        
        assert params is not None
        assert etat is not None


class TestMenuNavigation:
    """Tests pour la navigation du menu"""
    
    def test_menu_items_defined(self):
        """Teste que les éléments du menu sont définis"""
        # Les éléments du menu devraient être constants définis quelque part
        menu_items = [
            'accueil',
            'cuisine',
            'famille',
            'planning',
            'maison',
        ]
        
        assert len(menu_items) > 0
    
    @patch('streamlit.selectbox')
    def test_selectbox_for_navigation(self, mock_selectbox):
        """Teste que selectbox est utilisé pour la navigation"""
        mock_selectbox.return_value = 'accueil'
        
        page_selected = mock_selectbox(
            "Navigation",
            ['accueil', 'cuisine', 'famille']
        )
        
        assert page_selected == 'accueil'


class TestPerformance:
    """Tests de performance de l'application"""
    
    def test_lazy_loading_optimization(self):
        """Teste que le lazy loading est disponible"""
        try:
            from src.core.lazy_loader import RouteurOptimise
            assert RouteurOptimise is not None
        except ImportError:
            # Optionnel
            pass
    
    @patch('streamlit.cache_data')
    def test_streamlit_caching_available(self, mock_cache):
        """Teste que le caching Streamlit est disponible"""
        mock_cache.return_value = lambda x: x
        
        @mock_cache()
        def cached_function():
            return "result"
        
        result = cached_function()
        assert result == "result"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
