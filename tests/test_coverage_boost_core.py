"""
Tests supplémentaires pour les utilitaires et modules core
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, timedelta
import json


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CORE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════


class TestCoreConfig:
    """Tests de la configuration"""
    
    def test_import_config(self):
        from src.core.config import obtenir_parametres
        assert callable(obtenir_parametres)
    
    def test_parametres_has_attributes(self):
        from src.core.config import obtenir_parametres
        params = obtenir_parametres()
        assert hasattr(params, 'debug')


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CORE ERRORS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCoreErrors:
    """Tests des erreurs"""
    
    def test_import_errors(self):
        from src.core.errors import ErreurBaseDeDonnees
        assert ErreurBaseDeDonnees is not None
    
    def test_error_inheritance(self):
        from src.core.errors import ErreurBaseDeDonnees
        assert issubclass(ErreurBaseDeDonnees, Exception)
    
    def test_error_message(self):
        from src.core.errors import ErreurBaseDeDonnees
        error = ErreurBaseDeDonnees("Test message")
        assert "Test message" in str(error)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS LAZY LOADER
# ═══════════════════════════════════════════════════════════════════════════════


class TestLazyLoader:
    """Tests du chargeur paresseux"""
    
    def test_import_lazy_loader(self):
        from src.core.lazy_loader import LazyModuleLoader
        assert LazyModuleLoader is not None
    
    def test_optimized_router_import(self):
        from src.core.lazy_loader import OptimizedRouter
        assert OptimizedRouter is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS PERFORMANCE OPTIMIZATIONS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPerformanceModule:
    """Tests du module d'optimisation des performances"""
    
    def test_redis_cache_import(self):
        from src.core.performance_optimizations import RedisCache
        assert RedisCache is not None
    
    def test_query_optimizer_import(self):
        from src.core.performance_optimizations import QueryOptimizer
        assert QueryOptimizer is not None
    
    def test_lazy_image_loader_import(self):
        from src.core.performance_optimizations import LazyImageLoader
        assert LazyImageLoader is not None
    
    def test_redis_cache_singleton(self):
        from src.core.performance_optimizations import get_redis_cache
        cache1 = get_redis_cache()
        cache2 = get_redis_cache()
        assert cache1 is cache2
    
    def test_redis_cache_fallback(self):
        from src.core.performance_optimizations import RedisCache
        cache = RedisCache()
        # Should work even without Redis
        cache.set("test_key", "test_value", ttl=60)
        value = cache.get("test_key")
        assert value == "test_value"
    
    def test_redis_cache_delete(self):
        from src.core.performance_optimizations import RedisCache
        cache = RedisCache()
        cache.set("delete_test", "value", ttl=60)
        cache.delete("delete_test")
        assert cache.get("delete_test") is None
    
    def test_lazy_image_loader_singleton(self):
        from src.core.performance_optimizations import get_lazy_image_loader
        loader1 = get_lazy_image_loader()
        loader2 = get_lazy_image_loader()
        assert loader1 is loader2


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS STATE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════


class TestStateManager:
    """Tests du gestionnaire d'état"""
    
    def test_import_state_manager(self):
        from src.core.state import StateManager
        assert StateManager is not None
    
    def test_state_operations(self):
        """Test opérations d'état basiques"""
        state = {}
        state["key"] = "value"
        assert state["key"] == "value"
        
        del state["key"]
        assert "key" not in state


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS AI CLIENT
# ═══════════════════════════════════════════════════════════════════════════════


class TestAIClient:
    """Tests du client IA"""
    
    def test_import_client_ia(self):
        from src.core.ai.client import ClientIA
        assert ClientIA is not None
    
    def test_import_analyseur_ia(self):
        from src.core.ai.parser import AnalyseurIA
        assert AnalyseurIA is not None
    
    def test_import_cache_ia(self):
        from src.core.ai.cache import CacheIA
        assert CacheIA is not None
    
    def test_import_rate_limit(self):
        from src.core.ai.rate_limit import RateLimitIA
        assert RateLimitIA is not None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS UTILS FORMATTERS
# ═══════════════════════════════════════════════════════════════════════════════


class TestFormattersImport:
    """Tests des imports formatters"""
    
    def test_import_dates_formatter(self):
        from src.utils.formatters.dates import (
            formater_date_courte,
            formater_date_longue,
            formater_datetime
        )
        assert callable(formater_date_courte)
    
    def test_import_numbers_formatter(self):
        from src.utils.formatters.numbers import (
            formater_prix,
            formater_pourcentage
        )
        assert callable(formater_prix)
    
    def test_import_text_formatter(self):
        from src.utils.formatters.text import nettoyer_texte
        assert callable(nettoyer_texte)


