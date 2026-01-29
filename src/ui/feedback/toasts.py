"""
UI Feedback - Toast notifications
"""

from datetime import datetime, timedelta

import streamlit as st


class ToastManager:
    """
    Gestionnaire de notifications toast

    Affiche des notifications temporaires

    Usage:
        ToastManager.show("Sauvegarde réussie", "success", duration=3)
        ToastManager.render()  # À appeler dans le main
    """

    TOAST_KEY = "toast_notifications"

    @staticmethod
    def _init():
        if ToastManager.TOAST_KEY not in st.session_state:
            st.session_state[ToastManager.TOAST_KEY] = []

    @staticmethod
    def show(message: str, type: str = "info", duration: int = 3):
        """
        Affiche une notification toast

        Args:
            message: Message
            type: "success", "error", "warning", "info"
            duration: Durée en secondes
        """
        ToastManager._init()

        toast = {
            "message": message,
            "type": type,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=duration),
        }

        st.session_state[ToastManager.TOAST_KEY].append(toast)

    @staticmethod
    def render():
        """Affiche les toasts actifs"""
        ToastManager._init()

        toasts = st.session_state[ToastManager.TOAST_KEY]
        now = datetime.now()

        # Filtrer expirés
        active_toasts = [toast for toast in toasts if toast["expires_at"] > now]

        st.session_state[ToastManager.TOAST_KEY] = active_toasts

        # Afficher (max 3)
        if active_toasts:
            toast_container = st.container()

            with toast_container:
                for toast in active_toasts[-3:]:
                    type_map = {
                        "success": st.success,
                        "error": st.error,
                        "warning": st.warning,
                        "info": st.info,
                    }

                    display_func = type_map.get(toast["type"], st.info)
                    display_func(toast["message"])


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


def show_success(message: str, duration: int = 3):
    """Raccourci pour toast success"""
    ToastManager.show(message, "success", duration)


def show_error(message: str, duration: int = 5):
    """Raccourci pour toast error"""
    ToastManager.show(message, "error", duration)


def show_warning(message: str, duration: int = 4):
    """Raccourci pour toast warning"""
    ToastManager.show(message, "warning", duration)


def show_info(message: str, duration: int = 3):
    """Raccourci pour toast info"""
    ToastManager.show(message, "info", duration)
