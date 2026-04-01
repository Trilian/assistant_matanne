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


class DummyResponse(BaseModel):
    """Réponse simple pour les tests."""
    message: str
    status: int = 200


class ServiceBasic(metaclass=ServiceMeta):
    """Service de base para tester la génération automatique."""

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

    async def _private_method(self) -> str:
        return "private"

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
    """Service utilisant le décorateur @dual_api."""

    async def get_data(self) -> dict[str, str]:
        return {"key": "value"}

    async def _private_method(self) -> str:
        return "private"


@pytest.mark.unit
class TestServiceMetaGeneration:
    """Tests de génération de méthodes _sync."""

    def test_sync_method_generated(self) -> None:
        """Vérifie qu'une méthode _sync a été générée."""
        service = ServiceBasic()
        assert hasattr(service, "get_greeting_sync")
        assert callable(service.get_greeting_sync)

    def test_sync_method_works(self) -> None:
        """Vérifie que la méthode _sync fonctionne."""
        service = ServiceBasic()
        result = service.get_greeting_sync("Alice")
        assert result == "Hello, Alice!"

    def test_private_method_not_generated(self) -> None:
        """Vérifie que les méthodes privées n'ont pas de _sync."""
        service = ServiceBasic()
        assert not hasattr(service, "_private_method_sync")

    def test_special_method_not_generated(self) -> None:
        """Vérifie que les méthodes spéciales n'ont pas de _sync."""
        service = ServiceBasic()
        assert not hasattr(service, "__aenter___sync")
        assert not hasattr(service, "__aexit___sync")

    def test_manual_override_preserved(self) -> None:
        """Vérifie que le override manuel est préservé."""
        service = ServiceWithManualSync()
        result = service.do_something_sync()
        assert result == "manual_sync_override"


@pytest.mark.unit
class TestServiceMetaSignatures:
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

    def test_method_with_no_args(self) -> None:
        """Vérifie qu'une méthode sans arguments fonctionne."""
        service = ServiceBasic()
        result = service.get_response_sync()
        assert isinstance(result, DummyResponse)
        assert result.message == "OK"


@pytest.mark.unit
class TestServiceMetaReturnTypes:
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


@pytest.mark.unit
class TestServiceMetaExceptions:
    """Tests de la gestion des exceptions."""

    def test_exception_propagated_in_sync(self) -> None:
        """Vérifie que les exceptions sont propagées."""
        service = ServiceBasic()
        with pytest.raises(ValueError, match="Test error"):
            service.raise_error_sync()


@pytest.mark.unit
class TestServiceMetaInstance:
    """Tests de l'état et des instances."""

    def test_self_state_preserved(self) -> None:
        """Vérifie que l'état d'instance est préservé."""
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


@pytest.mark.unit
class TestServiceMetaInheritance:
    """Tests de l'héritage."""

    def test_base_class_method_accessible(self) -> None:
        """Vérifie que la méthode de la classe de base fonctionne."""
        service = ServiceDerived()
        result = service.base_method_sync()
        assert result == "from_base"

    def test_derived_class_method_accessible(self) -> None:
        """Vérifie que la méthode de la classe dérivée fonctionne."""
        service = ServiceDerived()
        result = service.derived_method_sync()
        assert result == "from_derived"


@pytest.mark.unit
class TestDualApiDecorator:
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


@pytest.mark.unit
class TestServiceMetaAsyncSyncIntegration:
    """Tests d'intégration entre async et sync."""

    def test_async_and_sync_produce_same_result(self) -> None:
        """Vérifie que async et sync produisent le même résultat."""
        service = ServiceBasic()
        async_result = asyncio.run(service.get_greeting("David"))
        sync_result = service.get_greeting_sync("David")
        assert async_result == sync_result

    def test_called_with_keyword_args(self) -> None:
        """Vérifie que les keyword arguments fonctionnent."""
        service = ServiceBasic()
        result = service.get_greeting_sync(user="Eve")
        assert result == "Hello, Eve!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
