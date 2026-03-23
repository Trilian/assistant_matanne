"""Décorateur: gestion centralisée d'erreurs avec logging."""

import logging
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def avec_gestion_erreurs(
    default_return: Any = None,
    log_level: str = "ERROR",
    afficher_erreur: bool = False,
    relancer_metier: bool = True,
    afficher_details_debug: bool = True,
):
    """
    Décorateur unifié pour gestion centralisée d'erreurs avec affichage UI.

    Gère intelligemment les exceptions métier (``ExceptionApp``) et génériques:

    - **Exceptions métier** : log au bon niveau, puis relancées
      (ou fallback selon ``relancer_metier``).
    - **Exceptions génériques** : loguées, puis retournent ``default_return``.

    Usage::

        @avec_gestion_erreurs(default_return=None)
        def operation_risquee(data: dict) -> dict:
            # Code qui peut lever des exceptions
            return resultat

        # Avec gestion fine des erreurs métier
        @avec_gestion_erreurs(
            default_return=[],
            relancer_metier=False,  # Retourne default_return même pour ExceptionApp
        )
        def charger_recettes() -> list:
            return service.get_all()

    Args:
        default_return: Valeur retournée en cas d'erreur
        log_level: Niveau de log ("DEBUG", "INFO", "WARNING", "ERROR")
        afficher_erreur: Log l'erreur (conservé pour rétrocompatibilité).
        relancer_metier: Re-raise les ExceptionApp (défaut True pour backward compat).
            Si False, retourne ``default_return`` pour toutes les erreurs.
        afficher_details_debug: Log la stack trace en mode debug (défaut True)

    Returns:
        Résultat de la fonction ou default_return
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                from src.core.exceptions import (
                    ErreurBaseDeDonnees,
                    ErreurLimiteDebit,
                    ErreurNonTrouve,
                    ErreurServiceExterne,
                    ErreurServiceIA,
                    ErreurValidation,
                    ExceptionApp,
                )

                # ── Déterminer le niveau de log adapté ──
                if isinstance(e, ExceptionApp):
                    _LOG_MAP: dict[type, str] = {
                        ErreurValidation: "warning",
                        ErreurNonTrouve: "info",
                        ErreurLimiteDebit: "warning",
                        ErreurServiceExterne: "warning",
                        ErreurServiceIA: "warning",
                        ErreurBaseDeDonnees: "error",
                    }
                    effective_level = _LOG_MAP.get(type(e), log_level.lower())
                else:
                    effective_level = "critical" if log_level == "ERROR" else log_level.lower()

                log_msg = f"Erreur dans {func.__name__}: {e}"
                getattr(logger, effective_level, logger.error)(log_msg)

                # ── Log détaillé si demandé ──
                if afficher_erreur and afficher_details_debug:
                    logger.debug("Stack trace:\n%s", traceback.format_exc())

                # ── Relancer ou fallback ──
                if isinstance(e, ExceptionApp) and relancer_metier:
                    raise

                return default_return

        return wrapper  # type: ignore

    return decorator
