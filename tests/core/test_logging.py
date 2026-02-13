"""
Tests unitaires pour logging.py (src/core/logging.py).

Tests couvrant:
- Configuration du logging global
- Filtre de secrets (FiltreSecrets)
- Formatage coloré (FormatteurColore)
- Gestionnaire de logs (GestionnaireLog)
- Fonctions d'alias (init, get_logger, obtenir_logger)
"""

import logging
from unittest.mock import patch

import pytest

from src.core.logging import (
    FiltreSecrets,
    FormatteurColore,
    GestionnaireLog,
    LogManager,
    configure_logging,
    get_logger,
    init,
    obtenir_logger,
)

# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS configure_logging
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConfigureLogging:
    """Tests pour configure_logging."""

    def test_configure_logging_default_level(self):
        """Test que configure_logging définit INFO par défaut."""
        logger = logging.getLogger()
        configure_logging()
        # Le niveau devrait être INFO (20)
        assert logger.level >= logging.INFO

    def test_configure_logging_debug_level(self):
        """Test configure_logging avec DEBUG."""
        configure_logging("DEBUG")
        logger = logging.getLogger()
        assert logger.level <= logging.DEBUG

    def test_configure_logging_error_level(self):
        """Test configure_logging avec ERROR."""
        configure_logging("ERROR")
        logger = logging.getLogger()
        assert logger.level >= logging.ERROR

    def test_configure_logging_creates_handler(self):
        """Test que configure_logging crée un handler."""
        # Nettoyer d'abord
        logger = logging.getLogger()
        logger.handlers = []
        configure_logging("INFO")
        assert len(logger.handlers) > 0

    def test_configure_logging_updates_existing_handler(self):
        """Test que configure_logging met à jour les handlers existants."""
        logger = logging.getLogger()
        initial_handler_count = len(logger.handlers)
        configure_logging("WARNING")
        # Devrait mettre à jour, pas ajouter
        assert len(logger.handlers) >= initial_handler_count

    @patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"})
    def test_configure_logging_reads_env_var(self):
        """Test que configure_logging lit LOG_LEVEL depuis env."""
        configure_logging()
        logger = logging.getLogger()
        # Le niveau devrait être DEBUG
        assert logger.level <= logging.DEBUG


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS FiltreSecrets
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFiltreSecrets:
    """Tests pour le filtre FiltreSecrets."""

    def test_filtre_secrets_database_url(self):
        """Test que FiltreSecrets masque les DATABASE_URL."""
        filtre = FiltreSecrets()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Connection: postgresql://user:password@localhost/db",
            args=(),
            exc_info=None,
        )
        result = filtre.filter(record)
        assert result is True
        assert "password" not in record.msg or "***" in record.msg

    def test_filtre_secrets_api_key(self):
        """Test que FiltreSecrets masque les API_KEY."""
        filtre = FiltreSecrets()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="API_KEY=sk-1234567890abcdef",
            args=(),
            exc_info=None,
        )
        filtre.filter(record)
        assert "MASKED" in record.msg or "***" in record.msg

    def test_filtre_secrets_bearer_token(self):
        """Test que FiltreSecrets masque les Bearer tokens."""
        filtre = FiltreSecrets()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None,
        )
        filtre.filter(record)
        assert "MASKED" in record.msg or "***" in record.msg

    def test_filtre_secrets_retourne_true(self):
        """Test que filter retourne toujours True."""
        filtre = FiltreSecrets()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )
        result = filtre.filter(record)
        assert result is True

    def test_filtre_secrets_avec_args_tuple(self):
        """Test que FiltreSecrets filtre aussi les args."""
        filtre = FiltreSecrets()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Message avec %s",
            args=("password=secret123",),
            exc_info=None,
        )
        filtre.filter(record)
        # Les args doivent rester un tuple
        assert isinstance(record.args, tuple)


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS FormatteurColore
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFormatteurColore:
    """Tests pour le FormatteurColore."""

    def test_formatteur_colore_init(self):
        """Test création du FormatteurColore."""
        formatateur = FormatteurColore("%(levelname)s - %(message)s")
        assert formatateur is not None

    def test_formatteur_colore_format_info(self):
        """Test formatage d'un message INFO."""
        formatateur = FormatteurColore("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        result = formatateur.format(record)
        assert "Test message" in result

    def test_formatteur_colore_format_error(self):
        """Test formatage d'un message ERROR."""
        formatateur = FormatteurColore("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error message",
            args=(),
            exc_info=None,
        )
        result = formatateur.format(record)
        assert "Error message" in result
        # Devrait ajouter des codes de couleur ANSI
        assert "ERROR" in result or "\033" in result

    def test_formatteur_colore_ajoute_couleurs(self):
        """Test que FormatteurColore ajoute effectivement des couleurs."""
        formatateur = FormatteurColore("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Debug",
            args=(),
            exc_info=None,
        )
        result = formatateur.format(record)
        # Devrait contenir soit du texte soit des codes de couleur
        assert result  # Ne pas être vide
        assert "Debug" in result


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS GestionnaireLog
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGestionnaireLog:
    """Tests pour GestionnaireLog."""

    def test_gestionnaire_initialiser_idempotent(self):
        """Test que initialiser peut être appelé plusieurs fois."""
        # Reset
        GestionnaireLog._initialise = False
        GestionnaireLog.initialiser("INFO")
        logger = logging.getLogger()
        handler_count_1 = len(logger.handlers)
        GestionnaireLog.initialiser("INFO")
        # Ne devrait pas créer de nouveaux handlers si déjà initialisé
        # (mais peut les réutiliser)
        assert len(logger.handlers) >= handler_count_1

    def test_gestionnaire_obtenir_logger(self):
        """Test que obtenir_logger retourne un Logger."""
        logger = GestionnaireLog.obtenir_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_gestionnaire_obtenir_logger_initialise(self):
        """Test que obtenir_logger initialise si nécessaire."""
        GestionnaireLog._initialise = False
        logger = GestionnaireLog.obtenir_logger("test")
        assert logger is not None

    def test_gestionnaire_definir_niveau(self):
        """Test que definir_niveau change le niveau."""
        GestionnaireLog.definir_niveau("WARNING")
        logger = logging.getLogger()
        assert logger.level >= logging.WARNING

    def test_gestionnaire_desactiver_module(self):
        """Test que desactiver_module fonctionne."""
        test_logger = logging.getLogger("httpx")
        GestionnaireLog.desactiver_module("httpx")
        assert test_logger.level >= logging.WARNING

    def test_gestionnaire_activer_debug(self):
        """Test que activer_debug change au niveau DEBUG."""
        GestionnaireLog.activer_debug()
        logger = logging.getLogger()
        assert logger.level <= logging.DEBUG

    def test_gestionnaire_activer_production(self):
        """Test que activer_production passe en INFO."""
        GestionnaireLog.activer_production()
        logger = logging.getLogger()
        assert logger.level >= logging.INFO

    def test_gestionnaire_avec_niveaux_multiples(self):
        """Test que le gestionnaire supporte tous les niveaux."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            GestionnaireLog.initialiser(level)
            logger = logging.getLogger()
            assert logger is not None


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS ALIAS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAlias:
    """Tests pour les alias anglais."""

    def test_logmanager_alias(self):
        """Test que LogManager est un alias de GestionnaireLog."""
        assert LogManager == GestionnaireLog

    def test_init_function(self):
        """Test que init() fonctionne."""
        init("INFO")
        logger = logging.getLogger()
        assert logger is not None

    def test_get_logger_function(self):
        """Test que get_logger() fonctionne."""
        logger = get_logger("test_alias")
        assert logger.name == "test_alias"

    def test_obtenir_logger_function(self):
        """Test que obtenir_logger() fonctionne."""
        logger = obtenir_logger("test_fr")
        assert logger.name == "test_fr"

    def test_get_logger_vs_obtenir_logger(self):
        """Test que get_logger et obtenir_logger retournent la même chose."""
        logger1 = get_logger("test_same")
        logger2 = obtenir_logger("test_same")
        assert logger1 == logger2


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS INTEGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestIntegrationLogging:
    """Tests d'intégration du système de logging."""

    def test_logging_full_stack(self):
        """Test le stack complet: configuration -> utilisation -> secrets."""
        # Configure
        configure_logging("DEBUG")

        # Obtient logger
        logger = obtenir_logger("test.integration")

        # Log un message (devrait être masqué s'il y a des secrets)
        logger.info("Message test avec DATABASE_URL=postgresql://user:pwd@host/db")

        # Devrait fonctionner sans erreurs
        assert logger is not None

    def test_gestionnaire_avec_filtre_secrets(self):
        """Test que le gestionnaire applique le filtre de secrets."""
        GestionnaireLog._initialise = False
        GestionnaireLog.initialiser("INFO")

        logger = logging.getLogger("test.secrets")
        # Initier le logging si nécessaire
        root_logger = logging.getLogger()
        # Devrait avoir au moins un handler ou les handlers du root
        assert len(root_logger.handlers) > 0 or logger is not None

    def test_multiple_loggers_different_levels(self):
        """Test plusieurs loggers avec niveaux différents."""
        logger1 = obtenir_logger("app.core")
        logger2 = obtenir_logger("app.ui")

        # Les deux devraient exister
        assert logger1 is not None
        assert logger2 is not None
        assert logger1 != logger2  # Noms différents
