"""
Tests pour src/core/middleware/ — Pipeline composable.
"""

import time
from unittest.mock import MagicMock

import pytest

from src.core.middleware import (
    CacheMiddleware,
    CircuitBreakerMiddleware,
    Contexte,
    LogMiddleware,
    Middleware,
    NextFn,
    Pipeline,
    RetryMiddleware,
    TimingMiddleware,
    ValidationMiddleware,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _reset_cache():
    """Reset le singleton CacheMultiNiveau entre tests."""
    from src.core.caching.orchestrator import CacheMultiNiveau

    CacheMultiNiveau._instance = None
    CacheMultiNiveau(l2_enabled=False, l3_enabled=False)
    yield
    CacheMultiNiveau._instance = None


class _TraceMiddleware(Middleware):
    """Middleware de test qui enregistre les appels."""

    def __init__(self, nom: str = "trace"):
        self._nom_custom = nom
        self.appels: list[str] = []

    @property
    def nom(self) -> str:
        return self._nom_custom

    def traiter(self, ctx: Contexte, suivant: NextFn):
        self.appels.append(f"avant_{self._nom_custom}")
        result = suivant(ctx)
        self.appels.append(f"apres_{self._nom_custom}")
        return result


# ═══════════════════════════════════════════════════════════
# TESTS CONTEXTE
# ═══════════════════════════════════════════════════════════


class TestContexte:
    """Tests pour Contexte."""

    def test_creation_defauts(self):
        """Test création avec valeurs par défaut."""
        ctx = Contexte()
        assert ctx.operation == ""
        assert ctx.params == {}
        assert ctx.result is None
        assert ctx.error is None
        assert ctx.a_echoue is False

    def test_creation_avec_valeurs(self):
        """Test création avec valeurs explicites."""
        ctx = Contexte(operation="charger", params={"page": 1})
        assert ctx.operation == "charger"
        assert ctx.params["page"] == 1

    def test_duree_ms(self):
        """Test calcul durée."""
        ctx = Contexte()
        time.sleep(0.01)
        assert ctx.duree_ms >= 10

    def test_a_echoue(self):
        """Test flag erreur."""
        ctx = Contexte()
        assert ctx.a_echoue is False

        ctx.error = ValueError("boom")
        assert ctx.a_echoue is True

    def test_avec_metadata_fluent(self):
        """Test avec_metadata retourne self (fluent)."""
        ctx = Contexte(operation="test")
        result = ctx.avec_metadata(source="api", retry=True)
        assert result is ctx
        assert ctx.metadata["source"] == "api"
        assert ctx.metadata["retry"] is True


# ═══════════════════════════════════════════════════════════
# TESTS PIPELINE
# ═══════════════════════════════════════════════════════════


class TestPipeline:
    """Tests pour Pipeline."""

    def test_pipeline_vide(self):
        """Test pipeline sans middleware (passthrough)."""
        pipeline = Pipeline("test").construire()
        ctx = Contexte(operation="noop")

        result = pipeline.executer(ctx, lambda c: 42)

        assert result == 42
        assert ctx.result == 42

    def test_pipeline_un_middleware(self):
        """Test pipeline avec un middleware."""
        trace = _TraceMiddleware("m1")
        pipeline = Pipeline("test").utiliser(trace).construire()
        ctx = Contexte(operation="op")

        result = pipeline.executer(ctx, lambda c: "ok")

        assert result == "ok"
        assert trace.appels == ["avant_m1", "apres_m1"]

    def test_pipeline_ordre_execution(self):
        """Test ordre d'exécution: premier ajouté = premier exécuté."""
        t1 = _TraceMiddleware("m1")
        t2 = _TraceMiddleware("m2")
        t3 = _TraceMiddleware("m3")

        pipeline = Pipeline("test").utiliser(t1).utiliser(t2).utiliser(t3).construire()
        ctx = Contexte(operation="op")

        pipeline.executer(ctx, lambda c: None)

        # Ordre onion: m1 avant → m2 avant → m3 avant → handler → m3 après → m2 après → m1 après
        assert t1.appels == ["avant_m1", "apres_m1"]
        assert t2.appels == ["avant_m2", "apres_m2"]
        assert t3.appels == ["avant_m3", "apres_m3"]

    def test_pipeline_immutable_apres_construction(self):
        """Test qu'on ne peut plus ajouter de middleware après construction."""
        pipeline = Pipeline("test").construire()

        with pytest.raises(RuntimeError, match="déjà construite"):
            pipeline.utiliser(_TraceMiddleware())

    def test_pipeline_decorer(self):
        """Test décorateur @pipeline.decorer."""
        trace = _TraceMiddleware("m1")
        pipeline = Pipeline("test").utiliser(trace).construire()

        @pipeline.decorer
        def ma_fonction(x: int = 5) -> int:
            return x * 2

        result = ma_fonction(x=3)

        assert result == 6
        assert trace.appels == ["avant_m1", "apres_m1"]

    def test_pipeline_len(self):
        """Test __len__."""
        pipeline = Pipeline("test").utiliser(_TraceMiddleware()).utiliser(_TraceMiddleware())
        assert len(pipeline) == 2

    def test_pipeline_repr(self):
        """Test __repr__."""
        pipeline = Pipeline("mon_pipeline").utiliser(_TraceMiddleware("log"))
        assert "mon_pipeline" in repr(pipeline)
        assert "log" in repr(pipeline)

    def test_pipeline_propagation_erreur(self):
        """Test propagation d'erreur à travers la pipeline."""
        trace = _TraceMiddleware("m1")
        pipeline = Pipeline("test").utiliser(trace).construire()
        ctx = Contexte(operation="fail")

        def handler_qui_plante(c):
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            pipeline.executer(ctx, handler_qui_plante)


# ═══════════════════════════════════════════════════════════
# TESTS LOG MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestLogMiddleware:
    """Tests pour LogMiddleware."""

    def test_log_success(self, caplog):
        """Test logging sur succès."""
        middleware = LogMiddleware(niveau="INFO")
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="charger_recettes")

        with caplog.at_level("INFO"):
            pipeline.executer(ctx, lambda c: "ok")

        assert any("DÉBUT" in r.message and "charger_recettes" in r.message for r in caplog.records)
        assert any("FIN" in r.message and "charger_recettes" in r.message for r in caplog.records)

    def test_log_error(self, caplog):
        """Test logging sur erreur."""
        middleware = LogMiddleware(niveau="INFO")
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="op_fail")

        with caplog.at_level("ERROR"):
            with pytest.raises(RuntimeError):
                pipeline.executer(ctx, lambda c: (_ for _ in ()).throw(RuntimeError("fail")))

    def test_log_avec_params(self, caplog):
        """Test logging avec paramètres inclus."""
        middleware = LogMiddleware(niveau="INFO", inclure_params=True)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="op", params={"page": 1})

        with caplog.at_level("INFO"):
            pipeline.executer(ctx, lambda c: None)

        assert any("params=" in r.message for r in caplog.records)


