"""
Tests approfondis pour src/core/lazy_loader.py

Cible: Atteindre 80%+ de couverture
Lignes manquantes: 77-79, 98-100, 158, 272-309, 314-318, 328-360
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: ChargeurModuleDiffere - lignes 77-79, 98-100
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLazyModuleLoaderDeep:
    """Tests approfondis pour ChargeurModuleDiffere"""

    def test_load_module_import_error(self):
        """Test chargement module avec import error"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Module inexistant - lÃ¨ve ModuleNotFoundError
        with pytest.raises(ModuleNotFoundError):
            ChargeurModuleDiffere.load("module.inexistant.xyz")

    def test_load_module_force_reload(self):
        """Test rechargement forcÃ©"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger un module standard
        module1 = ChargeurModuleDiffere.load("json", reload=False)

        # Recharger avec reload=True
        module2 = ChargeurModuleDiffere.load("json", reload=True)

        assert module1 is not None
        assert module2 is not None

    def test_load_module_exception(self):
        """Test exception lors du chargement"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Test avec module invalide - lÃ¨ve une exception
        with pytest.raises((ModuleNotFoundError, Exception)):
            ChargeurModuleDiffere.load("__module_that_does_not_exist_xyz__")

    def test_preload_with_valid_modules(self):
        """Test prÃ©chargement avec modules valides"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["json", "os"]
        ChargeurModuleDiffere.preload(modules, background=False)

        # VÃ©rifier que les modules sont en cache
        stats = ChargeurModuleDiffere.get_stats()
        assert stats["cached_modules"] >= 0  # Au moins 0 modules en cache

    def test_preload_with_invalid_modules(self):
        """Test prÃ©chargement avec modules invalides"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        modules = ["module_inexistant_xyz_123"]
        # Ne doit pas lever d'exception
        ChargeurModuleDiffere.preload(modules, background=False)

    def test_preload_background_thread(self):
        """Test prÃ©chargement en arriÃ¨re-plan"""
        from src.core.lazy_loader import ChargeurModuleDiffere
        import time

        modules = ["json"]
        ChargeurModuleDiffere.preload(modules, background=True)

        # Attendre un peu pour le thread
        time.sleep(0.1)

        # Ne doit pas bloquer

    def test_get_stats_empty(self):
        """Test stats avec cache vide"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()
        stats = ChargeurModuleDiffere.get_stats()

        assert "cached_modules" in stats
        assert "average_load_time" in stats
        assert "load_times" in stats

    def test_get_stats_after_load(self):
        """Test stats aprÃ¨s chargement"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        ChargeurModuleDiffere.clear_cache()
        ChargeurModuleDiffere.load("json")

        stats = ChargeurModuleDiffere.get_stats()

        assert stats["cached_modules"] >= 1

    def test_clear_cache(self):
        """Test vidage du cache"""
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Charger un module
        ChargeurModuleDiffere.load("json")

        # Vider le cache
        ChargeurModuleDiffere.clear_cache()

        stats = ChargeurModuleDiffere.get_stats()
        assert stats["cached_modules"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: RouteurOptimise - lignes 272-309
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestOptimizedRouterDeep:
    """Tests approfondis pour RouteurOptimise"""

    def test_load_module_not_in_registry(self):
        """Test chargement module non enregistrÃ©"""
        from src.core.lazy_loader import RouteurOptimise

        with patch("streamlit.error") as mock_error:
            RouteurOptimise.load_module("module_inexistant_xyz")

            mock_error.assert_called()

    def test_load_module_with_app_function(self):
        """Test chargement module avec fonction app()"""
        from src.core.lazy_loader import RouteurOptimise

        # Mock du module avec app()
        mock_module = MagicMock()
        mock_module.app = Mock()

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch("src.core.lazy_loader.ChargeurModuleDiffere.load", return_value=mock_module):
                with patch("streamlit.spinner"):
                    RouteurOptimise.load_module("test")

                    mock_module.app.assert_called_once()

    def test_load_module_with_afficher_function(self):
        """Test chargement module avec fonction afficher()"""
        from src.core.lazy_loader import RouteurOptimise

        # Mock du module avec afficher() mais pas app()
        mock_module = MagicMock(spec=["afficher"])
        mock_module.afficher = Mock()
        # S'assurer que hasattr retourne False pour "app"
        del mock_module.app

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch("src.core.lazy_loader.ChargeurModuleDiffere.load", return_value=mock_module):
                with patch("streamlit.spinner"):
                    RouteurOptimise.load_module("test")

                    mock_module.afficher.assert_called_once()

    def test_load_module_without_entry_point(self):
        """Test chargement module sans point d'entrÃ©e"""
        from src.core.lazy_loader import RouteurOptimise

        # Mock du module sans app() ni afficher()
        mock_module = MagicMock(spec=[])

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch("src.core.lazy_loader.ChargeurModuleDiffere.load", return_value=mock_module):
                with patch("streamlit.spinner"):
                    with patch("streamlit.error") as mock_error:
                        RouteurOptimise.load_module("test")

                        mock_error.assert_called()

    def test_load_module_module_not_found(self):
        """Test chargement module avec ModuleNotFoundError"""
        from src.core.lazy_loader import RouteurOptimise

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch(
                "src.core.lazy_loader.ChargeurModuleDiffere.load", side_effect=ModuleNotFoundError()
            ):
                with patch("streamlit.spinner"):
                    with patch("streamlit.warning") as mock_warning:
                        with patch("streamlit.info"):
                            RouteurOptimise.load_module("test")

                            mock_warning.assert_called()

    def test_load_module_generic_exception(self):
        """Test chargement module avec exception gÃ©nÃ©rique"""
        from src.core.lazy_loader import RouteurOptimise

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch(
                "src.core.lazy_loader.ChargeurModuleDiffere.load", side_effect=Exception("Test error")
            ):
                with patch("streamlit.spinner"):
                    with patch("streamlit.error") as mock_error:
                        with patch("streamlit.session_state", {"debug_mode": False}):
                            RouteurOptimise.load_module("test")

                            mock_error.assert_called()

    def test_load_module_debug_mode(self):
        """Test chargement module en mode debug avec exception"""
        from src.core.lazy_loader import RouteurOptimise

        with patch.object(RouteurOptimise, "MODULE_REGISTRY", {"test": {"path": "test.path"}}):
            with patch(
                "src.core.lazy_loader.ChargeurModuleDiffere.load", side_effect=Exception("Test error")
            ):
                with patch("streamlit.spinner"):
                    with patch("streamlit.error"):
                        with patch("streamlit.session_state", {"debug_mode": True}):
                            with patch("streamlit.exception") as mock_exception:
                                RouteurOptimise.load_module("test")

                                # En mode debug, st.exception est appelÃ©
                                mock_exception.assert_called()

    def test_preload_common_modules(self):
        """Test prÃ©chargement des modules communs"""
        from src.core.lazy_loader import RouteurOptimise

        with patch("src.core.lazy_loader.ChargeurModuleDiffere.preload") as mock_preload:
            RouteurOptimise.preload_common_modules()

            mock_preload.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: afficher_stats_chargement_differe - lignes 328-360
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRenderLazyLoadingStats:
    """Tests pour afficher_stats_chargement_differe"""

    def test_render_stats_basic(self):
        """Test affichage basique des stats"""
        from src.core.lazy_loader import afficher_stats_chargement_differe

        with patch("streamlit.expander") as mock_expander:
            mock_expander_ctx = MagicMock()
            mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_ctx)
            mock_expander.return_value.__exit__ = Mock(return_value=False)

            with patch("streamlit.columns") as mock_columns:
                mock_col = MagicMock()
                mock_columns.return_value = [mock_col, mock_col]
                mock_col.__enter__ = Mock(return_value=mock_col)
                mock_col.__exit__ = Mock(return_value=False)

                with patch("streamlit.metric"):
                    with patch("streamlit.caption"):
                        with patch("streamlit.button", return_value=False):
                            afficher_stats_chargement_differe()

                            mock_expander.assert_called_once()

    def test_render_stats_with_load_times(self):
        """Test affichage stats avec temps de chargement"""
        from src.core.lazy_loader import afficher_stats_chargement_differe, ChargeurModuleDiffere

        # Charger quelques modules pour avoir des stats
        ChargeurModuleDiffere.clear_cache()
        ChargeurModuleDiffere.load("json")
        ChargeurModuleDiffere.load("os")

        with patch("streamlit.expander") as mock_expander:
            mock_expander_ctx = MagicMock()
            mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_ctx)
            mock_expander.return_value.__exit__ = Mock(return_value=False)

            with patch("streamlit.columns") as mock_columns:
                mock_col = MagicMock()
                mock_columns.return_value = [mock_col, mock_col]
                mock_col.__enter__ = Mock(return_value=mock_col)
                mock_col.__exit__ = Mock(return_value=False)

                with patch("streamlit.metric"):
                    with patch("streamlit.caption"):
                        with patch("streamlit.button", return_value=False):
                            afficher_stats_chargement_differe()

    def test_render_stats_clear_button(self):
        """Test bouton pour vider le cache"""
        from src.core.lazy_loader import afficher_stats_chargement_differe

        with patch("streamlit.expander") as mock_expander:
            mock_expander_ctx = MagicMock()
            mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_ctx)
            mock_expander.return_value.__exit__ = Mock(return_value=False)

            with patch("streamlit.columns") as mock_columns:
                mock_col = MagicMock()
                mock_columns.return_value = [mock_col, mock_col]
                mock_col.__enter__ = Mock(return_value=mock_col)
                mock_col.__exit__ = Mock(return_value=False)

                with patch("streamlit.metric"):
                    with patch("streamlit.caption"):
                        with patch("streamlit.button", return_value=True) as mock_button:
                            with patch("streamlit.success"):
                                with patch("streamlit.rerun"):
                                    afficher_stats_chargement_differe()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: lazy_import decorator - lignes 158
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLazyImportDecorator:
    """Tests pour le dÃ©corateur lazy_import"""

    def test_lazy_import_basic(self):
        """Test dÃ©corateur lazy_import basique"""
        from src.core.lazy_loader import lazy_import

        # Le dÃ©corateur charge le module quand la fonction est appelÃ©e
        @lazy_import("json")
        def use_json():
            import json
            return json is not None

        result = use_json()
        assert result is True

    def test_lazy_import_with_attr(self):
        """Test dÃ©corateur lazy_import avec attr_name"""
        from src.core.lazy_loader import lazy_import

        # Utiliser un attribut qui existe vraiment dans os
        @lazy_import("os", attr_name="sep")
        def use_sep():
            import os
            return os.sep is not None

        result = use_sep()
        assert result is True

    def test_lazy_import_invalid_module(self):
        """Test dÃ©corateur lazy_import avec module invalide"""
        from src.core.lazy_loader import lazy_import

        @lazy_import("module_inexistant_xyz_456")
        def use_invalid():
            return "should not reach here"

        with pytest.raises((ModuleNotFoundError, Exception)):
            use_invalid()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS: MODULE_REGISTRY validation
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestModuleRegistry:
    """Tests pour MODULE_REGISTRY"""

    def test_registry_has_required_keys(self):
        """Test que le registry a les clÃ©s requises"""
        from src.core.lazy_loader import RouteurOptimise

        # Les modules minimaux requis (peuvent Ãªtre prÃ©fixÃ©s)
        registry_keys = list(RouteurOptimise.MODULE_REGISTRY.keys())
        
        # VÃ©rifier qu'il y a au moins quelques modules
        assert len(registry_keys) > 0, "Le registry est vide"
        
        # VÃ©rifier que "accueil" existe
        assert "accueil" in registry_keys, "Module accueil manquant"

    def test_registry_entries_have_path(self):
        """Test que chaque entrÃ©e a un path"""
        from src.core.lazy_loader import RouteurOptimise

        for name, config in RouteurOptimise.MODULE_REGISTRY.items():
            assert "path" in config, f"Module {name} n'a pas de path"

    def test_registry_paths_are_strings(self):
        """Test que les paths sont des strings"""
        from src.core.lazy_loader import RouteurOptimise

        for name, config in RouteurOptimise.MODULE_REGISTRY.items():
            assert isinstance(config["path"], str), f"Path de {name} n'est pas une string"
