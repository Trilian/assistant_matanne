"""Tests pour Result[T, E] — Pattern Result pour contrôle de flux explicite."""

import pytest

from src.services.core.base.result import (
    ErrorCode,
    ErrorInfo,
    Failure,
    Success,
    collect,
    collect_all,
    failure,
    from_exception,
    safe,
    success,
)

# ═══════════════════════════════════════════════════════════
# SUCCESS
# ═══════════════════════════════════════════════════════════


class TestSuccess:
    """Tests du type Success."""

    def test_creation(self):
        result = Success(42)
        assert result.value == 42
        assert result.is_success is True
        assert result.is_failure is False
        assert result.error is None

    def test_creation_avec_none(self):
        result = Success(None)
        assert result.value is None
        assert result.is_success is True

    def test_creation_avec_objet_complexe(self):
        data = {"nom": "Tarte", "ingredients": ["farine", "beurre"]}
        result = Success(data)
        assert result.value == data

    def test_map_transforme_valeur(self):
        result = Success(5).map(lambda x: x * 2)
        assert isinstance(result, Success)
        assert result.value == 10

    def test_map_chainable(self):
        result = Success("hello").map(str.upper).map(lambda s: s + "!")
        assert isinstance(result, Success)
        assert result.value == "HELLO!"

    def test_map_capture_exception(self):
        result = Success(0).map(lambda x: 1 / x)
        assert isinstance(result, Failure)
        assert isinstance(result.error, ErrorInfo)
        assert result.error.code == ErrorCode.INTERNAL_ERROR

    def test_flat_map_succes(self):
        def double_positif(x: int):
            if x > 0:
                return Success(x * 2)
            return Failure("Nombre négatif")

        result = Success(5).flat_map(double_positif)
        assert isinstance(result, Success)
        assert result.value == 10

    def test_flat_map_echec(self):
        def double_positif(x: int):
            if x > 0:
                return Success(x * 2)
            return Failure("Nombre négatif")

        result = Success(-1).flat_map(double_positif)
        assert isinstance(result, Failure)
        assert result.error == "Nombre négatif"

    def test_flat_map_capture_exception(self):
        def raise_func(x):
            raise RuntimeError("boom")

        result = Success(1).flat_map(raise_func)
        assert isinstance(result, Failure)

    def test_or_else_ignore_fallback(self):
        result = Success(42).or_else(lambda _: Success(0))
        assert isinstance(result, Success)
        assert result.value == 42

    def test_unwrap(self):
        assert Success(99).unwrap() == 99

    def test_unwrap_or(self):
        assert Success(42).unwrap_or(0) == 42

    def test_unwrap_or_else(self):
        assert Success(42).unwrap_or_else(lambda _: 0) == 42

    def test_on_success_execute_callback(self):
        side_effects = []
        result = Success(42).on_success(lambda v: side_effects.append(v))
        assert side_effects == [42]
        assert isinstance(result, Success)

    def test_on_success_exception_dans_callback_ne_propage_pas(self):
        result = Success(42).on_success(lambda v: (_ for _ in ()).throw(RuntimeError("boom")))
        # Ne doit pas lever d'exception, juste logger un warning
        assert isinstance(result, Success)

    def test_on_failure_ne_fait_rien(self):
        side_effects = []
        result = Success(42).on_failure(lambda e: side_effects.append(e))
        assert side_effects == []
        assert isinstance(result, Success)


# ═══════════════════════════════════════════════════════════
# FAILURE
# ═══════════════════════════════════════════════════════════


