"""
Central logging configuration for the application.

Provides a small helper to configure Python logging consistently
across Streamlit and normal execution environments.
"""

import logging
import os


def configure_logging(level: str | None = None):
    """Configure le logging global.

    Args:
        level: Niveau de log en string (DEBUG, INFO, WARNING, ERROR).
               If None, will read from `LOG_LEVEL` env var or default to INFO.
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        # update level on existing handlers
        root.setLevel(numeric_level)
        for h in root.handlers:
            h.setLevel(numeric_level)
        return

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(numeric_level)

    root.setLevel(numeric_level)
    root.addHandler(handler)


__all__ = [
    "configure_logging",
    "FiltreSecrets",
    "FormatteurColore",
    "GestionnaireLog",
    "LogManager",
    "obtenir_logger",
    "get_logger",
]
"""
Logging - Système de logging centralisé.

Ce module fournit un gestionnaire de logs avec :
- Formatage coloré pour la console
- Configuration automatique
- Niveaux de log adaptatifs
- Filtrage automatique des secrets
"""
import re
import sys


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
        (r'(postgresql|mysql|mongodb|redis):\/\/[^:]+:[^@]+@', r'\1://***:***@'),
        # DATABASE_URL complète
        (r'DATABASE_URL[=:]\s*["\']?[^"\'\s]+["\']?', 'DATABASE_URL=***MASKED***'),
        # Clés API génériques
        (r'(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)[=:]\s*["\']?[\w\-]+["\']?', r'\1=***MASKED***'),
        # Tokens Bearer
        (r'Bearer\s+[\w\-\.]+', 'Bearer ***MASKED***'),
        # Mots de passe dans les chaînes
        (r'(password|pwd|pass)[=:]\s*["\']?[^"\'\s]+["\']?', r'\1=***MASKED***'),
        # Clés Mistral
        (r'(mistral[_-]?api[_-]?key)[=:]\s*["\']?[\w\-]+["\']?', r'\1=***MASKED***'),
    ]
    """Patterns de détection des secrets avec leur remplacement."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtre un enregistrement de log pour masquer les secrets.
        
        Args:
            record: Enregistrement de log
            
        Returns:
            True (on garde toujours l'enregistrement, on le modifie juste)
        """
        if record.msg:
            message = str(record.msg)
            for pattern, replacement in self.PATTERNS_SECRETS:
                message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
            record.msg = message
            
        # Aussi filtrer les arguments
        if record.args:
            args_list = list(record.args) if isinstance(record.args, tuple) else [record.args]
            filtered_args = []
            for arg in args_list:
                if isinstance(arg, str):
                    for pattern, replacement in self.PATTERNS_SECRETS:
                        arg = re.sub(pattern, replacement, arg, flags=re.IGNORECASE)
                filtered_args.append(arg)
            record.args = tuple(filtered_args)
            
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
        root_logger.info(f"✅ Logging initialisé (niveau: {niveau_log})")

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


# ═══════════════════════════════════════════════════════════
# ALIAS ANGLAIS (pour compatibilité)
# ═══════════════════════════════════════════════════════════

# Alias de classe
LogManager = GestionnaireLog


# Alias de méthodes au niveau module
def init(log_level: str = "INFO"):
    """Alias anglais pour initialiser()"""
    return GestionnaireLog.initialiser(log_level)


def get_logger(name: str) -> logging.Logger:
    """Alias anglais pour obtenir_logger()"""
    return GestionnaireLog.obtenir_logger(name)


# Ajouter les alias directement sur la classe
LogManager.init = staticmethod(init)
LogManager.get_logger = staticmethod(get_logger)


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


# Initialisation automatique au chargement du module
GestionnaireLog.initialiser()
