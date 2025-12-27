"""
Système d'Exceptions Unifié + Error Handler
Standardise la gestion d'erreurs dans toute l'application

"""
from typing import Optional, Dict, Any, Callable
from functools import wraps
import logging
import traceback
import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# EXCEPTIONS PERSONNALISÉES
# ═══════════════════════════════════════════════════════════════

class AppException(Exception):
    """
    Exception de base de l'application

    Toutes les exceptions custom héritent de celle-ci
    """

    def __init__(
            self,
            message: str,
            details: Optional[Dict[str, Any]] = None,
            user_message: Optional[str] = None
    ):
        """
        Args:
            message: Message technique (logs)
            details: Dict avec contexte additionnel
            user_message: Message friendly pour l'utilisateur
        """
        self.message = message
        self.details = details or {}
        self.user_message = user_message or message
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dict pour logs/API"""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "user_message": self.user_message,
            "details": self.details
        }


class ValidationError(AppException):
    """
    Erreur de validation de données

    Usage:
        if not nom:
            raise ValidationError(
                "Nom manquant",
                details={"field": "nom"},
                user_message="Le nom est obligatoire"
            )
    """
    pass


class NotFoundError(AppException):
    """
    Ressource introuvable

    Usage:
        recette = db.query(Recette).get(id)
        if not recette:
            raise NotFoundError(
                f"Recette {id} non trouvée",
                details={"recette_id": id},
                user_message="Cette recette n'existe pas"
            )
    """
    pass


class DatabaseError(AppException):
    """
    Erreur base de données

    Usage:
        try:
            db.commit()
        except SQLAlchemyError as e:
            raise DatabaseError(
                f"Erreur DB: {e}",
                details={"operation": "commit"},
                user_message="Erreur de sauvegarde, réessaie"
            )
    """
    pass


class AIServiceError(AppException):
    """
    Erreur service IA (Mistral API)

    Usage:
        if response.status_code != 200:
            raise AIServiceError(
                f"API error: {response.status_code}",
                details={"status": response.status_code},
                user_message="L'IA est temporairement indisponible"
            )
    """
    pass


class RateLimitError(AppException):
    """
    Rate limit dépassé

    Usage:
        if not RateLimiter.can_call():
            raise RateLimitError(
                "Rate limit atteint",
                details={"calls_today": 100},
                user_message="Limite d'appels IA atteinte, réessaie dans 1h"
            )
    """
    pass


class AuthorizationError(AppException):
    """
    Erreur d'autorisation

    Usage:
        if not user.can_delete(recette):
            raise AuthorizationError(
                "User cannot delete this recipe",
                user_message="Tu n'as pas les droits pour supprimer"
            )
    """
    pass


class BusinessLogicError(AppException):
    """
    Erreur de logique métier

    Usage:
        if stock.quantite < 0:
            raise BusinessLogicError(
                "Stock négatif détecté",
                details={"stock_id": stock.id, "quantite": stock.quantite},
                user_message="Impossible d'avoir un stock négatif"
            )
    """
    pass


class ExternalServiceError(AppException):
    """
    Erreur service externe (météo, scraping, etc.)

    Usage:
        if not weather_data:
            raise ExternalServiceError(
                "API météo timeout",
                details={"service": "OpenWeatherMap"},
                user_message="Impossible de récupérer la météo"
            )
    """
    pass


# ═══════════════════════════════════════════════════════════════
# ERROR HANDLER DECORATOR
# ═══════════════════════════════════════════════════════════════

def handle_errors(
        show_in_ui: bool = True,
        log_level: str = "ERROR",
        reraise: bool = False,
        fallback_value: Any = None
):
    """
    Decorator pour gérer automatiquement les erreurs

    Args:
        show_in_ui: Si True, affiche erreur dans Streamlit
        log_level: Niveau de log (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        reraise: Si True, re-raise l'exception après handling
        fallback_value: Valeur de retour si erreur (si reraise=False)

    Usage:
        @handle_errors(show_in_ui=True)
        def create_recette(self, data):
            # Code métier
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
                    st.error(f"💾 Erreur de base de données")
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
                    st.error("❌ Une erreur inattendue s'est produite")

                    # Mode debug : afficher détails
                    if st.session_state.get("debug_mode", False):
                        with st.expander("🐛 Stack trace (debug)"):
                            st.code(traceback.format_exc())

                # Toujours re-raise les erreurs inattendues en mode strict
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


# ═══════════════════════════════════════════════════════════════
# CONTEXT MANAGER POUR GESTION D'ERREURS
# ═══════════════════════════════════════════════════════════════

class error_context:
    """
    Context manager pour gérer erreurs dans un bloc de code

    Usage:
        with error_context("Création recette", show_in_ui=True):
            recette = create_recette(data)
            # Si erreur ici, gérée automatiquement
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


# ═══════════════════════════════════════════════════════════════
# HELPERS POUR VALIDATION
# ═══════════════════════════════════════════════════════════════

def require_fields(data: Dict, fields: list[str], object_name: str = "objet"):
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


# ═══════════════════════════════════════════════════════════════
# ERROR RECOVERY HELPERS
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

            # Ne devrait jamais arriver ici
            return None

        return wrapper
    return decorator