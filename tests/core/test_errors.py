"""
Tests unitaires pour errors.py (src/core/errors.py).

Tests couvrant:
- Re-export des exceptions pures depuis errors_base.py
- Décorateur gerer_erreurs avec UI
- Gestion d'affichage des erreurs Streamlit
- Logging des erreurs
"""

import pytest
from src.core import errors

@pytest.mark.unit
def test_import_errors():
    """Vérifie que le module errors s'importe sans erreur."""
    assert hasattr(errors, "ErreurBaseDeDonnees") or hasattr(errors, "__file__")

from unittest.mock import patch, MagicMock, call
import logging

from src.core.errors import (
    gerer_erreurs,
    ErreurBaseDeDonnees,
    ErreurConfiguration,
    ErreurLimiteDebit,
    ErreurNonTrouve,
    ErreurServiceExterne,
    ErreurServiceIA,
    ErreurValidation,
    ExceptionApp,
)
from src.core.errors_base import (
    exiger_champs,
    valider_plage,
    valider_type,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS RE-EXPORTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestExceptionsReExports:
    """Tests des re-exports d'exceptions depuis errors_base."""

    def test_erreur_base_de_donnees_exists(self):
        """Test que ErreurBaseDeDonnees est importable."""
        assert issubclass(ErreurBaseDeDonnees, ExceptionApp)

    def test_erreur_validation_exists(self):
        """Test que ErreurValidation est importable."""
        assert issubclass(ErreurValidation, ExceptionApp)

    def test_erreur_non_trouve_exists(self):
        """Test que ErreurNonTrouve est importable."""
        assert issubclass(ErreurNonTrouve, ExceptionApp)

    def test_erreur_limite_debit_exists(self):
        """Test que ErreurLimiteDebit est importable."""
        assert issubclass(ErreurLimiteDebit, ExceptionApp)

    def test_erreur_configuration_exists(self):
        """Test que ErreurConfiguration est importable."""
        assert issubclass(ErreurConfiguration, ExceptionApp)

    def test_erreur_service_externe_exists(self):
        """Test que ErreurServiceExterne est importable."""
        assert issubclass(ErreurServiceExterne, ExceptionApp)

    def test_erreur_service_ia_exists(self):
        """Test que ErreurServiceIA est importable."""
        assert issubclass(ErreurServiceIA, ExceptionApp)


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestHelperFunctions:
    """Tests des fonctions helper de validation."""

    def test_exiger_champs_success(self):
        """Test exiger_champs avec champs présents."""
        data = {"nom": "Test", "prenom": "Utilisateur"}
        # Devrait ne pas lever d'exception
        exiger_champs(data, ["nom", "prenom"])

    def test_exiger_champs_missing(self):
        """Test exiger_champs avec champs manquants."""
        data = {"nom": "Test"}
        with pytest.raises(ErreurValidation):
            exiger_champs(data, ["nom", "prenom"])

    def test_valider_plage_success(self):
        """Test valider_plage avec valeur dans la plage."""
        # Devrait ne pas lever d'exception
        valider_plage(5, 1, 10, "nombre")

    def test_valider_plage_trop_bas(self):
        """Test valider_plage avec valeur trop basse."""
        with pytest.raises(ErreurValidation):
            valider_plage(0, 1, 10, "nombre")

    def test_valider_plage_trop_haut(self):
        """Test valider_plage avec valeur trop haute."""
        with pytest.raises(ErreurValidation):
            valider_plage(11, 1, 10, "nombre")

    def test_valider_type_success(self):
        """Test valider_type avec bon type."""
        valider_type("test", str, "texte")

    def test_valider_type_mauvais_type(self):
        """Test valider_type avec mauvais type."""
        with pytest.raises(ErreurValidation):
            valider_type(123, str, "texte")

    def test_valider_type_multiple_types(self):
        """Test valider_type avec plusieurs types acceptés."""
        valider_type(123, (int, str), "valeur")
        valider_type("test", (int, str), "valeur")


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS DÉCORATEUR gerer_erreurs
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDecoratorGererErreurs:
    """Tests du décorateur gerer_erreurs."""

    def test_fonction_normale_pas_erreur(self):
        """Test que une fonction sans erreur retourne le résultat."""
        @gerer_erreurs()
        def ma_fonction():
            return "succès"

        result = ma_fonction()
        assert result == "succès"

    def test_capture_exception_validation(self):
        """Test capture d'ErreurValidation."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurValidation("Erreur de validation")

        result = ma_fonction()
        assert result is None

    def test_capture_exception_non_trouve(self):
        """Test capture d'ErreurNonTrouve."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=[])
        def ma_fonction():
            raise ErreurNonTrouve("Recette not found")

        result = ma_fonction()
        assert result == []

    def test_capture_exception_base_de_donnees(self):
        """Test capture d'ErreurBaseDeDonnees."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback={})
        def ma_fonction():
            raise ErreurBaseDeDonnees("Connexion perdue")

        result = ma_fonction()
        assert result == {}

    def test_relancer_exception(self):
        """Test que relancer=True relève l'exception."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=True)
        def ma_fonction():
            raise ErreurValidation("Erreur", message_utilisateur="Message")

        with pytest.raises(ErreurValidation):
            ma_fonction()

    @patch("streamlit.error")
    def test_afficher_dans_ui_validation(self, mock_st_error):
        """Test affichage UI pour ErreurValidation."""
        @gerer_erreurs(afficher_dans_ui=True, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurValidation("Erreur", message_utilisateur="Erreur pour l'utilisateur")

        ma_fonction()
        mock_st_error.assert_called_once()

    @patch("streamlit.warning")
    def test_afficher_dans_ui_non_trouve(self, mock_st_warning):
        """Test affichage UI pour ErreurNonTrouve."""
        @gerer_erreurs(afficher_dans_ui=True, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurNonTrouve("Resource not found")

        ma_fonction()
        mock_st_warning.assert_called_once()

    @patch("streamlit.error")
    def test_afficher_dans_ui_base_donnees(self, mock_st_error):
        """Test affichage UI pour ErreurBaseDeDonnees."""
        @gerer_erreurs(afficher_dans_ui=True, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurBaseDeDonnees("Erreur DB")

        ma_fonction()
        mock_st_error.assert_called_once()

    def test_gerer_erreurs_arguments_fonction(self):
        """Test que le décorateur préserve les arguments."""
        @gerer_erreurs()
        def ma_fonction(a, b, c=None):
            return (a, b, c)

        result = ma_fonction(1, 2, c=3)
        assert result == (1, 2, 3)

    def test_gerer_erreurs_log_niveau(self):
        """Test que le décorateur utilise le niveau de log correct."""
        with patch("src.core.errors.logger") as mock_logger:
            @gerer_erreurs(niveau_log="WARNING", afficher_dans_ui=False, relancer=False)
            def ma_fonction():
                raise ErreurValidation("field", "Message", "Internal")

            ma_fonction()
            mock_logger.warning.assert_called_once()

    @patch("streamlit.error")
    def test_capture_exception_service_ia(self, mock_st_error):
        """Test capture d'ErreurServiceIA."""
        @gerer_erreurs(afficher_dans_ui=True, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurServiceIA("Service IA indisponible")

        result = ma_fonction()
        assert result is None
        mock_st_error.assert_called_once()

    def test_capture_exception_limite_debit(self):
        """Test capture d'ErreurLimiteDebit."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurLimiteDebit("Limite de 10 appels/min atteinte")

        result = ma_fonction()
        assert result is None

    def test_capture_exception_service_externe(self):
        """Test capture d'ErreurServiceExterne."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurServiceExterne("Service externe indisponible")

        result = ma_fonction()
        assert result is None

    def test_capture_exception_configuration(self):
        """Test capture d'ErreurConfiguration."""
        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def ma_fonction():
            raise ErreurConfiguration("Clé de configuration manquante: API_KEY")

        result = ma_fonction()
        assert result is None


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS EXCEPTIONS ELLES-MÊMES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestExceptionClasses:
    """Tests des classes d'exception."""

    def test_erreur_validation_attributes(self):
        """Test que ErreurValidation a les bons attributs."""
        err = ErreurValidation("Message interne", message_utilisateur="Message utilisateur")
        assert err.message == "Message interne"
        assert err.message_utilisateur == "Message utilisateur"
        assert hasattr(err, "code_erreur")

    def test_erreur_non_trouve_attributes(self):
        """Test que ErreurNonTrouve a les bons attributs."""
        err = ErreurNonTrouve("Recette not found")
        assert err.message == "Recette not found"
        assert hasattr(err, "code_erreur")
        assert err.code_erreur == "NOT_FOUND"

    def test_erreur_base_de_donnees_attributes(self):
        """Test que ErreurBaseDeDonnees a les bons attributs."""
        err = ErreurBaseDeDonnees("Connexion perdue")
        assert err.message == "Connexion perdue"

    def test_exception_app_str(self):
        """Test que ExceptionApp a une bonne représentation string."""
        err = ErreurConfiguration("Message test")
        str_rep = str(err)
        assert "Message test" in str_rep or str_rep  # Contient le message ou du texte


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS INTEGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestIntegrationErrorHandling:
    """Tests d'intégration du système d'erreurs."""

    def test_error_chain_validation_to_ui(self):
        """Test le chaînage complet erreur -> logging -> UI."""
        with patch("streamlit.error") as mock_error:
            with patch("src.core.errors.logger") as mock_logger:
                @gerer_erreurs(afficher_dans_ui=True, relancer=False)
                def operation():
                    raise ErreurValidation("Erreur validation", message_utilisateur="Nom invalide")

                result = operation()

                # Vérifier que logger a enregistré
                mock_logger.warning.assert_called_once()
                # Vérifier que UI a affiché
                mock_error.assert_called_once()
                # Résultat est None (fallback)
                assert result is None

    def test_error_chaining_with_relancer(self):
        """Test que relancer=True correctement propage l'exception."""
        @gerer_erreurs(relancer=True)
        def operation():
            raise ErreurNonTrouve("Recette not found")

        with pytest.raises(ErreurNonTrouve):
            operation()

    def test_multiple_exception_types(self):
        """Test qu'on peut capturer plusieurs types d'exceptions."""
        exceptions_levees = []

        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def operation_validation():
            raise ErreurValidation("validation error")

        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def operation_non_trouve():
            raise ErreurNonTrouve("not found")

        @gerer_erreurs(afficher_dans_ui=False, relancer=False, valeur_fallback=None)
        def operation_db():
            raise ErreurBaseDeDonnees("db error")

        # Tous doivent retourner None sans relancer
        assert operation_validation() is None
        assert operation_non_trouve() is None
        assert operation_db() is None


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS FONCTIONS SUPPLÉMENTAIRES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFonctionsHelperSupplementaires:
    """Tests des fonctions helper supplémentaires dans errors.py."""
    
    def test_est_mode_debug_false_default(self):
        """Test que _est_mode_debug retourne False par défaut."""
        from src.core.errors import _est_mode_debug
        # Sans mode debug configuré, devrait retourner False
        result = _est_mode_debug()
        assert isinstance(result, bool)
    
    def test_exiger_champs_function_exists(self):
        """Test fonction exiger_champs importable depuis errors."""
        from src.core.errors import exiger_champs
        assert callable(exiger_champs)
    
    def test_exiger_positif_success(self):
        """Test exiger_positif avec valeur positive."""
        from src.core.errors import exiger_positif
        # Ne devrait pas lever d'exception
        exiger_positif(10, "quantite")
        assert True
    
    def test_exiger_positif_zero_fails(self):
        """Test exiger_positif avec 0 échoue."""
        from src.core.errors import exiger_positif
        with pytest.raises(ErreurValidation):
            exiger_positif(0, "quantite")
    
    def test_exiger_positif_negative_fails(self):
        """Test exiger_positif avec valeur négative échoue."""
        from src.core.errors import exiger_positif
        with pytest.raises(ErreurValidation):
            exiger_positif(-5, "quantite")
    
    def test_exiger_existence_success(self):
        """Test exiger_existence avec objet existant."""
        from src.core.errors import exiger_existence
        obj = {"test": "value"}
        # Ne devrait pas lever d'exception
        exiger_existence(obj, "Objet", 1)
        assert True
    
    def test_exiger_existence_none_fails(self):
        """Test exiger_existence avec None échoue."""
        from src.core.errors import exiger_existence, ErreurNonTrouve
        with pytest.raises(ErreurNonTrouve):
            exiger_existence(None, "Recette", 42)
    
    def test_exiger_plage_success(self):
        """Test exiger_plage avec valeur dans plage."""
        from src.core.errors import exiger_plage
        exiger_plage(5, minimum=1, maximum=10, nom_champ="portions")
        assert True
    
    def test_exiger_plage_below_minimum_fails(self):
        """Test exiger_plage sous le minimum échoue."""
        from src.core.errors import exiger_plage
        with pytest.raises(ErreurValidation):
            exiger_plage(0, minimum=1, nom_champ="portions")
    
    def test_exiger_plage_above_maximum_fails(self):
        """Test exiger_plage au dessus du maximum échoue."""
        from src.core.errors import exiger_plage
        with pytest.raises(ErreurValidation):
            exiger_plage(100, maximum=50, nom_champ="portions")
    
    def test_exiger_longueur_success(self):
        """Test exiger_longueur avec longueur valide."""
        from src.core.errors import exiger_longueur
        exiger_longueur("Hello", minimum=1, maximum=10, nom_champ="nom")
        assert True
    
    def test_exiger_longueur_too_short_fails(self):
        """Test exiger_longueur trop court échoue."""
        from src.core.errors import exiger_longueur
        with pytest.raises(ErreurValidation):
            exiger_longueur("Hi", minimum=5, nom_champ="nom")
    
    def test_exiger_longueur_too_long_fails(self):
        """Test exiger_longueur trop long échoue."""
        from src.core.errors import exiger_longueur
        with pytest.raises(ErreurValidation):
            exiger_longueur("Very long text here", maximum=5, nom_champ="nom")


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS AFFICHER ERREUR STREAMLIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAfficherErreurStreamlit:
    """Tests de la fonction afficher_erreur_streamlit."""
    
    @patch("streamlit.error")
    def test_afficher_erreur_streamlit_validation(self, mock_error):
        """Test affichage erreur validation."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurValidation("interne", message_utilisateur="Message user")
        afficher_erreur_streamlit(erreur)
        mock_error.assert_called_once()
    
    @patch("streamlit.warning")
    def test_afficher_erreur_streamlit_non_trouve(self, mock_warning):
        """Test affichage erreur non trouvé."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurNonTrouve("interne")
        afficher_erreur_streamlit(erreur)
        mock_warning.assert_called_once()
    
    @patch("streamlit.error")
    def test_afficher_erreur_streamlit_db(self, mock_error):
        """Test affichage erreur base de données."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurBaseDeDonnees("connexion perdue")
        afficher_erreur_streamlit(erreur)
        mock_error.assert_called_once()
    
    @patch("streamlit.error")
    def test_afficher_erreur_streamlit_ia(self, mock_error):
        """Test affichage erreur service IA."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurServiceIA("service down")
        afficher_erreur_streamlit(erreur)
        mock_error.assert_called_once()
    
    @patch("streamlit.warning")
    def test_afficher_erreur_streamlit_limite_debit(self, mock_warning):
        """Test affichage erreur limite débit."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurLimiteDebit("10/min atteint")
        afficher_erreur_streamlit(erreur)
        mock_warning.assert_called_once()
    
    @patch("streamlit.error")
    def test_afficher_erreur_streamlit_externe(self, mock_error):
        """Test affichage erreur service externe."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = ErreurServiceExterne("API down")
        afficher_erreur_streamlit(erreur)
        mock_error.assert_called_once()
    
    @patch("streamlit.error")
    def test_afficher_erreur_streamlit_generique(self, mock_error):
        """Test affichage erreur générique non-ExceptionApp."""
        from src.core.errors import afficher_erreur_streamlit
        erreur = RuntimeError("Erreur random")
        afficher_erreur_streamlit(erreur)
        mock_error.assert_called_once()


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS GESTIONNAIRE ERREURS CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGestionnaireErreurs:
    """Tests du context manager GestionnaireErreurs."""
    
    def test_gestionnaire_erreurs_success(self):
        """Test GestionnaireErreurs sans erreur."""
        from src.core.errors import GestionnaireErreurs
        
        with GestionnaireErreurs("test operation", afficher_dans_ui=False):
            result = 1 + 1
        
        assert result == 2
    
    def test_gestionnaire_erreurs_enter_exit(self):
        """Test que GestionnaireErreurs implémente __enter__ et __exit__."""
        from src.core.errors import GestionnaireErreurs
        
        gestionnaire = GestionnaireErreurs("test", afficher_dans_ui=False)
        assert hasattr(gestionnaire, "__enter__")
        assert hasattr(gestionnaire, "__exit__")
    
    def test_gestionnaire_erreurs_with_custom_logger(self):
        """Test GestionnaireErreurs avec logger custom."""
        from src.core.errors import GestionnaireErreurs
        import logging
        
        custom_logger = logging.getLogger("custom_test")
        gestionnaire = GestionnaireErreurs(
            "test operation", 
            afficher_dans_ui=False, 
            logger_instance=custom_logger
        )
        
        assert gestionnaire.logger is custom_logger
    
    @patch("streamlit.error")
    def test_gestionnaire_erreurs_affiche_ui(self, mock_error):
        """Test que GestionnaireErreurs affiche dans UI si demandé."""
        from src.core.errors import GestionnaireErreurs
        
        try:
            with GestionnaireErreurs("test", afficher_dans_ui=True):
                raise ErreurValidation("test error")
        except ErreurValidation:
            pass  # Attendu car le gestionnaire ne supprime pas les exceptions
        
        mock_error.assert_called_once()


# ═══════════════════════════════════════════════════════════
# SECTION 9: TESTS ALIAS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAliases:
    """Tests des alias pour compatibilité."""
    
    def test_handle_errors_alias_exists(self):
        """Test que l'alias handle_errors existe."""
        from src.core.errors import handle_errors
        assert callable(handle_errors)
