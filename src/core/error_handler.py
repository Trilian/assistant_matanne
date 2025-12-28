# src/core/error_handler.py
"""
Error Handler Universel - Middleware
Évite try/catch répétés dans tous les services
"""
import streamlit as st
import logging
import traceback
from functools import wraps
from typing import Callable, Optional, Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DECORATOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def safe_execute(
        fallback_value: Any = None,
        show_error: bool = True,
        log_level: str = "ERROR",
        error_message: Optional[str] = None,
        toast: bool = False
):
    """
    Decorator universel pour gestion d'erreurs

    Args:
        fallback_value: Valeur retournée en cas d'erreur
        show_error: Afficher l'erreur dans Streamlit
        log_level: Niveau de log (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        error_message: Message personnalisé (sinon auto)
        toast: Utiliser st.toast au lieu de st.error

    Usage:
        @safe_execute(fallback_value=[], show_error=True)
        def my_function():
            # Code qui peut planter
            return data

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                # ───────────────────────────────────────────────────
                # LOG
                # ───────────────────────────────────────────────────
                log_func = getattr(logger, log_level.lower(), logger.error)
                log_func(
                    f"Error in {func.__module__}.{func.__name__}: {str(e)}",
                    exc_info=True
                )

                # ───────────────────────────────────────────────────
                # UI
                # ───────────────────────────────────────────────────
                if show_error:
                    msg = error_message or f"❌ Erreur dans {func.__name__}"

                    if toast and hasattr(st, "toast"):
                        st.toast(msg, icon="❌")
                    else:
                        st.error(msg)

                    # Mode debug (afficher stack trace)
                    if st.session_state.get("debug_mode", False):
                        with st.expander("🐛 Stack Trace (Debug)"):
                            st.code(traceback.format_exc())

                return fallback_value

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# VERSION ASYNC
# ═══════════════════════════════════════════════════════════════

def async_safe_execute(
        fallback_value: Any = None,
        show_error: bool = True,
        error_message: Optional[str] = None
):
    """
    Version async du decorator

    Usage:
        @async_safe_execute(fallback_value=[])
        async def fetch_data():
            return await api.call()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                logger.error(f"Async error in {func.__name__}: {str(e)}")

                if show_error:
                    msg = error_message or f"❌ Erreur: {str(e)}"
                    st.error(msg)

                return fallback_value

        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# CONTEXT MANAGER (alternative)
# ═══════════════════════════════════════════════════════════════

class SafeContext:
    """
    Context manager pour gérer erreurs dans un bloc

    Usage:
        with SafeContext("Création recette"):
            recette = create_recette(data)
            # Si erreur ici, gérée automatiquement
    """

    def __init__(
            self,
            operation_name: str,
            show_error: bool = True,
            reraise: bool = False
    ):
        self.operation_name = operation_name
        self.show_error = show_error
        self.reraise = reraise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True

        # Log
        logger.error(
            f"Error during {self.operation_name}: {str(exc_val)}",
            exc_info=(exc_type, exc_val, exc_tb)
        )

        # UI
        if self.show_error:
            st.error(f"❌ Erreur lors de {self.operation_name}")

            if st.session_state.get("debug_mode"):
                with st.expander("🐛 Stack Trace"):
                    st.code("".join(traceback.format_exception(exc_type, exc_val, exc_tb)))

        # Supprimer l'exception si reraise=False
        return not self.reraise


# ═══════════════════════════════════════════════════════════════
# HELPERS VALIDATION
# ═══════════════════════════════════════════════════════════════

class ValidationError(Exception):
    """Exception pour erreurs de validation"""
    pass


def require_fields(data: dict, fields: list[str], object_name: str = "objet"):
    """
    Vérifie que les champs requis sont présents

    Usage:
        require_fields(data, ["nom", "quantite"], "recette")

    Raises:
        ValidationError si champ manquant
    """
    missing = [f for f in fields if not data.get(f)]

    if missing:
        raise ValidationError(
            f"Champs manquants pour {object_name}: {', '.join(missing)}"
        )


def require_positive(value: float, field_name: str = "valeur"):
    """
    Vérifie qu'une valeur est positive

    Raises:
        ValidationError si négatif ou zéro
    """
    if value <= 0:
        raise ValidationError(f"{field_name} doit être positif (reçu: {value})")


def require_not_none(value: Any, field_name: str = "valeur"):
    """
    Vérifie qu'une valeur n'est pas None

    Raises:
        ValidationError si None
    """
    if value is None:
        raise ValidationError(f"{field_name} ne peut pas être vide")


# ═══════════════════════════════════════════════════════════════
# RETRY DECORATOR
# ═══════════════════════════════════════════════════════════════

def retry_on_error(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
):
    """
    Decorator pour retry automatique en cas d'erreur

    Args:
        max_retries: Nombre max de tentatives
        delay: Délai initial entre tentatives (secondes)
        backoff: Multiplicateur du délai (exponentiel)
        exceptions: Tuple d'exceptions à retry

    Usage:
        @retry_on_error(max_retries=3, delay=2.0)
        def call_external_api():
            # Appel API fragile
            return response
    """
    import time

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_retries - 1:
                        # Dernière tentative, re-raise
                        raise

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}"
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper
    return decorator