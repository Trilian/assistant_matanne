"""Tests pour l'API safe de BaseService — Result[T, ErrorInfo].

Vérifie que les méthodes safe_* retournent des Result au lieu d'exceptions.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.result import (
    ErrorCode,
    ErrorInfo,
    Failure,
    Success,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


class FakeModel:
    """Modèle SQLAlchemy simulé pour les tests."""

    __name__ = "FakeModel"
    id = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def service():
    """Service BaseService avec modèle simulé."""
    from src.services.core.base.types import BaseService

    svc = BaseService(model=FakeModel, cache_ttl=0)
    return svc


# ═══════════════════════════════════════════════════════════
# TESTS safe_create
# ═══════════════════════════════════════════════════════════


class TestSafeCreate:
    """Tests pour safe_create."""

    def test_success(self, service):
        """safe_create retourne Success si create réussit."""
        entity = FakeModel(id=1, nom="Test")
        service.create = MagicMock(return_value=entity)
        service._emettre_evenement = MagicMock()

        result = service.safe_create({"nom": "Test"})

        assert isinstance(result, Success)
        assert result.value.id == 1
        assert result.value.nom == "Test"
        service._emettre_evenement.assert_called_once_with("created", {"id": 1})

    def test_failure_on_exception(self, service):
        """safe_create retourne Failure si create lève une exception."""
        service.create = MagicMock(side_effect=RuntimeError("DB error"))

        result = service.safe_create({"nom": "Test"})

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.INTERNAL_ERROR
        assert "DB error" in result.error.message

    def test_failure_maps_validation_error(self, service):
        """safe_create mappe ErreurValidation vers VALIDATION_ERROR."""
        from src.core.errors_base import ErreurValidation

        service.create = MagicMock(side_effect=ErreurValidation("Champ requis"))

        result = service.safe_create({"nom": ""})

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    def test_failure_maps_integrity_error(self, service):
        """safe_create mappe IntegrityError vers CONSTRAINT_VIOLATION."""
        from sqlalchemy.exc import IntegrityError

        service.create = MagicMock(
            side_effect=IntegrityError("dup", params=None, orig=Exception("unique"))
        )

        result = service.safe_create({"nom": "doublon"})

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.CONSTRAINT_VIOLATION

    def test_source_is_model_name(self, service):
        """La source dans ErrorInfo est le nom du modèle."""
        service.create = MagicMock(side_effect=RuntimeError("err"))

        result = service.safe_create({})

        assert result.error.source == "FakeModel"


# ═══════════════════════════════════════════════════════════
# TESTS safe_get_by_id
# ═══════════════════════════════════════════════════════════


class TestSafeGetById:
    """Tests pour safe_get_by_id."""

    def test_success_when_found(self, service):
        """safe_get_by_id retourne Success si trouvé."""
        entity = FakeModel(id=42, nom="Trouvé")
        service.get_by_id = MagicMock(return_value=entity)

        result = service.safe_get_by_id(42)

        assert isinstance(result, Success)
        assert result.value.id == 42

    def test_failure_when_not_found(self, service):
        """safe_get_by_id retourne Failure NOT_FOUND si None."""
        service.get_by_id = MagicMock(return_value=None)

        result = service.safe_get_by_id(99)

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.NOT_FOUND
        assert "99" in result.error.message
        assert result.error.message_utilisateur  # Message user-friendly

    def test_failure_on_exception(self, service):
        """safe_get_by_id retourne Failure si exception."""
        service.get_by_id = MagicMock(side_effect=RuntimeError("connection lost"))

        result = service.safe_get_by_id(1)

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.INTERNAL_ERROR

    def test_unwrap_or_returns_default(self, service):
        """unwrap_or retourne le default si non trouvé."""
        service.get_by_id = MagicMock(return_value=None)

        result = service.safe_get_by_id(99)
        value = result.unwrap_or(None)

        assert value is None


# ═══════════════════════════════════════════════════════════
# TESTS safe_get_all
# ═══════════════════════════════════════════════════════════


class TestSafeGetAll:
    """Tests pour safe_get_all."""

    def test_success_with_results(self, service):
        """safe_get_all retourne Success avec la liste."""
        entities = [FakeModel(id=1), FakeModel(id=2)]
        service.get_all = MagicMock(return_value=entities)

        result = service.safe_get_all()

        assert isinstance(result, Success)
        assert len(result.value) == 2

    def test_success_empty_list(self, service):
        """safe_get_all retourne Success([]) si vide."""
        service.get_all = MagicMock(return_value=[])

        result = service.safe_get_all()

        assert isinstance(result, Success)
        assert result.value == []

    def test_failure_on_exception(self, service):
        """safe_get_all retourne Failure si exception."""
        service.get_all = MagicMock(side_effect=RuntimeError("timeout"))

        result = service.safe_get_all()

        assert isinstance(result, Failure)

    def test_passes_parameters(self, service):
        """safe_get_all transmet les paramètres."""
        service.get_all = MagicMock(return_value=[])

        service.safe_get_all(skip=10, limit=5, filters={"actif": True})

        service.get_all.assert_called_once_with(10, 5, {"actif": True}, "id", False, None)


# ═══════════════════════════════════════════════════════════
# TESTS safe_update
# ═══════════════════════════════════════════════════════════


class TestSafeUpdate:
    """Tests pour safe_update."""

    def test_success(self, service):
        """safe_update retourne Success si mis à jour."""
        entity = FakeModel(id=1, nom="Modifié")
        service.update = MagicMock(return_value=entity)
        service._emettre_evenement = MagicMock()

        result = service.safe_update(1, {"nom": "Modifié"})

        assert isinstance(result, Success)
        assert result.value.nom == "Modifié"
        service._emettre_evenement.assert_called_once_with("updated", {"id": 1})

    def test_failure_not_found(self, service):
        """safe_update retourne Failure NOT_FOUND si non trouvé."""
        from src.core.errors_base import ErreurNonTrouve

        service.update = MagicMock(side_effect=ErreurNonTrouve("pas trouvé"))

        result = service.safe_update(99, {"nom": "X"})

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.NOT_FOUND
        assert result.error.message_utilisateur  # User-friendly message

    def test_failure_on_other_exception(self, service):
        """safe_update retourne Failure INTERNAL si autre exception."""
        service.update = MagicMock(side_effect=RuntimeError("DB error"))

        result = service.safe_update(1, {"nom": "X"})

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.INTERNAL_ERROR


# ═══════════════════════════════════════════════════════════
# TESTS safe_delete
# ═══════════════════════════════════════════════════════════


class TestSafeDelete:
    """Tests pour safe_delete."""

    def test_success(self, service):
        """safe_delete retourne Success(True) si supprimé."""
        service.delete = MagicMock(return_value=True)
        service._emettre_evenement = MagicMock()

        result = service.safe_delete(1)

        assert isinstance(result, Success)
        assert result.value is True
        service._emettre_evenement.assert_called_once_with("deleted", {"id": 1})

    def test_failure_when_not_deleted(self, service):
        """safe_delete retourne Failure NOT_FOUND si False."""
        service.delete = MagicMock(return_value=False)

        result = service.safe_delete(99)

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.NOT_FOUND

    def test_failure_on_exception(self, service):
        """safe_delete retourne Failure si exception."""
        service.delete = MagicMock(side_effect=RuntimeError("FK violation"))

        result = service.safe_delete(1)

        assert isinstance(result, Failure)


# ═══════════════════════════════════════════════════════════
# TESTS safe_count
# ═══════════════════════════════════════════════════════════


class TestSafeCount:
    """Tests pour safe_count."""

    def test_success(self, service):
        """safe_count retourne Success(int)."""
        service.count = MagicMock(return_value=42)

        result = service.safe_count()

        assert isinstance(result, Success)
        assert result.value == 42

    def test_success_zero(self, service):
        """safe_count retourne Success(0)."""
        service.count = MagicMock(return_value=0)

        result = service.safe_count()

        assert isinstance(result, Success)
        assert result.value == 0

    def test_failure_on_exception(self, service):
        """safe_count retourne Failure si exception."""
        service.count = MagicMock(side_effect=RuntimeError("connection"))

        result = service.safe_count()

        assert isinstance(result, Failure)


# ═══════════════════════════════════════════════════════════
# TESTS _mapper_code_erreur
# ═══════════════════════════════════════════════════════════


class TestMapperCodeErreur:
    """Tests pour le mapping exception → ErrorCode."""

    def test_maps_erreur_non_trouve(self, service):
        """Mappe ErreurNonTrouve → NOT_FOUND."""
        from src.core.errors_base import ErreurNonTrouve

        code = service._mapper_code_erreur(ErreurNonTrouve("x"))
        assert code == ErrorCode.NOT_FOUND

    def test_maps_erreur_validation(self, service):
        """Mappe ErreurValidation → VALIDATION_ERROR."""
        from src.core.errors_base import ErreurValidation

        code = service._mapper_code_erreur(ErreurValidation("x"))
        assert code == ErrorCode.VALIDATION_ERROR

    def test_maps_erreur_ia(self, service):
        """Mappe ErreurServiceIA → AI_ERROR."""
        from src.core.errors_base import ErreurServiceIA

        code = service._mapper_code_erreur(ErreurServiceIA("x"))
        assert code == ErrorCode.AI_ERROR

    def test_maps_unknown_to_internal(self, service):
        """Exception inconnue → INTERNAL_ERROR."""
        code = service._mapper_code_erreur(ValueError("x"))
        assert code == ErrorCode.INTERNAL_ERROR


# ═══════════════════════════════════════════════════════════
# TESTS _emettre_evenement
# ═══════════════════════════════════════════════════════════


class TestEmettreEvenement:
    """Tests pour l'émission d'événements domaine."""

    def test_emits_event(self, service):
        """_emettre_evenement émet via le bus."""
        with patch("src.services.core.events.bus.obtenir_bus") as mock_bus:
            mock_instance = MagicMock()
            mock_bus.return_value = mock_instance

            service._emettre_evenement("created", {"id": 1})

            mock_instance.emettre.assert_called_once_with(
                "entity.FakeModel.created",
                {"model": "FakeModel", "id": 1},
                source="FakeModel",
            )

    def test_event_never_blocks_operations(self, service):
        """Si le bus échoue, l'opération ne bloque pas."""
        with patch(
            "src.services.core.events.bus.obtenir_bus",
            side_effect=RuntimeError("bus broken"),
        ):
            # Ne doit pas lever d'exception
            service._emettre_evenement("created", {"id": 1})

    def test_event_data_defaults_to_empty(self, service):
        """Si data est None, utilise un dict vide."""
        with patch("src.services.core.events.bus.obtenir_bus") as mock_bus:
            mock_instance = MagicMock()
            mock_bus.return_value = mock_instance

            service._emettre_evenement("deleted")

            mock_instance.emettre.assert_called_once_with(
                "entity.FakeModel.deleted",
                {"model": "FakeModel"},
                source="FakeModel",
            )


