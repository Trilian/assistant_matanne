"""
Tests approfondis pour src/core/decorators.py

Cible: Atteindre 80%+ de couverture
Lignes manquantes: 63-72, 126-152, 227-228, 268-298
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import inspect


# ═══════════════════════════════════════════════════════════
# TESTS: with_db_session - lignes 63-72
# ═══════════════════════════════════════════════════════════


class TestWithDbSessionDeep:
    """Tests approfondis pour @with_db_session"""

    def test_with_db_session_creates_session_when_none_provided(self):
        """Test création de session quand aucune n'est fournie"""
        from src.core.decorators import with_db_session

        called_with_session = []

        @with_db_session
        def ma_fonction(data: dict, db=None):
            called_with_session.append(db)
            return data

        with patch("src.core.database.get_db_context") as mock_context:
            mock_session = Mock()
            mock_context.return_value.__enter__ = Mock(return_value=mock_session)
            mock_context.return_value.__exit__ = Mock(return_value=False)

            result = ma_fonction({"test": 1})

            assert result == {"test": 1}
            mock_context.assert_called_once()

    def test_with_db_session_uses_provided_session(self):
        """Test utilisation de session fournie"""
        from src.core.decorators import with_db_session

        @with_db_session
        def ma_fonction(data: dict, db=None):
            return db

        mock_db = Mock()
        result = ma_fonction({"test": 1}, db=mock_db)

        assert result == mock_db

    def test_with_db_session_with_session_param(self):
        """Test avec paramètre nommé 'session' au lieu de 'db'"""
        from src.core.decorators import with_db_session

        @with_db_session
        def ma_fonction(data: dict, session=None):
            return session

        mock_session = Mock()
        result = ma_fonction({"test": 1}, session=mock_session)

        assert result == mock_session

    def test_with_db_session_auto_injects_session_param(self):
        """Test injection auto du paramètre 'session'"""
        from src.core.decorators import with_db_session

        injected_session = []

        @with_db_session
        def ma_fonction(data: dict, session=None):
            injected_session.append(session)
            return data

        with patch("src.core.database.get_db_context") as mock_context:
            mock_session = Mock()
            mock_context.return_value.__enter__ = Mock(return_value=mock_session)
            mock_context.return_value.__exit__ = Mock(return_value=False)

            result = ma_fonction({"test": 1})

            assert result == {"test": 1}
            assert len(injected_session) == 1
            # La session devrait être injectée (mock ou vraie)

    def test_with_db_session_preserves_function_metadata(self):
        """Test préservation des métadonnées de fonction"""
        from src.core.decorators import with_db_session

        @with_db_session
        def ma_super_fonction(data: dict, db=None) -> dict:
            """Ma docstring"""
            return data

        assert ma_super_fonction.__name__ == "ma_super_fonction"
        assert "Ma docstring" in (ma_super_fonction.__doc__ or "")


# ═══════════════════════════════════════════════════════════
# TESTS: with_cache key_func - lignes 126-152
# ═══════════════════════════════════════════════════════════


class TestWithCacheKeyFunc:
    """Tests pour with_cache avec key_func personnalisée"""

    def test_with_cache_key_func_simple(self):
        """Test key_func simple"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        @with_cache(key_func=lambda x: f"custom_{x}", ttl=60)
        def my_func(x):
            return x * 2

        result = my_func(5)
        assert result == 10

    def test_with_cache_key_func_with_kwargs(self):
        """Test key_func avec kwargs"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        @with_cache(key_func=lambda **kw: f"key_{kw.get('id', 0)}", ttl=60)
        def my_func(id=0, name="test"):
            return f"{id}_{name}"

        result = my_func(id=42, name="hello")
        assert result == "42_hello"

    def test_with_cache_key_func_type_error_fallback(self):
        """Test fallback quand key_func échoue avec TypeError"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        # Key func qui attend des paramètres différents
        def bad_key_func(self, nom=None):
            return f"key_{nom}"

        @with_cache(key_func=bad_key_func, ttl=60)
        def my_func(self, nom="default", db=None):
            return f"result_{nom}"

        # Appel avec self=object mock
        mock_self = Mock()
        result = my_func(mock_self, nom="test")

        assert "test" in result

    def test_with_cache_without_key_func_uses_prefix(self):
        """Test sans key_func utilise le préfixe"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        @with_cache(key_prefix="mon_prefix", ttl=120)
        def my_func(x, y):
            return x + y

        result = my_func(1, 2)
        assert result == 3

    def test_with_cache_excludes_db_from_key(self):
        """Test que db est exclu de la clé de cache"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        @with_cache(ttl=60)
        def my_func(x, db=None):
            return x * 2

        mock_db = Mock()
        result = my_func(5, db=mock_db)
        assert result == 10

    def test_with_cache_hit_returns_cached(self):
        """Test retourne valeur en cache si disponible"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()
        call_count = [0]

        @with_cache(key_prefix="test", ttl=60)
        def my_func(x):
            call_count[0] += 1
            return x * 2

        # Premier appel - cache miss
        result1 = my_func(5)

        # Deuxième appel - cache hit
        result2 = my_func(5)

        assert result1 == 10
        assert result2 == 10
        # La fonction devrait n'être appelée qu'une fois grâce au cache
        assert call_count[0] == 1


