"""Tests pour le Middleware Pipeline — Composable middleware chain."""

import pytest

from src.services.core.middleware.pipeline import (
    ErrorHandlerMiddleware,
    LoggingMiddleware,
    Middleware,
    MiddlewareContext,
    ServicePipeline,
    service_method,
)

# ═══════════════════════════════════════════════════════════
# MIDDLEWARE CONTEXT
# ═══════════════════════════════════════════════════════════


class TestMiddlewareContext:
    """Tests du contexte middleware."""

    def test_creation_defaut(self):
        ctx = MiddlewareContext()
        assert ctx.service_name == ""
        assert ctx.method_name == ""
        assert ctx.use_cache is False
        assert ctx.use_rate_limit is False
        assert ctx.cache_hit is False

    def test_duration(self):
        ctx = MiddlewareContext()
        ctx.set_timing()
        # Simulate some work
        _ = sum(range(1000))
        ctx.end_timing()
        assert ctx.duration_ms > 0

    def test_duration_sans_timing(self):
        ctx = MiddlewareContext()
        assert ctx.duration_ms == 0.0

    def test_metadata(self):
        ctx = MiddlewareContext(
            service_name="recettes",
            method_name="get_all",
            metadata={"key": "value"},
        )
        assert ctx.metadata["key"] == "value"


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE DE BASE
# ═══════════════════════════════════════════════════════════


class TestMiddlewareBase:
    """Tests du middleware de base (passthrough)."""

    def test_passthrough(self):
        """Le middleware de base passe simplement au suivant."""
        middleware = Middleware()
        ctx = MiddlewareContext()
        result = middleware.process(ctx, lambda c: "résultat")
        assert result == "résultat"


# ═══════════════════════════════════════════════════════════
# LOGGING MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestLoggingMiddleware:
    """Tests du middleware de logging."""

    def test_log_succes(self):
        middleware = LoggingMiddleware()
        ctx = MiddlewareContext(service_name="test", method_name="op")

        result = middleware.process(ctx, lambda c: 42)
        assert result == 42
        assert ctx.start_time > 0
        assert ctx.end_time > 0
        assert ctx.duration_ms >= 0

    def test_log_exception(self):
        middleware = LoggingMiddleware()
        ctx = MiddlewareContext(service_name="test", method_name="op")

        def next_handler(c):
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            middleware.process(ctx, next_handler)

        assert ctx.error is not None
        assert ctx.end_time > 0


# ═══════════════════════════════════════════════════════════
# ERROR HANDLER MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestErrorHandlerMiddleware:
    """Tests du middleware de gestion d'erreurs."""

    def test_succes_passe_a_travers(self):
        middleware = ErrorHandlerMiddleware()
        ctx = MiddlewareContext()
        result = middleware.process(ctx, lambda c: "ok")
        assert result == "ok"

    def test_exception_retourne_fallback(self):
        middleware = ErrorHandlerMiddleware()
        ctx = MiddlewareContext(fallback_value="défaut")

        def next_handler(c):
            raise RuntimeError("erreur inattendue")

        result = middleware.process(ctx, next_handler)
        assert result == "défaut"
        assert ctx.error is not None

    def test_exception_fallback_none(self):
        middleware = ErrorHandlerMiddleware()
        ctx = MiddlewareContext()  # fallback_value=None par défaut

        def next_handler(c):
            raise RuntimeError("erreur")

        result = middleware.process(ctx, next_handler)
        assert result is None

    def test_pas_de_couplage_streamlit(self):
        """Vérifie que le middleware n'importe PAS streamlit."""
        import sys

        # S'assurer que streamlit n'est pas importé par ce middleware
        module = sys.modules.get("src.services.core.middleware.pipeline")
        if module:
            source = getattr(module, "__file__", "")
            if source:
                with open(source, encoding="utf-8") as f:
                    content = f.read()
                assert "import streamlit" not in content
                assert "from streamlit" not in content


# ═══════════════════════════════════════════════════════════
# SERVICE PIPELINE
# ═══════════════════════════════════════════════════════════


