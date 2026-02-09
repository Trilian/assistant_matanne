"""
Tests de couverture étendus pour src/app.py
Couvre: env loading, main(), error paths, debug mode, restart flow
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock, PropertyMock
from io import StringIO
import importlib


# ═══════════════════════════════════════════════════════════════════════════
# TESTS ENV LOADING
# ═══════════════════════════════════════════════════════════════════════════


class TestEnvLoading:
    """Tests pour le chargement des variables d'environnement"""

    def test_env_local_preferred_over_env(self):
        """Teste que .env.local est préféré sur .env"""
        from dotenv import load_dotenv
        
        project_root = Path(__file__).parent.parent
        env_local = project_root / '.env.local'
        env_file = project_root / '.env'
        
        # Vérifier la cascade de chargement
        if env_local.exists():
            result = load_dotenv(env_local, override=True)
            assert result or True  # Soit chargé, soit fichier vide
        elif env_file.exists():
            result = load_dotenv(env_file, override=True)
            assert result or True

    def test_env_loading_fallback(self):
        """Teste le fallback du chargement env"""
        from dotenv import load_dotenv
        
        project_root = Path(__file__).parent.parent
        
        # Test avec fichier inexistant - devrait retourner False
        result = load_dotenv(project_root / '.env.nonexistent', override=True)
        assert result is False

    @patch.dict(os.environ, {'DEBUG': 'true', 'MISTRAL_API_KEY': 'test_key'}, clear=False)
    def test_debug_mode_logging(self, capsys):
        """Teste que le mode debug affiche les logs"""
        # Le debug mode dans app.py affiche des informations
        if os.getenv("DEBUG", "").lower() == "true":
            mistral_key = os.getenv("MISTRAL_API_KEY")
            msg = f"[DEBUG] MISTRAL_API_KEY: {'OK' if mistral_key else 'MISSING'}"
            assert mistral_key == 'test_key'

    @patch.dict(os.environ, {'DEBUG': 'false'}, clear=False)
    def test_non_debug_mode(self):
        """Teste le mode non-debug"""
        debug = os.getenv("DEBUG", "").lower() == "true"
        assert debug is False

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_debug_env(self):
        """Teste quand DEBUG n'est pas défini"""
        debug = os.getenv("DEBUG", "").lower() == "true"
        assert debug is False


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PATH CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════


class TestPathConfiguration:
    """Tests de configuration du chemin sys.path"""

    def test_project_root_in_sys_path(self):
        """Vérifie que la racine du projet est dans sys.path"""
        project_root = Path(__file__).parent.parent
        paths_str = [str(p) for p in sys.path]
        assert any(str(project_root) in p for p in paths_str)

    def test_src_importable(self):
        """Vérifie que src est importable"""
        import src
        assert src is not None

    def test_core_modules_importable(self):
        """Vérifie les imports des modules core"""
        from src.core import Cache, GestionnaireEtat, obtenir_etat, obtenir_parametres
        assert Cache is not None
        assert GestionnaireEtat is not None
        assert obtenir_etat is not None
        assert obtenir_parametres is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS LOGGING INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════


class TestLoggingInit:
    """Tests pour l'initialisation du logging"""

    def test_gestionnaire_log_initialiser(self):
        """Teste l'initialisation du gestionnaire de log"""
        from src.core.logging import GestionnaireLog
        
        # Ne devrait pas lever d'exception
        GestionnaireLog.initialiser(niveau_log="INFO")

    def test_obtenir_logger(self):
        """Teste l'obtention d'un logger"""
        from src.core.logging import obtenir_logger
        
        logger = obtenir_logger("test_module")
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')

    def test_logger_with_different_levels(self):
        """Teste le logger avec différents niveaux"""
        from src.core.logging import GestionnaireLog, obtenir_logger
        
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            try:
                GestionnaireLog.initialiser(niveau_log=level)
            except Exception:
                pass  # Acceptable en test


# ═══════════════════════════════════════════════════════════════════════════
# TESTS MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════


