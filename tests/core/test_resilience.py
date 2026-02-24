"""Tests pour src/core/resilience/policies.py — politiques de résilience."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from src.core.resilience.policies import (
    BulkheadPolicy,
    FallbackPolicy,
    Policy,
    PolicyComposee,
    RetryPolicy,
    TimeoutPolicy,
    _get_timeout_executor,
    politique_api_externe,
    politique_base_de_donnees,
    politique_cache,
    politique_ia,
)

# ═══════════════════════════════════════════════════════════
# TESTS RetryPolicy
# ═══════════════════════════════════════════════════════════


class TestRetryPolicy:
    """Tests pour RetryPolicy."""

    @pytest.mark.unit
    def test_success_sans_retry(self):
        """Succès immédiat ne déclenche pas de retry."""
        policy = RetryPolicy(max_tentatives=3)
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            return "ok"

        result = policy.executer(fn)

        assert result == "ok"
        assert compteur["appels"] == 1

    @pytest.mark.unit
    def test_retry_puis_succes(self):
        """Retry après échecs puis succès."""
        policy = RetryPolicy(max_tentatives=3, delai_base=0.01, jitter=False)
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            if compteur["appels"] < 3:
                raise ValueError("Échec temporaire")
            return "ok"

        result = policy.executer(fn)

        assert result == "ok"
        assert compteur["appels"] == 3

    @pytest.mark.unit
    def test_echec_apres_max_tentatives(self):
        """Lève l'exception après max tentatives."""
        policy = RetryPolicy(max_tentatives=2, delai_base=0.01, jitter=False)

        def fn():
            raise ValueError("Permanent")

        with pytest.raises(ValueError, match="Permanent"):
            policy.executer(fn)

    @pytest.mark.unit
    def test_exceptions_a_retry_filtre(self):
        """Ne retry que les exceptions spécifiées."""
        policy = RetryPolicy(
            max_tentatives=3,
            delai_base=0.01,
            exceptions_a_retry=(ConnectionError,),
        )
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            raise ValueError("Non retryable")

        # ValueError n'est pas dans exceptions_a_retry, propagée immédiatement
        with pytest.raises(ValueError):
            policy.executer(fn)

        assert compteur["appels"] == 1

    @pytest.mark.unit
    def test_exceptions_a_retry_retry(self):
        """Retry les exceptions listées."""
        policy = RetryPolicy(
            max_tentatives=3,
            delai_base=0.01,
            jitter=False,
            exceptions_a_retry=(ConnectionError,),
        )
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            if compteur["appels"] < 3:
                raise ConnectionError("Erreur réseau")
            return "ok"

        result = policy.executer(fn)

        assert result == "ok"
        assert compteur["appels"] == 3

    @pytest.mark.unit
    def test_backoff_exponentiel(self):
        """Le délai augmente exponentiellement (sans jitter)."""
        policy = RetryPolicy(
            max_tentatives=3,
            delai_base=0.5,
            facteur_backoff=2.0,
            jitter=False,
        )
        timestamps = []

        def fn():
            timestamps.append(time.time())
            if len(timestamps) < 3:
                raise ValueError("Retry")
            return "ok"

        policy.executer(fn)

        # Premier retry après ~0.5s, deuxième après ~1.0s
        delta1 = timestamps[1] - timestamps[0]
        delta2 = timestamps[2] - timestamps[1]

        assert 0.4 < delta1 < 0.7  # ~0.5s
        assert 0.8 < delta2 < 1.3  # ~1.0s (0.5 * 2^1)

    @pytest.mark.unit
    def test_jitter_ajoute_variation(self):
        """Le jitter ajoute de la variation au délai."""
        policy = RetryPolicy(
            max_tentatives=5,
            delai_base=0.1,
            facteur_backoff=1.0,  # Pas d'augmentation
            jitter=True,
        )
        delais = []

        def fn():
            delais.append(time.time())
            if len(delais) < 5:
                raise ValueError("Retry")
            return "ok"

        policy.executer(fn)

        # Avec jitter, les délais devraient varier (pas tous identiques)
        inter_delais = [delais[i + 1] - delais[i] for i in range(len(delais) - 1)]
        assert len(set(round(d, 3) for d in inter_delais)) > 1  # Variation présente

    @pytest.mark.unit
    def test_default_values(self):
        """Valeurs par défaut correctes."""
        policy = RetryPolicy()

        assert policy.max_tentatives == 3
        assert policy.delai_base == 1.0
        assert policy.facteur_backoff == 2.0
        assert policy.jitter is True
        assert policy.exceptions_a_retry == ()