class TestServicePipeline:
    """Tests du pipeline composable."""

    def test_pipeline_vide(self):
        """Un pipeline vide exécute directement la fonction."""
        pipeline = ServicePipeline()
        ctx = MiddlewareContext(args=(), kwargs={"x": 5})

        result = pipeline.execute(lambda x=0: x * 2, ctx)
        assert result == 10

    def test_pipeline_avec_middleware(self):
        pipeline = ServicePipeline()
        pipeline.add(LoggingMiddleware())

        ctx = MiddlewareContext(args=(), kwargs={"x": 5})
        result = pipeline.execute(lambda x=0: x * 2, ctx)
        assert result == 10
        assert ctx.duration_ms >= 0

    def test_pipeline_chainage_add(self):
        """add() retourne self pour le chaînage."""
        pipeline = ServicePipeline()
        result = pipeline.add(LoggingMiddleware()).add(ErrorHandlerMiddleware())
        assert result is pipeline

    def test_pipeline_ordre_execution(self):
        """Les middlewares s'exécutent dans l'ordre d'ajout."""
        order = []

        class TrackingMiddleware(Middleware):
            def __init__(self, name):
                self.name = name

            def process(self, ctx, next_handler):
                order.append(f"pre_{self.name}")
                result = next_handler(ctx)
                order.append(f"post_{self.name}")
                return result

        pipeline = ServicePipeline()
        pipeline.add(TrackingMiddleware("A"))
        pipeline.add(TrackingMiddleware("B"))
        pipeline.add(TrackingMiddleware("C"))

        ctx = MiddlewareContext(args=(), kwargs={})
        pipeline.execute(lambda: "done", ctx)

        assert order == ["pre_A", "pre_B", "pre_C", "post_C", "post_B", "post_A"]

    def test_middleware_court_circuite(self):
        """Un middleware peut court-circuiter le pipeline."""

        class ShortCircuit(Middleware):
            def process(self, ctx, next_handler):
                return "court-circuité"  # N'appelle PAS next_handler

        pipeline = ServicePipeline()
        pipeline.add(ShortCircuit())

        # Cette fonction ne devrait pas être appelée
        called = {"value": False}

        def should_not_run():
            called["value"] = True
            return "original"

        ctx = MiddlewareContext(args=(), kwargs={})
        result = pipeline.execute(should_not_run, ctx)
        assert result == "court-circuité"
        assert called["value"] is False


# ═══════════════════════════════════════════════════════════
# FACTORIES DE PIPELINE
# ═══════════════════════════════════════════════════════════


class TestPipelineFactories:
    """Tests des méthodes de création de pipeline."""

    def test_default(self):
        pipeline = ServicePipeline.default()
        assert len(pipeline._middlewares) == 5

    def test_minimal(self):
        pipeline = ServicePipeline.minimal()
        assert len(pipeline._middlewares) == 2

    def test_ai_pipeline(self):
        pipeline = ServicePipeline.ai_pipeline()
        assert len(pipeline._middlewares) == 4


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR @service_method
# ═══════════════════════════════════════════════════════════


class TestServiceMethodDecorator:
    """Tests du décorateur @service_method."""

    def test_basique(self):
        """Le décorateur exécute la fonction normalement."""

        class MyService:
            service_name = "test"

            @service_method()
            def do_work(self, value: int) -> int:
                return value * 2

        service = MyService()
        result = service.do_work(5)
        assert result == 10

    def test_preserve_nom(self):
        class MyService:
            @service_method()
            def ma_methode(self):
                return 42

        assert MyService.ma_methode.__name__ == "ma_methode"

    def test_fallback_sur_erreur(self):
        """En cas d'erreur, retourne la valeur de fallback."""

        class MyService:
            service_name = "test"

            @service_method(fallback=[])
            def do_work(self) -> list:
                raise RuntimeError("boom")

        service = MyService()
        result = service.do_work()
        assert result == []

    def test_avec_pipeline_custom(self):
        """Un pipeline custom peut être passé."""
        custom_pipeline = ServicePipeline()
        custom_pipeline.add(LoggingMiddleware())

        class MyService:
            service_name = "custom"

            @service_method(pipeline=custom_pipeline)
            def do_work(self) -> str:
                return "custom"

        service = MyService()
        result = service.do_work()
        assert result == "custom"

    def test_sans_service_name(self):
        """Fonctionne même sans attribut service_name."""

        class SomeClass:
            @service_method()
            def compute(self, x: int) -> int:
                return x + 1

        obj = SomeClass()
        result = obj.compute(5)
        assert result == 6


# ═══════════════════════════════════════════════════════════
# INTÉGRATION — Pipeline complet
# ═══════════════════════════════════════════════════════════


class TestPipelineIntegration:
    """Tests d'intégration end-to-end du pipeline."""

    def test_logging_plus_error_handling(self):
        """Scénario réaliste: logging + error handling."""
        pipeline = ServicePipeline.minimal()

        ctx = MiddlewareContext(
            service_name="recettes",
            method_name="get_all",
            args=(),
            kwargs={},
            fallback_value=[],
        )

        def get_recettes():
            raise ValueError("DB indisponible")

        result = pipeline.execute(get_recettes, ctx)
        assert result == []
        assert ctx.error is not None

    def test_pipeline_succes_complet(self):
        """Scénario: appel réussi à travers tout le pipeline."""
        pipeline = ServicePipeline()
        pipeline.add(LoggingMiddleware())
        pipeline.add(ErrorHandlerMiddleware())

        data = [{"nom": "Tarte"}, {"nom": "Gratin"}]
        ctx = MiddlewareContext(
            service_name="recettes",
            method_name="get_all",
            args=(),
            kwargs={},
        )

        result = pipeline.execute(lambda: data, ctx)
        assert result == data
        assert ctx.duration_ms >= 0
        assert ctx.error is None
