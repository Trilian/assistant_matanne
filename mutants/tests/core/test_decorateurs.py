"""Tests unitaires pour les décorateurs core (P2-01).

Couvre:
- @avec_session_db (injection automatique de session)
- @avec_cache (cache multi-niveaux avec TTL)
- @avec_gestion_erreurs (gestion centralisée d'erreurs)
- @avec_validation (validation Pydantic)
- @avec_resilience (composition retry/timeout/fallback)
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# TESTS @avec_session_db
# ═══════════════════════════════════════════════════════════


class TestAvecSessionDb:
    """Tests pour le décorateur @avec_session_db."""

    def test_injecte_session_quand_non_fournie(self, engine):
        """Quand db=None, le décorateur crée et injecte une session."""
        from src.core.decorators import avec_session_db

        @avec_session_db
        def ma_fonction(db=None):
            assert db is not None
            return "ok"

        result = ma_fonction()
        assert result == "ok"

    def test_utilise_session_fournie(self, db):
        """Quand db est fourni, le décorateur ne crée pas de nouvelle session."""
        from src.core.decorators import avec_session_db

        @avec_session_db
        def ma_fonction(db=None):
            return db

        result = ma_fonction(db=db)
        assert result is db

    def test_session_keyword_arg(self, db):
        """Le décorateur supporte aussi le paramètre 'session'."""
        from src.core.decorators import avec_session_db

        @avec_session_db
        def ma_fonction(session=None):
            return session

        result = ma_fonction(session=db)
        assert result is db

    def test_session_auto_avec_autres_params(self, engine):
        """Le décorateur fonctionne avec d'autres paramètres."""
        from src.core.decorators import avec_session_db

        @avec_session_db
        def creer_something(nom: str, db=None):
            assert db is not None
            return nom

        result = creer_something("test")
        assert result == "test"


# ═══════════════════════════════════════════════════════════
# TESTS @avec_cache
# ═══════════════════════════════════════════════════════════


