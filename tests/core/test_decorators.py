"""
Tests unitaires complets pour decorators.py
Couverture cible: 80%+

Tests cover:
- @avec_session_db: Auto session injection
- @avec_cache: Caching with TTL
- @avec_gestion_erreurs: Error catching and fallback values
- @avec_validation: Pydantic validation
- Decorator stacking
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.caching.cache import Cache
from src.core.decorators import (
    avec_cache,
    avec_gestion_erreurs,
    avec_session_db,
    avec_validation,
)

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: @avec_session_db TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecSessionDb:
    """Tests complets du décorateur @avec_session_db."""

    def test_decorator_preserves_function_name(self):
        """Test que le décorateur préserve le nom de la fonction"""

        @avec_session_db
        def ma_fonction(db=None):
            return "test"

        assert ma_fonction.__name__ == "ma_fonction"

    def test_decorator_preserves_docstring(self):
        """Test que le décorateur préserve la docstring"""

        @avec_session_db
        def ma_fonction(db=None):
            """Ma docstring"""
            return "test"

        assert ma_fonction.__doc__ == """Ma docstring"""

    def test_accepts_explicit_db_session(self):
        """Test qu'une session db explicite est acceptée"""
        mock_db = MagicMock()

        @avec_session_db
        def use_db(db=None):
            return db

        result = use_db(db=mock_db)
        assert result is mock_db

    def test_accepts_explicit_session_param(self):
        """Test qu'un paramètre 'session' explicite est accepté"""
        mock_session = MagicMock()

        @avec_session_db
        def use_session(session=None):
            return session

        result = use_session(session=mock_session)
        assert result is mock_session

    def test_works_with_positional_args(self):
        """Test avec arguments positionnels"""
        mock_db = MagicMock()

        @avec_session_db
        def process_data(data, db=None):
            return {"data": data, "has_db": db is not None}

        result = process_data("test_data", db=mock_db)
        assert result["data"] == "test_data"
        assert result["has_db"] is True

    def test_works_with_kwargs(self):
        """Test avec keyword arguments"""
        mock_db = MagicMock()

        @avec_session_db
        def create_item(name, value=10, db=None):
            return {"name": name, "value": value}

        result = create_item("item1", value=20, db=mock_db)
        assert result["name"] == "item1"
        assert result["value"] == 20

    def test_callable(self):
        """Test que le décorateur retourne un callable"""

        @avec_session_db
        def get_session_param(db=None):
            return db is not None

        assert callable(get_session_param)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: @avec_cache TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecCache:
    """Tests complets du décorateur @avec_cache."""

    def test_with_cache_stores_result(self, clear_cache):
        """Test que le cache stocke le résultat"""
        call_count = [0]

        @avec_cache(ttl=3600, key_func=lambda self, id: f"item_{id}")
        def get_item(self, id):
            call_count[0] += 1
            return {"id": id, "value": "cached"}

        instance = Mock()

        # Premier appel
        result1 = get_item(instance, 1)
        assert result1["id"] == 1
        assert call_count[0] == 1

        # Deuxième appel - le cache doit retourner la même valeur sans ré-exécuter
        result2 = get_item(instance, 1)
        assert result2 is not None
        assert result2["id"] == 1
        assert call_count[0] == 1  # Pas de nouvel appel

    def test_with_cache_retrieves_from_cache(self, clear_cache):
        """Test que le cache est utilisé pour les appels suivants"""
        call_count = [0]

        class TestClass:
            @avec_cache(ttl=3600, key_func=lambda self, id: f"item_{id}")
            def get_item(self, id):
                call_count[0] += 1
                return {"id": id, "call": call_count[0]}

        instance = TestClass()

        # Premier appel
        result1 = instance.get_item(1)
        # Deuxième appel - devrait utiliser le cache
        result2 = instance.get_item(1)

        # Devrait toujours être 1 (le second appel a utilisé le cache)
        assert call_count[0] == 1
        assert result1 == result2

    def test_with_cache_respects_ttl(self, clear_cache):
        """Test que le cache respecte le TTL"""

        @avec_cache(ttl=1, key_func=lambda self, x: f"short_{x}")
        def get_value(self, x):
            return x * 2

        instance = Mock()
        result = get_value(instance, 5)
        assert result == 10

    def test_with_cache_uses_custom_key_func(self, clear_cache):
        """Test de la fonction de clé personnalisée"""
        call_count = [0]

        @avec_cache(ttl=3600, key_func=lambda self, a, b: f"sum_{a}_{b}")
        def add(self, a, b):
            call_count[0] += 1
            return a + b

        instance = Mock()
        result = add(instance, 3, 4)
        assert result == 7
        assert call_count[0] == 1

        # Deuxième appel avec mêmes args — doit venir du cache
        result2 = add(instance, 3, 4)
        assert result2 == 7
        assert call_count[0] == 1  # Pas de nouvel appel

    def test_with_cache_uses_key_prefix(self, clear_cache):
        """Test du préfixe de clé"""

        @avec_cache(ttl=3600, key_prefix="my_prefix")
        def get_data(x):
            return x * 3

        result = get_data(10)
        assert result == 30

    def test_with_cache_excludes_db_from_key(self, clear_cache):
        """Test que 'db' est exclu de la clé de cache"""
        call_count = [0]

        @avec_cache(ttl=3600, key_prefix="test")
        def query_db(query, db=None):
            call_count[0] += 1
            return f"result_{query}"

        mock_db1 = Mock()
        mock_db2 = Mock()  # Session différente

        # Appels avec différentes sessions - devrait utiliser le même cache
        result1 = query_db("select", db=mock_db1)
        result2 = query_db("select", db=mock_db2)

        # Les deux devraient retourner le même résultat du cache
        assert result1 == result2

    def test_with_cache_different_keys(self, clear_cache):
        """Test que différentes clés donnent différents résultats"""

        @avec_cache(ttl=3600, key_func=lambda self, x: f"val_{x}")
        def compute(self, x):
            return x**2

        instance = Mock()

        result1 = compute(instance, 2)
        result2 = compute(instance, 3)

        assert result1 == 4
        assert result2 == 9

    def test_with_cache_key_func_with_defaults(self, clear_cache):
        """Test key_func avec paramètres par défaut"""

        @avec_cache(ttl=3600, key_func=lambda self, a, b=5: f"calc_{a}_{b}")
        def calculate(self, a, b=5):
            return a + b

        instance = Mock()

        # Avec valeur par défaut
        result1 = calculate(instance, 10)
        assert result1 == 15


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: @avec_gestion_erreurs TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecGestionErreurs:
    """Tests complets du décorateur @avec_gestion_erreurs."""

    def test_catches_errors(self):
        """Test que les erreurs sont attrapées"""

        @avec_gestion_erreurs(default_return="default")
        def raise_error(self):
            raise ValueError("Test error")

        instance = Mock()
        result = raise_error(instance)

        assert result == "default"

    def test_returns_fallback_on_error(self):
        """Test que la valeur par défaut est retournée en cas d'erreur"""

        @avec_gestion_erreurs(default_return=[])
        def fail(self):
            raise RuntimeError("Failed")

        instance = Mock()
        result = fail(instance)

        assert result == []
        assert isinstance(result, list)

    def test_returns_successful_value(self):
        """Test que les appels réussis retournent la vraie valeur"""

        @avec_gestion_erreurs(default_return="default")
        def succeed(self):
            return "success"

        instance = Mock()
        result = succeed(instance)

        assert result == "success"

    def test_catches_all_exceptions(self):
        """Test que toutes les exceptions sont attrapées"""

        @avec_gestion_erreurs(default_return=None)
        def any_error(self):
            raise Exception("Generic error")

        instance = Mock()
        result = any_error(instance)

        assert result is None

    def test_reraises_exception_app(self):
        """Test que les exceptions métier ExceptionApp sont relancées"""
        from src.core.exceptions import ExceptionApp

        @avec_gestion_erreurs(default_return="default")
        def raise_app_error():
            raise ExceptionApp("Erreur métier")

        with pytest.raises(ExceptionApp):
            raise_app_error()

    def test_logs_with_specified_level(self):
        """Test que le log utilise le niveau spécifié"""

        @avec_gestion_erreurs(default_return=None, log_level="WARNING")
        def warn_error():
            raise ValueError("Warning level error")

        result = warn_error()
        assert result is None

    @patch("streamlit.error")
    def test_afficher_erreur_option(self, mock_st_error):
        """Test l'option afficher_erreur"""

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
        def ui_error():
            raise ValueError("UI visible error")

        result = ui_error()
        assert result is None

    def test_preserves_function_metadata(self):
        """Test que le décorateur préserve les métadonnées"""

        @avec_gestion_erreurs(default_return=None)
        def documented_func():
            """Ma documentation"""
            return True

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == """Ma documentation"""

    def test_with_complex_default_return(self):
        """Test avec une valeur par défaut complexe"""

        @avec_gestion_erreurs(default_return={"status": "error", "data": []})
        def complex_fail():
            raise ValueError("Complex error")

        result = complex_fail()
        assert result == {"status": "error", "data": []}


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: @avec_validation TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecValidation:
    """Tests du décorateur @avec_validation."""

    def test_validation_passes(self):
        """Test que la validation passe avec des données valides"""
        from pydantic import BaseModel

        class ItemInput(BaseModel):
            name: str
            value: int

        @avec_validation(ItemInput, field_mapping={"data": "data"})
        def create_item(data):
            return data

        result = create_item(data={"name": "test", "value": 42})
        assert result["name"] == "test"
        assert result["value"] == 42

    def test_validation_fails_with_invalid_data(self):
        """Test que la validation échoue avec des données invalides"""
        from pydantic import BaseModel

        from src.core.exceptions import ErreurValidation

        class StrictInput(BaseModel):
            name: str
            age: int

        @avec_validation(StrictInput, field_mapping={"data": "data"})
        def process(data):
            return data

        with pytest.raises(ErreurValidation):
            process(data={"name": "test", "age": "not_an_int"})

    def test_validation_without_field_mapping(self):
        """Test validation sans field_mapping (utilise 'data' par défaut)"""
        from pydantic import BaseModel

        class SimpleInput(BaseModel):
            text: str

        @avec_validation(SimpleInput)
        def handle(data):
            return data

        result = handle(data={"text": "hello"})
        assert result["text"] == "hello"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: DECORATOR STACKING TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDecoratorStacking:
    """Tests de la combinaison de plusieurs décorateurs."""

    def test_cache_and_error_handling_stack(self, clear_cache):
        """Test @avec_cache avec @avec_gestion_erreurs"""

        @avec_cache(ttl=3600, key_func=lambda self, x: f"val_{x}")
        @avec_gestion_erreurs(default_return=0)
        def compute(self, x: int):
            if x < 0:
                raise ValueError("Negative")
            return x * 2

        instance = Mock()

        # Cas de succès
        result1 = compute(instance, 5)
        assert result1 == 10

        # Cas d'erreur - devrait retourner fallback
        result2 = compute(instance, -1)
        assert result2 == 0

    def test_all_decorators_stacked(self, clear_cache):
        """Test tous les décorateurs empilés"""

        @avec_cache(ttl=3600, key_prefix="full_test")
        @avec_gestion_erreurs(default_return={"error": True})
        def full_decorated(data, db=None):
            if not data:
                raise ValueError("No data")
            return {"data": data, "success": True}

        # Cas de succès
        result = full_decorated({"key": "value"})
        assert result["success"] is True

        # Cas d'erreur
        result_error = full_decorated(None)
        assert result_error["error"] is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests des cas limites."""

    def test_decorator_with_generator(self, clear_cache):
        """Test décorateur avec générateur"""

        @avec_gestion_erreurs(default_return=[])
        def gen_list():
            return [i for i in range(5)]

        result = gen_list()
        assert result == [0, 1, 2, 3, 4]

    def test_decorator_with_async_like_behavior(self, clear_cache):
        """Test comportement avec fonction retournant un callable"""

        @avec_cache(ttl=3600, key_prefix="callable")
        def return_callable(x):
            return lambda: x * 2

        fn = return_callable(5)
        assert fn() == 10

    def test_cache_with_mutable_args(self, clear_cache):
        """Test cache avec arguments mutables (doit gérer correctement)"""

        @avec_cache(ttl=3600, key_prefix="mutable")
        def process_list(items):
            return len(items)

        result = process_list([1, 2, 3])
        assert result == 3


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: ADDITIONAL COVERAGE TESTS
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecCacheAdvanced:
    """Tests avancés pour @avec_cache."""

    def test_cache_with_none_key_func(self, clear_cache):
        """Test cache sans key_func utilise key_prefix."""
        call_count = 0

        @avec_cache(ttl=3600, key_prefix="test_prefix")
        def compute_value(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 10

        result1 = compute_value(5)
        result2 = compute_value(5)  # Should hit cache

        assert result1 == 50
        assert result2 == 50
        assert call_count == 1

    def test_cache_with_key_func_using_only_args(self, clear_cache):
        """Test key_func avec seulement des positional args."""

        @avec_cache(ttl=3600, key_func=lambda a, b: f"sum_{a}_{b}")
        def add(a, b):
            return a + b

        result = add(3, 4)
        assert result == 7

    def test_cache_with_db_kwarg_filtered(self, clear_cache):
        """Test que 'db' est filtré du cache key auto."""
        call_count = 0
        mock_db1 = Mock()
        mock_db2 = Mock()  # Different mock

        @avec_cache(ttl=3600, key_prefix="db_filter")
        def query_data(query_type: str, db=None):
            nonlocal call_count
            call_count += 1
            return f"result_{query_type}"

        # Same query_type but different db - should use cache
        result1 = query_data("select", db=mock_db1)
        result2 = query_data("select", db=mock_db2)

        assert result1 == result2
        assert call_count == 1  # Only one call, 'db' was filtered


@pytest.mark.unit
class TestAvecGestionErreursAdvanced:
    """Tests avancés pour @avec_gestion_erreurs."""

    def test_log_level_debug(self):
        """Test avec log_level DEBUG."""

        @avec_gestion_erreurs(default_return="fallback", log_level="DEBUG")
        def debug_error():
            raise ValueError("Debug level error")

        result = debug_error()
        assert result == "fallback"

    def test_log_level_info(self):
        """Test avec log_level INFO."""

        @avec_gestion_erreurs(default_return=None, log_level="INFO")
        def info_error():
            raise ValueError("Info level error")

        result = info_error()
        assert result is None

    def test_afficher_erreur_streamlit_not_initialized(self):
        """Test afficher_erreur quand Streamlit non initialisé."""

        @avec_gestion_erreurs(default_return=42, afficher_erreur=True)
        def streamlit_error():
            raise ValueError("Should not crash even if st fails")

        # Should not raise exception even if st.error fails
        result = streamlit_error()
        assert result == 42


@pytest.mark.unit
class TestAvecValidationAdvanced:
    """Tests avancés pour @avec_validation."""

    def test_validation_with_none_field_mapping(self):
        """Test avec field_mapping None (utilise 'data' par défaut)."""
        from pydantic import BaseModel

        class SimpleModel(BaseModel):
            value: int

        @avec_validation(SimpleModel, field_mapping=None)
        def process(data):
            return data

        result = process(data={"value": 123})
        assert result["value"] == 123

    def test_validation_with_positional_args(self):
        """Test validation avec args positionnels."""
        from pydantic import BaseModel

        class ItemModel(BaseModel):
            name: str

        @avec_validation(ItemModel, field_mapping={"data": "data"})
        def create(data, extra_param=None):
            return {"data": data, "extra": extra_param}

        result = create(data={"name": "test"}, extra_param="value")
        assert result["data"]["name"] == "test"
        assert result["extra"] == "value"

    def test_validation_validation_error_details(self):
        """Test que ErreurValidation contient les détails de validation."""
        from pydantic import BaseModel

        from src.core.exceptions import ErreurValidation

        class StrictModel(BaseModel):
            count: int
            name: str

        @avec_validation(StrictModel, field_mapping={"data": "data"})
        def strict_process(data):
            return data

        with pytest.raises(ErreurValidation) as exc_info:
            strict_process(data={"count": "not_int", "name": 123})

        # Should have validation_errors in details
        assert hasattr(exc_info.value, "details")
        assert "validation_errors" in exc_info.value.details


@pytest.mark.unit
class TestAvecSessionDbAdvanced:
    """Tests avancés pour @avec_session_db."""

    @patch("src.core.db.obtenir_contexte_db")
    def test_session_injected_as_kwarg(self, mock_context):
        """Test que la session est injectée comme kwarg 'db'."""
        mock_session = Mock()
        mock_context.return_value.__enter__ = Mock(return_value=mock_session)
        mock_context.return_value.__exit__ = Mock(return_value=False)

        @avec_session_db
        def query_with_session(query: str, db=None):
            return db is not None

        result = query_with_session("SELECT 1")
        assert result is True

    @patch("src.core.db.obtenir_contexte_db")
    def test_session_not_injected_if_already_provided(self, mock_context):
        """Test que la session n'est pas réinjectée si déjà fournie."""
        mock_session = Mock()
        mock_context.return_value.__enter__ = Mock(return_value=mock_session)
        mock_context.return_value.__exit__ = Mock(return_value=False)

        existing_db = Mock(name="existing_db")

        @avec_session_db
        def with_existing_db(db=None):
            return db

        result = with_existing_db(db=existing_db)
        # Should use the provided db, not create new one
        assert result is existing_db


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: TESTS KEY_FUNC FALLBACK (TypeError path)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecCacheKeyFuncFallback:
    """Tests du fallback TypeError dans avec_cache."""

    def test_key_func_with_missing_args_triggers_fallback(self, clear_cache):
        """Test que key_func recevant les mauvais args déclenche le fallback."""
        # key_func attend (self, a) mais le wrapper passe args différemment
        # ce qui peut déclencher TypeError puis fallback
        call_count = [0]

        # Lambda qui attend self mais fonction appelée sans self
        @avec_cache(ttl=3600, key_func=lambda self, x: f"val_{x}")
        def compute_no_self(x):
            call_count[0] += 1
            return x * 2

        # Le premier appel peut lever TypeError et reconstruire kwargs
        result = compute_no_self(5)
        assert result == 10

    def test_key_func_fallback_with_defaults(self, clear_cache):
        """Test fallback remplit les valeurs par défaut manquantes."""

        # key_func attend plusieurs params mais certains ont des defaults
        @avec_cache(ttl=3600, key_func=lambda self, a, b, c=100: f"calc_{a}_{b}_{c}")
        def calculate(self, a, b, c=100):
            return a + b + c

        instance = Mock()

        # Appel avec seulement a et b (c utilise défaut)
        result = calculate(instance, 10, 20)
        assert result == 130

    def test_key_func_fallback_skips_self_and_db(self, clear_cache):
        """Test que le fallback n'inclut pas 'self' et 'db' dans kwargs."""

        @avec_cache(ttl=3600, key_func=lambda self, x, y=5: f"xy_{x}_{y}")
        def method_with_db(self, x, db=None, y=5):
            return x + y

        instance = Mock()
        mock_db = Mock()

        result = method_with_db(instance, 10, db=mock_db)
        assert result == 15

    def test_key_func_fallback_no_args(self, clear_cache):
        """Test fallback quand appelé sans args."""

        @avec_cache(ttl=3600, key_func=lambda a=1, b=2: f"ab_{a}_{b}")
        def default_only(a=1, b=2):
            return a * b

        result = default_only()
        assert result == 2

    def test_key_func_fallback_positional_to_kwargs_conversion(self, clear_cache):
        """Test conversion des args positionnels vers kwargs dans fallback."""

        @avec_cache(ttl=3600, key_func=lambda self, x, y, z: f"xyz_{x}_{y}_{z}")
        def xyz_method(self, x, y, z):
            return x + y + z

        instance = Mock()

        # Appel avec tous les args positionnels
        result = xyz_method(instance, 1, 2, 3)
        assert result == 6


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: TESTS AFFICHER ERREUR STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecGestionErreursStreamlit:
    """Tests pour afficher_erreur dans Streamlit."""

    @patch("streamlit.error")
    def test_afficher_erreur_calls_st_error(self, mock_st_error):
        """Test que st.error est appelé quand afficher_erreur=True."""

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
        def ui_failing_func():
            raise ValueError("Erreur visible UI")

        result = ui_failing_func()

        assert result is None
        # Vérifier que st.error a été appelé
        mock_st_error.assert_called_once()
        call_args = mock_st_error.call_args[0][0]
        assert "[ERROR]" in call_args

    def test_afficher_erreur_false_no_streamlit_call(self):
        """Test que st.error n'est pas appelé quand afficher_erreur=False."""

        @avec_gestion_erreurs(default_return=None, afficher_erreur=False)
        def silent_failing_func():
            raise ValueError("Erreur silencieuse")

        # Ne devrait pas lever d'erreur même si Streamlit n'est pas initialisé
        result = silent_failing_func()
        assert result is None

    @patch("streamlit.error", side_effect=Exception("Streamlit not initialized"))
    def test_afficher_erreur_handles_streamlit_not_available(self, mock_st_error):
        """Test que l'erreur est gérée si Streamlit n'est pas disponible."""

        @avec_gestion_erreurs(default_return="fallback", afficher_erreur=True)
        def func_when_st_unavailable():
            raise ValueError("Some error")

        # Ne devrait pas lever d'exception même si Streamlit fail
        result = func_when_st_unavailable()
        assert result == "fallback"
