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
    *,
    param_name: str = "data",
    inject_validated: bool = True,
):
    """
    Décorateur pour validation Pydantic automatique.

    Valide le paramètre ``param_name`` (dict) avec ``validator_class``
    et remplace la valeur par le résultat de ``model_dump()`` si
    ``inject_validated`` est True.

    Usage::

        # Simple dict validation — le paramètre 'data' est validé automatiquement
        @avec_validation(RecetteInput)
        def creer_recette(data: dict, db: Session) -> Recette:
            # data est déjà validé et normalisé
            ...

        # Avec mapping de paramètre
        @avec_validation(ArticleCoursesInput, param_name="article_data")
        def ajouter_article(article_data: dict, db: Session):
            ...

        # Sans remplacement (validation seule, lève si invalide)
        @avec_validation(RecetteInput, inject_validated=False)
        def creer_recette(data: dict, db: Session):
            ...

    Args:
        validator_class: Modèle Pydantic pour validation
        field_mapping: Mapping des paramètres (déprécié, utiliser param_name)
        param_name: Nom du paramètre dict à valider (défaut: "data")
        inject_validated: Remplacer le dict par les données validées (défaut: True)

    Returns:
        Fonction décorée avec validation automatique

    Raises:
        ErreurValidation: Si validation échoue
    """
    # Rétrocompatibilité: field_mapping override param_name
    effective_param = list(field_mapping.keys())[0] if field_mapping else param_name

    def decorator(func: F) -> F:
        import inspect

        _sig = inspect.signature(func)
        _params = list(_sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from pydantic import ValidationError

            from src.core.exceptions import ErreurValidation

            try:
                # Résoudre le paramètre: d'abord dans kwargs, puis dans args positionnels
                data = None
                in_kwargs = effective_param in kwargs

                if in_kwargs:
                    data = kwargs[effective_param]
                elif effective_param in _params:
                    idx = _params.index(effective_param)
                    if idx < len(args):
                        data = args[idx]

                if data is not None and isinstance(data, dict):
                    validated = validator_class(**data)
                    if inject_validated:
                        validated_data = validated.model_dump()
                        if in_kwargs:
                            kwargs[effective_param] = validated_data
                        elif effective_param in _params:
                            idx = _params.index(effective_param)
                            args = list(args)
                            args[idx] = validated_data
                            args = tuple(args)

                return func(*args, **kwargs)

            except ValidationError as e:
                raise ErreurValidation(
                    f"Validation échouée pour {validator_class.__name__}: {e}",
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
