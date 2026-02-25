"""Décorateur: gestion centralisée d'erreurs avec affichage UI Streamlit."""

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

    - **Exceptions métier** : affichage typé dans l'UI (icônes par type),
      log au bon niveau, puis relancées (ou fallback selon ``relancer_metier``).
    - **Exceptions génériques** : loguées, affichées si demandé, puis
      retournent ``default_return``.
    - **Mode debug** : affiche automatiquement la stack trace dans un
      expander Streamlit.

    Usage::

        @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
        def operation_risquee(data: dict) -> dict:
            # Code qui peut lever des exceptions
            return resultat

        # Avec gestion fine des erreurs métier
        @avec_gestion_erreurs(
            default_return=[],
            afficher_erreur=True,
            relancer_metier=False,  # Retourne default_return même pour ExceptionApp
        )
        def charger_recettes() -> list:
            return service.get_all()

    Args:
        default_return: Valeur retournée en cas d'erreur
        log_level: Niveau de log ("DEBUG", "INFO", "WARNING", "ERROR")
        afficher_erreur: Afficher l'erreur dans Streamlit
        relancer_metier: Re-raise les ExceptionApp (défaut True pour backward compat).
            Si False, retourne ``default_return`` pour toutes les erreurs.
        afficher_details_debug: Affiche la stack trace en mode debug (défaut True)

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

                # ── Affichage UI intelligent par type d'erreur ──
                if afficher_erreur:
                    _afficher_erreur_ui(e, func.__name__, afficher_details_debug)

                # ── Relancer ou fallback ──
                if isinstance(e, ExceptionApp) and relancer_metier:
                    raise

                return default_return

        return wrapper  # type: ignore

    return decorator


def _afficher_erreur_ui(
    erreur: Exception,
    nom_fonction: str,
    afficher_details_debug: bool = True,
) -> None:
    """Affiche une erreur dans Streamlit avec formatage intelligent par type."""
    try:
        import streamlit as st
    except Exception:
        return

    from src.core.exceptions import (
        ErreurBaseDeDonnees,
        ErreurLimiteDebit,
        ErreurNonTrouve,
        ErreurServiceExterne,
        ErreurServiceIA,
        ErreurValidation,
        ExceptionApp,
    )

    try:
        if isinstance(erreur, ExceptionApp):
            _UI_MAP: dict[type, tuple[Any, str]] = {
                ErreurValidation: (st.error, "[ERROR]"),
                ErreurNonTrouve: (st.warning, "[!]"),
                ErreurBaseDeDonnees: (st.error, "\U0001f4be"),  # 💾
                ErreurServiceIA: (st.error, "\U0001f916"),  # 🤖
                ErreurLimiteDebit: (st.warning, "\u23f3"),  # ⏳
                ErreurServiceExterne: (st.error, "\U0001f310"),  # 🌐
            }
            afficher_fn, prefix = _UI_MAP.get(type(erreur), (st.error, "[ERROR]"))
            afficher_fn(f"{prefix} {erreur.message_utilisateur}")
        else:
            st.error("[ERROR] Une erreur inattendue s'est produite")
    except Exception:
        # Streamlit non initialisé ou contexte invalide
        return

    # Stack trace en mode debug
    if afficher_details_debug:
        try:
            import os

            is_debug = os.environ.get("DEBUG", "").lower() in ("1", "true")
            if not is_debug:
                is_debug = st.session_state.get("debug_mode", False)
            if is_debug:
                with st.expander("\U0001f41b Stack trace"):  # 🐛
                    st.code(traceback.format_exc())
        except Exception:
            pass