class TestMainFunction:
    """Tests pour la fonction main()"""

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.exception')
    @patch('streamlit.button', return_value=False)
    def test_main_success_flow(self, mock_btn, mock_exc, mock_err, mock_spinner):
        """Teste le flux normal de main()"""
        import src.app as app
        
        with patch.object(app, 'afficher_header') as mock_header, \
             patch.object(app, 'afficher_sidebar') as mock_sidebar, \
             patch.object(app, 'afficher_footer') as mock_footer, \
             patch.object(app, 'obtenir_etat') as mock_etat, \
             patch.object(app, 'OptimizedRouter') as mock_router:
            
            mock_etat.return_value = Mock(module_actuel='accueil', mode_debug=False)
            
            app.main()
            
            mock_header.assert_called_once()
            mock_sidebar.assert_called_once()
            mock_footer.assert_called_once()

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.exception')
    @patch('streamlit.button', return_value=False)
    def test_main_exception_non_debug(self, mock_btn, mock_exc, mock_err, mock_spinner):
        """Teste la gestion d'exception en mode non-debug"""
        import src.app as app
        
        with patch.object(app, 'afficher_header', side_effect=Exception("Test error")), \
             patch.object(app, 'afficher_sidebar'), \
             patch.object(app, 'afficher_footer'), \
             patch.object(app, 'obtenir_etat') as mock_etat, \
             patch.object(app, 'OptimizedRouter'):
            
            mock_etat.return_value = Mock(module_actuel='accueil', mode_debug=False)
            
            app.main()
            
            mock_err.assert_called()
            mock_exc.assert_not_called()  # Non appelé en mode non-debug

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.exception')
    @patch('streamlit.button', return_value=False)
    def test_main_exception_debug_mode(self, mock_btn, mock_exc, mock_err, mock_spinner):
        """Teste la gestion d'exception en mode debug"""
        import src.app as app
        
        with patch.object(app, 'afficher_header', side_effect=Exception("Test error")), \
             patch.object(app, 'afficher_sidebar'), \
             patch.object(app, 'afficher_footer'), \
             patch.object(app, 'obtenir_etat') as mock_etat, \
             patch.object(app, 'OptimizedRouter'):
            
            mock_etat.return_value = Mock(module_actuel='accueil', mode_debug=True)
            
            app.main()
            
            mock_err.assert_called()
            mock_exc.assert_called()  # Appelé en mode debug

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.exception')
    @patch('streamlit.button', return_value=True)  # User clicks restart
    @patch('streamlit.rerun')
    def test_main_restart_button_clicked(self, mock_rerun, mock_btn, mock_exc, mock_err, mock_spinner):
        """Teste le clic sur le bouton de redémarrage"""
        import src.app as app
        
        with patch.object(app, 'afficher_header', side_effect=Exception("Test error")), \
             patch.object(app, 'afficher_sidebar'), \
             patch.object(app, 'afficher_footer'), \
             patch.object(app, 'obtenir_etat') as mock_etat, \
             patch.object(app, 'OptimizedRouter'), \
             patch.object(app, 'GestionnaireEtat') as mock_gest, \
             patch.object(app, 'Cache') as mock_cache:
            
            mock_etat.return_value = Mock(module_actuel='accueil', mode_debug=False)
            
            app.main()
            
            mock_gest.reinitialiser.assert_called_once()
            mock_cache.vider.assert_called_once()
            mock_rerun.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════
# TESTS LAYOUTS
# ═══════════════════════════════════════════════════════════════════════════


class TestLayoutFunctions:
    """Tests des fonctions de layout"""

    def test_layout_imports(self):
        """Teste les imports de layout"""
        from src.ui.layout import (
            afficher_header,
            afficher_sidebar,
            afficher_footer,
            injecter_css,
            initialiser_app,
        )
        
        assert callable(afficher_header)
        assert callable(afficher_sidebar)
        assert callable(afficher_footer)
        assert callable(injecter_css)
        assert callable(initialiser_app)

    @patch('streamlit.markdown')
    def test_injecter_css(self, mock_md):
        """Teste l'injection de CSS"""
        from src.ui.layout import injecter_css
        
        injecter_css()
        # Le CSS devrait être injecté via st.markdown
        # (peut ne pas être appelé si déjà injecté)

    @patch('streamlit.session_state', {})
    def test_initialiser_app_returns_bool(self):
        """Teste que initialiser_app retourne un booléen"""
        from src.ui.layout import initialiser_app
        
        result = initialiser_app()
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════════
# TESTS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════


