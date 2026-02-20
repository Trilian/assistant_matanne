"""
Errors - Gestion des erreurs avec intégration UI (Streamlit).

Ce module :
- Ré-exporte les exceptions pures depuis errors_base.py
- Ajoute les fonctions d'affichage UI
- Fournit des décorateurs de gestion d'erreurs avec UI

[!] IMPORTANT: Les exceptions pures sont dans errors_base.py (sans dépendances UI)
"""

import logging
import traceback
from collections.abc import Callable
from functools import wraps
from typing import Any

import streamlit as st

# Ré-exporter les exceptions et helpers purs
from .errors_base import (  # noqa: F401
    ErreurBaseDeDonnees,
    ErreurConfiguration,
    ErreurLimiteDebit,
    ErreurNonTrouve,
    ErreurServiceExterne,
    ErreurServiceIA,
    ErreurValidation,
    ExceptionApp,
    exiger_champs,
    exiger_existence,
    exiger_longueur,
    exiger_plage,
    exiger_positif,
    valider_plage,
    valider_type,
)
from .session_keys import SK

logger = logging.getLogger(__name__)


def _est_mode_debug() -> bool:
    """
    Retourne l'état du mode debug de l'application.

    Essaie d'utiliser le `EtatApp.mode_debug` via `obtenir_etat()` si disponible,
    sinon fallback sur `st.session_state['debug_mode']` pour compatibilité.
    """
    try:
        from .state import obtenir_etat

        etat = obtenir_etat()
        return bool(getattr(etat, "mode_debug", False))
    except Exception:
        # Fallback safe: st may not be initialisé
        try:
            return bool(st.session_state.get(SK.DEBUG_MODE, False))
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR DE GESTION D'ERREURS
# ═══════════════════════════════════════════════════════════


def gerer_erreurs(
    afficher_dans_ui: bool = True,
    niveau_log: str = "ERROR",
    relancer: bool = False,
    valeur_fallback: Any = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Décorateur pour gérer automatiquement les erreurs.

    Capture les exceptions, les log, et optionnellement :
    - Affiche un message à l'utilisateur (Streamlit)
    - Retourne une valeur de fallback
    - Relance l'exception

    Args:
        afficher_dans_ui: Afficher l'erreur dans Streamlit
        niveau_log: Niveau de log (ERROR, WARNING, INFO)
        relancer: Relancer l'exception après traitement
        valeur_fallback: Valeur à retourner en cas d'erreur

    Returns:
        Décorateur de fonction

    Example:
        >>> @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=[])
        >>> def obtenir_recettes():
        >>>     return recette_service.get_all()
    """

    def decorateur(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)

            except ErreurValidation as e:
                logger.warning(f"ErreurValidation dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"[ERROR] {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurNonTrouve as e:
                logger.info(f"ErreurNonTrouve dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.warning(f"[!] {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurBaseDeDonnees as e:
                logger.error(f"ErreurBaseDeDonnees dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error("💾 Erreur de base de données")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurServiceIA as e:
                logger.warning(f"ErreurServiceIA dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"🤖 {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurLimiteDebit as e:
                logger.warning(f"ErreurLimiteDebit dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.warning(f"⏳ {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except ErreurServiceExterne as e:
                logger.warning(f"ErreurServiceExterne dans {func.__name__}: {e.message}")
                if afficher_dans_ui:
                    st.error(f"🌐 {e.message_utilisateur}")
                if relancer:
                    raise
                return valeur_fallback

            except Exception as e:
                logger.critical(f"Erreur inattendue dans {func.__name__}: {e}", exc_info=True)
                if afficher_dans_ui:
                    st.error("[ERROR] Une erreur inattendue s'est produite")

                    # Afficher stack trace en mode debug
                    if _est_mode_debug():
                        with st.expander("🐛 Stack trace"):
                            st.code(traceback.format_exc())

                if relancer:
                    raise
                return valeur_fallback

        return wrapper

    return decorateur


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE D'ERREURS STREAMLIT
# ═══════════════════════════════════════════════════════════


def afficher_erreur_streamlit(erreur: Exception, contexte: str = "") -> None:
    """
    Affiche une erreur formatée dans Streamlit.

    Gère l'affichage selon le type d'erreur et le mode debug.

    Args:
        erreur: Exception à afficher
        contexte: Contexte additionnel (optionnel)
    """
    if isinstance(erreur, ExceptionApp):
        mapping = {
            ErreurValidation: (st.error, "[ERROR]"),
            ErreurNonTrouve: (st.warning, "[!]"),
            ErreurBaseDeDonnees: (st.error, "💾"),
            ErreurServiceIA: (st.error, "🤖"),
            ErreurLimiteDebit: (st.warning, "⏳"),
            ErreurServiceExterne: (st.error, "🌐"),
        }

        for exc_type, (afficher_fn, prefix) in mapping.items():
            if isinstance(erreur, exc_type):
                afficher_fn(f"{prefix} {erreur.message_utilisateur}")
                break
        else:
            st.error(f"[ERROR] {erreur.message_utilisateur}")

        # Afficher détails en mode debug
        if _est_mode_debug() and getattr(erreur, "details", None):
            with st.expander("[SEARCH] Détails"):
                st.json(erreur.details)
    else:
        # Erreurs inconnues
        st.error("[ERROR] Une erreur inattendue s'est produite")

        if contexte:
            st.caption(f"Contexte : {contexte}")

        # Stack trace en mode debug
        if _est_mode_debug():
            with st.expander("🐛 Stack trace"):
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGER POUR GESTION D'ERREURS
# ═══════════════════════════════════════════════════════════


class GestionnaireErreurs:
    """
    Context manager pour gérer les erreurs dans un bloc de code.

    Example:
        >>> with GestionnaireErreurs("Création recette"):
        >>>     recette = recette_service.create(data)
    """

    def __init__(
        self,
        contexte: str,
        afficher_dans_ui: bool = True,
        logger_instance: logging.Logger | None = None,
    ):
        """
        Initialise le gestionnaire.

        Args:
            contexte: Description du contexte pour les logs
            afficher_dans_ui: Afficher erreur dans Streamlit
            logger_instance: Logger à utiliser (optionnel)
        """
        self.contexte = contexte
        self.afficher_dans_ui = afficher_dans_ui
        self.logger = logger_instance or logger

    def __enter__(self):
        """Entre dans le contexte."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Sort du contexte et gère les erreurs.

        Returns:
            True si l'exception est gérée, False sinon
        """
        if exc_type is None:
            return True

        # Logger l'erreur
        self.logger.error(
            f"Erreur dans {self.contexte}: {exc_val}", exc_info=(exc_type, exc_val, exc_tb)
        )

        # Afficher dans UI si demandé
        if self.afficher_dans_ui:
            afficher_erreur_streamlit(exc_val, self.contexte)

        # Ne pas supprimer l'exception (elle sera relancée)
        return False
