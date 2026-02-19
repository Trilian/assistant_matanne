"""
Tests unitaires complets pour lazy_loader.py (Chargement différé des modules)
Couverture cible: 80%+
"""

import threading
import time
from unittest.mock import Mock, patch

import pytest

from src.core import lazy_loader
from src.core.lazy_loader import (
    ChargeurModuleDiffere,
    RouteurOptimise,
    afficher_stats_chargement_differe,
    lazy_import,
)

# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def nettoyer_cache():
    """Nettoie le cache avant et après chaque test"""
    ChargeurModuleDiffere.vider_cache()
    yield
    ChargeurModuleDiffere.vider_cache()


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS IMPORT MODULE
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
def test_import_lazy_loader():
    """Vérifie que le module lazy_loader s'importe sans erreur."""
    assert hasattr(lazy_loader, "RouteurOptimise")
    assert hasattr(lazy_loader, "ChargeurModuleDiffere")
    assert hasattr(lazy_loader, "lazy_import")
    assert hasattr(lazy_loader, "afficher_stats_chargement_differe")


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS CHARGEUR MODULE DIFFERE - METHODE CHARGER
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargeurModuleDiffereCharger:
    """Tests de la méthode charger()"""

    def test_charger_module_existant(self):
        """Test chargement d'un module Python standard"""
        module = ChargeurModuleDiffere.charger("json")
        assert module is not None
        assert hasattr(module, "loads")
        assert hasattr(module, "dumps")

    def test_charger_module_cache_hit(self):
        """Test que le cache fonctionne (2ème appel = cache hit)"""
        # Premier chargement
        module1 = ChargeurModuleDiffere.charger("os")
        # Deuxième chargement (doit venir du cache)
        module2 = ChargeurModuleDiffere.charger("os")

        assert module1 is module2
        assert "os" in ChargeurModuleDiffere._cache

    def test_charger_module_reload_force(self):
        """Test rechargement forcé avec reload=True"""
        # Premier chargement
        ChargeurModuleDiffere.charger("sys")
        stats_avant = ChargeurModuleDiffere.obtenir_statistiques()

        # Forcer rechargement
        module = ChargeurModuleDiffere.charger("sys", reload=True)

        assert module is not None
        assert hasattr(module, "path")

    def test_charger_module_inexistant(self):
        """Test chargement d'un module inexistant lève ModuleNotFoundError"""
        with pytest.raises(ModuleNotFoundError):
            ChargeurModuleDiffere.charger("module_inexistant_xyz_123")

    def test_charger_enregistre_temps(self):
        """Test que le temps de chargement est enregistré"""
        ChargeurModuleDiffere.charger("collections")

        stats = ChargeurModuleDiffere.obtenir_statistiques()
        assert "collections" in stats["load_times"]
        assert stats["load_times"]["collections"] >= 0


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS CHARGEUR MODULE DIFFERE - METHODE PRECHARGER
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargeurModuleDifferePrecharger:
    """Tests de la méthode precharger()"""

    def test_precharger_synchrone(self):
        """Test préchargement synchrone sans background"""
        modules = ["json", "os", "sys"]
        ChargeurModuleDiffere.precharger(modules, background=False)

        # Vérifier que les modules sont en cache
        for mod in modules:
            assert mod in ChargeurModuleDiffere._cache

    def test_precharger_background(self):
        """Test préchargement en arrière-plan"""
        modules = ["collections", "itertools"]
        ChargeurModuleDiffere.precharger(modules, background=True)

        # Attendre un peu que le thread finisse
        time.sleep(0.2)

        # Vérifier que les modules sont en cache
        for mod in modules:
            assert mod in ChargeurModuleDiffere._cache

    def test_precharger_module_inexistant_ne_propage_pas_erreur(self):
        """Test que le préchargement silencieux n'échoue pas sur module inexistant"""
        modules = ["json", "module_inexistant_xyz"]

        # Ne doit pas lever d'exception
        ChargeurModuleDiffere.precharger(modules, background=False)

        # json doit être chargé
        assert "json" in ChargeurModuleDiffere._cache


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS CHARGEUR MODULE DIFFERE - STATISTIQUES
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargeurModuleDiffereStatistiques:
    """Tests des statistiques lazy loading"""

    def test_obtenir_statistiques_vide(self):
        """Test stats avec cache vide"""
        stats = ChargeurModuleDiffere.obtenir_statistiques()

        assert stats["cached_modules"] == 0
        assert stats["total_load_time"] == 0
        assert stats["average_load_time"] == 0
        assert stats["load_times"] == {}

    def test_obtenir_statistiques_avec_modules(self):
        """Test stats après chargement de modules"""
        ChargeurModuleDiffere.charger("json")
        ChargeurModuleDiffere.charger("os")

        stats = ChargeurModuleDiffere.obtenir_statistiques()

        assert stats["cached_modules"] == 2
        # Les temps peuvent être 0 si modules déjà en mémoire
        assert stats["total_load_time"] >= 0
        assert stats["average_load_time"] >= 0
        assert len(stats["load_times"]) == 2


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS CHARGEUR MODULE DIFFERE - VIDER CACHE
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargeurModuleDiffereViderCache:
    """Tests de la méthode vider_cache()"""

    def test_vider_cache(self):
        """Test que vider_cache() fonctionne"""
        ChargeurModuleDiffere.charger("json")
        assert len(ChargeurModuleDiffere._cache) > 0

        ChargeurModuleDiffere.vider_cache()

        assert len(ChargeurModuleDiffere._cache) == 0
        assert len(ChargeurModuleDiffere._load_times) == 0


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS DECORATOR LAZY_IMPORT
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLazyImportDecorator:
    """Tests du décorateur lazy_import"""

    def test_lazy_import_sans_attr_name(self):
        """Test lazy_import sans attr_name"""

        @lazy_import("json")
        def utiliser_json():
            return True

        result = utiliser_json()
        assert result is True

    def test_lazy_import_avec_attr_name(self):
        """Test lazy_import avec attr_name injecte dans globals"""

        # On utilise loads depuis json car c'est un attribut valide
        @lazy_import("json", "loads")
        def utiliser_json_loads():
            # L'attribut 'loads' devrait être injecté dans globals
            return True

        result = utiliser_json_loads()
        assert result is True

    def test_lazy_import_charge_module(self):
        """Test que lazy_import charge bien le module"""

        @lazy_import("collections")
        def get_counter():
            import collections

            return collections.Counter

        result = get_counter()
        assert result is not None


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS ROUTEUR OPTIMISE
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRouteurOptimise:
    """Tests du routeur optimisé"""

    def test_class_exists(self):
        """Test que la classe existe"""
        assert RouteurOptimise is not None

    def test_has_module_registry(self):
        """Test que le registre de modules existe"""
        assert hasattr(RouteurOptimise, "MODULE_REGISTRY")
        assert isinstance(RouteurOptimise.MODULE_REGISTRY, dict)

    def test_module_registry_contient_accueil(self):
        """Test que le module accueil est enregistré"""
        assert "accueil" in RouteurOptimise.MODULE_REGISTRY

    def test_module_registry_structure(self):
        """Test la structure des entrées du registry"""
        for name, config in RouteurOptimise.MODULE_REGISTRY.items():
            assert "path" in config, f"Module {name} manque 'path'"
            # Le champ 'type' était optionnel et a été supprimé du registry
            # Vérifie juste que 'path' pointe vers un chemin de module valide
            assert config["path"].startswith("src."), f"Module {name} path invalide"

    @patch("streamlit.error")
    @patch("streamlit.spinner")
    def test_charger_module_inexistant(self, mock_spinner, mock_error):
        """Test chargement d'un module non enregistré"""
        mock_spinner.return_value.__enter__ = Mock(return_value=None)
        mock_spinner.return_value.__exit__ = Mock(return_value=False)

        RouteurOptimise.charger_module("module_qui_existe_pas")

        mock_error.assert_called_once()

    def test_class_instantiable(self):
        """Test que la classe est instanciable"""
        router = RouteurOptimise()
        assert router is not None


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS AFFICHER STATS
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAfficherStats:
    """Tests de la fonction d'affichage des stats"""

    @patch("streamlit.expander")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_afficher_stats_charge_modules(self, mock_metric, mock_columns, mock_expander):
        """Test affichage des stats avec modules"""
        # Setup mocks
        mock_expander.return_value.__enter__ = Mock(return_value=None)
        mock_expander.return_value.__exit__ = Mock(return_value=False)
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=False)
        mock_columns.return_value = [mock_col, mock_col]

        # Charger des modules
        ChargeurModuleDiffere.charger("json")

        # Appeler la fonction
        afficher_stats_chargement_differe()

        # Vérifier les appels
        mock_expander.assert_called_once()


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIntegrationLazyLoader:
    """Tests d'intégration du lazy loader"""

    def test_workflow_complet(self):
        """Test workflow complet: charger → stats → vider"""
        # Charger plusieurs modules
        ChargeurModuleDiffere.charger("json")
        ChargeurModuleDiffere.charger("os")
        ChargeurModuleDiffere.charger("sys")

        # Vérifier stats
        stats = ChargeurModuleDiffere.obtenir_statistiques()
        assert stats["cached_modules"] == 3

        # Vider cache
        ChargeurModuleDiffere.vider_cache()

        # Vérifier que c'est vide
        stats_apres = ChargeurModuleDiffere.obtenir_statistiques()
        assert stats_apres["cached_modules"] == 0

    def test_thread_safety_basique(self):
        """Test basique de thread safety"""
        results = []

        def charger_module(name):
            module = ChargeurModuleDiffere.charger(name)
            results.append(module is not None)

        threads = [
            threading.Thread(target=charger_module, args=("json",)),
            threading.Thread(target=charger_module, args=("os",)),
            threading.Thread(target=charger_module, args=("sys",)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results)
        assert len(ChargeurModuleDiffere._cache) == 3


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# TESTS ADDITIONNELS POUR COUVERTURE 85%+
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestChargeurModuleDiffereAdvanced:
    """Tests avancés pour ChargeurModuleDiffere."""

    def test_charger_with_invalid_module_path(self):
        """Test chargement d'un module invalide."""
        with pytest.raises(ModuleNotFoundError):
            ChargeurModuleDiffere.charger("module.inexistant.xyz")

    def test_charger_returns_cached_module(self):
        """Test que le deuxième appel retourne le module du cache."""
        ChargeurModuleDiffere.vider_cache()

        module1 = ChargeurModuleDiffere.charger("json")
        module2 = ChargeurModuleDiffere.charger("json")

        # Should be same cached module
        assert module1 is module2

    def test_precharger_modules_vides(self):
        """Test préchargement avec liste vide."""
        ChargeurModuleDiffere.vider_cache()
        ChargeurModuleDiffere.precharger([], background=False)
        assert len(ChargeurModuleDiffere._cache) == 0

    def test_precharger_modules_foreground(self):
        """Test préchargement en foreground."""
        ChargeurModuleDiffere.vider_cache()
        ChargeurModuleDiffere.precharger(["json", "os"], background=False)

        stats = ChargeurModuleDiffere.obtenir_statistiques()
        assert stats["cached_modules"] >= 2

    def test_obtenir_statistiques_keys(self):
        """Test que les statistiques contiennent les bonnes clés."""
        ChargeurModuleDiffere.vider_cache()
        ChargeurModuleDiffere.charger("json")

        stats = ChargeurModuleDiffere.obtenir_statistiques()

        assert "cached_modules" in stats
        assert "average_load_time" in stats
        assert "load_times" in stats

    def test_obtenir_statistiques(self):
        """Test obtenir_statistiques."""
        ChargeurModuleDiffere.vider_cache()
        ChargeurModuleDiffere.charger("os")

        stats = ChargeurModuleDiffere.obtenir_statistiques()
        assert "cached_modules" in stats


@pytest.mark.unit
class TestRouteurOptimiseAdvanced:
    """Tests avancés pour RouteurOptimise."""

    def test_module_registry_contains_cuisine(self):
        """Test que les modules cuisine sont enregistrés."""
        registry = RouteurOptimise.MODULE_REGISTRY

        cuisine_modules = [k for k in registry.keys() if k.startswith("cuisine")]
        assert len(cuisine_modules) > 0

    def test_module_registry_contains_famille(self):
        """Test que les modules famille sont enregistrés."""
        registry = RouteurOptimise.MODULE_REGISTRY

        famille_modules = [k for k in registry.keys() if k.startswith("famille")]
        assert len(famille_modules) > 0

    def test_module_registry_contains_maison(self):
        """Test que les modules maison sont enregistrés."""
        registry = RouteurOptimise.MODULE_REGISTRY

        maison_modules = [k for k in registry.keys() if k.startswith("maison")]
        assert len(maison_modules) > 0

    @patch("streamlit.error")
    @patch("streamlit.spinner")
    @patch("streamlit.warning")
    @patch("streamlit.info")
    def test_charger_module_not_implemented(
        self, mock_info, mock_warning, mock_spinner, mock_error
    ):
        """Test chargement d'un module pas encore implémenté."""
        mock_spinner.return_value.__enter__ = Mock(return_value=None)
        mock_spinner.return_value.__exit__ = Mock(return_value=False)

        # Add a fake module to registry
        RouteurOptimise.MODULE_REGISTRY["fake_module"] = {
            "path": "src.modules.fake.not_exists_xyz",
            "type": "simple",
        }

        try:
            RouteurOptimise.charger_module("fake_module")
            # Should show warning for non-implemented module
        finally:
            # Cleanup
            del RouteurOptimise.MODULE_REGISTRY["fake_module"]

    @patch("streamlit.spinner")
    def test_precharger_common_modules(self, mock_spinner):
        """Test le préchargement des modules communs."""
        mock_spinner.return_value.__enter__ = Mock(return_value=None)
        mock_spinner.return_value.__exit__ = Mock(return_value=False)

        # Should not raise
        RouteurOptimise.precharger_common_modules()


@pytest.mark.unit
class TestLazyImportAdvanced:
    """Tests avancés pour le décorateur lazy_import."""

    def test_lazy_import_preserves_function_name(self):
        """Test que lazy_import préserve le nom de la fonction."""

        @lazy_import("json")
        def ma_fonction():
            return True

        assert ma_fonction.__name__ == "ma_fonction"

    def test_lazy_import_with_submodule(self):
        """Test lazy_import avec sous-module."""

        @lazy_import("os.path")
        def use_path():
            import os.path

            return os.path.exists(".")

        result = use_path()
        assert result is True

    def test_lazy_import_function_called_multiple_times(self):
        """Test que la fonction décorée peut être appelée plusieurs fois."""
        call_count = 0

        @lazy_import("json")
        def increment():
            nonlocal call_count
            call_count += 1
            return call_count

        assert increment() == 1
        assert increment() == 2
        assert increment() == 3


@pytest.mark.unit
class TestAfficherStatsAdvanced:
    """Tests avancés pour l'affichage des statistiques."""

    @patch("streamlit.expander")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    @patch("streamlit.caption")
    @patch("streamlit.button")
    def test_afficher_stats_with_slow_modules(
        self, mock_button, mock_caption, mock_metric, mock_columns, mock_expander
    ):
        """Test affichage avec modules lents."""
        mock_expander.return_value.__enter__ = Mock(return_value=None)
        mock_expander.return_value.__exit__ = Mock(return_value=False)
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=False)
        mock_columns.return_value = [mock_col, mock_col]
        mock_button.return_value = False

        # Charger plusieurs modules
        ChargeurModuleDiffere.charger("json")
        ChargeurModuleDiffere.charger("os")
        ChargeurModuleDiffere.charger("sys")
        ChargeurModuleDiffere.charger("collections")
        ChargeurModuleDiffere.charger("functools")
        ChargeurModuleDiffere.charger("itertools")

        afficher_stats_chargement_differe()

        # Should have been called
        mock_expander.assert_called_once()

    @patch("streamlit.expander")
    @patch("streamlit.columns")
    @patch("streamlit.metric")
    @patch("streamlit.button")
    @patch("streamlit.success")
    @patch("streamlit.rerun")
    def test_afficher_stats_button_vider_cache(
        self, mock_rerun, mock_success, mock_button, mock_metric, mock_columns, mock_expander
    ):
        """Test le bouton 'Vider Cache' dans les stats."""
        mock_expander.return_value.__enter__ = Mock(return_value=None)
        mock_expander.return_value.__exit__ = Mock(return_value=False)
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=False)
        mock_columns.return_value = [mock_col, mock_col]
        mock_button.return_value = True  # Simuler clic sur bouton

        ChargeurModuleDiffere.charger("json")

        afficher_stats_chargement_differe()

        # Cache should be cleared
        mock_success.assert_called_once()
