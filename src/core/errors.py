"""
Errors - Gestion des erreurs avec intégration UI (Streamlit).

Ce module :
- Ré-exporte les exceptions pures depuis errors_base.py
- Ajoute les fonctions d'affichage UI (avec import lazy de Streamlit)
- Fournit des décorateurs de gestion d'erreurs avec UI

[!] IMPORTANT: Les exceptions pures sont dans errors_base.py (sans dépendances UI)

.. note::
    ``gerer_erreurs`` est déprécié au profit de ``avec_gestion_erreurs``
    dans ``src.core.decorators`` (version plus complète et unifiée).
"""

import logging
import os
import traceback
import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any

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


def _get_st():
    """Import lazy de Streamlit (None si indisponible)."""
    try:
        import streamlit as st

        return st
    except Exception:
        return None


def _est_mode_debug() -> bool:
    """
    Retourne l'état du mode debug de l'application.

    Utilise os.environ et st.session_state directement pour éviter
    la chaîne de dépendances errors → state → storage.
    """
    # Priorité 1: Variable d'environnement (évite toute dépendance)
    env_debug = os.environ.get("DEBUG", "").lower()
    if env_debug in ("1", "true", "yes"):
        return True

    # Priorité 2: Streamlit session_state (accès direct, pas via state.py)
    try:
        st = _get_st()
        if st is not None:
            return bool(st.session_state.get(SK.DEBUG_MODE, False))
    except Exception:
        pass

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

    .. deprecated:: 2.0
        Utiliser :func:`src.core.decorators.avec_gestion_erreurs` à la place.
        Ce décorateur est conservé pour compatibilité et délègue au décorateur
        unifié.

    Args:
        afficher_dans_ui: Afficher l'erreur dans Streamlit
        niveau_log: Niveau de log (ERROR, WARNING, INFO)
        relancer: Relancer l'exception après traitement
        valeur_fallback: Valeur à retourner en cas d'erreur
    """
    warnings.warn(
        "gerer_erreurs() est déprécié, utiliser avec_gestion_erreurs() de src.core.decorators",
        DeprecationWarning,
        stacklevel=2,
    )

    from .decorators import avec_gestion_erreurs

    return avec_gestion_erreurs(
        default_return=valeur_fallback,
        log_level=niveau_log,
        afficher_erreur=afficher_dans_ui,
        relancer_metier=relancer,
    )


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
    st = _get_st()
    if st is None:
        logger.error(f"Erreur (Streamlit indisponible): {erreur}")
        return

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


__all__ = [
    # Ré-exportées depuis errors_base
    "ExceptionApp",
    "ErreurValidation",
    "ErreurBaseDeDonnees",
    "ErreurNonTrouve",
    "ErreurServiceIA",
    "ErreurLimiteDebit",
    "ErreurServiceExterne",
    "ErreurConfiguration",
    "exiger_champs",
    "exiger_existence",
    "exiger_longueur",
    "exiger_plage",
    "exiger_positif",
    "valider_plage",
    "valider_type",
    # Fonctions UI
    "gerer_erreurs",
    "afficher_erreur_streamlit",
    "GestionnaireErreurs",
]


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
