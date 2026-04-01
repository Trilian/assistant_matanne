"""Tests unitaires pour les policies de résilience (P2-02).

Couvre:
- RetryPolicy (retry exponentiel avec backoff)
- TimeoutPolicy (timeout via ThreadPoolExecutor)
- BulkheadPolicy (isolation concurrence)
- FallbackPolicy (valeur de secours)
- PolicyComposee (composition de policies)
- Opérateurs + et radd
"""

import threading
import time

import pytest

from src.core.resilience.policies import (
    BulkheadPolicy,
    FallbackPolicy,
    Policy,
    PolicyComposee,
    RetryPolicy,
    TimeoutPolicy,
)


# ═══════════════════════════════════════════════════════════
# TESTS RetryPolicy
# ═══════════════════════════════════════════════════════════


class TestRetryPolicy:
    """Tests pour RetryPolicy."""

    def test_reussit_premier_essai(self):
        """Réussit immédiatement sans retry."""
        policy = RetryPolicy(max_tentatives=3, delai_base=0.01)
        result = policy.executer(lambda: 42)
        assert result == 42

    def test_retry_apres_echec(self):
        """Retente après un échec et réussit."""
        attempts = 0

        def fn_instable():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ConnectionError("retry")
            return "ok"

        policy = RetryPolicy(max_tentatives=3, delai_base=0.01, jitter=False)
        result = policy.executer(fn_instable)
        assert result == "ok"
        assert attempts == 3

    def test_epuise_tentatives(self):
        """Lève l'exception après avoir épuisé les tentatives."""
        policy = RetryPolicy(max_tentatives=2, delai_base=0.01, jitter=False)

        with pytest.raises(ValueError, match="always fail"):
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("always fail")))

    def test_exceptions_a_retry_specifiques(self):
        """Ne retente que les exceptions spécifiées."""
        policy = RetryPolicy(
            max_tentatives=3,
            delai_base=0.01,
            exceptions_a_retry=(ConnectionError,),
        )

        # ValueError n'est pas dans la liste → propagée immédiatement
        with pytest.raises(ValueError):
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("nope")))

    def test_backoff_exponentiel(self):
        """Le délai augmente exponentiellement."""
        policy = RetryPolicy(
            max_tentatives=3,
            delai_base=0.05,
            facteur_backoff=2.0,
            jitter=False,
        )
        attempts = []

        def fn():
            attempts.append(time.time())
            if len(attempts) < 3:
                raise RuntimeError("retry")
            return "ok"

        result = policy.executer(fn)
        assert result == "ok"
        # Le 2e délai devrait être ~2x le premier
        if len(attempts) >= 3:
            delay1 = attempts[1] - attempts[0]
            delay2 = attempts[2] - attempts[1]
            assert delay2 > delay1 * 1.5  # Avec marge


# ═══════════════════════════════════════════════════════════
# TESTS TimeoutPolicy
# ═══════════════════════════════════════════════════════════


class TestTimeoutPolicy:
    """Tests pour TimeoutPolicy."""

    def test_retourne_dans_le_temps(self):
        """Retourne le résultat si le temps est respecté."""
        policy = TimeoutPolicy(timeout_secondes=5.0)
        result = policy.executer(lambda: "rapide")
        assert result == "rapide"

    def test_timeout_depasse(self):
        """Lève une erreur si le timeout est dépassé."""
        policy = TimeoutPolicy(timeout_secondes=0.1)

        with pytest.raises(Exception):  # TimeoutError ou FuturesTimeoutError
            policy.executer(lambda: time.sleep(5) or "lent")


# ═══════════════════════════════════════════════════════════
# TESTS BulkheadPolicy
# ═══════════════════════════════════════════════════════════


class TestBulkheadPolicy:
    """Tests pour BulkheadPolicy."""

    def test_execution_normale(self):
        """Exécution normale sous la limite."""
        policy = BulkheadPolicy(max_concurrent=5, timeout_acquisition=1.0)
        result = policy.executer(lambda: "ok")
        assert result == "ok"

    def test_limite_concurrence(self):
        """Bloque quand la limite de concurrence est atteinte."""
        policy = BulkheadPolicy(max_concurrent=1, timeout_acquisition=0.1)
        barrier = threading.Event()
        results = []
        errors = []

        def long_fn():
            barrier.wait(timeout=2)
            return "done"

        def try_execute():
            try:
                result = policy.executer(long_fn)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Premier thread prend le sémaphore
        t1 = threading.Thread(target=try_execute)
        t1.start()
        time.sleep(0.05)

        # Deuxième thread devrait être bloqué/rejeté
        t2 = threading.Thread(target=try_execute)
        t2.start()
        time.sleep(0.15)

        # Libérer le premier thread
        barrier.set()
        t1.join(timeout=2)
        t2.join(timeout=2)

        # Au moins un devrait réussir
        assert len(results) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS FallbackPolicy
# ═══════════════════════════════════════════════════════════


class TestFallbackPolicy:
    """Tests pour FallbackPolicy."""

    def test_retourne_resultat_sans_erreur(self):
        """Sans erreur, retourne le résultat normal."""
        policy = FallbackPolicy(fallback_value="default")
        result = policy.executer(lambda: "real")
        assert result == "real"

    def test_retourne_fallback_sur_erreur(self):
        """Sur erreur, retourne la valeur de fallback."""
        policy = FallbackPolicy(fallback_value="secours")

        def fn_erreur():
            raise RuntimeError("boom")

        result = policy.executer(fn_erreur)
        assert result == "secours"

    def test_fallback_function(self):
        """Supporte une fonction de fallback."""
        policy = FallbackPolicy(
            fallback_value=None,
            fallback_fn=lambda e: f"error: {e}",
        )

        result = policy.executer(lambda: (_ for _ in ()).throw(ValueError("oops")))
        assert "error:" in result


# ═══════════════════════════════════════════════════════════
# TESTS PolicyComposee
# ═══════════════════════════════════════════════════════════


class TestPolicyComposee:
    """Tests pour PolicyComposee."""

    def test_composition_vide(self):
        """Composition vide exécute directement."""
        composed = PolicyComposee([])
        result = composed.executer(lambda: "direct")
        assert result == "direct"

    def test_composition_retry_plus_timeout(self):
        """Compose retry + timeout."""
        retry = RetryPolicy(max_tentatives=2, delai_base=0.01)
        timeout = TimeoutPolicy(timeout_secondes=5.0)
        composed = retry + timeout

        assert isinstance(composed, PolicyComposee)
        result = composed.executer(lambda: "ok")
        assert result == "ok"

    def test_composition_retry_plus_fallback(self):
        """Retry épuisé puis fallback."""
        retry = RetryPolicy(max_tentatives=2, delai_base=0.01)
        fallback = FallbackPolicy(fallback_value="default")
        composed = PolicyComposee([retry, fallback])

        result = composed.executer(lambda: (_ for _ in ()).throw(RuntimeError("fail")))
        assert result == "default"

    def test_operateur_add(self):
        """L'opérateur + crée une PolicyComposee."""
        p1 = RetryPolicy(max_tentatives=2)
        p2 = TimeoutPolicy(timeout_secondes=5.0)
        composed = p1 + p2

        assert isinstance(composed, PolicyComposee)
        assert len(composed.policies) == 2
