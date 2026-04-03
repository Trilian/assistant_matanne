"""Tests pour le décorateur @service_factory et la migration des factories.

Vérifie que le décorateur enregistre les services dans le registre
et que les factories migrées fonctionnent correctement.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.core.registry import (
    ServiceRegistry,
    service_factory,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def fresh_registry():
    """Registre frais pour chaque test."""
    registry = ServiceRegistry()
    return registry


# ═══════════════════════════════════════════════════════════
# TESTS @service_factory
# ═══════════════════════════════════════════════════════════


class TestServiceFactoryDecorator:
    """Tests pour le décorateur @service_factory."""

    def test_registers_factory_in_registry(self, fresh_registry):
        """Le décorateur enregistre la factory dans le registre."""
        with patch(
            "src.services.core.registry.obtenir_registre",
            return_value=fresh_registry,
        ):

            @service_factory("test_service", tags={"test"})
            def create_service():
                return MagicMock(name="TestService")

            assert fresh_registry.est_enregistre("test_service")

    def test_decorated_function_returns_singleton(self, fresh_registry):
        """La factory décorée retourne toujours la même instance."""
        call_count = 0

        with patch(
            "src.services.core.registry.obtenir_registre",
            return_value=fresh_registry,
        ):

            @service_factory("singleton_test")
            def create_service():
                nonlocal call_count
                call_count += 1
                return MagicMock(name=f"Instance-{call_count}")

            # Appeler 3 fois → même instance
            s1 = create_service()
            s2 = create_service()
            s3 = create_service()

            assert s1 is s2
            assert s2 is s3
            assert call_count == 1  # factory appelée une seule fois

    def test_tags_are_stored(self, fresh_registry):
        """Les tags sont correctement stockés."""
        with patch(
            "src.services.core.registry.obtenir_registre",
            return_value=fresh_registry,
        ):

            @service_factory("tagged", tags={"cuisine", "ia"})
            def create_tagged():
                return MagicMock()

            create_tagged()  # Instancie le service

            cuisine = fresh_registry.par_tag("cuisine")
            assert "tagged" in cuisine

            ia = fresh_registry.par_tag("ia")
            assert "tagged" in ia

    def test_accessible_via_registry(self, fresh_registry):
        """Le service est accessible via registre.obtenir()."""
        with patch(
            "src.services.core.registry.obtenir_registre",
            return_value=fresh_registry,
        ):
            instance = MagicMock(name="DirectAccess")

            @service_factory("direct_access")
            def create():
                return instance

            # Accès via le registre
            from_registry = fresh_registry.obtenir("direct_access")
            assert from_registry is instance

    def test_factory_no_tags(self, fresh_registry):
        """Le décorateur fonctionne sans tags."""
        with patch(
            "src.services.core.registry.obtenir_registre",
            return_value=fresh_registry,
        ):

            @service_factory("no_tags")
            def create():
                return MagicMock()

            assert fresh_registry.est_enregistre("no_tags")


# ═══════════════════════════════════════════════════════════
# TESTS Factory avec callable (non-classe)
# ═══════════════════════════════════════════════════════════


class TestRegistryCallableFactory:
    """Vérifie que le registre accepte des callables (pas seulement des types)."""

    def test_register_lambda(self, fresh_registry):
        """Enregistrer une lambda comme factory."""
        fresh_registry.enregistrer("lambda_svc", lambda: {"type": "lambda"})

        result = fresh_registry.obtenir("lambda_svc")
        assert result == {"type": "lambda"}

    def test_register_function(self, fresh_registry):
        """Enregistrer une fonction comme factory."""

        def create_service():
            svc = MagicMock()
            svc.service_type = "FunctionService"
            return svc

        fresh_registry.enregistrer("func_svc", create_service)

        result = fresh_registry.obtenir("func_svc")
        assert result.service_type == "FunctionService"

    def test_register_class(self, fresh_registry):
        """Enregistrer une classe (le pattern classique)."""

        class SimpleService:
            pass

        fresh_registry.enregistrer("class_svc", SimpleService)

        result = fresh_registry.obtenir("class_svc")
        assert isinstance(result, SimpleService)


# ═══════════════════════════════════════════════════════════
# TESTS Factory migrées — Smoke tests
# ═══════════════════════════════════════════════════════════


class TestMigratedFactories:
    """Smoke tests vérifiant que l'import des factories migrées fonctionne."""

    def test_recettes_factory_importable(self):
        """obtenir_service_recettes est importable."""
        from src.services.cuisine.recettes.service import obtenir_service_recettes

        assert callable(obtenir_service_recettes)

    def test_courses_factory_importable(self):
        """obtenir_service_courses est importable."""
        from src.services.cuisine.courses.service import obtenir_service_courses

        assert callable(obtenir_service_courses)

    def test_inventaire_factory_importable(self):
        """obtenir_service_inventaire est importable."""
        from src.services.inventaire.service import obtenir_service_inventaire

        assert callable(obtenir_service_inventaire)

    def test_service_factory_decorator_importable(self):
        """Le décorateur est importable depuis le package core."""
        from src.services.core.registry import service_factory

        assert callable(service_factory)