class TestFailure:
    """Tests du type Failure."""

    def test_creation(self):
        result = Failure("erreur")
        assert result.error == "erreur"
        assert result.is_success is False
        assert result.is_failure is True
        assert result.value is None

    def test_creation_avec_error_info(self):
        info = ErrorInfo(
            code=ErrorCode.VALIDATION_ERROR,
            message="Champ requis",
            source="test",
        )
        result = Failure(info)
        assert result.error.code == ErrorCode.VALIDATION_ERROR
        assert result.error.message == "Champ requis"

    def test_map_ne_fait_rien(self):
        original = Failure("erreur")
        result = original.map(lambda x: x * 2)
        assert isinstance(result, Failure)
        assert result.error == "erreur"

    def test_flat_map_ne_fait_rien(self):
        original = Failure("erreur")
        result = original.flat_map(lambda x: Success(x * 2))
        assert isinstance(result, Failure)
        assert result.error == "erreur"

    def test_or_else_execute_fallback(self):
        result = Failure("erreur").or_else(lambda e: Success(f"récupéré: {e}"))
        assert isinstance(result, Success)
        assert result.value == "récupéré: erreur"

    def test_or_else_capture_exception(self):
        def bad_fallback(e):
            raise RuntimeError("fallback échoué")

        result = Failure("erreur").or_else(bad_fallback)
        assert isinstance(result, Failure)

    def test_unwrap_leve_exception(self):
        with pytest.raises(ValueError, match="Tentative de unwrap"):
            Failure("erreur").unwrap()

    def test_unwrap_avec_error_info(self):
        info = ErrorInfo(
            code=ErrorCode.NOT_FOUND,
            message="Recette introuvable",
        )
        with pytest.raises(ValueError, match="NOT_FOUND"):
            Failure(info).unwrap()

    def test_unwrap_or(self):
        assert Failure("erreur").unwrap_or(42) == 42

    def test_unwrap_or_else(self):
        assert Failure("erreur").unwrap_or_else(lambda e: len(e)) == 6

    def test_on_success_ne_fait_rien(self):
        side_effects = []
        result = Failure("erreur").on_success(lambda v: side_effects.append(v))
        assert side_effects == []
        assert isinstance(result, Failure)

    def test_on_failure_execute_callback(self):
        side_effects = []
        result = Failure("erreur").on_failure(lambda e: side_effects.append(e))
        assert side_effects == ["erreur"]
        assert isinstance(result, Failure)

    def test_on_failure_exception_dans_callback_ne_propage_pas(self):
        def bad_callback(e):
            raise RuntimeError("boom")

        result = Failure("erreur").on_failure(bad_callback)
        assert isinstance(result, Failure)


# ═══════════════════════════════════════════════════════════
# ERROR INFO
# ═══════════════════════════════════════════════════════════


class TestErrorInfo:
    """Tests de ErrorInfo."""

    def test_creation_basique(self):
        info = ErrorInfo(code=ErrorCode.NOT_FOUND, message="Introuvable")
        assert info.code == ErrorCode.NOT_FOUND
        assert info.message == "Introuvable"
        assert info.message_utilisateur == "Introuvable"  # Auto-rempli

    def test_message_utilisateur_custom(self):
        info = ErrorInfo(
            code=ErrorCode.DATABASE_ERROR,
            message="UNIQUE constraint failed",
            message_utilisateur="Cette recette existe déjà",
        )
        assert info.message != info.message_utilisateur
        assert info.message_utilisateur == "Cette recette existe déjà"

    def test_immutable(self):
        info = ErrorInfo(code=ErrorCode.NOT_FOUND, message="test")
        with pytest.raises(AttributeError):
            info.message = "modifié"  # type: ignore[misc]

    def test_to_dict(self):
        info = ErrorInfo(
            code=ErrorCode.VALIDATION_ERROR,
            message="Champ requis",
            source="test_service",
            details={"field": "nom"},
        )
        d = info.to_dict()
        assert d["code"] == "VALIDATION_ERROR"
        assert d["message"] == "Champ requis"
        assert d["source"] == "test_service"
        assert d["details"] == {"field": "nom"}
        assert "timestamp" in d


# ═══════════════════════════════════════════════════════════
# ERROR CODE
# ═══════════════════════════════════════════════════════════


class TestErrorCode:
    """Tests de ErrorCode enum."""

    def test_est_string_enum(self):
        assert ErrorCode.NOT_FOUND == "NOT_FOUND"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"

    def test_toutes_les_categories_existent(self):
        codes = [e.value for e in ErrorCode]
        # Validation
        assert "VALIDATION_ERROR" in codes
        assert "MISSING_FIELD" in codes
        # Base de données
        assert "NOT_FOUND" in codes
        assert "DATABASE_ERROR" in codes
        # IA
        assert "AI_ERROR" in codes
        assert "RATE_LIMITED" in codes
        # Système
        assert "INTERNAL_ERROR" in codes

    def test_minimum_20_codes(self):
        assert len(ErrorCode) >= 20


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


class TestFactories:
    """Tests des fonctions factory."""

    def test_success_factory(self):
        result = success(42)
        assert isinstance(result, Success)
        assert result.value == 42

    def test_failure_factory(self):
        result = failure(ErrorCode.NOT_FOUND, "Introuvable")
        assert isinstance(result, Failure)
        assert isinstance(result.error, ErrorInfo)
        assert result.error.code == ErrorCode.NOT_FOUND
        assert result.error.message == "Introuvable"

    def test_failure_factory_avec_details(self):
        result = failure(
            ErrorCode.VALIDATION_ERROR,
            "Champ invalide",
            message_utilisateur="Veuillez corriger",
            details={"field": "nom"},
            source="test_service",
        )
        assert result.error.message_utilisateur == "Veuillez corriger"
        assert result.error.details == {"field": "nom"}
        assert result.error.source == "test_service"

    def test_from_exception_standard(self):
        try:
            raise ValueError("test error")
        except ValueError as e:
            result = from_exception(e, source="test")

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.INTERNAL_ERROR
        assert result.error.message == "test error"
        assert result.error.source == "test"

    def test_from_exception_avec_code_custom(self):
        try:
            raise RuntimeError("timeout")
        except RuntimeError as e:
            result = from_exception(e, code=ErrorCode.TIMEOUT)

        assert result.error.code == ErrorCode.TIMEOUT


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR @safe
# ═══════════════════════════════════════════════════════════


