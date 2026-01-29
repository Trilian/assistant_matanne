"""
Tests pour le module errors_base.py.

Tests couverts:
- Toutes les classes d'exceptions
- Méthodes to_dict, __str__, __repr__
- Fonctions de validation (exiger_champs, valider_type, valider_plage)
"""

import pytest

from src.core.errors_base import (
    ExceptionApp,
    ErreurValidation,
    ErreurNonTrouve,
    ErreurBaseDeDonnees,
    ErreurServiceIA,
    ErreurLimiteDebit,
    ErreurServiceExterne,
    ErreurConfiguration,
    exiger_champs,
    valider_type,
    valider_plage,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXCEPTION DE BASE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExceptionApp:
    """Tests pour la classe ExceptionApp de base."""

    def test_creation_simple(self):
        """Test création avec message seul."""
        exc = ExceptionApp("Test error")
        
        assert exc.message == "Test error"
        assert exc.details == {}
        assert exc.message_utilisateur == "Test error"
        assert exc.code_erreur == "APP_ERROR"

    def test_creation_complete(self):
        """Test création avec tous les paramètres."""
        exc = ExceptionApp(
            message="Technical error",
            details={"key": "value"},
            message_utilisateur="Erreur technique",
            code_erreur="CUSTOM_ERROR",
        )
        
        assert exc.message == "Technical error"
        assert exc.details == {"key": "value"}
        assert exc.message_utilisateur == "Erreur technique"
        assert exc.code_erreur == "CUSTOM_ERROR"

    def test_str(self):
        """Test __str__."""
        exc = ExceptionApp("My error")
        assert str(exc) == "My error"

    def test_repr(self):
        """Test __repr__."""
        exc = ExceptionApp("My error")
        assert repr(exc) == "ExceptionApp('My error')"

    def test_to_dict(self):
        """Test conversion en dictionnaire."""
        exc = ExceptionApp(
            message="Error message",
            details={"id": 42},
            message_utilisateur="Message utilisateur",
            code_erreur="CODE123",
        )
        
        data = exc.to_dict()
        
        assert data["type"] == "ExceptionApp"
        assert data["message"] == "Error message"
        assert data["code_erreur"] == "CODE123"
        assert data["message_utilisateur"] == "Message utilisateur"
        assert data["details"] == {"id": 42}

    def test_can_be_raised(self):
        """Test qu'on peut lever l'exception."""
        with pytest.raises(ExceptionApp) as exc_info:
            raise ExceptionApp("Test raise")
        
        assert exc_info.value.message == "Test raise"

    def test_inherits_from_exception(self):
        """Test héritage de Exception."""
        exc = ExceptionApp("Test")
        assert isinstance(exc, Exception)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXCEPTIONS SPÃ‰CIALISÃ‰ES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestErreurValidation:
    """Tests pour ErreurValidation."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurValidation("Invalid data")
        assert exc.code_erreur == "VALIDATION_ERROR"

    def test_inherits_exception_app(self):
        """Test héritage de ExceptionApp."""
        exc = ErreurValidation("Invalid")
        assert isinstance(exc, ExceptionApp)

    def test_to_dict_type(self):
        """Test type dans to_dict."""
        exc = ErreurValidation("Test")
        data = exc.to_dict()
        assert data["type"] == "ErreurValidation"


class TestErreurNonTrouve:
    """Tests pour ErreurNonTrouve."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurNonTrouve("Resource not found")
        assert exc.code_erreur == "NOT_FOUND"

    def test_with_details(self):
        """Test avec détails."""
        exc = ErreurNonTrouve(
            "Recette non trouvée",
            details={"id": 123, "table": "recettes"},
        )
        
        assert exc.details["id"] == 123
        assert exc.details["table"] == "recettes"


class TestErreurBaseDeDonnees:
    """Tests pour ErreurBaseDeDonnees."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurBaseDeDonnees("Connection failed")
        assert exc.code_erreur == "DATABASE_ERROR"

    def test_can_override_code(self):
        """Test qu'on peut surcharger le code."""
        exc = ErreurBaseDeDonnees("Error", code_erreur="DB_TIMEOUT")
        assert exc.code_erreur == "DB_TIMEOUT"


class TestErreurServiceIA:
    """Tests pour ErreurServiceIA."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurServiceIA("API error")
        assert exc.code_erreur == "AI_SERVICE_ERROR"

    def test_with_api_details(self):
        """Test avec détails API."""
        exc = ErreurServiceIA(
            "Timeout",
            details={"endpoint": "/chat", "timeout": 30},
        )
        
        assert exc.details["endpoint"] == "/chat"
        assert exc.details["timeout"] == 30


class TestErreurLimiteDebit:
    """Tests pour ErreurLimiteDebit."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurLimiteDebit("Rate limit exceeded")
        assert exc.code_erreur == "RATE_LIMIT_EXCEEDED"

    def test_with_rate_details(self):
        """Test avec détails de rate limit."""
        exc = ErreurLimiteDebit(
            "Limite atteinte",
            details={
                "calls_remaining": 0,
                "reset_at": "2024-01-15T12:00:00",
                "period": "hourly",
            },
        )
        
        assert exc.details["calls_remaining"] == 0
        assert exc.details["period"] == "hourly"


class TestErreurServiceExterne:
    """Tests pour ErreurServiceExterne."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurServiceExterne("External API failed")
        assert exc.code_erreur == "EXTERNAL_SERVICE_ERROR"


class TestErreurConfiguration:
    """Tests pour ErreurConfiguration."""

    def test_code_erreur_default(self):
        """Test code erreur par défaut."""
        exc = ErreurConfiguration("Missing env var")
        assert exc.code_erreur == "CONFIGURATION_ERROR"

    def test_with_config_details(self):
        """Test avec détails de configuration."""
        exc = ErreurConfiguration(
            "DATABASE_URL manquant",
            details={"variable": "DATABASE_URL", "required": True},
            message_utilisateur="Configuration manquante",
        )
        
        assert exc.details["variable"] == "DATABASE_URL"
        assert exc.message_utilisateur == "Configuration manquante"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FONCTION EXIGER_CHAMPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExigerChamps:
    """Tests pour la fonction exiger_champs."""

    def test_all_fields_present(self):
        """Test avec tous les champs présents."""
        data = {"nom": "Tarte", "temps": 30, "portions": 4}
        
        # Ne doit pas lever d'exception
        exiger_champs(data, ["nom", "temps", "portions"], "recette")

    def test_missing_field_raises(self):
        """Test avec champ manquant."""
        data = {"nom": "Tarte", "temps": 30}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps", "portions"], "recette")
        
        assert "portions" in str(exc_info.value)
        assert exc_info.value.details["champs_manquants"] == ["portions"]

    def test_empty_field_treated_as_missing(self):
        """Test champ vide traité comme manquant."""
        data = {"nom": "Tarte", "temps": 30, "portions": ""}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps", "portions"], "recette")
        
        assert "portions" in exc_info.value.details["champs_manquants"]

    def test_none_field_treated_as_missing(self):
        """Test champ None traité comme manquant."""
        data = {"nom": "Tarte", "temps": None}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps"], "recette")
        
        assert "temps" in exc_info.value.details["champs_manquants"]

    def test_multiple_missing_fields(self):
        """Test plusieurs champs manquants."""
        data = {"nom": "Tarte"}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps", "portions", "difficulte"], "recette")
        
        manquants = exc_info.value.details["champs_manquants"]
        assert "temps" in manquants
        assert "portions" in manquants
        assert "difficulte" in manquants

    def test_message_utilisateur_formatted(self):
        """Test message utilisateur formaté."""
        data = {"nom": "Tarte"}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps", "portions"], "recette")
        
        assert "Champs obligatoires manquants" in exc_info.value.message_utilisateur

    def test_default_nom_objet(self):
        """Test nom objet par défaut."""
        data = {}
        
        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["champ"])
        
        assert "objet" in str(exc_info.value)

    def test_empty_champs_list(self):
        """Test liste de champs vide."""
        data = {"any": "value"}
        
        # Ne doit pas lever d'exception
        exiger_champs(data, [], "test")

    def test_zero_value_accepted(self):
        """Test valeur 0 acceptée (truthy test)."""
        data = {"count": 0}
        
        # 0 est falsy, donc sera traité comme manquant
        with pytest.raises(ErreurValidation):
            exiger_champs(data, ["count"], "test")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FONCTION VALIDER_TYPE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderType:
    """Tests pour la fonction valider_type."""

    def test_correct_type(self):
        """Test avec type correct."""
        # Ne doit pas lever d'exception
        valider_type("hello", str, "message")
        valider_type(42, int, "count")
        valider_type(3.14, float, "value")
        valider_type([1, 2], list, "items")
        valider_type({"a": 1}, dict, "data")

    def test_wrong_type_raises(self):
        """Test avec type incorrect."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_type(42, str, "age")
        
        assert "age" in str(exc_info.value)
        assert "str" in str(exc_info.value)
        assert "int" in str(exc_info.value)

    def test_multiple_types_accepted(self):
        """Test avec plusieurs types acceptés."""
        # Ne doit pas lever d'exception
        valider_type(42, (int, str), "value")
        valider_type("hello", (int, str), "value")

    def test_multiple_types_rejected(self):
        """Test avec plusieurs types, aucun ne correspond."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_type(3.14, (int, str), "value")
        
        assert "int ou str" in str(exc_info.value)

    def test_details_populated(self):
        """Test détails remplis."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_type([1, 2], str, "data")
        
        details = exc_info.value.details
        assert details["parametre"] == "data"
        assert details["type_attendu"] == "str"
        assert details["type_recu"] == "list"

    def test_default_nom_param(self):
        """Test nom paramètre par défaut."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_type(42, str)
        
        assert "paramètre" in str(exc_info.value)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FONCTION VALIDER_PLAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderPlage:
    """Tests pour la fonction valider_plage."""

    def test_value_in_range(self):
        """Test valeur dans la plage."""
        # Ne doit pas lever d'exception
        valider_plage(5, min_val=1, max_val=10)
        valider_plage(1, min_val=1, max_val=10)  # Limite basse
        valider_plage(10, min_val=1, max_val=10)  # Limite haute

    def test_below_min_raises(self):
        """Test valeur sous le minimum."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_plage(0, min_val=1, max_val=10, nom_param="age")
        
        assert ">= 1" in str(exc_info.value)
        assert exc_info.value.details["min"] == 1
        assert exc_info.value.details["recu"] == 0

    def test_above_max_raises(self):
        """Test valeur au-dessus du maximum."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_plage(15, min_val=1, max_val=10, nom_param="age")
        
        assert "<= 10" in str(exc_info.value)
        assert exc_info.value.details["max"] == 10
        assert exc_info.value.details["recu"] == 15

    def test_min_only(self):
        """Test avec min seulement."""
        valider_plage(100, min_val=1)  # Pas de max, OK
        
        with pytest.raises(ErreurValidation):
            valider_plage(0, min_val=1)

    def test_max_only(self):
        """Test avec max seulement."""
        valider_plage(-100, max_val=10)  # Pas de min, OK
        
        with pytest.raises(ErreurValidation):
            valider_plage(20, max_val=10)

    def test_float_values(self):
        """Test avec valeurs float."""
        valider_plage(5.5, min_val=1.0, max_val=10.0)
        
        with pytest.raises(ErreurValidation):
            valider_plage(0.5, min_val=1.0)

    def test_negative_range(self):
        """Test avec plage négative."""
        valider_plage(-5, min_val=-10, max_val=-1)
        
        with pytest.raises(ErreurValidation):
            valider_plage(0, min_val=-10, max_val=-1)

    def test_default_nom_param(self):
        """Test nom paramètre par défaut."""
        with pytest.raises(ErreurValidation) as exc_info:
            valider_plage(100, max_val=10)
        
        assert "valeur" in str(exc_info.value)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS D'INTÃ‰GRATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExceptionsIntegration:
    """Tests d'intégration des exceptions."""

    def test_exception_hierarchy(self):
        """Test hiérarchie des exceptions."""
        exc = ErreurValidation("Test")
        
        assert isinstance(exc, ErreurValidation)
        assert isinstance(exc, ExceptionApp)
        assert isinstance(exc, Exception)

    def test_catch_base_catches_all(self):
        """Test que capturer ExceptionApp capture toutes les sous-classes."""
        exceptions = [
            ErreurValidation("test"),
            ErreurNonTrouve("test"),
            ErreurBaseDeDonnees("test"),
            ErreurServiceIA("test"),
            ErreurLimiteDebit("test"),
            ErreurServiceExterne("test"),
            ErreurConfiguration("test"),
        ]
        
        for exc in exceptions:
            try:
                raise exc
            except ExceptionApp as caught:
                assert caught is exc

    def test_all_exceptions_have_to_dict(self):
        """Test toutes les exceptions ont to_dict."""
        exceptions = [
            ExceptionApp("test"),
            ErreurValidation("test"),
            ErreurNonTrouve("test"),
            ErreurBaseDeDonnees("test"),
            ErreurServiceIA("test"),
            ErreurLimiteDebit("test"),
            ErreurServiceExterne("test"),
            ErreurConfiguration("test"),
        ]
        
        for exc in exceptions:
            data = exc.to_dict()
            assert "type" in data
            assert "message" in data
            assert "code_erreur" in data

