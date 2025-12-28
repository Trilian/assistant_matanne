"""
Logging Manager Unifié
Système de logging centralisé pour toute l'application
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler
import streamlit as st

from ..config import get_settings


class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""

    # Codes couleur ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Vert
        'WARNING': '\033[33m',    # Jaune
        'ERROR': '\033[31m',      # Rouge
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        # Ajouter couleur au niveau
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


class LogManager:
    """
    Gestionnaire de logging centralisé

    Features:
    - Logs console avec couleurs
    - Logs fichiers avec rotation
    - Logs Streamlit (UI)
    - Contexte enrichi
    - Métriques de logs
    """

    _initialized = False
    _loggers: Dict[str, logging.Logger] = {}

    @staticmethod
    def init(
            log_level: Optional[str] = None,
            log_to_file: bool = True,
            log_dir: Optional[Path] = None
    ):
        """
        Initialise le système de logging

        Args:
            log_level: Niveau de log (DEBUG/INFO/WARNING/ERROR)
            log_to_file: Si True, log dans des fichiers
            log_dir: Dossier des logs (défaut: logs/)
        """
        if LogManager._initialized:
            return

        settings = get_settings()
        log_level = log_level or settings.LOG_LEVEL

        # Configuration root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # Supprimer handlers existants
        root_logger.handlers = []

        # ═══════════════════════════════════════════════════════
        # HANDLER CONSOLE (avec couleurs)
        # ═══════════════════════════════════════════════════════
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        console_format = ColoredFormatter(
            '%(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)

        # ═══════════════════════════════════════════════════════
        # HANDLER FICHIER (si activé)
        # ═══════════════════════════════════════════════════════
        if log_to_file:
            log_dir = log_dir or Path("logs")
            log_dir.mkdir(exist_ok=True)

            # Fichier général
            general_log = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = RotatingFileHandler(
                general_log,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)

            file_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            root_logger.addHandler(file_handler)

            # Fichier erreurs uniquement
            error_log = log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
            error_handler = RotatingFileHandler(
                error_log,
                maxBytes=10 * 1024 * 1024,
                backupCount=10
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_format)
            root_logger.addHandler(error_handler)

        # ═══════════════════════════════════════════════════════
        # HANDLER STREAMLIT (UI)
        # ═══════════════════════════════════════════════════════
        if not settings.is_production():
            streamlit_handler = StreamlitLogHandler()
            streamlit_handler.setLevel(logging.WARNING)
            root_logger.addHandler(streamlit_handler)

        LogManager._initialized = True

        root_logger.info(f"✅ Logging initialisé (niveau: {log_level})")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Récupère un logger nommé

        Args:
            name: Nom du logger (généralement __name__)

        Returns:
            Logger configuré

        Usage:
            logger = LogManager.get_logger(__name__)
            logger.info("Message")
        """
        if not LogManager._initialized:
            LogManager.init()

        if name not in LogManager._loggers:
            LogManager._loggers[name] = logging.getLogger(name)

        return LogManager._loggers[name]

    @staticmethod
    def log_context(
            logger: logging.Logger,
            level: str,
            message: str,
            **context
    ):
        """
        Log avec contexte enrichi

        Args:
            logger: Logger à utiliser
            level: Niveau (debug/info/warning/error)
            message: Message
            **context: Contexte additionnel (user_id, recette_id, etc.)

        Usage:
            LogManager.log_context(
                logger,
                "info",
                "Recette créée",
                recette_id=123,
                user_id=456
            )
        """
        log_func = getattr(logger, level.lower())

        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            log_func(f"{message} | {context_str}")
        else:
            log_func(message)

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Récupère les statistiques de logging

        Returns:
            Dict avec métriques
        """
        if "log_stats" not in st.session_state:
            st.session_state.log_stats = {
                "debug": 0,
                "info": 0,
                "warning": 0,
                "error": 0,
                "critical": 0
            }

        return st.session_state.log_stats

    @staticmethod
    def reset_stats():
        """Reset les statistiques"""
        if "log_stats" in st.session_state:
            st.session_state.log_stats = {
                "debug": 0,
                "info": 0,
                "warning": 0,
                "error": 0,
                "critical": 0
            }


class StreamlitLogHandler(logging.Handler):
    """
    Handler pour afficher les logs dans Streamlit
    (seulement WARNING et au-dessus)
    """

    def emit(self, record):
        """Émet un log dans Streamlit"""
        try:
            msg = self.format(record)

            # Stocker dans session_state pour affichage
            if "recent_logs" not in st.session_state:
                st.session_state.recent_logs = []

            st.session_state.recent_logs.append({
                "timestamp": datetime.now(),
                "level": record.levelname,
                "message": msg,
                "module": record.module
            })

            # Garder seulement les 50 derniers
            st.session_state.recent_logs = st.session_state.recent_logs[-50:]

            # Incrémenter stats
            if "log_stats" not in st.session_state:
                st.session_state.log_stats = {
                    "debug": 0,
                    "info": 0,
                    "warning": 0,
                    "error": 0,
                    "critical": 0
                }

            level_key = record.levelname.lower()
            if level_key in st.session_state.log_stats:
                st.session_state.log_stats[level_key] += 1

        except Exception:
            self.handleError(record)


# ═══════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════

def log_execution(logger: logging.Logger = None, level: str = "INFO"):
    """
    Decorator pour logger l'exécution d'une fonction

    Usage:
        @log_execution(logger=my_logger, level="DEBUG")
        def my_function(param):
            return result
    """
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logger or LogManager.get_logger(func.__module__)

            func_logger.log(
                getattr(logging, level.upper()),
                f"Executing {func.__name__}"
            )

            try:
                result = func(*args, **kwargs)

                func_logger.log(
                    getattr(logging, level.upper()),
                    f"Completed {func.__name__}"
                )

                return result

            except Exception as e:
                func_logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# HELPERS STREAMLIT
# ═══════════════════════════════════════════════════════════

def render_log_viewer(key: str = "logs"):
    """
    Widget Streamlit pour afficher les logs récents

    Usage (dans sidebar):
        with st.sidebar:
            render_log_viewer()
    """
    if "recent_logs" not in st.session_state:
        st.session_state.recent_logs = []

    stats = LogManager.get_stats()

    with st.expander("📋 Logs Récents", expanded=False):
        # Stats
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Warnings", stats.get("warning", 0))
        with col2:
            st.metric("Errors", stats.get("error", 0))
        with col3:
            st.metric("Critical", stats.get("critical", 0))

        st.markdown("---")

        # Logs
        if st.session_state.recent_logs:
            for log in reversed(st.session_state.recent_logs[-10:]):
                level = log["level"]

                # Icône selon niveau
                icon_map = {
                    "DEBUG": "🔍",
                    "INFO": "ℹ️",
                    "WARNING": "⚠️",
                    "ERROR": "❌",
                    "CRITICAL": "🔥"
                }
                icon = icon_map.get(level, "📝")

                # Couleur selon niveau
                color_map = {
                    "DEBUG": "#6c757d",
                    "INFO": "#17a2b8",
                    "WARNING": "#ffc107",
                    "ERROR": "#dc3545",
                    "CRITICAL": "#d63384"
                }
                color = color_map.get(level, "#6c757d")

                st.markdown(
                    f'<div style="padding: 0.5rem; margin: 0.25rem 0; '
                    f'border-left: 3px solid {color}; background: #f8f9fa;">'
                    f'{icon} <strong>{level}</strong> | {log["module"]}<br>'
                    f'<small>{log["message"]}</small><br>'
                    f'<small style="color: #6c757d;">{log["timestamp"].strftime("%H:%M:%S")}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("Aucun log récent")

        # Actions
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Effacer logs", key=f"{key}_clear"):
                st.session_state.recent_logs = []
                st.rerun()

        with col2:
            if st.button("🔄 Reset stats", key=f"{key}_reset"):
                LogManager.reset_stats()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# FONCTION HELPER
# ═══════════════════════════════════════════════════════════

def get_logger(name: str) -> logging.Logger:
    """
    Shortcut pour récupérer un logger

    Usage:
        from src.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Message")
    """
    return LogManager.get_logger(name)


# ═══════════════════════════════════════════════════════════
# INITIALISATION AUTO
# ═══════════════════════════════════════════════════════════

# Initialiser au premier import
LogManager.init()