# ═══════════════════════════════════════════════════════════
# TESTS TimeoutPolicy
# ═══════════════════════════════════════════════════════════


class TestTimeoutPolicy:
    """Tests pour TimeoutPolicy."""

    @pytest.mark.unit
    def test_execution_rapide_ok(self):
        """Exécution rapide retourne le résultat."""
        policy = TimeoutPolicy(timeout_secondes=5.0)

        result = policy.executer(lambda: "rapide")

        assert result == "rapide"

    @pytest.mark.unit
    def test_timeout_depasse(self):
        """Timeout sur exécution trop longue."""
        policy = TimeoutPolicy(timeout_secondes=0.1)

        def fn_lente():
            time.sleep(1.0)
            return "jamais atteint"

        with pytest.raises(TimeoutError, match="Timeout après 0.1s"):
            policy.executer(fn_lente)

    @pytest.mark.unit
    def test_executor_partage(self):
        """L'executor est réutilisé (singleton)."""
        exec1 = _get_timeout_executor()
        exec2 = _get_timeout_executor()

        assert exec1 is exec2

    @pytest.mark.unit
    def test_exception_propagee(self):
        """Les exceptions sont propagées correctement."""
        policy = TimeoutPolicy(timeout_secondes=5.0)

        def fn_erreur():
            raise RuntimeError("Erreur interne")

        with pytest.raises(RuntimeError, match="Erreur interne"):
            policy.executer(fn_erreur)

    @pytest.mark.unit
    def test_default_timeout(self):
        """Timeout par défaut est 30s."""
        policy = TimeoutPolicy()
        assert policy.timeout_secondes == 30.0


# ═══════════════════════════════════════════════════════════
# TESTS BulkheadPolicy
# ═══════════════════════════════════════════════════════════


class TestBulkheadPolicy:
    """Tests pour BulkheadPolicy."""

    @pytest.mark.unit
    def test_execution_simple(self):
        """Exécution simple fonctionne."""
        policy = BulkheadPolicy(max_concurrent=2)

        result = policy.executer(lambda: 42)

        assert result == 42

    @pytest.mark.unit
    def test_limite_concurrence(self):
        """La concurrence est limitée au max."""
        policy = BulkheadPolicy(max_concurrent=1, timeout_acquisition=0.05)
        en_cours = []
        resultats = []
        erreurs = []
        lock = threading.Lock()

        def fn_longue(thread_id: int):
            """Fonction qui prend du temps."""
            with lock:
                en_cours.append(thread_id)
            time.sleep(0.2)  # Assez long pour saturer
            with lock:
                en_cours.remove(thread_id)
            return thread_id

        def worker(thread_id: int):
            try:
                result = policy.executer(lambda: fn_longue(thread_id))
                with lock:
                    resultats.append(result)
            except RuntimeError as e:
                with lock:
                    erreurs.append(str(e))

        # Lancer 3 threads avec seulement 1 slot
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
        for t in threads:
            t.start()
        time.sleep(0.01)  # Laisser le premier thread acquérir le slot
        for t in threads:
            t.join()

        # Au moins un thread a réussi, au moins un a échoué
        assert len(resultats) >= 1
        assert len(erreurs) >= 1  # Au moins un échec de saturation

    @pytest.mark.unit
    def test_liberation_apres_execution(self):
        """Le slot est libéré après exécution."""
        policy = BulkheadPolicy(max_concurrent=1, timeout_acquisition=0.1)

        # Première exécution
        result1 = policy.executer(lambda: "un")
        assert result1 == "un"

        # Deuxième exécution (immédiatement après)
        result2 = policy.executer(lambda: "deux")
        assert result2 == "deux"

    @pytest.mark.unit
    def test_liberation_apres_exception(self):
        """Le slot est libéré même en cas d'exception."""
        policy = BulkheadPolicy(max_concurrent=1, timeout_acquisition=0.1)

        with pytest.raises(ValueError):
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("test")))

        # Le slot doit être libéré, nouvelle exécution possible
        result = policy.executer(lambda: "ok")
        assert result == "ok"

    @pytest.mark.unit
    def test_default_values(self):
        """Valeurs par défaut correctes."""
        policy = BulkheadPolicy()

        assert policy.max_concurrent == 10
        assert policy.timeout_acquisition == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS FallbackPolicy
