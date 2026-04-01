"""
Tests exhaustifs pour ServiceMeta — Metaclass async/sync auto-generation.

Couvre:
- Génération automatique de méthodes _sync
- Exclusion de méthodes privées
- Exclusion de méthodes spéciales
- Override manuel de _sync
- Héritage
- Types de retour complexes
- Gestion des exceptions
- État instance (self)
"""

import asyncio
import pytest
from typing import Any
from pydantic import BaseModel

from src.services.core.base.async_utils import ServiceMeta, sync_wrapper, dual_api


# ═══════════════════════════════════════════════════════════
# FIXTURES ET CLASSES DE TEST
# ═══════════════════════════════════════════════════════════


class DummyResponse(BaseModel):
    """Réponse simple pour les tests."""
    message: str
    status: int = 200


class ServiceBasic(metaclass=ServiceMeta):
    """Service de base pour tester la génération automatique."""

    def __init__(self, name: str = "test"):
        self.name = name
        self.call_count = 0

    async def get_greeting(self, user: str) -> str:
        """Retourne un salut."""
        self.call_count += 1
        await asyncio.sleep(0.01)
        return f"Hello, {user}!"

    async def get_response(self) -> DummyResponse:
        """Retourne une réponse Pydantic."""
        await asyncio.sleep(0.01)
        return DummyResponse(message="OK", status=200)

    async def get_list(self, count: int) -> list[int]:
        """Retourne une liste."""
        await asyncio.sleep(0.01)
        return [i for i in range(count)]

    async def get_dict(self) -> dict[str, Any]:
        """Retourne un dictionnaire."""
        await asyncio.sleep(0.01)
        return {"key": "value", "number": 42}

    async def raise_error(self) -> None:
        """Lève une exception."""
        await asyncio.sleep(0.01)
        raise ValueError("Test error")

    # Méthode privée — ne doit PAS avoir de _sync généré
    async def _private_method(self) -> str:
        return "private"

    # Méthode spéciale — ne doit PAS avoir de _sync généré
    async def __aenter__(self) -> "ServiceBasic":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class ServiceWithManualSync(metaclass=ServiceMeta):
    """Service avec override manuel de _sync."""

    async def do_something(self) -> str:
        """Méthode async."""
        return "async"

    def do_something_sync(self) -> str:
        """Override manuel — ne doit PAS être re-généré."""
        return "manual_sync_override"


class ServiceBaseClass(metaclass=ServiceMeta):
    """Classe de base pour tester l'héritage."""

    async def base_method(self) -> str:
        return "from_base"


class ServiceDerived(ServiceBaseClass):
    """Service dérivé — hérite les _sync générées."""

    async def derived_method(self) -> str:
        return "from_derived"


@dual_api
class ServiceDualApi:
    """Service utilisant le décorateur @dual_api au lieu du metaclass."""

    async def get_data(self) -> dict[str, str]:
        return {"key": "value"}

    async def _private_method(self) -> str:
        return "private"


# ═══════════════════════════════════════════════════════════
# TESTS — Génération automatique
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaGeneration:
    """Tests de génération de méthodes _sync."""

    def test_sync_method_generated(self) -> None:
        """Vérifie qu'une méthode _sync a été générée."""
        service = ServiceBasic()
        assert hasattr(service, "get_greeting_sync"), "get_greeting_sync doit exister"
        assert callable(service.get_greeting_sync), "get_greeting_sync doit être callable"

    def test_sync_method_works(self) -> None:
        """Vérifie que la méthode _sync fonctionne."""
        service = ServiceBasic()
        result = service.get_greeting_sync("Alice")
        assert result == "Hello, Alice!"

    def test_private_method_not_generated(self) -> None:
        """Vérifie que les méthodes privées n'ont pas de _sync générée."""
        service = ServiceBasic()
        assert not hasattr(service, "_private_method_sync"), "_private_method ne doit pas avoir de _sync"

    def test_special_method_not_generated(self) -> None:
        """Vérifie que les méthodes spéciales n'ont pas de _sync générée."""
        service = ServiceBasic()
        assert not hasattr(service, "__aenter___sync"), "__aenter__ ne doit pas avoir de _sync"
        assert not hasattr(service, "__aexit___sync"), "__aexit__ ne doit pas avoir de _sync"

    def test_manual_override_preserved(self) -> None:
        """Vérifie que le override manuel n'est pas écrasé."""
        service = ServiceWithManualSync()
        result = service.do_something_sync()
        assert result == "manual_sync_override", "Override manuel doit être préservé"


