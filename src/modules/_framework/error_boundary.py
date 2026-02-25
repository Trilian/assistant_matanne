"""
Error Boundary - Gestion d'erreurs unifiée pour modules Streamlit.

Inspiré du pattern Error Boundary de React, ce module fournit une
gestion d'erreurs élégante avec fallback UI et logging automatique.

Patterns disponibles:
1. Context manager ``error_boundary()`` pour blocs de code
2. Décorateur ``@avec_gestion_erreurs_ui()`` pour fonctions entières
3. Helper ``safe_call()`` pour appels silencieux

Usage basique:
    with error_boundary("Chargement des données"):
        data = service.get_data()
        afficher_tableau(data)

Usage avec fallback personnalisé:
    def mon_fallback():
        st.info("Données indisponibles, réessayez plus tard")

    with error_boundary("Chargement", fallback_ui=mon_fallback):
        ...

Usage décorateur:
    @avec_gestion_erreurs_ui("Erreur formulaire")
    def afficher_formulaire():
        ...
"""

from __future__ import annotations

import logging
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, TypeVar

import streamlit as st

from src.core.state import rerun

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ErrorBoundaryContext:
    """Contexte d'une erreur capturée par un error boundary.

    Attributes:
        titre: Titre affiché à l'utilisateur
        exception: L'exception capturée
        traceback_str: Stack trace formatée
        afficher_details: Si True, affiche les détails techniques
        retry_key: Clé unique pour le bouton retry
        metadata: Données additionnelles pour le debugging
    """

    titre: str
    exception: Exception
    traceback_str: str = ""
    afficher_details: bool = False
    retry_key: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.traceback_str:
            self.traceback_str = traceback.format_exc()
        if not self.retry_key:
            self.retry_key = f"retry_{hash(self.titre) % 10000}"


def _get_user_message(exception: Exception) -> str:
    """Extrait un message utilisateur friendly de l'exception."""
    # Essayer d'obtenir le message utilisateur si c'est une ErreurApplication
    if hasattr(exception, "message_utilisateur"):
        return str(exception.message_utilisateur)

    # Messages génériques selon le type d'erreur
    error_type = type(exception).__name__
    messages = {
        "ConnectionError": "Problème de connexion réseau",
        "TimeoutError": "La requête a pris trop de temps",
        "ValueError": "Données invalides",
        "KeyError": "Donnée manquante",
        "PermissionError": "Permission refusée",
        "FileNotFoundError": "Fichier non trouvé",
        "AttributeError": "Configuration incorrecte",
        "TypeError": "Type de données incorrect",
        "RuntimeError": "Erreur d'exécution",
    }

    return messages.get(error_type, str(exception)[:200])


def _render_error_ui(ctx: ErrorBoundaryContext) -> None:
    """Affiche l'UI d'erreur standard."""
    with st.container(border=True):
        st.error(f"❌ {ctx.titre}")

        user_message = _get_user_message(ctx.exception)
        st.markdown(f"**Détail:** {user_message}")

        if ctx.afficher_details:
            with st.expander("🔍 Détails techniques", expanded=False):
                st.code(ctx.traceback_str, language="python")
                if ctx.metadata:
                    st.json(ctx.metadata)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Réessayer", key=ctx.retry_key, type="primary"):
                rerun()
        with col2:
            st.caption("Si le problème persiste, contactez le support.")


def _render_warning_ui(ctx: ErrorBoundaryContext) -> None:
    """Affiche l'UI d'avertissement (erreurs non-critiques)."""
    st.warning(f"⚠️ {ctx.titre}: {_get_user_message(ctx.exception)}")