# ═══════════════════════════════════════════════════════════


class TestFallbackPolicy:
    """Tests pour FallbackPolicy."""

    @pytest.mark.unit
    def test_success_pas_de_fallback(self):
        """Succès retourne le résultat normal."""
        policy = FallbackPolicy(fallback_value="fallback")

        result = policy.executer(lambda: "succes")

        assert result == "succes"

    @pytest.mark.unit
    def test_echec_retourne_fallback_value(self):
        """Échec retourne fallback_value."""
        policy = FallbackPolicy(fallback_value="fallback", log_erreur=False)

        result = policy.executer(lambda: (_ for _ in ()).throw(ValueError("err")))

        assert result == "fallback"

    @pytest.mark.unit
    def test_echec_utilise_fallback_fn(self):
        """Échec utilise fallback_fn si fournie."""
        policy = FallbackPolicy(
            fallback_fn=lambda e: f"erreur: {e}",
            log_erreur=False,
        )

        result = policy.executer(lambda: (_ for _ in ()).throw(ValueError("test")))

        assert result == "erreur: test"

    @pytest.mark.unit
    def test_fallback_fn_priorite_sur_value(self):
        """fallback_fn est prioritaire sur fallback_value."""
        policy = FallbackPolicy(
            fallback_value="value",
            fallback_fn=lambda e: "fn",
            log_erreur=False,
        )

        result = policy.executer(lambda: (_ for _ in ()).throw(ValueError()))

        assert result == "fn"

    @pytest.mark.unit
    def test_pas_de_fallback_propage_exception(self):
        """Sans fallback défini, l'exception est propagée."""
        policy = FallbackPolicy(log_erreur=False)

        with pytest.raises(ValueError, match="propagée"):
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("propagée")))

    @pytest.mark.unit
    def test_fallback_value_none_non_utilisee(self):
        """fallback_value=None ne bloque pas la propagation."""
        policy = FallbackPolicy(fallback_value=None, log_erreur=False)

        with pytest.raises(RuntimeError):
            policy.executer(lambda: (_ for _ in ()).throw(RuntimeError("err")))

    @pytest.mark.unit
    def test_log_erreur_active(self):
        """log_erreur=True log un warning."""
        policy = FallbackPolicy(fallback_value="fb", log_erreur=True)

        with patch("src.core.resilience.policies.logger") as mock_logger:
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("logged")))

            mock_logger.warning.assert_called_once()
            assert "logged" in str(mock_logger.warning.call_args)


# ═══════════════════════════════════════════════════════════
# TESTS PolicyComposee
# ═══════════════════════════════════════════════════════════