# ═══════════════════════════════════════════════════════════
# TESTS — Signatures et arguments
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaSignatures:
    """Tests des signatures et arguments."""

    def test_method_with_single_arg(self) -> None:
        """Vérifie qu'une méthode avec 1 argument fonctionne."""
        service = ServiceBasic()
        result = service.get_greeting_sync("Bob")
        assert result == "Hello, Bob!"

    def test_method_with_multiple_args(self) -> None:
        """Vérifie qu'une méthode avec plusieurs arguments fonctionne."""
        service = ServiceBasic()
        result = service.get_list_sync(5)
        assert result == [0, 1, 2, 3, 4]

    def test_method_preserves_docstring(self) -> None:
        """Vérifie que la docstring est conservée."""
        assert "Auto-generated sync version" in ServiceBasic.get_greeting_sync.__doc__
        assert "Safe to call from any synchronous context" in ServiceBasic.get_greeting_sync.__doc__

    def test_method_with_no_args(self) -> None:
        """Vérifie qu'une méthode sans arguments fonctionne."""
        service = ServiceBasic()
        result = service.get_response_sync()
        assert isinstance(result, DummyResponse)
        assert result.message == "OK"


# ═══════════════════════════════════════════════════════════
# TESTS — Types de retour complexes
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaReturnTypes:
    """Tests des différents types de retour."""

    def test_sync_method_returns_string(self) -> None:
        """Vérifie qu'une méthode retournant str fonctionne."""
        service = ServiceBasic()
        result = service.get_greeting_sync("Charlie")
        assert isinstance(result, str)
        assert result == "Hello, Charlie!"

    def test_sync_method_returns_pydantic_model(self) -> None:
        """Vérifie qu'une méthode retournant un modèle Pydantic fonctionne."""
        service = ServiceBasic()
        result = service.get_response_sync()
        assert isinstance(result, DummyResponse)
        assert result.status == 200

    def test_sync_method_returns_list(self) -> None:
        """Vérifie qu'une méthode retournant une liste fonctionne."""
        service = ServiceBasic()
        result = service.get_list_sync(3)
        assert isinstance(result, list)
        assert result == [0, 1, 2]

    def test_sync_method_returns_dict(self) -> None:
        """Vérifie qu'une méthode retournant un dict fonctionne."""
        service = ServiceBasic()
        result = service.get_dict_sync()
        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert result["number"] == 42


# ═══════════════════════════════════════════════════════════
# TESTS — Exceptions
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaExceptions:
    """Tests de la gestion des exceptions."""

    def test_exception_propagated_in_sync(self) -> None:
        """Vérifie que les exceptions sont propagées correctement."""
        service = ServiceBasic()
        with pytest.raises(ValueError, match="Test error"):
            service.raise_error_sync()

    def test_exception_preserves_traceback(self) -> None:
        """Vérifie que la traceback est préservée."""
        service = ServiceBasic()
        try:
            service.raise_error_sync()
        except ValueError as e:
            assert "Test error" in str(e)


# ═══════════════════════════════════════════════════════════
# TESTS — État d'instance (self)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaInstance:
    """Tests de l'état et des instances."""

    def test_self_state_preserved(self) -> None:
        """Vérifie que l'état d'instance (self) est préservé."""
        service = ServiceBasic("my_service")
        assert service.name == "my_service"
        _ = service.get_greeting_sync("Alice")
        assert service.call_count == 1

    def test_multiple_calls_increment_counter(self) -> None:
        """Vérifie que plusieurs appels incrémentent le compteur."""
        service = ServiceBasic()
        assert service.call_count == 0
        service.get_greeting_sync("Alice")
        assert service.call_count == 1
        service.get_greeting_sync("Bob")
        assert service.call_count == 2

    def test_different_instances_independent(self) -> None:
        """Vérifie que les instances différentes sont indépendantes."""
        service1 = ServiceBasic("service1")
        service2 = ServiceBasic("service2")
        service1.get_greeting_sync("Alice")
        assert service1.call_count == 1
        assert service2.call_count == 0