class TestAvecCache:
    """Tests pour le décorateur @avec_cache."""

    def test_cache_retourne_valeur_cachee(self):
        """Le résultat est mis en cache et retourné au deuxième appel."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=60, key_prefix="test_cache")
        def calcul_couteux(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = calcul_couteux(5)
        result2 = calcul_couteux(5)
        assert result1 == result2 == 10
        assert call_count == 1  # Appelé une seule fois grâce au cache

    def test_cache_cle_differente(self):
        """Des arguments différents produisent des clés différentes."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=60, key_prefix="test_diff")
        def calc(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        calc(1)
        calc(2)
        assert call_count == 2

    def test_cache_none_non_cache_par_defaut(self):
        """Par défaut, les résultats None ne sont pas cachés."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=60, key_prefix="test_none", cache_none=False)
        def retourne_none() -> None:
            nonlocal call_count
            call_count += 1
            return None

        retourne_none()
        retourne_none()
        assert call_count == 2  # Chaque appel exécute la fonction

    def test_cache_none_quand_active(self):
        """Avec cache_none=True, les résultats None sont cachés."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=60, key_prefix="test_none_ok", cache_none=True)
        def retourne_none() -> None:
            nonlocal call_count
            call_count += 1
            return None

        retourne_none()
        retourne_none()
        assert call_count == 1

    def test_cache_custom_key_func(self):
        """Test avec une fonction de clé personnalisée."""
        from src.core.decorators import avec_cache

        call_count = 0

        @avec_cache(ttl=60, key_func=lambda x: f"custom_{x}")
        def func_custom(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + 1

        func_custom(3)
        func_custom(3)
        assert call_count == 1


# ═══════════════════════════════════════════════════════════
# TESTS @avec_gestion_erreurs
# ═══════════════════════════════════════════════════════════


class TestAvecGestionErreurs:
    """Tests pour le décorateur @avec_gestion_erreurs."""

    def test_retourne_default_sur_exception(self):
        """Une exception générique retourne la valeur par défaut."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(default_return=[])
        def func_erreur():
            raise RuntimeError("boom")

        result = func_erreur()
        assert result == []

    def test_retourne_resultat_normal(self):
        """Sans exception, le résultat normal est retourné."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(default_return=None)
        def func_ok():
            return {"data": 42}

        assert func_ok() == {"data": 42}

    def test_relance_exception_metier(self):
        """Les exceptions métier sont relancées par défaut."""
        from src.core.decorators import avec_gestion_erreurs
        from src.core.exceptions import ErreurValidation

        @avec_gestion_erreurs(default_return=None, relancer_metier=True)
        def func_metier():
            raise ErreurValidation("Données invalides")

        with pytest.raises(ErreurValidation):
            func_metier()

    def test_ne_relance_pas_si_desactive(self):
        """Avec relancer_metier=False, retourne default_return."""
        from src.core.decorators import avec_gestion_erreurs
        from src.core.exceptions import ErreurValidation

        @avec_gestion_erreurs(default_return="fallback", relancer_metier=False)
        def func_metier():
            raise ErreurValidation("Données invalides")

        result = func_metier()
        assert result == "fallback"

    def test_default_return_none(self):
        """Le défaut est None."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs()
        def func_boom():
            raise ValueError("oops")

        assert func_boom() is None


# ═══════════════════════════════════════════════════════════
# TESTS @avec_validation
# ═══════════════════════════════════════════════════════════


class MonSchema(BaseModel):
    nom: str = Field(..., min_length=1)
    age: int = Field(..., ge=0)


class TestAvecValidation:
    """Tests pour le décorateur @avec_validation."""

    def test_validation_reussie(self):
        """Données valides passent la validation et sont normalisées."""
        from src.core.decorators import avec_validation

        @avec_validation(MonSchema)
        def creer(data: dict) -> dict:
            return data

        result = creer(data={"nom": "Test", "age": 25})
        assert result == {"nom": "Test", "age": 25}

    def test_validation_echouee_leve_erreur(self):
        """Données invalides lèvent ErreurValidation."""
        from src.core.decorators import avec_validation
        from src.core.exceptions import ErreurValidation

        @avec_validation(MonSchema)
        def creer(data: dict) -> dict:
            return data

        with pytest.raises(ErreurValidation):
            creer(data={"nom": "", "age": -1})

    def test_validation_avec_param_name(self):
        """Supporte un nom de paramètre personnalisé."""
        from src.core.decorators import avec_validation

        @avec_validation(MonSchema, param_name="donnees")
        def creer(donnees: dict) -> dict:
            return donnees

        result = creer(donnees={"nom": "Alice", "age": 30})
        assert result["nom"] == "Alice"

    def test_validation_sans_injection(self):
        """Avec inject_validated=False, valide mais ne remplace pas."""
        from src.core.decorators import avec_validation

        raw_data = {"nom": "Bob", "age": 20, "extra": "ignored"}

        @avec_validation(MonSchema, inject_validated=False)
        def creer(data: dict) -> dict:
            return data

        result = creer(data=raw_data)
        assert "extra" in result  # Les données originales sont conservées


# ═══════════════════════════════════════════════════════════
# TESTS @avec_resilience
# ═══════════════════════════════════════════════════════════


class TestAvecResilience:
    """Tests pour le décorateur @avec_resilience."""

    def test_sans_policies(self):
        """Sans retry/timeout, exécute directement."""
        from src.core.decorators import avec_resilience

        @avec_resilience()
        def func_simple():
            return 42

        assert func_simple() == 42

    def test_avec_fallback(self):
        """Avec fallback, retourne la valeur de fallback sur erreur."""
        from src.core.decorators import avec_resilience

        @avec_resilience(fallback="fallback_value")
        def func_erreur():
            raise RuntimeError("boom")

        assert func_erreur() == "fallback_value"

    def test_retry_reussit(self):
        """Retry réussit après des échecs."""
        from src.core.decorators import avec_resilience

        attempts = 0

        @avec_resilience(retry=3, fallback="failed")
        def func_instable():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ConnectionError("retry me")
            return "success"

        result = func_instable()
        assert result == "success"
        assert attempts == 3

    def test_propage_exception_sans_fallback(self):
        """Sans fallback, l'exception est propagée."""
        from src.core.decorators import avec_resilience

        @avec_resilience(retry=1)
        def func_erreur():
            raise ValueError("fatal")

        with pytest.raises(ValueError, match="fatal"):
            func_erreur()
