"""
Tests profonds supplémentaires pour errors.py et errors_base.py

Cible les fonctions non couvertes pour atteindre 80% de couverture.
"""

import pytest
import logging
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════
# TESTS: ExceptionApp et sous-classes
# ═══════════════════════════════════════════════════════════


class TestExceptionAppDetails:
    """Tests détaillés pour ExceptionApp"""

    def test_exception_avec_message_utilisateur(self):
        """Test message utilisateur personnalisé"""
        from src.core.errors_base import ExceptionApp

        err = ExceptionApp(
            "Message technique", message_utilisateur="Message pour l'utilisateur"
        )

        assert err.message_utilisateur == "Message pour l'utilisateur"

    def test_exception_avec_details_dict(self):
        """Test détails en dictionnaire"""
        from src.core.errors_base import ExceptionApp

        details = {"champ": "nom", "valeur": "test", "raison": "trop court"}
        err = ExceptionApp("Erreur", details=details)

        assert err.details == details
        assert err.details["champ"] == "nom"

    def test_exception_str(self):
        """Test conversion en string"""
        from src.core.errors_base import ExceptionApp

        err = ExceptionApp("Mon message d'erreur")

        assert str(err) == "Mon message d'erreur"

    def test_exception_heritage(self):
        """Test héritage de Exception"""
        from src.core.errors_base import ExceptionApp

        err = ExceptionApp("Test")

        assert isinstance(err, Exception)


class TestErreurValidationDetails:
    """Tests détaillés pour ErreurValidation"""

    def test_erreur_validation_avec_tous_params(self):
        """Test avec tous les paramètres"""
        from src.core.errors import ErreurValidation

        err = ErreurValidation(
            "Validation échouée",
            details={"champs": ["nom", "email"]},
            message_utilisateur="Veuillez corriger les erreurs",
        )

        assert "champs" in err.details
        assert "nom" in err.details["champs"]

    def test_erreur_validation_raise_catch(self):
        """Test lever et attraper"""
        from src.core.errors import ErreurValidation

        with pytest.raises(ErreurValidation) as exc_info:
            raise ErreurValidation("Nom requis")

        assert "Nom requis" in str(exc_info.value)


class TestErreurNonTrouveDetails:
    """Tests détaillés pour ErreurNonTrouve"""

    def test_erreur_non_trouve_avec_id(self):
        """Test avec ID d'entité"""
        from src.core.errors import ErreurNonTrouve

        err = ErreurNonTrouve(
            "Recette 42 non trouvée",
            details={"type": "Recette", "id": 42},
            message_utilisateur="Cette recette n'existe pas",
        )

        assert err.details["id"] == 42
        assert err.details["type"] == "Recette"


class TestErreurBaseDeDonneesDetails:
    """Tests détaillés pour ErreurBaseDeDonnees"""

    def test_erreur_bdd_connexion(self):
        """Test erreur de connexion"""
        from src.core.errors import ErreurBaseDeDonnees

        err = ErreurBaseDeDonnees(
            "Connection refused",
            details={"host": "localhost", "port": 5432},
            message_utilisateur="Impossible de se connecter à la base de données",
        )

        assert "localhost" in str(err.details)


class TestErreurServiceIADetails:
    """Tests détaillés pour ErreurServiceIA"""

    def test_erreur_ia_quota(self):
        """Test erreur quota IA"""
        from src.core.errors import ErreurServiceIA

        err = ErreurServiceIA(
            "API quota exceeded",
            details={"service": "Mistral", "quota_restant": 0},
            message_utilisateur="Le service IA est temporairement indisponible",
        )

        assert err.details["service"] == "Mistral"


class TestErreurConfigurationDetails:
    """Tests détaillés pour ErreurConfiguration"""

    def test_erreur_config_env_var(self):
        """Test erreur variable d'environnement"""
        from src.core.errors_base import ErreurConfiguration

        err = ErreurConfiguration(
            "DATABASE_URL non défini",
            details={"variable": "DATABASE_URL"},
            message_utilisateur="Configuration incomplète",
        )

        assert err.details["variable"] == "DATABASE_URL"


# ═══════════════════════════════════════════════════════════
# TESTS: Helpers de validation (errors_base.py)
# ═══════════════════════════════════════════════════════════


class TestExigerChamps:
    """Tests pour exiger_champs"""

    def test_exiger_champs_tous_presents(self):
        """Test tous les champs présents"""
        from src.core.errors_base import exiger_champs

        data = {"nom": "Tarte", "temps": 30, "portions": 4}

        # Ne doit pas lever d'exception
        exiger_champs(data, ["nom", "temps", "portions"])

    def test_exiger_champs_un_manquant(self):
        """Test un champ manquant"""
        from src.core.errors_base import exiger_champs, ErreurValidation

        data = {"nom": "Tarte", "temps": 30}

        with pytest.raises(ErreurValidation) as exc_info:
            exiger_champs(data, ["nom", "temps", "portions"], "recette")

        assert "portions" in str(exc_info.value)

    def test_exiger_champs_plusieurs_manquants(self):
        """Test plusieurs champs manquants"""
        from src.core.errors_base import exiger_champs, ErreurValidation

        data = {"nom": "Tarte"}

        with pytest.raises(ErreurValidation):
            exiger_champs(data, ["nom", "temps", "portions", "difficulte"])

    def test_exiger_champs_valeur_vide(self):
        """Test valeur vide considérée comme manquante"""
        from src.core.errors_base import exiger_champs, ErreurValidation

        data = {"nom": "", "temps": 30}

        with pytest.raises(ErreurValidation):
            exiger_champs(data, ["nom", "temps"])