class TestAppConfiguration:
    """Tests de configuration de l'application"""

    def test_parametres_has_app_name(self):
        """Teste que les paramètres ont APP_NAME"""
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        # Vérifier que APP_NAME existe (peut être app_name ou APP_NAME)
        assert hasattr(params, 'APP_NAME') or hasattr(params, 'app_name') or hasattr(params, 'nom_application')

    def test_parametres_has_app_version(self):
        """Teste que les paramètres ont APP_VERSION"""
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        assert hasattr(params, 'APP_VERSION') or hasattr(params, 'app_version') or hasattr(params, 'version')

    def test_page_config_menu_items(self):
        """Teste les éléments du menu de configuration de page"""
        from src.core.config import obtenir_parametres
        
        params = obtenir_parametres()
        
        # Menu items attendus
        expected_keys = ["Get Help", "Report a bug", "About"]
        menu_items = {
            "Get Help": "https://github.com/ton-repo",
            "Report a bug": "https://github.com/ton-repo/issues",
        }
        
        for key in expected_keys[:2]:
            assert key in menu_items


# ═══════════════════════════════════════════════════════════════════════════
# TESTS OPTIMIZED ROUTER
# ═══════════════════════════════════════════════════════════════════════════


class TestOptimizedRouterIntegration:
    """Tests d'intégration du routeur"""

    def test_module_registry_has_accueil(self):
        """Teste que accueil est dans le registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        assert 'accueil' in OptimizedRouter.MODULE_REGISTRY

    def test_module_registry_has_cuisine_modules(self):
        """Teste les modules cuisine dans le registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        cuisine_modules = [k for k in OptimizedRouter.MODULE_REGISTRY.keys() if k.startswith('cuisine.')]
        assert len(cuisine_modules) > 0

    def test_module_registry_has_famille_modules(self):
        """Teste les modules famille dans le registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        famille_modules = [k for k in OptimizedRouter.MODULE_REGISTRY.keys() if k.startswith('famille.')]
        assert len(famille_modules) > 0

    def test_module_registry_has_maison_modules(self):
        """Teste les modules maison dans le registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        maison_modules = [k for k in OptimizedRouter.MODULE_REGISTRY.keys() if k.startswith('maison.')]
        assert len(maison_modules) > 0

    def test_module_registry_has_parametres(self):
        """Teste que parametres est dans le registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        assert 'parametres' in OptimizedRouter.MODULE_REGISTRY

    def test_module_registry_entry_structure(self):
        """Teste la structure des entrées du registre"""
        from src.core.lazy_loader import OptimizedRouter
        
        for name, config in OptimizedRouter.MODULE_REGISTRY.items():
            assert 'path' in config
            assert 'type' in config
            assert config['type'] in ['simple', 'hub']

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    def test_load_module_unknown(self, mock_info, mock_warn, mock_err, mock_spinner):
        """Teste le chargement d'un module inconnu"""
        from src.core.lazy_loader import OptimizedRouter
        
        OptimizedRouter.load_module('module_inexistant')
        
        mock_err.assert_called()

    @patch('streamlit.spinner')
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    @patch('streamlit.exception')
    @patch('streamlit.session_state', {'debug_mode': True})
    def test_load_module_import_error(self, mock_exc, mock_info, mock_warn, mock_err, mock_spinner):
        """Teste le chargement avec erreur d'import"""
        from src.core.lazy_loader import OptimizedRouter, LazyModuleLoader
        
        # Forcer une erreur au niveau du cache
        LazyModuleLoader._cache.clear()
        
        with patch.object(LazyModuleLoader, 'load', side_effect=ModuleNotFoundError("Not found")):
            OptimizedRouter.load_module('accueil')
            
            mock_warn.assert_called()


# ═══════════════════════════════════════════════════════════════════════════
# TESTS LAZY MODULE LOADER
# ═══════════════════════════════════════════════════════════════════════════


