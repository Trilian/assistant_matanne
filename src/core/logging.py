"""
Logging - Système de logging centralisé.

Ce module fournit :
- Formatage coloré pour la console (dev)
- Formatage JSON structuré (production / observabilité)
- Filtrage automatique des secrets
- Intégration correlation_id via ContexteExecution
- Configuration automatique via GestionnaireLog
- Fonction raccourci obtenir_logger()
"""

import json
import logging
import os
import re
import sys
from datetime import UTC, datetime, timezone


def configure_logging(level: str | None = None, structured: bool = False):
    """Configure le logging global.

    Délègue à GestionnaireLog.initialiser() pour une configuration unifiée
    avec couleurs et filtrage des secrets.

    Args:
        level: Niveau de log en string (DEBUG, INFO, WARNING, ERROR).
               If None, will read from `LOG_LEVEL` env var or default to INFO.
        structured: Si True, utilise le format JSON structuré (production).
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    if structured or os.getenv("LOG_FORMAT", "").lower() == "json":
        GestionnaireLog.activer_mode_structure(level)
    elif GestionnaireLog._initialise:
        GestionnaireLog.definir_niveau(level)
    else:
        GestionnaireLog.initialiser(level)


__all__ = [
    "configure_logging",
    "FiltreSecrets",
    "FormatteurColore",
    "FormatteurStructure",
    "GestionnaireLog",
    "obtenir_logger",
]


class FiltreSecrets(logging.Filter):
    """
    Filtre qui masque les informations sensibles dans les logs.

    Patterns masqués :
    - URLs de base de données (postgresql://, mysql://, etc.)
    - Clés API (API_KEY, SECRET_KEY, etc.)
    - Tokens d'authentification
    """

    PATTERNS_SECRETS = [
        # URLs de base de données avec credentials
        (r"(postgresql|mysql|mongodb|redis):\/\/[^:]+:[^@]+@", r"\1://***:***@"),
        # DATABASE_URL complète
        (r'DATABASE_URL[=:]\s*["\']?[^"\'\s]+["\']?', "DATABASE_URL=***MASKED***"),
        # Clés API génériques
        (
            r'(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)[=:]\s*["\']?[\w\-]+["\']?',
            r"\1=***MASKED***",
        ),
        # Tokens Bearer
        (r"Bearer\s+[\w\-\.]+", "Bearer ***MASKED***"),
        # Mots de passe dans les chaînes
        (r'(password|pwd|pass)[=:]\s*["\']?[^"\'\s]+["\']?', r"\1=***MASKED***"),
        # Clés Mistral
        (r'(mistral[_-]?api[_-]?key)[=:]\s*["\']?[\w\-]+["\']?', r"\1=***MASKED***"),
    ]
    """Patterns de détection des secrets avec leur remplacement."""

    def _masquer_texte(self, texte: str) -> str:
        """Applique tous les patterns de masquage sur un texte."""
        for pattern, replacement in self.PATTERNS_SECRETS:
            texte = re.sub(pattern, replacement, texte, flags=re.IGNORECASE)
        return texte

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtre un enregistrement de log pour masquer les secrets.

        Masque dans: message, arguments formatés, et tracebacks d'exception.

        Args:
            record: Enregistrement de log

        Returns:
            True (on garde toujours l'enregistrement, on le modifie juste)
        """
        if record.msg:
            record.msg = self._masquer_texte(str(record.msg))

        # Aussi filtrer les arguments
        if record.args:
            args_list = list(record.args) if isinstance(record.args, tuple) else [record.args]
            filtered_args = []
            for arg in args_list:
                if isinstance(arg, str):
                    arg = self._masquer_texte(arg)
                filtered_args.append(arg)
            record.args = tuple(filtered_args)

        # Masquer les secrets dans les tracebacks d'exception
        if record.exc_text:
            record.exc_text = self._masquer_texte(record.exc_text)

        return True


class FormatteurColore(logging.Formatter):
    """
    Formateur avec couleurs ANSI pour la console.

    Améliore la lisibilité des logs en ajoutant des couleurs
    selon le niveau de log.
    """

    COULEURS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Vert
        "WARNING": "\033[33m",  # Jaune
        "ERROR": "\033[31m",  # Rouge
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formate un enregistrement de log avec couleur.

        Args:
            record: Enregistrement à formater

        Returns:
            Message formaté avec couleurs
        """
        levelname = record.levelname
        if levelname in self.COULEURS:
            record.levelname = f"{self.COULEURS[levelname]}{levelname}{self.COULEURS['RESET']}"
        return super().format(record)


class FormatteurStructure(logging.Formatter):
    """Formateur JSON structuré pour l'observabilité en production.

    Chaque ligne de log est un objet JSON contenant:
    - ``timestamp``: ISO-8601 UTC
    - ``level``: Niveau de log (INFO, ERROR, …)
    - ``logger``: Nom du logger (module source)
    - ``message``: Message texte
    - ``correlation_id``: ID de corrélation (si disponible via ContexteExecution)
    - ``operation``: Opération en cours (si disponible)
    - ``module``: Module applicatif (si disponible)
    - ``exception``: Traceback (si présent)

    Usage::

        handler = logging.StreamHandler()
        handler.setFormatter(FormatteurStructure())
    """

    def format(self, record: logging.LogRecord) -> str:
        """Produit une ligne JSON par enregistrement de log."""
        entry: dict = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Enrichir avec le contexte de corrélation (si disponible)
        try:
            from src.core.observability.context import _contexte_execution

            ctx = _contexte_execution.get()
            if ctx is not None:
                entry["correlation_id"] = ctx.correlation_id
                if ctx.operation:
                    entry["operation"] = ctx.operation
                if ctx.module:
                    entry["module"] = ctx.module
        except Exception:  # noqa: BLE001
            pass

        # Ajouter l'exception si présente
        if record.exc_info and record.exc_info[1] is not None:
            entry["exception"] = self.formatException(record.exc_info)

        # Champs supplémentaires passés via extra={}
        for key in ("correlation_id", "operation", "duree_ms", "utilisateur"):
            val = getattr(record, key, None)
            if val is not None and key not in entry:
                entry[key] = val

        return json.dumps(entry, ensure_ascii=False, default=str)


class GestionnaireLog:
    """
    Gestionnaire de logging centralisé.

    Gère l'initialisation et la configuration des logs pour
    toute l'application.
    """

    _initialise = False
    """Flag d'initialisation."""

    @staticmethod
    def initialiser(niveau_log: str = "INFO"):
        """
        Initialise le système de logging.

        Configure le logger root avec un handler console coloré
        et un filtre pour masquer les secrets.
        Cette méthode est idempotente (peut être appelée plusieurs fois).

        Args:
            niveau_log: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if GestionnaireLog._initialise:
            return

        # Récupérer logger root
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, niveau_log.upper()))

        # Supprimer handlers existants
        root_logger.handlers = []

        # Handler console avec couleurs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, niveau_log.upper()))

        # Format avec couleurs
        format_console = FormatteurColore(
            "%(levelname)-8s | %(name)-25s | %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(format_console)

        # Ajouter le filtre de secrets
        console_handler.addFilter(FiltreSecrets())

        root_logger.addHandler(console_handler)

        GestionnaireLog._initialise = True
        root_logger.info(f"[OK] Logging initialisé (niveau: {niveau_log})")

    @staticmethod
    def obtenir_logger(nom: str) -> logging.Logger:
        """
        Récupère un logger pour un module.

        Initialise automatiquement le système si nécessaire.

        Args:
            nom: Nom du module (généralement __name__)

        Returns:
            Instance de Logger configuré

        Example:
            >>> logger = GestionnaireLog.obtenir_logger(__name__)
            >>> logger.info("Message de log")
        """
        if not GestionnaireLog._initialise:
            GestionnaireLog.initialiser()
        return logging.getLogger(nom)

    @staticmethod
    def definir_niveau(niveau: str):
        """
        Change le niveau de log dynamiquement.

        Args:
            niveau: Nouveau niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(getattr(logging, niveau.upper()))
        logging.info(f"🔄 Niveau de log changé: {niveau}")

    @staticmethod
    def desactiver_module(nom_module: str):
        """
        Désactive les logs d'un module spécifique.

        Utile pour réduire le bruit des bibliothèques externes.

        Args:
            nom_module: Nom du module à désactiver (ex: "httpx", "urllib3")
        """
        logging.getLogger(nom_module).setLevel(logging.WARNING)
        logging.debug(f"🔇 Module {nom_module} en mode WARNING")

    @staticmethod
    def activer_debug():
        """Active le mode debug pour tous les loggers."""
        GestionnaireLog.definir_niveau("DEBUG")

    @staticmethod
    def activer_production():
        """Active le mode production (INFO uniquement)."""
        GestionnaireLog.definir_niveau("INFO")

    @staticmethod
    def activer_mode_structure(niveau_log: str = "INFO"):
        """Bascule tous les handlers vers le format JSON structuré.

        Utile pour la production ou l'intégration avec des outils
        d'observabilité (ELK, Loki, Datadog, etc.).

        Args:
            niveau_log: Niveau de log (DEBUG, INFO, WARNING, ERROR).
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, niveau_log.upper()))

        # Remplacer tous les handlers par un handler JSON
        root_logger.handlers = []
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, niveau_log.upper()))
        console_handler.setFormatter(FormatteurStructure())
        console_handler.addFilter(FiltreSecrets())
        root_logger.addHandler(console_handler)

        root_logger.info("Logging structuré JSON activé")


# Fonction raccourci française
def obtenir_logger(nom: str) -> logging.Logger:
    """
    Raccourci pour récupérer un logger.

    Args:
        nom: Nom du module

    Returns:
        Logger configuré

    Example:
        >>> from src.core.logging import obtenir_logger
        >>> logger = obtenir_logger(__name__)
    """
    return GestionnaireLog.obtenir_logger(nom)


# Note: L'initialisation automatique a été supprimée.
# L'init se fait via obtenir_parametres() → configure_logging()
# ou explicitement via GestionnaireLog.initialiser().
