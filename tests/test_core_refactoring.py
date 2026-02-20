"""
Tests pour les nouveaux modules core refactorés.

Couvre:
- Result (monad)
- Resilience policies
- Observability (correlation ID)
- Query builder
- Config validator
- Bootstrap
"""

import time
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# TESTS RESULT MONAD
# ═══════════════════════════════════════════════════════════


class TestResultMonad:
    """Tests pour le pattern Result."""

    def test_ok_creation(self):
        """Ok contient une valeur."""
        from src.core.result import Ok

        result = Ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False
        assert result.ok() == 42
        assert result.err() is None

    def test_err_creation(self):
        """Err contient une erreur."""
        from src.core.result import Err

        result = Err("erreur")
        assert result.is_ok() is False
        assert result.is_err() is True
        assert result.ok() is None
        assert result.err() == "erreur"

    def test_unwrap_ok(self):
        """unwrap retourne la valeur pour Ok."""
        from src.core.result import Ok

        result = Ok(42)
        assert result.unwrap() == 42

    def test_unwrap_err_raises(self):
        """unwrap lève une exception pour Err."""
        from src.core.result import Err

        result = Err("erreur")
        with pytest.raises(ValueError, match="Appelé unwrap"):
            result.unwrap()

    def test_unwrap_or(self):
        """unwrap_or retourne le default pour Err."""
        from src.core.result import Err, Ok

        assert Ok(42).unwrap_or(0) == 42
        assert Err("erreur").unwrap_or(0) == 0

    def test_map_ok(self):
        """map applique la fonction sur Ok."""
        from src.core.result import Ok

        result = Ok(21).map(lambda x: x * 2)
        assert result.unwrap() == 42

    def test_map_err_skips(self):
        """map n'applique pas sur Err."""
        from src.core.result import Err

        result = Err("erreur").map(lambda x: x * 2)
        assert result.is_err()
        assert result.err() == "erreur"

    def test_map_err(self):
        """map_err transforme l'erreur."""
        from src.core.result import Err

        result = Err("erreur").map_err(lambda e: f"ERREUR: {e}")
        assert result.err() == "ERREUR: erreur"

    def test_and_then_chaining(self):
        """and_then chaîne les Results."""
        from src.core.result import Err, Ok

        def safe_div(a: int, b: int):
            if b == 0:
                return Err("division par zéro")
            return Ok(a / b)

        result = Ok(10).and_then(lambda x: safe_div(x, 2))
        assert result.unwrap() == 5.0

        result = Ok(10).and_then(lambda x: safe_div(x, 0))
        assert result.is_err()

    def test_capturer(self):
        """capturer convertit les exceptions en Err."""
        from src.core.result import capturer

        result = capturer(lambda: int("abc"))
        assert result.is_err()
        assert isinstance(result.err(), ValueError)

        result = capturer(lambda: 42)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_depuis_option(self):
        """depuis_option convertit None en Err."""
        from src.core.result import depuis_option

        assert depuis_option(42, "erreur").unwrap() == 42
        assert depuis_option(None, "erreur").err() == "erreur"

    def test_combiner(self):
        """combiner agrège plusieurs Results."""
        from src.core.result import Err, Ok, combiner

        result = combiner(Ok(1), Ok(2), Ok(3))
        assert result.unwrap() == [1, 2, 3]

        result = combiner(Ok(1), Err("oops"), Ok(3))
        assert result.is_err()

    def test_bool_conversion(self):
        """Result supporte la conversion en bool."""
        from src.core.result import Err, Ok

        assert bool(Ok(42)) is True
        assert bool(Err("err")) is False

        # if result: pattern
        if Ok(42):
            pass  # OK
        else:
            pytest.fail("Ok devrait être truthy")


# ═══════════════════════════════════════════════════════════
# TESTS RESILIENCE POLICIES
# ═══════════════════════════════════════════════════════════


