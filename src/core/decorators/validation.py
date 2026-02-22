"""Décorateurs: validation Pydantic automatique et résilience composée."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from .errors import _afficher_erreur_ui

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def avec_validation(
    validator_class: type,
    field_mapping: dict[str, str] | None = None,
):
    """
    Décorateur pour validation Pydantic automatique.

    Usage::

        @avec_validation(RecetteInput, field_mapping={
            "data": "recipe_data"
        })
        def creer_recette(data: dict, db: Session) -> Recette:
            validated = RecetteInput(**data)
            # ...

    Args:
        validator_class: Modèle Pydantic pour validation
        field_mapping: Mapping des paramètres

    Returns:
        Fonction décorée avec validation automatique

    Raises:
        ErreurValidation: Si validation échoue
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from pydantic import ValidationError

            from src.core.errors_base import ErreurValidation

            try:
                # Chercher le paramètre à valider
                param_key = list(field_mapping.keys())[0] if field_mapping else "data"

                if param_key in kwargs:
                    data = kwargs[param_key]
                    validated = validator_class(**data)
                    kwargs[param_key] = validated.model_dump()

                return func(*args, **kwargs)

            except ValidationError as e:
                raise ErreurValidation(
                    f"Validation échouée: {e}",
                    details={"validation_errors": e.errors()},
                    message_utilisateur="Les données fournies sont invalides",
                ) from e

        return wrapper  # type: ignore

    return decorator


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR: AVEC_RESILIENCE (UNIFIÉ)
# ═══════════════════════════════════════════════════════════

# Sentinel pour distinguer «fallback None» de «pas de fallback»
_NO_FALLBACK = object()


def avec_resilience(
    *,
    retry: int = 0,
    timeout_s: float | None = None,
    fallback: Any = None,
    circuit: str | None = None,
    log_level: str = "error",
    afficher_ui: bool = False,
):
    """
    Décorateur unifié de résilience — compose retry, timeout, circuit breaker et fallback.

    Construit la chaîne de policies à la décoration (pas à chaque appel)
    pour une performance optimale.

    Args:
        retry: Nombre de retentatives (0 = pas de retry)
        timeout_s: Timeout en secondes (None = pas de timeout)
        fallback: Valeur retournée en cas d'échec final (None = relève l'exception)
        circuit: Nom du circuit breaker (None = pas de circuit breaker)
        log_level: Niveau de log pour les erreurs ('debug', 'info', 'warning', 'error')
        afficher_ui: Afficher l'erreur dans Streamlit UI

    Returns:
        Décorateur de fonction

    Usage::

        # Appel IA avec retry + timeout + fallback
        @avec_resilience(retry=3, timeout_s=30, fallback=[], afficher_ui=True)
        def generer_recettes(contexte: str) -> list[Recette]:
            return service.generer(contexte)

        # Requête DB avec circuit breaker
        @avec_resilience(circuit="database", timeout_s=10, log_level="warning")
        def charger_donnees() -> list[dict]:
            return db.query(Model).all()

        # Simple protection avec fallback
        @avec_resilience(fallback={})
        def operation_risquee() -> dict:
            return api.call()
    """
    _fallback = _NO_FALLBACK if fallback is None else fallback

    def decorator(func: F) -> F:
        # Construire la chaîne de policies à la décoration (lazy import)
        from src.core.resilience import (
            PolicyComposee,
            RetryPolicy,
            TimeoutPolicy,
        )

        policies = []

        if timeout_s is not None:
            policies.append(TimeoutPolicy(timeout_secondes=timeout_s))

        if retry > 0:
            policies.append(RetryPolicy(max_tentatives=retry, delai_base=1.0, jitter=True))

        composed = PolicyComposee(policies) if policies else None

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Fonction interne avec circuit breaker optionnel
            def _inner() -> Any:
                if circuit is not None:
                    from src.core.ai.circuit_breaker import obtenir_circuit

                    cb = obtenir_circuit(circuit)
                    return cb.appeler(fn=lambda: func(*args, **kwargs))
                return func(*args, **kwargs)

            try:
                if composed is not None:
                    return composed.executer(_inner)
                else:
                    return _inner()

            except Exception as e:
                # Logger
                log_fn = getattr(logger, log_level.lower(), logger.error)
                log_fn(f"Erreur dans {func.__name__}: {e}")

                # Afficher dans l'UI (réutilise le helper unifié)
                if afficher_ui:
                    _afficher_erreur_ui(e, func.__name__)

                # Fallback ou re-raise
                if _fallback is not _NO_FALLBACK:
                    return _fallback
                raise

        return wrapper  # type: ignore

    return decorator