# ═══════════════════════════════════════════════════════════
# TESTS: with_validation - lignes 268-298
# ═══════════════════════════════════════════════════════════


class TestWithValidation:
    """Tests pour @with_validation"""

    def test_with_validation_success(self):
        """Test validation réussie"""
        from src.core.decorators import with_validation
        from pydantic import BaseModel

        class MonModele(BaseModel):
            nom: str
            prix: float

        @with_validation(MonModele, field_mapping={"data": "data"})
        def creer_article(data: dict, db=None):
            return data

        result = creer_article(data={"nom": "Test", "prix": 10.5})

        assert result["nom"] == "Test"
        assert result["prix"] == 10.5

    def test_with_validation_echec(self):
        """Test validation échouée lève ErreurValidation"""
        from src.core.decorators import with_validation
        from src.core.errors_base import ErreurValidation
        from pydantic import BaseModel

        class MonModele(BaseModel):
            nom: str
            prix: float

        @with_validation(MonModele, field_mapping={"data": "data"})
        def creer_article(data: dict, db=None):
            return data

        with pytest.raises(ErreurValidation):
            creer_article(data={"nom": "Test"})  # prix manquant

    def test_with_validation_sans_field_mapping(self):
        """Test validation sans field_mapping explicite"""
        from src.core.decorators import with_validation
        from pydantic import BaseModel

        class MonModele(BaseModel):
            valeur: int

        @with_validation(MonModele)  # Pas de field_mapping
        def ma_fonction(data: dict):
            return data

        result = ma_fonction(data={"valeur": 42})

        assert result["valeur"] == 42

    def test_with_validation_preserves_function_name(self):
        """Test préservation du nom de fonction"""
        from src.core.decorators import with_validation
        from pydantic import BaseModel

        class MonModele(BaseModel):
            x: int

        @with_validation(MonModele)
        def ma_super_fonction(data: dict):
            return data

        assert ma_super_fonction.__name__ == "ma_super_fonction"


# ═══════════════════════════════════════════════════════════
# TESTS: with_error_handling - lignes 227-228
# ═══════════════════════════════════════════════════════════


class TestWithErrorHandlingDeep:
    """Tests approfondis pour @with_error_handling"""

    def test_with_error_handling_no_args(self):
        """Test décorateur sans arguments"""
        from src.core.decorators import with_error_handling

        @with_error_handling()
        def ma_fonction():
            return 42

        result = ma_fonction()
        assert result == 42

    def test_with_error_handling_with_exception(self):
        """Test décorateur avec exception"""
        from src.core.decorators import with_error_handling

        @with_error_handling()
        def ma_fonction():
            raise ValueError("Test error")

        result = ma_fonction()
        assert result is None  # Valeur par défaut

    def test_with_error_handling_custom_default(self):
        """Test décorateur avec valeur par défaut personnalisée"""
        from src.core.decorators import with_error_handling

        @with_error_handling(default_return="fallback")
        def ma_fonction():
            raise Exception("Erreur")

        result = ma_fonction()
        assert result == "fallback"

    def test_with_error_handling_app_exception_raised(self):
        """Test que les exceptions app sont relancées"""
        from src.core.decorators import with_error_handling
        from src.core.errors_base import ExceptionApp

        @with_error_handling()
        def ma_fonction():
            raise ExceptionApp("App error")

        with pytest.raises(ExceptionApp):
            ma_fonction()


# ═══════════════════════════════════════════════════════════
# TESTS: Intégration complète
# ═══════════════════════════════════════════════════════════


class TestDecoratorsIntegration:
    """Tests d'intégration des décorateurs"""

    def test_combining_decorators(self):
        """Test combinaison de décorateurs"""
        from src.core.decorators import with_cache, with_error_handling
        from src.core.cache import Cache

        Cache.clear()

        @with_cache(ttl=60)
        @with_error_handling()
        def ma_fonction(x):
            return x * 2

        result = ma_fonction(5)
        assert result == 10

    def test_decorator_with_class_method(self):
        """Test décorateur avec méthode de classe"""
        from src.core.decorators import with_cache
        from src.core.cache import Cache

        Cache.clear()

        class MaClasse:
            @with_cache(key_func=lambda self, x: f"key_{x}", ttl=60)
            def ma_methode(self, x):
                return x * 3

        obj = MaClasse()
        result = obj.ma_methode(4)

        assert result == 12
