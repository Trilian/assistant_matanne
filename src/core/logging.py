"""
Logging - Système de logging centralisé.

Ce module fournit un gestionnaire de logs avec :
- Formatage coloré pour la console
- Configuration automatique
- Niveaux de log adaptatifs
"""
import logging
import sys
from typing import Optional


class FormatteurColore(logging.Formatter):
    """
    Formateur avec couleurs ANSI pour la console.

    Améliore la lisibilité des logs en ajoutant des couleurs
    selon le niveau de log.
    """

    COULEURS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Vert
        'WARNING': '\033[33m',   # Jaune
        'ERROR': '\033[31m',     # Rouge
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
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
            record.levelname = (
                f"{self.COULEURS[levelname]}{levelname}{self.COULEURS['RESET']}"
            )
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

        Configure le logger root avec un handler console coloré.
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
            '%(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(format_console)
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