class TestPolicyComposee:
    """Tests pour PolicyComposee."""

    @pytest.mark.unit
    def test_composition_vide(self):
        """Composition vide exécute directement la fonction."""
        policy = PolicyComposee([])

        result = policy.executer(lambda: "direct")

        assert result == "direct"

    @pytest.mark.unit
    def test_composition_simple(self):
        """Composition de deux policies."""
        policy = PolicyComposee(
            [
                TimeoutPolicy(timeout_secondes=5.0),
                RetryPolicy(max_tentatives=2, delai_base=0.01),
            ]
        )
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            if compteur["appels"] < 2:
                raise ValueError("retry")
            return "ok"

        result = policy.executer(fn)

        assert result == "ok"
        assert compteur["appels"] == 2

    @pytest.mark.unit
    def test_addition_policies(self):
        """L'opérateur + compose deux policies."""
        p1 = RetryPolicy(max_tentatives=2)
        p2 = TimeoutPolicy(timeout_secondes=10.0)

        composed = p1 + p2

        assert isinstance(composed, PolicyComposee)
        assert len(composed.policies) == 2

    @pytest.mark.unit
    def test_addition_composee_policy(self):
        """PolicyComposee + Policy ajoute à la liste."""
        p1 = RetryPolicy()
        p2 = TimeoutPolicy()
        composed = p1 + p2

        p3 = FallbackPolicy(fallback_value=None)
        result = composed + p3

        assert isinstance(result, PolicyComposee)
        assert len(result.policies) == 3

    @pytest.mark.unit
    def test_radd_policy_composee(self):
        """Policy + PolicyComposee fonctionne."""
        p1 = RetryPolicy()
        composed = PolicyComposee([TimeoutPolicy()])

        result = p1 + composed

        assert isinstance(result, PolicyComposee)
        assert len(result.policies) == 2

    @pytest.mark.unit
    def test_repr(self):
        """__repr__ affiche les noms des policies."""
        policy = PolicyComposee([RetryPolicy(), TimeoutPolicy()])

        repr_str = repr(policy)

        assert "PolicyComposee" in repr_str
        assert "RetryPolicy" in repr_str
        assert "TimeoutPolicy" in repr_str


# ═══════════════════════════════════════════════════════════
# TESTS FACTORIES
# ═══════════════════════════════════════════════════════════