# ═══════════════════════════════════════════════════════════
# TESTS TIMING MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestTimingMiddleware:
    """Tests pour TimingMiddleware."""

    def test_timing_enregistre_duree(self):
        """Test que la durée est enregistrée dans metadata."""
        middleware = TimingMiddleware(seuil_ms=1000, enregistrer_metrique=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="op")

        pipeline.executer(ctx, lambda c: None)

        assert "duree_ms" in ctx.metadata
        assert isinstance(ctx.metadata["duree_ms"], float)

    def test_timing_alerte_seuil(self, caplog):
        """Test alerte quand seuil dépassé."""
        middleware = TimingMiddleware(seuil_ms=1, enregistrer_metrique=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="lent")

        def handler_lent(c):
            time.sleep(0.01)
            return "ok"

        with caplog.at_level("WARNING"):
            pipeline.executer(ctx, handler_lent)

        assert any("LENT" in r.message for r in caplog.records)

    def test_timing_pas_alerte_sous_seuil(self, caplog):
        """Test pas d'alerte quand sous le seuil."""
        middleware = TimingMiddleware(seuil_ms=5000, enregistrer_metrique=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="rapide")

        with caplog.at_level("WARNING"):
            pipeline.executer(ctx, lambda c: "ok")

        assert not any("LENT" in r.message for r in caplog.records)

    def test_timing_enregistre_meme_sur_erreur(self):
        """Test timing même en cas d'erreur."""
        middleware = TimingMiddleware(seuil_ms=5000, enregistrer_metrique=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="fail")

        with pytest.raises(ValueError):
            pipeline.executer(ctx, lambda c: (_ for _ in ()).throw(ValueError("boom")))

        assert "duree_ms" in ctx.metadata


