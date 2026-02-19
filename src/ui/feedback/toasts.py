"""
UI Feedback - Notifications
"""

import streamlit as st


class GestionnaireNotifications:
    """
    Gestionnaire de notifications

    Affiche des notifications via les fonctions Streamlit natives.
    Les notifications persistent jusqu'au prochain rerun de l'application.

    Usage:
        GestionnaireNotifications.afficher("Sauvegarde réussie", "success")
        # Ou via les raccourcis:
        afficher_succes("Sauvegarde réussie")
    """

    @staticmethod
    def afficher(message: str, type_notif: str = "info"):
        """
        Affiche une notification immédiate.

        Args:
            message: Message
            type_notif: "success", "error", "warning", "info"
        """
        type_map = {
            "success": st.success,
            "error": st.error,
            "warning": st.warning,
            "info": st.info,
        }
        func_affichage = type_map.get(type_notif, st.info)
        func_affichage(message)


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


def afficher_succes(message: str, duree: int = 3):
    """Raccourci pour notification succès"""
    GestionnaireNotifications.afficher(message, "success")


def afficher_erreur(message: str, duree: int = 5):
    """Raccourci pour notification erreur"""
    GestionnaireNotifications.afficher(message, "error")


def afficher_avertissement(message: str, duree: int = 4):
    """Raccourci pour notification avertissement"""
    GestionnaireNotifications.afficher(message, "warning")


def afficher_info(message: str, duree: int = 3):
    """Raccourci pour notification info"""
    GestionnaireNotifications.afficher(message, "info")