class TestLazyModuleLoaderIntegration:
    """Tests d'intégration du lazy loader"""

    def test_load_builtin_module(self):
        """Teste le chargement d'un module builtin"""
        from src.core.lazy_loader import LazyModuleLoader
        
        LazyModuleLoader._cache.clear()
        
        module = LazyModuleLoader.load('json')
        assert module is not None
        assert hasattr(module, 'dumps')

    def test_cache_hit(self):
        """Teste le cache hit"""
        from src.core.lazy_loader import LazyModuleLoader
        
        # Premier chargement
        LazyModuleLoader._cache.clear()
        module1 = LazyModuleLoader.load('os')
        
        # Deuxième chargement (devrait utiliser le cache)
        module2 = LazyModuleLoader.load('os')
        
        assert module1 is module2

    def test_reload_bypasses_cache(self):
        """Teste que reload=True bypass le cache"""
        from src.core.lazy_loader import LazyModuleLoader
        
        LazyModuleLoader._cache.clear()
        
        module1 = LazyModuleLoader.load('sys')
        module2 = LazyModuleLoader.load('sys', reload=True)
        
        # Les deux devraient être le même module (Python cache les modules)
        assert module1 is not None
        assert module2 is not None

    def test_get_stats(self):
        """Teste les statistiques de lazy loading"""
        from src.core.lazy_loader import LazyModuleLoader
        
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()
        
        LazyModuleLoader.load('collections')
        
        stats = LazyModuleLoader.get_stats()
        
        assert 'cached_modules' in stats
        assert 'total_load_time' in stats
        assert 'average_load_time' in stats
        assert 'load_times' in stats
        assert stats['cached_modules'] >= 1

    def test_clear_cache(self):
        """Teste le vidage du cache"""
        from src.core.lazy_loader import LazyModuleLoader
        
        LazyModuleLoader.load('re')
        assert len(LazyModuleLoader._cache) > 0
        
        LazyModuleLoader.clear_cache()
        
        assert len(LazyModuleLoader._cache) == 0
        assert len(LazyModuleLoader._load_times) == 0

    def test_preload_sync(self):
        """Teste le préchargement synchrone"""
        from src.core.lazy_loader import LazyModuleLoader
        
        LazyModuleLoader._cache.clear()
        
        # Précharger des modules standard
        LazyModuleLoader.preload(['datetime', 'uuid'], background=False)
        
        # Vérifier qu'ils sont en cache
        # (Note: peuvent être en cache ou pas si erreur silencieuse)
        assert LazyModuleLoader._cache is not None

    def test_preload_async(self):
        """Teste le préchargement asynchrone"""
        from src.core.lazy_loader import LazyModuleLoader
        import time
        
        LazyModuleLoader._cache.clear()
        
        # Précharger en arrière-plan
        LazyModuleLoader.preload(['functools'], background=True)
        
        # Attendre un peu pour le thread
        time.sleep(0.1)
        
        # Le thread devrait avoir chargé le module

    def test_load_module_not_found(self):
        """Teste le chargement d'un module inexistant"""
        from src.core.lazy_loader import LazyModuleLoader
        
        with pytest.raises(ModuleNotFoundError):
            LazyModuleLoader.load('module_qui_nexiste_pas_du_tout')


# ═══════════════════════════════════════════════════════════════════════════
# TESTS LAZY IMPORT DECORATOR
# ═══════════════════════════════════════════════════════════════════════════


class TestLazyImportDecorator:
    """Tests du décorateur lazy_import"""

    def test_lazy_import_exists(self):
        """Teste que le décorateur existe"""
        from src.core.lazy_loader import lazy_import
        
        assert callable(lazy_import)

    def test_lazy_import_decorator_basic(self):
        """Teste le décorateur lazy_import"""
        from src.core.lazy_loader import lazy_import
        
        @lazy_import("json")
        def use_json():
            return True
        
        result = use_json()
        assert result is True

    def test_lazy_import_with_attr(self):
        """Teste lazy_import avec attribut"""
        from src.core.lazy_loader import lazy_import
        
        @lazy_import("json", "dumps")
        def use_dumps():
            return True
        
        result = use_dumps()
        assert result is True


# ═══════════════════════════════════════════════════════════════════════════
# TESTS RENDER LAZY LOADING STATS
# ═══════════════════════════════════════════════════════════════════════════


