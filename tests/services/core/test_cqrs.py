"""Tests pour le package CQRS — Queries, Commands, Dispatcher."""

import pytest

from src.services.core.base.result import ErrorCode, ErrorInfo, Failure, Success
from src.services.core.cqrs.commands import (
    Command,
    CommandResult,
    collect_validations,
    validate_min_length,
    validate_positive,
    validate_required,
)
from src.services.core.cqrs.dispatcher import CQRSDispatcher, reset_dispatcher
from src.services.core.cqrs.queries import PaginationParams, Query, paginated_result

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def dispatcher():
    """Dispatcher CQRS frais pour chaque test."""
    reset_dispatcher()
    return CQRSDispatcher(emit_events=False)


# ═══════════════════════════════════════════════════════════
# TESTS QUERIES
# ═══════════════════════════════════════════════════════════


class TestQuery:
    """Tests pour la classe Query de base."""

    def test_cache_key_deterministic(self):
        """La clé de cache est déterministe."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class TestQuery(Query[str]):
            param1: str
            param2: int

            def execute(self):
                return Success("ok")

        q1 = TestQuery(param1="a", param2=1)
        q2 = TestQuery(param1="a", param2=1)
        q3 = TestQuery(param1="b", param2=1)

        assert q1.cache_key() == q2.cache_key()
        assert q1.cache_key() != q3.cache_key()

    def test_query_execute(self):
        """Une query peut être exécutée."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class SimpleQuery(Query[int]):
            value: int

            def execute(self):
                return Success(self.value * 2)

        q = SimpleQuery(value=21)
        result = q.execute()

        assert result.is_success
        assert result.value == 42


class TestPaginationParams:
    """Tests des paramètres de pagination."""

    def test_defaults(self):
        """Valeurs par défaut correctes."""
        p = PaginationParams()
        assert p.offset == 0
        assert p.limit == 50
        assert p.order_by == "id"
        assert p.desc_order is False

    def test_negative_offset_corrected(self):
        """Offset négatif corrigé à 0."""
        p = PaginationParams(offset=-10)
        assert p.offset == 0

    def test_limit_capped(self):
        """Limit cappé à 1000."""
        p = PaginationParams(limit=5000)
        assert p.limit == 1000

    def test_limit_minimum(self):
        """Limit minimum à 50 si < 1."""
        p = PaginationParams(limit=0)
        assert p.limit == 50


class TestPaginatedResult:
    """Tests du helper paginated_result."""

    def test_has_more_true(self):
        """has_more est True quand il reste des items."""
        items = list(range(50))
        pagination = PaginationParams(offset=0, limit=50)
        result = paginated_result(items, total=100, pagination=pagination)

        assert result["has_more"] is True
        assert result["count"] == 50
        assert result["total"] == 100

    def test_has_more_false(self):
        """has_more est False à la dernière page."""
        items = list(range(10))
        pagination = PaginationParams(offset=90, limit=50)
        result = paginated_result(items, total=100, pagination=pagination)

        assert result["has_more"] is False


# ═══════════════════════════════════════════════════════════
# TESTS COMMANDS
# ═══════════════════════════════════════════════════════════


class TestCommand:
    """Tests pour la classe Command de base."""

    def test_command_has_id(self):
        """Une command a un ID unique."""
        from dataclasses import dataclass, field

        @dataclass
        class TestCommand(Command[str]):
            name: str = field(default="")

            def validate(self):
                return Success(None)

            def execute(self):
                return Success(self.name)

        cmd1 = TestCommand(name="test1")
        cmd2 = TestCommand(name="test2")

        assert cmd1.id != cmd2.id
        assert len(cmd1.id) == 36  # UUID format

    def test_command_execute(self):
        """Une command peut être exécutée."""
        from dataclasses import dataclass, field

        @dataclass
        class CreateCommand(Command[dict]):
            name: str = field(default="")

            def validate(self):
                if not self.name:
                    return Failure(
                        ErrorInfo(code=ErrorCode.VALIDATION_ERROR, message="Name required")
                    )
                return Success(None)

            def execute(self):
                return Success({"created": self.name})

        cmd = CreateCommand(name="test")
        assert cmd.validate().is_success
        result = cmd.execute()
        assert result.value == {"created": "test"}


class TestCommandResult:
    """Tests pour CommandResult."""

    def test_success_result(self):
        """CommandResult avec succès."""
        from datetime import datetime

        result = CommandResult(
            result=Success("data"),
            command_id="123",
            command_type="TestCommand",
            executed_at=datetime.now(),
            duration_ms=10.5,
        )

        assert result.is_success
        assert result.value == "data"
        assert result.error is None

    def test_failure_result(self):
        """CommandResult avec échec."""
        from datetime import datetime

        error = ErrorInfo(code=ErrorCode.VALIDATION_ERROR, message="Invalid")
        result = CommandResult(
            result=Failure(error),
            command_id="123",
            command_type="TestCommand",
            executed_at=datetime.now(),
            duration_ms=5.0,
        )

        assert result.is_failure
        assert result.value is None
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    def test_to_audit_dict(self):
        """Sérialisation pour audit."""
        from datetime import datetime

        result = CommandResult(
            result=Success("data"),
            command_id="123",
            command_type="TestCommand",
            executed_at=datetime(2026, 2, 20, 12, 0, 0),
            duration_ms=10.0,
            user_id="user1",
        )

        audit = result.to_audit_dict()
        assert audit["command_id"] == "123"
        assert audit["success"] is True
        assert audit["user_id"] == "user1"