# ═══════════════════════════════════════════════════════════
# TESTS health_check
# ═══════════════════════════════════════════════════════════


class TestHealthCheck:
    """Tests pour health_check de BaseService."""

    def test_healthy_when_db_ok(self, service):
        """health_check retourne HEALTHY si count() fonctionne."""
        from src.services.core.base.protocols import ServiceStatus

        service.count = MagicMock(return_value=10)

        health = service.health_check()

        assert health.status == ServiceStatus.HEALTHY
        assert "10" in health.message
        assert health.latency_ms >= 0
        assert health.details["count"] == 10
        assert "FakeModel" in health.service_name

    def test_unhealthy_when_db_fails(self, service):
        """health_check retourne UNHEALTHY si count() échoue."""
        from src.services.core.base.protocols import ServiceStatus

        service.count = MagicMock(side_effect=RuntimeError("connection refused"))

        health = service.health_check()

        assert health.status == ServiceStatus.UNHEALTHY
        assert "connection refused" in health.message
        assert health.latency_ms >= 0


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION — Chaînage Result
# ═══════════════════════════════════════════════════════════


class TestResultChaining:
    """Tests de chaînage fonctionnel avec les méthodes safe."""

    def test_map_on_success(self, service):
        """Chaînage .map() sur un safe_get_by_id réussi."""
        entity = FakeModel(id=1, nom="Tarte")
        service.get_by_id = MagicMock(return_value=entity)

        name = service.safe_get_by_id(1).map(lambda e: e.nom).unwrap_or("Inconnu")

        assert name == "Tarte"

    def test_map_on_failure(self, service):
        """Chaînage .map() sur un safe_get_by_id échoué → unwrap_or."""
        service.get_by_id = MagicMock(return_value=None)

        name = service.safe_get_by_id(99).map(lambda e: e.nom).unwrap_or("Inconnu")

        assert name == "Inconnu"

    def test_on_failure_callback(self, service):
        """on_failure exécute le callback sur erreur."""
        service.get_by_id = MagicMock(return_value=None)
        errors = []

        service.safe_get_by_id(99).on_failure(lambda e: errors.append(e.code))

        assert errors == [ErrorCode.NOT_FOUND]