class TestSafeDecorator:
    """Tests du décorateur @safe."""

    def test_safe_succes(self):
        @safe
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 2)
        assert isinstance(result, Success)
        assert result.value == 5.0

    def test_safe_echec(self):
        @safe
        def diviser(a: int, b: int) -> float:
            return a / b

        result = diviser(10, 0)
        assert isinstance(result, Failure)
        assert isinstance(result.error, ErrorInfo)
        assert result.error.code == ErrorCode.INTERNAL_ERROR

    def test_safe_preserve_nom_fonction(self):
        @safe
        def ma_fonction():
            return 42

        assert ma_fonction.__name__ == "ma_fonction"

    def test_safe_avec_kwargs(self):
        @safe
        def greet(name: str, prefix: str = "Bonjour") -> str:
            return f"{prefix} {name}"

        result = greet("Jules", prefix="Salut")
        assert isinstance(result, Success)
        assert result.value == "Salut Jules"


# ═══════════════════════════════════════════════════════════
# COMBINATEURS
# ═══════════════════════════════════════════════════════════


class TestCombinators:
    """Tests des combinateurs collect et collect_all."""

    def test_collect_tous_succes(self):
        results = [success(1), success(2), success(3)]
        combined = collect(results)
        assert isinstance(combined, Success)
        assert combined.value == [1, 2, 3]

    def test_collect_avec_echec(self):
        results = [
            success(1),
            failure(ErrorCode.NOT_FOUND, "introuvable"),
            success(3),
        ]
        combined = collect(results)
        assert isinstance(combined, Failure)
        assert combined.error.code == ErrorCode.NOT_FOUND

    def test_collect_liste_vide(self):
        combined = collect([])
        assert isinstance(combined, Success)
        assert combined.value == []

    def test_collect_premier_echec(self):
        """collect retourne le PREMIER échec."""
        results = [
            failure(ErrorCode.NOT_FOUND, "premier"),
            failure(ErrorCode.VALIDATION_ERROR, "second"),
        ]
        combined = collect(results)
        assert isinstance(combined, Failure)
        assert combined.error.message == "premier"

    def test_collect_all_separe(self):
        results = [
            success(1),
            failure(ErrorCode.NOT_FOUND, "err1"),
            success(3),
            failure(ErrorCode.VALIDATION_ERROR, "err2"),
        ]
        successes, failures = collect_all(results)
        assert successes == [1, 3]
        assert len(failures) == 2

    def test_collect_all_tous_succes(self):
        results = [success(1), success(2)]
        successes, failures = collect_all(results)
        assert successes == [1, 2]
        assert failures == []

    def test_collect_all_tous_echecs(self):
        results = [
            failure(ErrorCode.NOT_FOUND, "a"),
            failure(ErrorCode.NOT_FOUND, "b"),
        ]
        successes, failures = collect_all(results)
        assert successes == []
        assert len(failures) == 2


# ═══════════════════════════════════════════════════════════
# CHAÎNAGE FONCTIONNEL
# ═══════════════════════════════════════════════════════════


class TestChainage:
    """Tests du chaînage fonctionnel end-to-end."""

    def test_pipeline_complet(self):
        """Scénario: transformer une recette avec chaînage."""

        def valider_nom(nom: str):
            if len(nom) < 3:
                return failure(ErrorCode.VALIDATION_ERROR, "Nom trop court")
            return success(nom)

        def capitaliser(nom: str):
            return success(nom.title())

        result = (
            valider_nom("tarte aux pommes").flat_map(capitaliser).map(lambda n: f"Recette: {n}")
        )

        assert isinstance(result, Success)
        assert result.value == "Recette: Tarte Aux Pommes"

    def test_pipeline_avec_erreur(self):
        """Le chaînage s'arrête à la première erreur."""

        def valider_nom(nom: str):
            if len(nom) < 3:
                return failure(ErrorCode.VALIDATION_ERROR, "Nom trop court")
            return success(nom)

        def capitaliser(nom: str):
            return success(nom.title())

        result = valider_nom("ab").flat_map(capitaliser).map(lambda n: f"Recette: {n}")

        assert isinstance(result, Failure)
        assert result.error.code == ErrorCode.VALIDATION_ERROR

    def test_unwrap_or_en_fin_de_pipeline(self):
        result = Success("hello").map(str.upper).map(lambda s: s + "!").unwrap_or("default")
        assert result == "HELLO!"
