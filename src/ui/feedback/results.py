"""
Result → Streamlit — Affichage de Result[T, E] dans l'interface.

Pont entre le pattern Result (couche service) et le feedback Streamlit (couche UI).
Permet aux modules d'afficher le résultat d'une opération sans inspecter
manuellement Success/Failure.

Usage:
    from src.ui.feedback.results import afficher_resultat

    result = service.creer_recette(data)
    valeur = afficher_resultat(result, succes_msg="Recette créée !")
    if valeur is not None:
        st.write(valeur)
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


def afficher_resultat(
    result: Any,
    succes_msg: str = "Opération réussie",
    erreur_msg: str = "",
    afficher_details: bool = False,
) -> Any | None:
    """Affiche un ``Result`` dans l'interface Streamlit.

    - ``Success`` → ``st.success`` + retourne la valeur
    - ``Failure`` → ``st.error`` (+ détails optionnels) + retourne ``None``

    Compatible avec les ``Result[T, ErrorInfo]`` de
    ``src.services.core.base.result``.

    Args:
        result: Instance de ``Success`` ou ``Failure``
        succes_msg: Message affiché en cas de succès
        erreur_msg: Override du message d'erreur (sinon ``message_utilisateur``)
        afficher_details: Afficher les détails techniques en expander

    Returns:
        La valeur du ``Success``, ou ``None`` si ``Failure``

    Example:
        >>> result = service.creer_recette(data)
        >>> recette = afficher_resultat(result, succes_msg="Recette créée !")
    """
    if result.is_success:
        st.success(succes_msg)
        return result.value

    # Failure
    error = result.error
    if hasattr(error, "message_utilisateur"):
        msg = erreur_msg or error.message_utilisateur
        st.error(f"❌ {msg}")

        if afficher_details and hasattr(error, "code"):
            with st.expander("Détails techniques", expanded=False):
                st.code(
                    f"Code: {error.code.value}\nMessage: {error.message}\nSource: {error.source}"
                )
    else:
        st.error(f"❌ {erreur_msg or str(error)}")

    return None


def afficher_resultat_toast(
    result: Any,
    succes_msg: str = "Opération réussie",
) -> Any | None:
    """Version toast (non-bloquante) de ``afficher_resultat``.

    Utilise ``st.toast`` au lieu de ``st.success``/``st.error``.

    Args:
        result: Instance de ``Success`` ou ``Failure``
        succes_msg: Message affiché en cas de succès

    Returns:
        La valeur du ``Success``, ou ``None`` si ``Failure``
    """
    if result.is_success:
        st.toast(f"✅ {succes_msg}", icon="✅")
        return result.value

    error = result.error
    msg = getattr(error, "message_utilisateur", str(error))
    st.toast(f"❌ {msg}", icon="❌")
    return None


def result_ou_vide(result: Any, default: Any = None) -> Any:
    """Extrait la valeur du Result ou retourne un défaut (sans feedback UI).

    Utile dans les templates où on veut silencieusement ignorer les erreurs.

    Usage::
        recettes = result_ou_vide(service.lister(), default=[])
    """
    if result is not None and result.is_success:
        return result.value
    return default if default is not None else None


def result_ou_none(result: Any) -> Any | None:
    """Raccourci: extrait la valeur ou None (log l'erreur silencieusement).

    Usage::
        recette = result_ou_none(service.obtenir(42))
    """
    if result is not None and result.is_success:
        return result.value

    if result is not None and result.is_failure:
        error = result.error
        msg = getattr(error, "message", str(error))
        logger.debug(f"Result silencieux (None): {msg}")

    return None


def result_avec_spinner(
    fn: Any,
    message: str = "Chargement...",
    succes_msg: str = "",
) -> Any | None:
    """Exécute une fn retournant un Result avec un spinner Streamlit.

    Affiche automatiquement le spinner pendant l'exécution et le feedback
    résultat après.

    Usage::
        recette = result_avec_spinner(
            lambda: service.charger_recette(42),
            message="Chargement de la recette...",
            succes_msg="Recette chargée !"
        )

    Args:
        fn: Callable retournant un Result
        message: Message du spinner
        succes_msg: Message succès (si vide, pas de feedback succès)

    Returns:
        La valeur si succès, None sinon
    """
    with st.spinner(message):
        result = fn()

    if result is None:
        return None

    if result.is_success:
        if succes_msg:
            st.success(succes_msg)
        return result.value

    # Failure
    error = result.error
    msg = getattr(error, "message_utilisateur", str(error))
    st.error(f"❌ {msg}")
    return None


__all__ = [
    "afficher_resultat",
    "afficher_resultat_toast",
    "result_ou_vide",
    "result_ou_none",
    "result_avec_spinner",
]
