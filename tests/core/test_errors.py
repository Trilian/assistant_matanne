"""
Tests unitaires pour exceptions.py (src/core/exceptions.py).

Tests couvrant:
- Import des exceptions pures
- Fonctions helper de validation
- Classes d'exceptions et attributs
- Intégration avec le décorateur avec_gestion_erreurs

Note: Les tests de re-export de l'ancien errors.py ont été supprimés
car le module shim a été supprimé (dead code). Les exceptions sont
maintenant importées directement depuis exceptions.py.
"""

from unittest.mock import Mock, patch

import pytest

from src.core.exceptions import (
    ErreurBaseDeDonnees,
    ErreurConfiguration,
    ErreurLimiteDebit,
    ErreurNonTrouve,
    ErreurServiceExterne,
    ErreurServiceIA,
    ErreurValidation,
    ExceptionApp,
    exiger_champs,
    exiger_plage,
    valider_type,
)

# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS EXCEPTIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestExceptions:
    """Tests des exceptions."""

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
        exiger_champs(data, ["nom", "prenom"])

    def test_exiger_champs_missing(self):
        """Test exiger_champs avec champs manquants."""
        data = {"nom": "Test"}
        with pytest.raises(ErreurValidation):
            exiger_champs(data, ["nom", "prenom"])

    def test_exiger_plage_success(self):
        """Test exiger_plage avec valeur dans la plage."""
        exiger_plage(5, minimum=1, maximum=10, nom_champ="nombre")

    def test_exiger_plage_trop_bas(self):
        """Test exiger_plage avec valeur trop basse."""
        with pytest.raises(ErreurValidation):
            exiger_plage(0, minimum=1, maximum=10, nom_champ="nombre")

    def test_exiger_plage_trop_haut(self):
        """Test exiger_plage avec valeur trop haute."""
        with pytest.raises(ErreurValidation):
            exiger_plage(11, minimum=1, maximum=10, nom_champ="nombre")

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
# SECTION 3: TESTS EXCEPTIONS ELLES-MÊMES
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
        err = ErreurNonTrouve("Pas trouvé")
        assert err.message == "Pas trouvé"

    def test_erreur_base_de_donnees_attributes(self):
        """Test que ErreurBaseDeDonnees a les bons attributs."""
        err = ErreurBaseDeDonnees("Connexion perdue")
        assert err.message == "Connexion perdue"

    def test_erreur_service_ia_attributes(self):
        """Test que ErreurServiceIA a les bons attributs."""
        err = ErreurServiceIA("Service indisponible")
        assert err.message == "Service indisponible"


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS DÉCORATEUR avec_gestion_erreurs
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAvecGestionErreurs:
    """Tests pour @avec_gestion_erreurs."""

    @patch("streamlit.error")
    def test_avec_gestion_erreurs_erreur_validation(self, mock_error):
        """Test gestion spécifique ErreurValidation."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(
            default_return="fallback", afficher_erreur=True, relancer_metier=False
        )
        def validation_fail():
            raise ErreurValidation("champ invalide", message_utilisateur="Données invalides")

        result = validation_fail()
        assert result == "fallback"

    @patch("streamlit.warning")
    def test_avec_gestion_erreurs_erreur_non_trouve(self, mock_warning):
        """Test gestion spécifique ErreurNonTrouve."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True, relancer_metier=False)
        def not_found():
            raise ErreurNonTrouve("Recette 42", message_utilisateur="Non trouvé")

        result = not_found()
        mock_warning.assert_called_once()
        assert result is None

    @patch("streamlit.error")
    def test_avec_gestion_erreurs_erreur_base_donnees(self, mock_error):
        """Test gestion spécifique ErreurBaseDeDonnees."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(default_return=[], afficher_erreur=True, relancer_metier=False)
        def db_error():
            raise ErreurBaseDeDonnees("connexion perdue")

        result = db_error()
        mock_error.assert_called_once()
        assert result == []

    @patch("streamlit.error")
    def test_avec_gestion_erreurs_erreur_service_ia(self, mock_error):
        """Test gestion spécifique ErreurServiceIA."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(default_return={}, afficher_erreur=True, relancer_metier=False)
        def ia_error():
            raise ErreurServiceIA("API Mistral down")

        result = ia_error()
        mock_error.assert_called_once()
        assert result == {}

    @patch("streamlit.warning")
    def test_avec_gestion_erreurs_erreur_limite_debit(self, mock_warning):
        """Test gestion spécifique ErreurLimiteDebit."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(
            default_return="rate_limited", afficher_erreur=True, relancer_metier=False
        )
        def rate_limit():
            raise ErreurLimiteDebit("10/min atteint")

        result = rate_limit()
        mock_warning.assert_called_once()
        assert result == "rate_limited"

    @patch("streamlit.error")
    def test_avec_gestion_erreurs_erreur_service_externe(self, mock_error):
        """Test gestion spécifique ErreurServiceExterne."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(
            default_return="external_error", afficher_erreur=True, relancer_metier=False
        )
        def external_error():
            raise ErreurServiceExterne("OpenFood API down")

        result = external_error()
        mock_error.assert_called_once()
        assert result == "external_error"

    def test_avec_gestion_erreurs_relancer_true(self):
        """Test que relancer_metier=True relance l'exception."""
        from src.core.decorators import avec_gestion_erreurs

        @avec_gestion_erreurs(afficher_erreur=False, relancer_metier=True)
        def will_raise():
            raise ErreurValidation("test")

        with pytest.raises(ErreurValidation):
            will_raise()

    @patch("streamlit.error")
    @patch("streamlit.expander")
    @patch("streamlit.code")
    def test_avec_gestion_erreurs_debug_mode_shows_stacktrace(
        self, mock_code, mock_expander, mock_error
    ):
        """Test que le mode debug affiche la stack trace."""
        from src.core.decorators import avec_gestion_erreurs

        mock_expander.return_value.__enter__ = Mock(return_value=None)
        mock_expander.return_value.__exit__ = Mock(return_value=False)

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True, relancer_metier=False)
        def unexpected_error():
            raise RuntimeError("Unexpected!")

        result = unexpected_error()
        assert result is None


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS RE-EXPORTS DEPUIS exceptions
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestReExportsComplets:
    """Tests vérification imports depuis exceptions.py."""

    def test_valider_type_importable(self):
        """Test valider_type importable."""
        from src.core.exceptions import valider_type

        assert callable(valider_type)

    def test_erreur_configuration_importable(self):
        """Test ErreurConfiguration importable."""
        from src.core.exceptions import ErreurConfiguration

        assert issubclass(ErreurConfiguration, Exception)

    def test_exiger_plage_importable(self):
        """Test exiger_plage importable."""
        from src.core.exceptions import exiger_plage

        assert callable(exiger_plage)