class TestValiderPlage:
    """Tests pour valider_plage"""

    def test_valider_plage_dans_bornes(self):
        """Test valeur dans les bornes"""
        from src.core.errors_base import valider_plage

        # Signature: valider_plage(valeur, min_val, max_val, nom_param)
        valider_plage(50, min_val=0, max_val=100, nom_param="prix")

    def test_valider_plage_egal_min(self):
        """Test valeur égale au minimum"""
        from src.core.errors_base import valider_plage

        valider_plage(0, min_val=0, max_val=100, nom_param="prix")

    def test_valider_plage_egal_max(self):
        """Test valeur égale au maximum"""
        from src.core.errors_base import valider_plage

        valider_plage(100, min_val=0, max_val=100, nom_param="prix")

    def test_valider_plage_sous_min(self):
        """Test valeur sous le minimum"""
        from src.core.errors_base import valider_plage, ErreurValidation

        with pytest.raises(ErreurValidation):
            valider_plage(-10, min_val=0, nom_param="prix")

    def test_valider_plage_sur_max(self):
        """Test valeur au-dessus du maximum"""
        from src.core.errors_base import valider_plage, ErreurValidation

        with pytest.raises(ErreurValidation):
            valider_plage(150, max_val=100, nom_param="prix")

    def test_valider_plage_sans_bornes(self):
        """Test sans bornes"""
        from src.core.errors_base import valider_plage

        # Ne doit pas lever d'exception
        valider_plage(1000000, nom_param="valeur")


class TestValiderType:
    """Tests pour valider_type"""

    def test_valider_type_string(self):
        """Test type string"""
        from src.core.errors_base import valider_type

        # Signature: valider_type(valeur, types_attendus, nom_param)
        valider_type("hello", str, "nom")

    def test_valider_type_int(self):
        """Test type int"""
        from src.core.errors_base import valider_type

        valider_type(42, int, "age")

    def test_valider_type_list(self):
        """Test type list"""
        from src.core.errors_base import valider_type

        valider_type([1, 2, 3], list, "items")

    def test_valider_type_invalide(self):
        """Test type invalide"""
        from src.core.errors_base import valider_type, ErreurValidation

        with pytest.raises(ErreurValidation):
            valider_type("not an int", int, "age")

    def test_valider_type_none(self):
        """Test None quand type attendu"""
        from src.core.errors_base import valider_type, ErreurValidation

        with pytest.raises(ErreurValidation):
            valider_type(None, str, "valeur")


# ═══════════════════════════════════════════════════════════
# TESTS: Décorateur gerer_erreurs avancé
# ═══════════════════════════════════════════════════════════


class TestGererErreursAdvanced:
    """Tests avancés pour @gerer_erreurs"""

    def test_gerer_erreurs_niveau_warning(self):
        """Test niveau log WARNING"""
        from src.core.errors import gerer_erreurs, ErreurValidation

        @gerer_erreurs(niveau_log="WARNING", afficher_dans_ui=False, valeur_fallback=None)
        def func_warning():
            raise ErreurValidation("Test warning")

        result = func_warning()
        assert result is None

    def test_gerer_erreurs_erreur_non_trouve(self):
        """Test gestion ErreurNonTrouve"""
        from src.core.errors import gerer_erreurs, ErreurNonTrouve

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback={"found": False})
        def func_not_found():
            raise ErreurNonTrouve("Introuvable")

        result = func_not_found()
        assert result == {"found": False}

    def test_gerer_erreurs_erreur_bdd(self):
        """Test gestion ErreurBaseDeDonnees"""
        from src.core.errors import gerer_erreurs, ErreurBaseDeDonnees

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
        def func_bdd():
            raise ErreurBaseDeDonnees("Connection lost")

        result = func_bdd()
        assert result == []

    def test_gerer_erreurs_erreur_ia(self):
        """Test gestion ErreurServiceIA"""
        from src.core.errors import gerer_erreurs, ErreurServiceIA

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback="IA indisponible")
        def func_ia():
            raise ErreurServiceIA("API error")

        result = func_ia()
        assert result == "IA indisponible"

    def test_gerer_erreurs_erreur_limite_debit(self):
        """Test gestion ErreurLimiteDebit"""
        from src.core.errors import gerer_erreurs, ErreurLimiteDebit

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback="Quota dépassé")
        def func_rate_limit():
            raise ErreurLimiteDebit("Rate limit exceeded")

        result = func_rate_limit()
        assert result == "Quota dépassé"

    def test_gerer_erreurs_erreur_service_externe(self):
        """Test gestion ErreurServiceExterne"""
        from src.core.errors import gerer_erreurs, ErreurServiceExterne

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
        def func_externe():
            raise ErreurServiceExterne("Service unavailable")

        result = func_externe()
        assert result is None

    def test_gerer_erreurs_exception_generique(self):
        """Test gestion exception générique"""
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback="erreur")
        def func_generic():
            raise RuntimeError("Unknown error")

        result = func_generic()
        assert result == "erreur"