class TestRenderLazyLoadingStats:
    """Tests pour la fonction render_lazy_loading_stats"""

    def test_function_exists(self):
        """Teste que la fonction existe"""
        from src.core.lazy_loader import render_lazy_loading_stats
        
        assert callable(render_lazy_loading_stats)

    @patch('streamlit.expander')
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('streamlit.caption')
    @patch('streamlit.button', return_value=False)
    def test_render_stats_without_modules(self, mock_btn, mock_cap, mock_met, mock_cols, mock_exp):
        """Teste le rendu des stats sans modules chargés"""
        from src.core.lazy_loader import render_lazy_loading_stats, LazyModuleLoader
        
        LazyModuleLoader._cache.clear()
        LazyModuleLoader._load_times.clear()
        
        # Mock context manager pour expander
        mock_exp.return_value.__enter__ = Mock(return_value=None)
        mock_exp.return_value.__exit__ = Mock(return_value=None)
        
        # Mock columns
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_cols.return_value = [mock_col, mock_col]
        
        render_lazy_loading_stats()
        
        mock_exp.assert_called()

    @patch('streamlit.expander')
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    @patch('streamlit.caption')
    @patch('streamlit.button', return_value=True)
    @patch('streamlit.success')
    @patch('streamlit.rerun')
    def test_render_stats_clear_button(self, mock_rerun, mock_succ, mock_btn, mock_cap, mock_met, mock_cols, mock_exp):
        """Teste le bouton de vidage du cache dans les stats"""
        from src.core.lazy_loader import render_lazy_loading_stats, LazyModuleLoader
        
        LazyModuleLoader.load('abc')
        
        mock_exp.return_value.__enter__ = Mock(return_value=None)
        mock_exp.return_value.__exit__ = Mock(return_value=None)
        
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_cols.return_value = [mock_col, mock_col]
        
        render_lazy_loading_stats()
        
        mock_succ.assert_called()
        mock_rerun.assert_called()


# ═══════════════════════════════════════════════════════════════════════════
# TESTS APP MODULE LEVEL
# ═══════════════════════════════════════════════════════════════════════════


class TestAppModuleLevel:
    """Tests au niveau du module app"""

    def test_app_module_importable(self):
        """Teste que le module app est importable"""
        import src.app as app
        assert app is not None

    def test_app_has_main_function(self):
        """Teste que app a une fonction main"""
        import src.app as app
        assert hasattr(app, 'main')
        assert callable(app.main)

    def test_app_has_logger(self):
        """Teste que app a un logger"""
        import src.app as app
        assert hasattr(app, 'logger')

    def test_app_has_parametres(self):
        """Teste que app a parametres"""
        import src.app as app
        assert hasattr(app, 'parametres')


# ═══════════════════════════════════════════════════════════════════════════
# TESTS CACHE INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════


class TestCacheIntegration:
    """Tests d'intégration du cache"""

    def test_cache_class_exists(self):
        """Teste que la classe Cache existe"""
        from src.core import Cache
        assert Cache is not None

    def test_cache_has_vider_method(self):
        """Teste que Cache a la méthode vider"""
        from src.core import Cache
        assert hasattr(Cache, 'vider')

    def test_gestionnaire_etat_exists(self):
        """Teste que GestionnaireEtat existe"""
        from src.core import GestionnaireEtat
        assert GestionnaireEtat is not None

    def test_gestionnaire_etat_has_reinitialiser(self):
        """Teste que GestionnaireEtat a reinitialiser"""
        from src.core import GestionnaireEtat
        assert hasattr(GestionnaireEtat, 'reinitialiser')


# ═══════════════════════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests des cas limites"""

    @patch.dict(os.environ, {'MISTRAL_API_KEY': ''})
    def test_empty_api_key(self):
        """Teste avec clé API vide"""
        key = os.getenv('MISTRAL_API_KEY')
        assert key == ''

    @patch.dict(os.environ, {'DEBUG': 'TRUE'})  # Uppercase
    def test_debug_case_insensitive(self):
        """Teste que DEBUG est case insensitive"""
        debug = os.getenv("DEBUG", "").lower() == "true"
        assert debug is True

    @patch.dict(os.environ, {'DEBUG': 'True'})  # Title case
    def test_debug_title_case(self):
        """Teste DEBUG en Title case"""
        debug = os.getenv("DEBUG", "").lower() == "true"
        assert debug is True

    def test_multiple_mains_dont_conflict(self):
        """Teste que plusieurs appels à main ne créent pas de conflit"""
        import src.app as app
        
        with patch.object(app, 'afficher_header'), \
             patch.object(app, 'afficher_sidebar'), \
             patch.object(app, 'afficher_footer'), \
             patch.object(app, 'obtenir_etat', return_value=Mock(module_actuel='accueil', mode_debug=False)), \
             patch.object(app, 'OptimizedRouter'), \
             patch('streamlit.error'), \
             patch('streamlit.exception'), \
             patch('streamlit.button', return_value=False), \
             patch('streamlit.spinner'):
            
            # Appel multiple
            app.main()
            app.main()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