class TestResiliencePolicies:
    """Tests pour les policies de résilience."""

    def test_retry_policy_success(self):
        """RetryPolicy retourne Ok en cas de succès."""
        from src.core.resilience import RetryPolicy

        policy = RetryPolicy(max_tentatives=3)
        result = policy.executer(lambda: 42)

        assert result.is_ok()
        assert result.unwrap() == 42

    def test_retry_policy_eventual_success(self):
        """RetryPolicy réussit après plusieurs tentatives."""
        from src.core.resilience import RetryPolicy

        counter = {"count": 0}

        def flaky():
            counter["count"] += 1
            if counter["count"] < 3:
                raise ValueError("échec temporaire")
            return "succès"

        policy = RetryPolicy(max_tentatives=3, delai_base=0.01)
        result = policy.executer(flaky)

        assert result.is_ok()
        assert result.unwrap() == "succès"
        assert counter["count"] == 3

    def test_retry_policy_all_failures(self):
        """RetryPolicy retourne Err après max_tentatives."""
        from src.core.resilience import RetryPolicy

        policy = RetryPolicy(max_tentatives=2, delai_base=0.01)
        result = policy.executer(lambda: 1 / 0)

        assert result.is_err()
        assert isinstance(result.err(), ZeroDivisionError)

    def test_timeout_policy_success(self):
        """TimeoutPolicy retourne Ok si dans le temps."""
        from src.core.resilience import TimeoutPolicy

        policy = TimeoutPolicy(timeout_secondes=5.0)
        result = policy.executer(lambda: 42)

        assert result.is_ok()
        assert result.unwrap() == 42

    def test_timeout_policy_timeout(self):
        """TimeoutPolicy retourne Err si timeout."""
        from src.core.resilience import TimeoutPolicy

        policy = TimeoutPolicy(timeout_secondes=0.1)
        result = policy.executer(lambda: time.sleep(1) or 42)

        assert result.is_err()
        assert isinstance(result.err(), TimeoutError)

    def test_fallback_policy_success(self):
        """FallbackPolicy retourne Ok si succès."""
        from src.core.resilience import FallbackPolicy

        policy = FallbackPolicy(fallback_value="default")
        result = policy.executer(lambda: "success")

        assert result.is_ok()
        assert result.unwrap() == "success"

    def test_fallback_policy_uses_fallback(self):
        """FallbackPolicy utilise le fallback en cas d'erreur."""
        from src.core.resilience import FallbackPolicy

        policy = FallbackPolicy(fallback_value="default", log_erreur=False)
        result = policy.executer(lambda: 1 / 0)

        assert result.is_ok()
        assert result.unwrap() == "default"

    def test_policy_composition(self):
        """Les policies peuvent être composées."""
        from src.core.resilience import FallbackPolicy, RetryPolicy, TimeoutPolicy

        policy = TimeoutPolicy(5.0) + RetryPolicy(2, delai_base=0.01) + FallbackPolicy("default")

        result = policy.executer(lambda: 42)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_factory_politique_api_externe(self):
        """politique_api_externe crée une policy composée."""
        from src.core.resilience import politique_api_externe

        policy = politique_api_externe()
        assert len(policy.policies) == 3  # Timeout + Retry + Bulkhead


# ═══════════════════════════════════════════════════════════
# TESTS OBSERVABILITY
# ═══════════════════════════════════════════════════════════