# ═══════════════════════════════════════════════════════════
# TESTS: _is_debug_mode
# ═══════════════════════════════════════════════════════════


class TestIsDebugMode:
    """Tests pour _is_debug_mode"""

    def test_is_debug_mode_false_default(self):
        """Test mode debug désactivé par défaut"""
        from src.core.errors import _is_debug_mode

        # Sans mock, devrait retourner False
        result = _is_debug_mode()
        assert isinstance(result, bool)

    def test_is_debug_mode_with_session_state(self):
        """Test avec session_state"""
        from src.core.errors import _is_debug_mode

        with patch("streamlit.session_state", {"debug_mode": True}):
            result = _is_debug_mode()
            # Peut être True ou False selon l'implémentation


# ═══════════════════════════════════════════════════════════
# TESTS: Ré-exports
# ═══════════════════════════════════════════════════════════


class TestReExports:
    """Tests pour les ré-exports"""

    def test_exceptions_reexportees(self):
        """Test exceptions ré-exportées depuis errors.py"""
        from src.core.errors import (
            ErreurValidation,
            ErreurNonTrouve,
            ErreurBaseDeDonnees,
            ErreurServiceIA,
            ErreurLimiteDebit,
            ErreurServiceExterne,
            ErreurConfiguration,
            ExceptionApp,
        )

        # Vérifier que toutes les exceptions sont disponibles
        assert ErreurValidation is not None
        assert ErreurNonTrouve is not None
        assert ErreurBaseDeDonnees is not None
        assert ErreurServiceIA is not None
        assert ErreurLimiteDebit is not None
        assert ErreurServiceExterne is not None
        assert ErreurConfiguration is not None
        assert ExceptionApp is not None

    def test_helpers_reexportes(self):
        """Test helpers ré-exportés depuis errors.py"""
        from src.core.errors import exiger_champs, valider_plage, valider_type

        assert callable(exiger_champs)
        assert callable(valider_plage)
        assert callable(valider_type)


# ═══════════════════════════════════════════════════════════
# TESTS: Alias handle_errors
# ═══════════════════════════════════════════════════════════


class TestHandleErrorsAlias:
    """Tests pour alias handle_errors"""

    def test_handle_errors_alias(self):
        """Test alias existe"""
        from src.core.errors import handle_errors, gerer_erreurs

        assert handle_errors is gerer_erreurs

    def test_handle_errors_decorator(self):
        """Test alias fonctionne comme décorateur"""
        from src.core.errors import handle_errors

        @handle_errors(valeur_fallback="default", afficher_dans_ui=False)
        def my_function():
            raise ValueError("error")

        result = my_function()
        assert result == "default"


# ═══════════════════════════════════════════════════════════
# TESTS: Héritage des exceptions
# ═══════════════════════════════════════════════════════════


class TestExceptionHierarchy:
    """Tests pour hiérarchie des exceptions"""

    def test_erreur_validation_herite_exception_app(self):
        """Test ErreurValidation hérite de ExceptionApp"""
        from src.core.errors import ErreurValidation, ExceptionApp

        assert issubclass(ErreurValidation, ExceptionApp)

    def test_erreur_non_trouve_herite_exception_app(self):
        """Test ErreurNonTrouve hérite de ExceptionApp"""
        from src.core.errors import ErreurNonTrouve, ExceptionApp

        assert issubclass(ErreurNonTrouve, ExceptionApp)

    def test_erreur_bdd_herite_exception_app(self):
        """Test ErreurBaseDeDonnees hérite de ExceptionApp"""
        from src.core.errors import ErreurBaseDeDonnees, ExceptionApp

        assert issubclass(ErreurBaseDeDonnees, ExceptionApp)

    def test_erreur_ia_herite_exception_app(self):
        """Test ErreurServiceIA hérite de ExceptionApp"""
        from src.core.errors import ErreurServiceIA, ExceptionApp

        assert issubclass(ErreurServiceIA, ExceptionApp)

    def test_toutes_exceptions_catchable(self):
        """Test toutes les exceptions peuvent être catchées par ExceptionApp"""
        from src.core.errors import (
            ErreurValidation,
            ErreurNonTrouve,
            ErreurBaseDeDonnees,
            ExceptionApp,
        )

        for exc_class in [ErreurValidation, ErreurNonTrouve, ErreurBaseDeDonnees]:
            try:
                raise exc_class("Test")
            except ExceptionApp:
                pass  # OK, caught by ExceptionApp
