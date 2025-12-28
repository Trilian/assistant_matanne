"""
Gestionnaires d'Erreurs - Decorators et Helpers
Gestion centralisée des erreurs avec feedback UI automatique
"""
import streamlit as st
from functools import wraps
from typing import Callable, Any, Dict, List
import logging
import traceback

from .exceptions import (
    AppException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    AIServiceError,
    RateLimitError,
    AuthorizationError,
    BusinessLogicError,
    ExternalServiceError
)

logger = logging.getLogger(__name__)


def handle_errors(
        show_in_ui: bool = True,
        log_level: str = "ERROR",
        reraise: bool = False,
        fallback_value: Any = None,
        error_message: Optional[str] = None
):
    """
    Decorator pour gérer automatiquement les erreurs

    Args:
        show_in_ui: Si True, affiche erreur dans Streamlit
        log_level: Niveau de log
        reraise: Si True, re-raise l'exception après handling
        fallback_value: Valeur de retour si erreur
        error_message: Message custom à afficher

    Usage:
        @handle_errors(show_in_ui=True)
        def create_recette(self, data):
            if not data.get("nom"):
                raise ValidationError("Nom manquant")
            return recette_service.create(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            # ───────────────────────────────────────────────────
            # EXCEPTIONS MÉTIER (gérées proprement)
            # ───────────────────────────────────────────────────
            except ValidationError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.error(f"❌ {e.user_message}")
                    if e.details:
                        with st.expander("Détails"):
                            st.json(e.details)

                if reraise:
                    raise
                return fallback_value

            except NotFoundError as e:
                _log_exception(func, e, "INFO")

                if show_in_ui:
                    st.warning(f"⚠️ {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            except DatabaseError as e:
                _log_exception(func, e, "ERROR")

                if show_in_ui:
                    st.error("💾 Erreur de base de données")
                    st.caption("Réessaie dans quelques instants")

                if reraise:
                    raise
                return fallback_value

            except AIServiceError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.error(f"🤖 {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            except RateLimitError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.warning(f"⏳ {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            except AuthorizationError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.error(f"🔒 {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            except BusinessLogicError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.error(f"⚠️ {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            except ExternalServiceError as e:
                _log_exception(func, e, "WARNING")

                if show_in_ui:
                    st.warning(f"🌐 {e.user_message}")

                if reraise:
                    raise
                return fallback_value

            # ───────────────────────────────────────────────────
            # EXCEPTIONS INATTENDUES
            # ───────────────────────────────────────────────────
            except Exception as e:
                _log_exception(func, e, "CRITICAL")

                if show_in_ui:
                    display_msg = error_message or "❌ Une erreur inattendue s'est produite"
                    st.error(display_msg)

                    # Mode debug : afficher détails
                    if st.session_state.get("debug_mode", False):
                        with st.expander("🐛 Stack trace (debug)"):
                            st.code(traceback.format_exc())

                if reraise or st.session_state.get("debug_mode", False):
                    raise

                return fallback_value

        return wrapper
    return decorator


def _log_exception(func: Callable, exception: Exception, level: str):
    """Helper pour logger les exceptions"""
    log_func = getattr(logger, level.lower(), logger.error)

    func_name = f"{func.__module__}.{func.__name__}"

    if isinstance(exception, AppException):
        log_func(
            f"{exception.__class__.__name__} in {func_name}: {exception.message}",
            extra={"details": exception.details}
        )
    else:
        log_func(
            f"Unexpected error in {func_name}: {str(exception)}",
            exc_info=True
        )


# ═══════════════════════════════════════════════════════════
# HELPERS DE VALIDATION
# ═══════════════════════════════════════════════════════════

def require_fields(data: Dict, fields: List[str], object_name: str = "objet"):
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
            f"Champs manquants: {missing}",
            details={"missing_fields": missing},
            user_message=f"Les champs suivants sont obligatoires : {', '.join(missing)}"
        )


def require_positive(value: float, field_name: str):
    """
    Vérifie qu'une valeur est positive

    Usage:
        require_positive(quantite, "quantite")

    Raises:
        ValidationError si négatif ou zéro
    """
    if value <= 0:
        raise ValidationError(
            f"{field_name} doit être positif",
            details={"field": field_name, "value": value},
            user_message=f"{field_name} doit être supérieur à 0"
        )


def require_exists(obj: Any, object_type: str, object_id: Any):
    """
    Vérifie qu'un objet existe

    Usage:
        recette = db.query(Recette).get(id)
        require_exists(recette, "Recette", id)

    Raises:
        NotFoundError si None
    """
    if obj is None:
        raise NotFoundError(
            f"{object_type} {object_id} not found",
            details={"type": object_type, "id": object_id},
            user_message=f"{object_type} introuvable"
        )


def require_permission(condition: bool, action: str):
    """
    Vérifie les permissions

    Usage:
        require_permission(user.is_admin, "supprimer des recettes")

    Raises:
        AuthorizationError si False
    """
    if not condition:
        raise AuthorizationError(
            f"Permission denied for: {action}",
            details={"action": action},
            user_message=f"Tu n'as pas la permission de {action}"
        )


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════

class error_context:
    """
    Context manager pour gérer erreurs dans un bloc de code

    Usage:
        with error_context("Création recette", show_in_ui=True):
            recette = create_recette(data)
    """

    def __init__(
            self,
            operation_name: str,
            show_in_ui: bool = True,
            reraise: bool = False
    ):
        self.operation_name = operation_name
        self.show_in_ui = show_in_ui
        self.reraise = reraise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True

        # Gérer l'exception
        if isinstance(exc_val, AppException):
            logger.warning(
                f"{exc_type.__name__} during {self.operation_name}: {exc_val.message}"
            )

            if self.show_in_ui:
                st.error(f"❌ {exc_val.user_message}")

        else:
            logger.error(
                f"Unexpected error during {self.operation_name}",
                exc_info=(exc_type, exc_val, exc_tb)
            )

            if self.show_in_ui:
                st.error(f"❌ Erreur lors de {self.operation_name}")

        # Supprimer l'exception si reraise=False
        return not self.reraise