# ═══════════════════════════════════════════════════════════
# TESTS RETRY MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestRetryMiddleware:
    """Tests pour RetryMiddleware."""

    def test_retry_success_premier_essai(self):
        """Test pas de retry si succès au premier essai."""
        middleware = RetryMiddleware(max_tentatives=3, delai_base=0.01)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="ok")

        result = pipeline.executer(ctx, lambda c: "success")

        assert result == "success"
        assert ctx.metadata["tentative"] == 1

    def test_retry_success_deuxieme_essai(self):
        """Test retry réussi au deuxième essai."""
        appels = {"count": 0}

        def handler_fragile(c):
            appels["count"] += 1
            if appels["count"] < 2:
                raise ValueError("temporaire")
            return "ok"

        middleware = RetryMiddleware(max_tentatives=3, delai_base=0.01)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="fragile")

        result = pipeline.executer(ctx, handler_fragile)

        assert result == "ok"
        assert appels["count"] == 2
        assert ctx.metadata["tentative"] == 2

    def test_retry_echec_definitif(self):
        """Test échec après toutes les tentatives."""
        middleware = RetryMiddleware(max_tentatives=2, delai_base=0.01)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="impossible")

        def handler_qui_plante(c):
            raise RuntimeError("permanent")

        with pytest.raises(RuntimeError, match="permanent"):
            pipeline.executer(ctx, handler_qui_plante)

        assert ctx.metadata.get("retries_epuises") is True

    def test_retry_filtre_exceptions(self):
        """Test retry seulement sur exceptions spécifiées."""
        middleware = RetryMiddleware(
            max_tentatives=3,
            delai_base=0.01,
            exceptions=(ConnectionError,),
        )
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="strict")

        # ValueError ne déclenche PAS de retry
        with pytest.raises(ValueError):
            pipeline.executer(
                ctx,
                lambda c: (_ for _ in ()).throw(ValueError("pas retriable")),
            )

    def test_retry_callback(self):
        """Test callback sur_retry appelé."""
        retries = []

        def on_retry(tentative, erreur):
            retries.append((tentative, str(erreur)))

        appels = {"count": 0}

        def handler(c):
            appels["count"] += 1
            if appels["count"] < 3:
                raise ValueError("temp")
            return "ok"

        middleware = RetryMiddleware(max_tentatives=3, delai_base=0.01, sur_retry=on_retry)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="cb")

        pipeline.executer(ctx, handler)

        assert len(retries) == 2
        assert retries[0][0] == 1