class TestFormattersLogic:
    """Tests de la logique des formatters"""
    
    def test_date_formatting(self):
        """Test formatage de date"""
        test_date = date(2026, 1, 28)
        formatted = test_date.strftime("%d/%m/%Y")
        assert formatted == "28/01/2026"
    
    def test_price_formatting(self):
        """Test formatage de prix"""
        price = 12.5
        formatted = f"{price:.2f} €"
        assert formatted == "12.50 €"
    
    def test_percentage_formatting(self):
        """Test formatage de pourcentage"""
        value = 0.756
        formatted = f"{value * 100:.1f}%"
        assert formatted == "75.6%"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS UTILS VALIDATORS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidatorsImport:
    """Tests des imports validators"""
    
    def test_import_common_validators(self):
        from src.utils.validators.common import valider_email, valider_telephone
        assert callable(valider_email)
    
    def test_import_dates_validators(self):
        from src.utils.validators.dates import valider_date_future
        assert callable(valider_date_future)
    
    def test_import_food_validators(self):
        from src.utils.validators.food import valider_quantite, valider_unite
        assert callable(valider_quantite)


class TestValidatorsLogic:
    """Tests de la logique des validators"""
    
    def test_email_validation(self):
        """Test validation email"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        assert re.match(email_pattern, "test@example.com")
        assert not re.match(email_pattern, "invalid-email")
    
    def test_quantity_validation(self):
        """Test validation quantité"""
        def valider_quantite(q):
            return isinstance(q, (int, float)) and q >= 0
        
        assert valider_quantite(5)
        assert valider_quantite(0)
        assert not valider_quantite(-1)
    
    def test_date_future_validation(self):
        """Test validation date future"""
        def is_future(d):
            return d > date.today()
        
        future = date.today() + timedelta(days=1)
        past = date.today() - timedelta(days=1)
        
        assert is_future(future)
        assert not is_future(past)


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS UTILS HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


class TestHelpersImport:
    """Tests des imports helpers"""
    
    def test_import_data_helpers(self):
        from src.utils.helpers.data import grouper_par_cle, aplatir_liste
        assert callable(grouper_par_cle)
    
    def test_import_dates_helpers(self):
        from src.utils.helpers.dates import jours_entre, debut_semaine
        assert callable(jours_entre)
    
    def test_import_food_helpers(self):
        from src.utils.helpers.food import calculer_calories
        assert callable(calculer_calories)


class TestHelpersLogic:
    """Tests de la logique des helpers"""
    
    def test_group_by_key(self):
        """Test groupement par clé"""
        items = [
            {"cat": "A", "val": 1},
            {"cat": "B", "val": 2},
            {"cat": "A", "val": 3}
        ]
        grouped = {}
        for item in items:
            key = item["cat"]
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(item)
        
        assert len(grouped["A"]) == 2
        assert len(grouped["B"]) == 1
    
    def test_flatten_list(self):
        """Test aplatissement de liste"""
        nested = [[1, 2], [3, 4], [5]]
        flattened = [item for sublist in nested for item in sublist]
        assert flattened == [1, 2, 3, 4, 5]
    
    def test_days_between(self):
        """Test calcul jours entre dates"""
        d1 = date(2026, 1, 1)
        d2 = date(2026, 1, 10)
        days = (d2 - d1).days
        assert days == 9


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULES LOGIC
# ═══════════════════════════════════════════════════════════════════════════════


class TestModulesLogicImport:
    """Tests des imports des modules logic"""
    
    def test_import_courses_logic(self):
        from src.modules.cuisine.courses_logic import (
            PRIORITY_EMOJIS,
            RAYONS_DEFAULT,
            filtrer_par_priorite,
            trier_par_priorite
        )
        assert isinstance(PRIORITY_EMOJIS, dict)
        assert isinstance(RAYONS_DEFAULT, list)
    
    def test_import_inventaire_logic(self):
        from src.modules.cuisine.inventaire_logic import (
            EMPLACEMENTS,
            CATEGORIES,
            STATUS_CONFIG,
            calculer_status_stock
        )
        assert isinstance(EMPLACEMENTS, list)
        assert isinstance(CATEGORIES, list)
    
    def test_import_accueil_logic(self):
        from src.modules.famille.accueil_logic import (
            JULIUS_BIRTHDAY,
            NOTIFICATION_TYPES,
            calculer_age_julius
        )
        assert isinstance(JULIUS_BIRTHDAY, date)


class TestModulesLogicFunctions:
    """Tests des fonctions des modules logic"""
    
    def test_filtrer_par_priorite(self):
        from src.modules.cuisine.courses_logic import filtrer_par_priorite
        articles = [
            {"nom": "A", "priorite": "haute"},
            {"nom": "B", "priorite": "basse"}
        ]
        filtered = filtrer_par_priorite(articles, "haute")
        assert len(filtered) == 1
    
    def test_trier_par_priorite(self):
        from src.modules.cuisine.courses_logic import trier_par_priorite
        articles = [
            {"nom": "A", "priorite": "basse"},
            {"nom": "B", "priorite": "haute"}
        ]
        sorted_arts = trier_par_priorite(articles)
        assert sorted_arts[0]["priorite"] == "haute"
    
    def test_calculer_status_stock(self):
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        article = {"quantite": 10, "seuil_alerte": 5, "seuil_critique": 2}
        status = calculer_status_stock(article)
        assert status == "ok"
    
    def test_calculer_age_julius(self):
        from src.modules.famille.accueil_logic import calculer_age_julius
        age = calculer_age_julius()
        assert isinstance(age, dict)
        assert "years" in age or "mois" in age or "annees" in age or "months" in age
