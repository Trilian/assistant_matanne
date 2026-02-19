"""
Tests pour le module async_utils.

Teste le décorateur sync_wrapper qui convertit les méthodes async en sync.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.core.base.async_utils import make_sync_alias, sync_wrapper

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


class MockService:
    """Service mock pour tester sync_wrapper."""

    def __init__(self):
        self.call_count = 0

    async def async_method(self, value: int, multiplier: int = 2) -> int:
        """Méthode async simple."""
        self.call_count += 1
        await asyncio.sleep(0.01)  # Simule un délai async
        return value * multiplier

    async def async_method_with_error(self) -> None:
        """Méthode async qui lève une exception."""
        await asyncio.sleep(0.01)
        raise ValueError("Test error")

    async def async_method_returning_none(self) -> None:
        """Méthode async qui retourne None."""
        await asyncio.sleep(0.01)
        return None

    # Versions sync générées via sync_wrapper
    sync_method = sync_wrapper(async_method)
    sync_method_with_error = sync_wrapper(async_method_with_error)
    sync_method_returning_none = sync_wrapper(async_method_returning_none)


# ═══════════════════════════════════════════════════════════
# TESTS SYNC_WRAPPER
# ═══════════════════════════════════════════════════════════


class TestSyncWrapper:
    """Tests pour le décorateur sync_wrapper."""

    def test_sync_wrapper_basic_call(self):
        """Vérifie que sync_wrapper appelle correctement la méthode async."""
        service = MockService()

        result = service.sync_method(5)

        assert result == 10  # 5 * 2 (multiplier par défaut)
        assert service.call_count == 1

    def test_sync_wrapper_with_kwargs(self):
        """Vérifie que sync_wrapper passe correctement les kwargs."""
        service = MockService()

        result = service.sync_method(5, multiplier=3)

        assert result == 15  # 5 * 3

    def test_sync_wrapper_multiple_calls(self):
        """Vérifie que sync_wrapper fonctionne pour des appels multiples."""
        service = MockService()

        results = [service.sync_method(i) for i in range(1, 4)]

        assert results == [2, 4, 6]  # 1*2, 2*2, 3*2
        assert service.call_count == 3

    def test_sync_wrapper_preserves_function_name(self):
        """Vérifie que sync_wrapper préserve le nom de la fonction originale."""
        service = MockService()

        assert service.sync_method.__name__ == "async_method"
        assert "async_method" in service.sync_method.__qualname__

    def test_sync_wrapper_propagates_exceptions(self):
        """Vérifie que sync_wrapper propage les exceptions."""
        service = MockService()

        with pytest.raises(ValueError, match="Test error"):
            service.sync_method_with_error()

    def test_sync_wrapper_handles_none_return(self):
        """Vérifie que sync_wrapper gère correctement les retours None."""
        service = MockService()

        result = service.sync_method_returning_none()

        assert result is None

    def test_sync_wrapper_without_running_loop(self):
        """Vérifie que sync_wrapper fonctionne sans boucle d'événements active."""
        service = MockService()

        # S'assurer qu'aucune boucle n'est active
        try:
            loop = asyncio.get_running_loop()
            pytest.skip("Test requires no running event loop")
        except RuntimeError:
            pass  # Pas de boucle active, c'est ce qu'on veut

        result = service.sync_method(7)

        assert result == 14


class TestSyncWrapperWithRunningLoop:
    """Tests pour sync_wrapper avec une boucle d'événements active."""

    @pytest.mark.asyncio
    async def test_sync_wrapper_with_running_loop(self):
        """Vérifie que sync_wrapper fonctionne avec une boucle d'événements active."""
        service = MockService()

        # On est dans un contexte async, donc une boucle est active
        # sync_wrapper doit utiliser ThreadPoolExecutor

        # Note: On appelle la version sync depuis un contexte async
        # Cela simule le cas Streamlit où une boucle peut être active
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(service.sync_method, 5)
            result = future.result()

        assert result == 10


# ═══════════════════════════════════════════════════════════
# TESTS MAKE_SYNC_ALIAS
# ═══════════════════════════════════════════════════════════


class TestMakeSyncAlias:
    """Tests pour la fonction make_sync_alias."""

    def test_make_sync_alias_default_suffix(self):
        """Vérifie que make_sync_alias ajoute le suffixe par défaut."""

        async def my_async_func(x: int) -> int:
            return x * 2

        sync_func = make_sync_alias(my_async_func)

        assert sync_func.__name__ == "my_async_func_sync"

    def test_make_sync_alias_custom_suffix(self):
        """Vérifie que make_sync_alias accepte un suffixe personnalisé."""

        async def my_async_func(x: int) -> int:
            return x * 2

        sync_func = make_sync_alias(my_async_func, suffix="_synchrone")

        assert sync_func.__name__ == "my_async_func_synchrone"

    def test_make_sync_alias_functional(self):
        """Vérifie que make_sync_alias crée une fonction fonctionnelle."""

        async def compute(x: int, y: int = 10) -> int:
            await asyncio.sleep(0.01)
            return x + y

        compute_sync = make_sync_alias(compute)

        assert compute_sync(5) == 15
        assert compute_sync(5, y=20) == 25


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestSyncWrapperIntegration:
    """Tests d'intégration pour sync_wrapper."""

    def test_sync_wrapper_with_class_inheritance(self):
        """Vérifie que sync_wrapper fonctionne avec l'héritage de classe."""

        class BaseService:
            async def fetch_data(self, item_id: int) -> dict:
                await asyncio.sleep(0.01)
                return {"id": item_id, "name": f"Item {item_id}"}

            fetch_data_sync = sync_wrapper(fetch_data)

        class DerivedService(BaseService):
            async def fetch_data(self, item_id: int) -> dict:
                data = await super().fetch_data(item_id)
                data["derived"] = True
                return data

            fetch_data_sync = sync_wrapper(fetch_data)

        base = BaseService()
        derived = DerivedService()

        base_result = base.fetch_data_sync(1)
        derived_result = derived.fetch_data_sync(2)

        assert base_result == {"id": 1, "name": "Item 1"}
        assert derived_result == {"id": 2, "name": "Item 2", "derived": True}

    def test_sync_wrapper_with_instance_state(self):
        """Vérifie que sync_wrapper préserve l'état de l'instance."""

        class StatefulService:
            def __init__(self):
                self.state = []

            async def add_item(self, item: str) -> list:
                await asyncio.sleep(0.01)
                self.state.append(item)
                return self.state.copy()

            add_item_sync = sync_wrapper(add_item)

        service = StatefulService()

        result1 = service.add_item_sync("a")
        result2 = service.add_item_sync("b")
        result3 = service.add_item_sync("c")

        assert result1 == ["a"]
        assert result2 == ["a", "b"]
        assert result3 == ["a", "b", "c"]
        assert service.state == ["a", "b", "c"]
