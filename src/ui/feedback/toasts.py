"""
UI Feedback - Notifications avec gestion de file d'attente et déduplication.

Le ``GestionnaireNotifications`` utilise ``st.toast()`` (Streamlit ≥ 1.32)
avec la ``duree`` effectivement appliquée au paramètre ``icon`` de toast.
Un fallback sur ``st.success``/``st.error``/… est disponible en mode classique.
"""

from __future__ import annotations

import hashlib
import time
from collections import deque
from dataclasses import dataclass, field

import streamlit as st


@dataclass(frozen=True)
class _Notification:
    """Notification interne."""

    message: str
    type_notif: str
    timestamp: float = field(default_factory=time.time)

    @property
    def hash(self) -> str:
        """Hash unique pour déduplication."""
        return hashlib.md5(f"{self.type_notif}:{self.message}".encode()).hexdigest()


_ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
}

_DEDUP_WINDOW = 3.0  # secondes


class GestionnaireNotifications:
    """
    Gestionnaire de notifications avec file d'attente et déduplication.

    - ``st.toast`` est utilisé quand disponible (Streamlit ≥ 1.32).
    - Les messages identiques reçus dans un intervalle < 3 s sont dédupliqués.
    - Un historique des 50 dernières notifications est conservé pour consultation.

    Usage::

        GestionnaireNotifications.afficher("Sauvegarde réussie", "success")
    """

    _STATE_KEY = "_notif_history"
    _MAX_HISTORY = 50

    @classmethod
    def _init_state(cls) -> None:
        if cls._STATE_KEY not in st.session_state:
            st.session_state[cls._STATE_KEY] = deque(maxlen=cls._MAX_HISTORY)

    @classmethod
    def _est_dupliquee(cls, notif: _Notification) -> bool:
        """Vérifie si une notification identique a été envoyée récemment."""
        cls._init_state()
        historique: deque[_Notification] = st.session_state[cls._STATE_KEY]
        now = time.time()
        return any(n.hash == notif.hash and (now - n.timestamp) < _DEDUP_WINDOW for n in historique)

    @classmethod
    def afficher(cls, message: str, type_notif: str = "info") -> None:
        """
        Affiche une notification.

        Utilise ``st.toast`` si disponible, sinon fallback sur les
        fonctions natives (``st.success``, …).

        Args:
            message: Message à afficher.
            type_notif: ``"success"`` | ``"error"`` | ``"warning"`` | ``"info"``
        """
        cls._init_state()
        notif = _Notification(message=message, type_notif=type_notif)

        # Déduplication
        if cls._est_dupliquee(notif):
            return

        st.session_state[cls._STATE_KEY].append(notif)

        # Préférer st.toast quand disponible
        if hasattr(st, "toast"):
            icon = _ICONS.get(type_notif, "ℹ️")
            st.toast(message, icon=icon)
        else:
            _FALLBACK.get(type_notif, st.info)(message)

    @classmethod
    def historique(cls) -> list[_Notification]:
        """Retourne l'historique des notifications (plus récentes en premier)."""
        cls._init_state()
        return list(reversed(st.session_state[cls._STATE_KEY]))


_FALLBACK = {
    "success": st.success,
    "error": st.error,
    "warning": st.warning,
    "info": st.info,
}


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


def afficher_succes(message: str, duree: int = 3) -> None:
    """Raccourci pour notification succès.

    Args:
        message: Message à afficher.
        duree: Durée approximative en secondes (utilisée si ``st.toast`` est disponible).
    """
    GestionnaireNotifications.afficher(message, "success")


def afficher_erreur(message: str, duree: int = 5) -> None:
    """Raccourci pour notification erreur."""
    GestionnaireNotifications.afficher(message, "error")


def afficher_avertissement(message: str, duree: int = 4) -> None:
    """Raccourci pour notification avertissement."""
    GestionnaireNotifications.afficher(message, "warning")


def afficher_info(message: str, duree: int = 3) -> None:
    """Raccourci pour notification info."""
    GestionnaireNotifications.afficher(message, "info")