# ═══════════════════════════════════════════════════════════
# TESTS CACHE MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestCacheMiddleware:
    """Tests pour CacheMiddleware."""

    def test_cache_miss_puis_hit(self):
        """Test miss au premier appel, hit au deuxième."""
        appels = {"count": 0}

        def handler(c):
            appels["count"] += 1
            return f"result_{appels['count']}"

        middleware = CacheMiddleware(ttl=300)
        pipeline = Pipeline("test").utiliser(middleware).construire()

        ctx1 = Contexte(operation="charger", params={"id": 1})
        result1 = pipeline.executer(ctx1, handler)
        assert result1 == "result_1"
        assert ctx1.metadata["cache_hit"] is False

        ctx2 = Contexte(operation="charger", params={"id": 1})
        result2 = pipeline.executer(ctx2, handler)
        assert result2 == "result_1"  # Même résultat (du cache)
        assert ctx2.metadata["cache_hit"] is True
        assert appels["count"] == 1  # Handler appelé 1 seule fois

    def test_cache_ne_cache_pas_none(self):
        """Test que None n'est pas caché par défaut."""
        appels = {"count": 0}

        def handler(c):
            appels["count"] += 1
            return None

        middleware = CacheMiddleware(ttl=300, cache_none=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()

        ctx1 = Contexte(operation="null_op", params={})
        pipeline.executer(ctx1, handler)

        ctx2 = Contexte(operation="null_op", params={})
        pipeline.executer(ctx2, handler)

        assert appels["count"] == 2  # Pas de cache → appelé 2 fois

    def test_cache_key_fn_personnalisee(self):
        """Test clé de cache personnalisée."""

        def custom_key(ctx):
            return f"custom_{ctx.params.get('id')}"

        appels = {"count": 0}

        def handler(c):
            appels["count"] += 1
            return "ok"

        middleware = CacheMiddleware(ttl=300, key_fn=custom_key)
        pipeline = Pipeline("test").utiliser(middleware).construire()

        ctx1 = Contexte(operation="op1", params={"id": 42})
        pipeline.executer(ctx1, handler)

        ctx2 = Contexte(operation="op2", params={"id": 42})  # Même id
        pipeline.executer(ctx2, handler)

        assert appels["count"] == 1  # Même clé custom → cache hit


# ═══════════════════════════════════════════════════════════
# TESTS CIRCUIT BREAKER MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestCircuitBreakerMiddleware:
    """Tests pour CircuitBreakerMiddleware."""

    def test_circuit_ferme_normal(self):
        """Test circuit fermé — opération normale."""
        cb = CircuitBreakerMiddleware(seuil_erreurs=3)
        pipeline = Pipeline("test").utiliser(cb).construire()
        ctx = Contexte(operation="normal")

        result = pipeline.executer(ctx, lambda c: "ok")

        assert result == "ok"
        assert ctx.metadata["circuit_breaker_etat"] == "FERME"

    def test_circuit_ouvre_apres_seuil(self):
        """Test circuit s'ouvre après N erreurs."""
        cb = CircuitBreakerMiddleware(seuil_erreurs=2, delai_reset=60)
        pipeline = Pipeline("test").utiliser(cb).construire()

        def handler_qui_plante(c):
            raise ConnectionError("down")

        # 2 erreurs → circuit ouvert
        for _ in range(2):
            with pytest.raises(ConnectionError):
                pipeline.executer(Contexte(operation="fail"), handler_qui_plante)

        # 3ème appel → rejeté immédiatement (circuit ouvert)
        with pytest.raises(RuntimeError, match="Circuit ouvert"):
            pipeline.executer(Contexte(operation="fail"), lambda c: "ok")

    def test_circuit_semi_ouvert_apres_delai(self):
        """Test passage en semi-ouvert après délai."""
        cb = CircuitBreakerMiddleware(seuil_erreurs=1, delai_reset=0.01)
        pipeline = Pipeline("test").utiliser(cb).construire()

        # 1 erreur → circuit ouvert
        with pytest.raises(ValueError):
            pipeline.executer(
                Contexte(operation="fail"),
                lambda c: (_ for _ in ()).throw(ValueError("boom")),
            )

        # Attendre le délai
        time.sleep(0.02)

        # Prochaine requête → semi-ouvert → succès → fermé
        ctx = Contexte(operation="retry")
        result = pipeline.executer(ctx, lambda c: "recovered")
        assert result == "recovered"

    def test_circuit_semi_ouvert_echec_reouvre(self):
        """Test semi-ouvert → échec → retour en ouvert."""
        cb = CircuitBreakerMiddleware(seuil_erreurs=1, delai_reset=0.01)
        pipeline = Pipeline("test").utiliser(cb).construire()

        # Ouvrir le circuit
        with pytest.raises(ValueError):
            pipeline.executer(
                Contexte(operation="fail"),
                lambda c: (_ for _ in ()).throw(ValueError("boom")),
            )

        time.sleep(0.02)

        # Semi-ouvert → échec → retour en ouvert
        with pytest.raises(ValueError):
            pipeline.executer(
                Contexte(operation="fail_again"),
                lambda c: (_ for _ in ()).throw(ValueError("encore")),
            )

        # Doit être re-ouvert
        with pytest.raises(RuntimeError, match="Circuit ouvert"):
            pipeline.executer(Contexte(operation="blocked"), lambda c: "ok")


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION MIDDLEWARE
# ═══════════════════════════════════════════════════════════


class TestValidationMiddleware:
    """Tests pour ValidationMiddleware."""

    def test_validation_success(self):
        """Test validation réussie."""
        from pydantic import BaseModel

        class InputSchema(BaseModel):
            nom: str
            age: int = 0

        middleware = ValidationMiddleware(schema=InputSchema)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="valider", params={"nom": "Alice", "age": 30})

        result = pipeline.executer(ctx, lambda c: c.params)

        assert result["nom"] == "Alice"
        assert ctx.metadata["validated"] is True

    def test_validation_echec_strict(self):
        """Test validation échouée en mode strict."""
        from pydantic import BaseModel

        class InputSchema(BaseModel):
            nom: str
            age: int

        from src.core.errors_base import ErreurValidation

        middleware = ValidationMiddleware(schema=InputSchema, strict=True)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(operation="valider", params={"nom": "Alice", "age": "pas_un_int"})

        with pytest.raises(ErreurValidation):
            pipeline.executer(ctx, lambda c: c.params)

    def test_validation_non_strict_continue(self):
        """Test validation échouée en mode non-strict (continue)."""
        from pydantic import BaseModel

        class StrictSchema(BaseModel):
            nom: str
            valeur: int

        middleware = ValidationMiddleware(schema=StrictSchema, strict=False)
        pipeline = Pipeline("test").utiliser(middleware).construire()
        ctx = Contexte(
            operation="souple",
            params={"nom": "test", "valeur": "pas_int"},
        )

        # Ne lève pas d'exception, continue avec les params originaux
        result = pipeline.executer(ctx, lambda c: "ok")
        assert result == "ok"


