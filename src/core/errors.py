"""
Errors Unifié - Exceptions + Handlers
Fusionne core/errors/exceptions.py + core/errors/handlers.py
"""
import streamlit as st
from functools import wraps
from typing import Callable, Any, Dict, List, Optional
import logging
import traceback

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# EXCEPTIONS
# ════════════════════════════════════════════════════════════

class AppException(Exception):
    """Exception de base de l'application"""
    def __init__(self, message: str, details: Optional[Dict] = None, user_message: Optional[str] = None):
        self.message = message
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(message)


class ValidationError(AppException):
    pass


class NotFoundError(AppException):
    pass


class DatabaseError(AppException):
    pass


class AIServiceError(AppException):
    pass


class RateLimitError(AppException):
    pass


# ════════════════════════════════════════════════════════════
# HANDLERS
# ════════════════════════════════════════════════════════════

def handle_errors(show_in_ui: bool = True, log_level: str = "ERROR",
                  reraise: bool = False, fallback_value: Any = None):
    """Decorator pour gérer automatiquement les erreurs"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"ValidationError in {func.__name__}: {e.message}")
                if show_in_ui:
                    st.error(f"❌ {e.user_message}")
                if reraise:
                    raise
                return fallback_value
            except NotFoundError as e:
                logger.info(f"NotFoundError in {func.__name__}: {e.message}")
                if show_in_ui:
                    st.warning(f"⚠️ {e.user_message}")
                if reraise:
                    raise
                return fallback_value
            except DatabaseError as e:
                logger.error(f"DatabaseError in {func.__name__}: {e.message}")
                if show_in_ui:
                    st.error("💾 Erreur de base de données")
                if reraise:
                    raise
                return fallback_value
            except AIServiceError as e:
                logger.warning(f"AIServiceError in {func.__name__}: {e.message}")
                if show_in_ui:
                    st.error(f"🤖 {e.user_message}")
                if reraise:
                    raise
                return fallback_value
            except RateLimitError as e:
                logger.warning(f"RateLimitError in {func.__name__}: {e.message}")
                if show_in_ui:
                    st.warning(f"⏳ {e.user_message}")
                if reraise:
                    raise
                return fallback_value
            except Exception as e:
                logger.critical(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                if show_in_ui:
                    st.error("❌ Une erreur inattendue s'est produite")
                    if st.session_state.get("debug_mode", False):
                        with st.expander("🐛 Stack trace"):
                            st.code(traceback.format_exc())
                if reraise:
                    raise
                return fallback_value
        return wrapper
    return decorator


# ════════════════════════════════════════════════════════════
# VALIDATION HELPERS
# ════════════════════════════════════════════════════════════

def require_fields(data: Dict, fields: List[str], object_name: str = "objet"):
    """Vérifie que les champs requis sont présents"""
    missing = [f for f in fields if not data.get(f)]
    if missing:
        raise ValidationError(
            f"Champs manquants: {missing}",
            details={"missing_fields": missing},
            user_message=f"Champs obligatoires : {', '.join(missing)}"
        )


def require_positive(value: float, field_name: str):
    """Vérifie qu'une valeur est positive"""
    if value <= 0:
        raise ValidationError(
            f"{field_name} doit être positif",
            user_message=f"{field_name} doit être supérieur à 0"
        )


def require_exists(obj: Any, object_type: str, object_id: Any):
    """Vérifie qu'un objet existe"""
    if obj is None:
        raise NotFoundError(
            f"{object_type} {object_id} not found",
            user_message=f"{object_type} introuvable"
        )