class TestObservability:
    """Tests pour l'observabilité et correlation ID."""

    def test_contexte_execution_creation(self):
        """ContexteExecution génère un correlation_id."""
        from src.core.observability import ContexteExecution

        ctx = ContexteExecution(operation="test")
        assert len(ctx.correlation_id) == 8
        assert ctx.operation == "test"

    def test_contexte_operation_context_manager(self):
        """contexte_operation définit le contexte."""
        from src.core.observability import contexte_operation, obtenir_contexte

        with contexte_operation("test_op", module="test_module") as ctx:
            assert ctx.operation == "test_op"
            assert ctx.module == "test_module"

            # Le contexte est accessible globalement
            ctx_global = obtenir_contexte()
            assert ctx_global.correlation_id == ctx.correlation_id

    def test_contexte_enfant_herite_correlation_id(self):
        """Les contextes enfants héritent du correlation_id."""
        from src.core.observability import contexte_operation

        with contexte_operation("parent") as parent_ctx:
            parent_id = parent_ctx.correlation_id

            with contexte_operation("enfant") as enfant_ctx:
                assert enfant_ctx.correlation_id == parent_id
                assert enfant_ctx.parent_id == parent_id

    def test_duree_ms(self):
        """duree_ms calcule la durée correctement."""
        from src.core.observability import ContexteExecution

        ctx = ContexteExecution()
        time.sleep(0.05)
        duree = ctx.duree_ms()

        assert duree >= 50  # Au moins 50ms

    def test_filtre_correlation_logging(self):
        """FiltreCorrelation ajoute le correlation_id aux logs."""
        import logging

        from src.core.observability import FiltreCorrelation, contexte_operation

        # Créer un logger de test
        logger = logging.getLogger("test_correlation")
        handler = logging.StreamHandler()
        handler.addFilter(FiltreCorrelation())
        logger.addHandler(handler)

        with contexte_operation("test_log") as ctx:
            # Le filtre devrait ajouter correlation_id au record
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="test",
                args=(),
                exc_info=None,
            )
            assert handler.filters[0].filter(record)
            assert record.correlation_id == ctx.correlation_id  # type: ignore


# ═══════════════════════════════════════════════════════════
# TESTS QUERY BUILDER
# ═══════════════════════════════════════════════════════════


class TestQueryBuilder:
    """Tests pour le Query Builder fluent."""

    def test_requete_creation(self):
        """Requete peut être créée avec un modèle."""
        from src.core.query import Requete

        # Mock model
        class FakeModel:
            __name__ = "FakeModel"

        query = Requete(FakeModel)
        assert query.model == FakeModel

    def test_requete_et_conditions(self):
        """et() ajoute des conditions AND."""
        from src.core.query import Requete

        class FakeModel:
            __name__ = "FakeModel"
            actif = True

        query = Requete(FakeModel).et(actif=True)
        assert len(query._conditions) == 1

    def test_requete_chaining(self):
        """Les méthodes sont chaînables."""
        from src.core.query import Requete

        class FakeModel:
            __name__ = "FakeModel"
            actif = True
            nom = "test"

        # Test la chaînabilité - trier_par ignore les colonnes non-SQLAlchemy
        query = Requete(FakeModel).et(actif=True).limite(10).trier_par("-nom")

        assert query._limit == 10
        # trier_par ignore silencieusement les colonnes non-SQLAlchemy (pas de .desc/.asc)
        assert len(query._ordre) == 0  # FakeModel.nom n'a pas .desc()
        assert len(query._conditions) == 1  # La condition actif=True est présente

    def test_requete_paginer(self):
        """paginer() calcule offset correctement."""
        from src.core.query import Requete

        class FakeModel:
            __name__ = "FakeModel"

        query = Requete(FakeModel).paginer(page=3, taille=20)

        assert query._limit == 20
        assert query._offset == 40  # (3-1) * 20

    def test_requete_repr(self):
        """__repr__ est informatif."""
        from src.core.query import Requete

        class FakeModel:
            __name__ = "FakeModel"
            actif = True

        query = Requete(FakeModel).et(actif=True).limite(10)
        repr_str = repr(query)

        assert "FakeModel" in repr_str
        assert "conditions=1" in repr_str
        assert "limit=10" in repr_str


# ═══════════════════════════════════════════════════════════
# TESTS CONFIG VALIDATOR
# ═══════════════════════════════════════════════════════════