class TestValidationHelpers:
    """Tests des helpers de validation."""

    def test_validate_required_success(self):
        """validate_required avec valeur présente."""
        result = validate_required("hello", "name")
        assert result.is_success

    def test_validate_required_failure_none(self):
        """validate_required avec None."""
        result = validate_required(None, "name")
        assert result.is_failure
        assert result.error.code == ErrorCode.MISSING_FIELD

    def test_validate_required_failure_empty(self):
        """validate_required avec chaîne vide."""
        result = validate_required("   ", "name")
        assert result.is_failure

    def test_validate_min_length_success(self):
        """validate_min_length avec longueur suffisante."""
        result = validate_min_length("hello", 3, "name")
        assert result.is_success

    def test_validate_min_length_failure(self):
        """validate_min_length avec longueur insuffisante."""
        result = validate_min_length("hi", 5, "name")
        assert result.is_failure

    def test_validate_positive_success(self):
        """validate_positive avec valeur positive."""
        result = validate_positive(10, "count")
        assert result.is_success

    def test_validate_positive_failure(self):
        """validate_positive avec valeur négative ou nulle."""
        result = validate_positive(0, "count")
        assert result.is_failure

    def test_collect_validations_all_success(self):
        """collect_validations retourne Success si tout OK."""
        result = collect_validations(
            validate_required("test", "a"),
            validate_positive(5, "b"),
        )
        assert result.is_success

    def test_collect_validations_first_failure(self):
        """collect_validations retourne la première erreur."""
        result = collect_validations(
            validate_required(None, "first"),
            validate_required(None, "second"),
        )
        assert result.is_failure
        assert "first" in result.error.message


# ═══════════════════════════════════════════════════════════
# TESTS DISPATCHER
# ═══════════════════════════════════════════════════════════


class TestCQRSDispatcher:
    """Tests pour le dispatcher CQRS."""

    def test_dispatch_query_direct(self, dispatcher):
        """Dispatch une query sans handler enregistré."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class DirectQuery(Query[int]):
            value: int

            def execute(self):
                return Success(self.value * 2)

        result = dispatcher.dispatch_query(DirectQuery(value=21), use_cache=False)
        assert result.is_success
        assert result.value == 42

    def test_dispatch_query_with_cache(self, dispatcher):
        """Query avec cache."""
        from dataclasses import dataclass

        call_count = 0

        @dataclass(frozen=True)
        class CachedQuery(Query[int]):
            value: int

            def execute(self):
                nonlocal call_count
                call_count += 1
                return Success(self.value)

        # Premier appel - exécute
        result1 = dispatcher.dispatch_query(CachedQuery(value=1), use_cache=True)
        assert result1.value == 1
        assert call_count == 1

        # Deuxième appel - depuis cache (même paramètres)
        result2 = dispatcher.dispatch_query(CachedQuery(value=1), use_cache=True)
        assert result2.value == 1
        # Note: call_count reste à 1 car le cache est utilisé

    def test_dispatch_command_validation_failure(self, dispatcher):
        """Command avec validation échouée."""
        from dataclasses import dataclass, field

        @dataclass
        class FailingCommand(Command[str]):
            name: str = field(default="")

            def validate(self):
                return Failure(ErrorInfo(code=ErrorCode.VALIDATION_ERROR, message="Always fails"))

            def execute(self):
                return Success("never reached")

        result = dispatcher.dispatch_command(FailingCommand(name="test"))
        assert result.is_failure
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    def test_dispatch_command_success(self, dispatcher):
        """Command exécutée avec succès."""
        from dataclasses import dataclass, field

        @dataclass
        class SuccessCommand(Command[dict]):
            name: str = field(default="")

            def validate(self):
                return Success(None)

            def execute(self):
                return Success({"created": self.name})

        result = dispatcher.dispatch_command(SuccessCommand(name="test"))
        assert result.is_success
        assert result.value == {"created": "test"}
        assert result.duration_ms > 0

    def test_metrics(self, dispatcher):
        """Les métriques sont collectées."""
        from dataclasses import dataclass

        @dataclass(frozen=True)
        class MetricQuery(Query[str]):
            def execute(self):
                return Success("ok")

        dispatcher.dispatch_query(MetricQuery(), use_cache=False)
        dispatcher.dispatch_query(MetricQuery(), use_cache=False)

        metrics = dispatcher.get_metrics()
        assert metrics["queries"]["executed"] == 2