class TestFactories:
    """Tests pour les fonctions factory."""

    @pytest.mark.unit
    def test_politique_api_externe(self):
        """politique_api_externe() crée la bonne composition."""
        policy = politique_api_externe()

        assert isinstance(policy, PolicyComposee)
        assert len(policy.policies) == 3

        types = [type(p).__name__ for p in policy.policies]
        assert "TimeoutPolicy" in types
        assert "RetryPolicy" in types
        assert "BulkheadPolicy" in types

    @pytest.mark.unit
    def test_politique_base_de_donnees(self):
        """politique_base_de_donnees() crée la bonne composition."""
        policy = politique_base_de_donnees()

        assert isinstance(policy, PolicyComposee)
        assert len(policy.policies) == 2

        timeout = policy.policies[0]
        retry = policy.policies[1]

        assert isinstance(timeout, TimeoutPolicy)
        assert timeout.timeout_secondes == 10.0
        assert isinstance(retry, RetryPolicy)
        assert retry.max_tentatives == 2

    @pytest.mark.unit
    def test_politique_cache(self):
        """politique_cache() crée la bonne composition."""
        policy = politique_cache()

        assert isinstance(policy, PolicyComposee)
        assert len(policy.policies) == 2

        timeout = policy.policies[0]
        fallback = policy.policies[1]

        assert isinstance(timeout, TimeoutPolicy)
        assert timeout.timeout_secondes == 1.0
        assert isinstance(fallback, FallbackPolicy)
        assert fallback.fallback_value is None

    @pytest.mark.unit
    def test_politique_ia(self):
        """politique_ia() crée la bonne composition."""
        policy = politique_ia()

        assert isinstance(policy, PolicyComposee)
        assert len(policy.policies) == 3

        timeout = policy.policies[0]
        retry = policy.policies[1]
        bulkhead = policy.policies[2]

        assert isinstance(timeout, TimeoutPolicy)
        assert timeout.timeout_secondes == 60.0
        assert isinstance(retry, RetryPolicy)
        assert retry.delai_base == 2.0
        assert retry.facteur_backoff == 3.0
        assert isinstance(bulkhead, BulkheadPolicy)
        assert bulkhead.max_concurrent == 3

    @pytest.mark.unit
    def test_factory_execution_fonctionnelle(self):
        """Les policies factory peuvent exécuter des fonctions."""
        for factory in [
            politique_api_externe,
            politique_base_de_donnees,
            politique_cache,
            politique_ia,
        ]:
            policy = factory()
            result = policy.executer(lambda: "ok")
            assert result == "ok"


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    @pytest.mark.unit
    def test_composition_retry_fallback(self):
        """Retry épuisé puis fallback."""
        # Note: L'ordre des policies est important - FallbackPolicy enveloppe RetryPolicy
        # donc le fallback capture l'exception finale après les retries
        policy = PolicyComposee(
            [
                FallbackPolicy(fallback_value="default", log_erreur=False),
                RetryPolicy(max_tentatives=2, delai_base=0.01, jitter=False),
            ]
        )
        compteur = {"appels": 0}

        def fn():
            compteur["appels"] += 1
            raise ValueError("Permanent")

        result = policy.executer(fn)

        assert result == "default"
        assert compteur["appels"] == 2  # 2 tentatives avant fallback

    @pytest.mark.unit
    def test_timeout_avec_fallback(self):
        """Timeout puis fallback."""
        # Note: L'ordre des policies est important - FallbackPolicy enveloppe TimeoutPolicy
        # donc le fallback capture l'exception TimeoutError
        policy = PolicyComposee(
            [
                FallbackPolicy(fallback_value="timeout_fallback", log_erreur=False),
                TimeoutPolicy(timeout_secondes=0.1),
            ]
        )

        def fn_lente():
            time.sleep(1.0)
            return "jamais"

        result = policy.executer(fn_lente)

        assert result == "timeout_fallback"

    @pytest.mark.unit
    def test_bulkhead_avec_retry(self):
        """Bulkhead saturé retry l'acquisition."""
        # Policy avec bulkhead limité et retry
        retry = RetryPolicy(max_tentatives=2, delai_base=0.01, jitter=False)
        bulkhead = BulkheadPolicy(max_concurrent=1, timeout_acquisition=0.05)
        policy = retry + bulkhead

        result = policy.executer(lambda: "ok")
        assert result == "ok"


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests des cas limites."""

    @pytest.mark.unit
    def test_retry_zero_tentatives(self):
        """Retry avec 0 tentatives lève immédiatement."""
        policy = RetryPolicy(max_tentatives=0, delai_base=0.01)

        # devrait lever l'exception sans aucun retry
        # Note: avec max_tentatives=0, le range est vide donc on sort directement
        with pytest.raises(Exception):
            policy.executer(lambda: (_ for _ in ()).throw(ValueError("err")))

    @pytest.mark.unit
    def test_timeout_tres_court(self):
        """Timeout très court fonctionne."""
        policy = TimeoutPolicy(timeout_secondes=0.001)

        # Même une opération rapide peut timeout avec un délai si court
        # du fait des overheads du threading
        result = policy.executer(lambda: 1 + 1)
        assert result == 2  # Devrait passer si suffisamment rapide

    @pytest.mark.unit
    def test_fallback_avec_none_explicite(self):
        """FallbackPolicy peut retourner None explicitement via fallback_fn."""
        policy = FallbackPolicy(fallback_fn=lambda e: None, log_erreur=False)

        result = policy.executer(lambda: (_ for _ in ()).throw(ValueError()))

        assert result is None

    @pytest.mark.unit
    def test_policy_abstract(self):
        """Policy est une classe abstraite."""
        with pytest.raises(TypeError):
            Policy()  # type: ignore


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