class TestConfigValidator:
    """Tests pour le validateur de configuration."""

    def test_validation_succes(self):
        """Validation réussie avec vérificateur True."""
        from src.core.config.validator import (
            NiveauValidation,
            ValidateurConfiguration,
        )

        validateur = ValidateurConfiguration()
        validateur.ajouter("test", NiveauValidation.CRITIQUE, lambda: True)

        rapport = validateur.executer()

        assert rapport.valide is True
        assert len(rapport.succes) == 1

    def test_validation_echec_critique(self):
        """Échec critique invalide le rapport."""
        from src.core.config.validator import (
            NiveauValidation,
            ValidateurConfiguration,
        )

        validateur = ValidateurConfiguration()
        validateur.ajouter("test", NiveauValidation.CRITIQUE, lambda: False, "erreur test")

        rapport = validateur.executer()

        assert rapport.valide is False
        assert len(rapport.erreurs_critiques) == 1

    def test_validation_avertissement_non_bloquant(self):
        """Les avertissements ne bloquent pas."""
        from src.core.config.validator import (
            NiveauValidation,
            ValidateurConfiguration,
        )

        validateur = ValidateurConfiguration()
        validateur.ajouter("ok", NiveauValidation.CRITIQUE, lambda: True)
        validateur.ajouter("warn", NiveauValidation.AVERTISSEMENT, lambda: False)

        rapport = validateur.executer()

        assert rapport.valide is True
        assert len(rapport.avertissements) == 1

    def test_validation_exception_capturee(self):
        """Les exceptions sont capturées comme échecs."""
        from src.core.config.validator import (
            NiveauValidation,
            ValidateurConfiguration,
        )

        def raise_error():
            raise RuntimeError("boom")

        validateur = ValidateurConfiguration()
        validateur.ajouter("test", NiveauValidation.CRITIQUE, raise_error)

        rapport = validateur.executer()

        assert rapport.valide is False
        assert "Exception" in rapport.erreurs_critiques[0].message

    def test_fluent_api(self):
        """L'API est fluent (retourne self)."""
        from src.core.config.validator import (
            NiveauValidation,
            ValidateurConfiguration,
        )

        validateur = (
            ValidateurConfiguration()
            .ajouter("a", NiveauValidation.CRITIQUE, lambda: True)
            .ajouter("b", NiveauValidation.INFO, lambda: True)
        )

        assert len(validateur._validations) == 2


# ═══════════════════════════════════════════════════════════
# TESTS BOOTSTRAP
# ═══════════════════════════════════════════════════════════


class TestBootstrap:
    """Tests pour le bootstrap de l'application."""

    def test_rapport_demarrage_to_dict(self):
        """RapportDemarrage peut être sérialisé."""
        from src.core.bootstrap import RapportDemarrage

        rapport = RapportDemarrage(
            succes=True,
            composants_enregistres=["A", "B"],
            erreurs=[],
            avertissements=["warn"],
        )

        d = rapport.to_dict()
        assert d["succes"] is True
        assert d["composants"] == ["A", "B"]
        assert d["avertissements"] == ["warn"]

    def test_est_demarree_initial(self):
        """est_demarree() retourne False initialement."""
        from src.core import bootstrap

        # Reset pour le test
        bootstrap._deja_demarre = False

        assert bootstrap.est_demarree() is False

    @patch("src.core.bootstrap._enregistrer_composants")
    def test_demarrer_application_sans_validation(self, mock_enregistrer):
        """demarrer_application peut skip la validation."""
        from src.core import bootstrap

        bootstrap._deja_demarre = False
        mock_enregistrer.return_value = ["Test"]

        rapport = bootstrap.demarrer_application(
            valider_config=False, initialiser_eager=False, enregistrer_atexit=False
        )

        assert rapport.succes is True
        assert "Test" in rapport.composants_enregistres

        # Cleanup
        bootstrap._deja_demarre = False

    def test_demarrer_application_deja_demarre(self):
        """demarrer_application skip si déjà démarré."""
        from src.core import bootstrap

        bootstrap._deja_demarre = True

        rapport = bootstrap.demarrer_application()

        assert rapport.succes is True  # Skip sans erreur

        # Cleanup
        bootstrap._deja_demarre = False