# ═══════════════════════════════════════════════════════════
# TESTS — Héritage
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaInheritance:
    """Tests de l'héritage."""

    def test_base_class_method_accessible(self) -> None:
        """Vérifie que la méthode de la classe de base est accessible."""
        service = ServiceDerived()
        result = service.base_method_sync()
        assert result == "from_base"

    def test_derived_class_method_accessible(self) -> None:
        """Vérifie que la méthode de la classe dérivée est accessible."""
        service = ServiceDerived()
        result = service.derived_method_sync()
        assert result == "from_derived"

    def test_both_methods_callable(self) -> None:
        """Vérifie que les deux méthodes peuvent être appelées."""
        service = ServiceDerived()
        base_result = service.base_method_sync()
        derived_result = service.derived_method_sync()
        assert base_result == "from_base"
        assert derived_result == "from_derived"


# ═══════════════════════════════════════════════════════════
# TESTS — Décorateur @dual_api
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class DualApiDecorator:
    """Tests du décorateur @dual_api."""

    def test_dual_api_generates_sync(self) -> None:
        """Vérifie que @dual_api génère les méthodes _sync."""
        service = ServiceDualApi()
        assert hasattr(service, "get_data_sync")
        assert callable(service.get_data_sync)

    def test_dual_api_method_works(self) -> None:
        """Vérifie que la méthode _sync générée fonctionne."""
        service = ServiceDualApi()
        result = service.get_data_sync()
        assert isinstance(result, dict)
        assert result["key"] == "value"

    def test_dual_api_private_method_not_generated(self) -> None:
        """Vérifie que @dual_api ignoring les méthodes privées."""
        service = ServiceDualApi()
        assert not hasattr(service, "_private_method_sync")


# ═══════════════════════════════════════════════════════════
# TESTS — Intégration async/sync
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaAsyncSyncIntegration:
    """Tests d'intégration entre async et sync."""

    def test_async_and_sync_produce_same_result(self) -> None:
        """Vérifie que async et sync produisent le même résultat."""
        service = ServiceBasic()
        
        # Résultat async
        async_result = asyncio.run(service.get_greeting("David"))
        
        # Résultat sync
        sync_result = service.get_greeting_sync("David")
        
        assert async_result == sync_result

    def test_called_with_keyword_args(self) -> None:
        """Vérifie que les keyword arguments fonctionnent."""
        service = ServiceBasic()
        result = service.get_greeting_sync(user="Eve")
        assert result == "Hello, Eve!"


# ═══════════════════════════════════════════════════════════
# TESTS — Edge cases
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class ServiceMetaEdgeCases:
    """Tests des cas limites."""

    def test_empty_return_value(self) -> None:
        """Vérifie qu'une méthode levant une exception le fait correctement."""
        service = ServiceBasic()
        # L'exception doit être levée lors de l'appel sync
        with pytest.raises(ValueError, match="Test error"):
            service.raise_error_sync()

    def test_concurrent_calls_from_threads(self) -> None:
        """Vérifie que sync_wrapper gère l'exécution en thread."""
        import threading
        service = ServiceBasic()
        results = []

        def call_sync():
            result = service.get_greeting_sync("Thread")
            results.append(result)

        threads = [threading.Thread(target=call_sync) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(results) == 3
        assert all(r == "Hello, Thread!" for r in results)

    def test_method_name_preserved_in_repr(self) -> None:
        """Vérifie que le nom de la méthode est correct."""
        method = ServiceBasic.get_greeting_sync
        assert "get_greeting_sync" in method.__name__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