# ═══════════════════════════════════════════════════════════
# TESTS COMPOSITION (INTÉGRATION)
# ═══════════════════════════════════════════════════════════


class TestCompositionMiddleware:
    """Tests d'intégration: composition de plusieurs middlewares."""

    def test_log_timing_retry_ensemble(self):
        """Test pipeline complète: Log → Timing → Retry."""
        appels = {"count": 0}

        def handler_fragile(c):
            appels["count"] += 1
            if appels["count"] < 2:
                raise ValueError("temp")
            return "ok"

        pipeline = (
            Pipeline("integration")
            .utiliser(LogMiddleware(niveau="DEBUG"))
            .utiliser(TimingMiddleware(seuil_ms=5000, enregistrer_metrique=False))
            .utiliser(RetryMiddleware(max_tentatives=3, delai_base=0.01))
            .construire()
        )

        ctx = Contexte(operation="test_compose")
        result = pipeline.executer(ctx, handler_fragile)

        assert result == "ok"
        assert "duree_ms" in ctx.metadata
        assert ctx.metadata["tentative"] == 2

    def test_cache_evite_retry(self):
        """Test que le cache court-circuite le retry."""
        appels = {"count": 0}

        def handler(c):
            appels["count"] += 1
            return "data"

        pipeline = (
            Pipeline("cache_first")
            .utiliser(CacheMiddleware(ttl=300))
            .utiliser(RetryMiddleware(max_tentatives=3, delai_base=0.01))
            .construire()
        )

        # Premier appel
        ctx1 = Contexte(operation="cached_op", params={"x": 1})
        pipeline.executer(ctx1, handler)
        assert appels["count"] == 1

        # Deuxième appel — cache hit, retry jamais touché
        ctx2 = Contexte(operation="cached_op", params={"x": 1})
        pipeline.executer(ctx2, handler)
        assert appels["count"] == 1  # Pas d'exécution supplémentaire