@contextmanager
def error_boundary(
    titre: str = "Une erreur est survenue",
    afficher_details: bool = False,
    fallback_ui: Callable[[], None] | None = None,
    niveau: str = "error",
    reraise: bool = False,
    metadata: dict[str, Any] | None = None,
):
    """Context manager pour gérer les erreurs UI de manière élégante.

    Args:
        titre: Message affiché à l'utilisateur en cas d'erreur
        afficher_details: Si True, affiche le traceback dans un expander
        fallback_ui: Fonction appelée pour afficher une UI alternative
        niveau: "error" (rouge) ou "warning" (jaune)
        reraise: Si True, relance l'exception après affichage
        metadata: Données additionnelles pour le logging

    Usage:
        with error_boundary("Chargement des données"):
            data = service.get_data()
            afficher_tableau(data)

    Avec fallback:
        def fallback():
            st.info("Service temporairement indisponible")

        with error_boundary("Chargement", fallback_ui=fallback):
            data = service.get_data()
    """
    try:
        yield
    except Exception as e:
        # Construire le contexte d'erreur
        ctx = ErrorBoundaryContext(
            titre=titre,
            exception=e,
            afficher_details=afficher_details,
            metadata=metadata or {},
        )

        # Log l'erreur
        log_message = f"{titre}: {type(e).__name__}: {e}"
        if metadata:
            log_message += f" | metadata={metadata}"

        if niveau == "error":
            logger.error(log_message, exc_info=True)
        else:
            logger.warning(log_message)

        # Afficher l'UI appropriée
        if fallback_ui is not None:
            try:
                fallback_ui()
            except Exception as fallback_error:
                logger.error(f"Erreur dans fallback_ui: {fallback_error}")
                _render_error_ui(ctx)
        elif niveau == "warning":
            _render_warning_ui(ctx)
        else:
            _render_error_ui(ctx)

        # Relancer si demandé
        if reraise:
            raise


def avec_gestion_erreurs_ui(
    titre: str = "Erreur",
    afficher_details: bool = False,
    fallback_ui: Callable[[], None] | None = None,
    niveau: str = "error",
) -> Callable[[F], F]:
    """Décorateur pour wrapper automatiquement les fonctions UI.

    Args:
        titre: Message d'erreur affiché
        afficher_details: Affiche le traceback si True
        fallback_ui: UI alternative en cas d'erreur
        niveau: "error" ou "warning"

    Usage:
        @avec_gestion_erreurs_ui("Erreur chargement recettes")
        def afficher_recettes():
            recettes = service.get_recettes()
            for r in recettes:
                st.write(r.nom)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with error_boundary(
                titre=titre,
                afficher_details=afficher_details,
                fallback_ui=fallback_ui,
                niveau=niveau,
                metadata={"function": func.__name__},
            ):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def safe_call(
    func: Callable[..., Any],
    *args: Any,
    default: Any = None,
    titre: str = "Erreur",
    log_error: bool = True,
    **kwargs: Any,
) -> Any:
    """Exécute une fonction avec gestion d'erreur silencieuse.

    Retourne `default` en cas d'erreur au lieu d'afficher une UI.
    Utile pour les opérations non-critiques en arrière-plan.

    Args:
        func: Fonction à exécuter
        *args: Arguments positionnels
        default: Valeur de retour en cas d'erreur
        titre: Titre pour le logging
        log_error: Si True, log l'erreur
        **kwargs: Arguments nommés

    Usage:
        count = safe_call(service.get_count, default=0)
        data = safe_call(fetch_data, url, default=[], titre="Fetch API")
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.warning(f"{titre}: {type(e).__name__}: {e}")
        return default


def try_render(
    render_fn: Callable[[], None],
    fallback_message: str = "Contenu indisponible",
) -> None:
    """Helper pour rendu avec fallback simple.

    Usage:
        try_render(
            render_fn=lambda: afficher_graphique(data),
            fallback_message="Graphique non disponible"
        )
    """
    with error_boundary(
        fallback_message,
        fallback_ui=lambda: st.info(f"ℹ️ {fallback_message}"),
        niveau="warning",
    ):
        render_fn()


__all__ = [
    "error_boundary",
    "ErrorBoundaryContext",
    "avec_gestion_erreurs_ui",
    "safe_call",
    "try_render",
]
