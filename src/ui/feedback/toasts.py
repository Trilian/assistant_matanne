"""
UI Feedback - Notifications
"""

from datetime import datetime, timedelta

import streamlit as st


class GestionnaireNotifications:
    """
    Gestionnaire de notifications

    Affiche des notifications temporaires

    Usage:
        GestionnaireNotifications.afficher("Sauvegarde réussie", "success", duree=3)
        GestionnaireNotifications.rendre()  # À appeler dans le main
    """

    CLE_NOTIFICATIONS = "notifications"

    @staticmethod
    def _init():
        if GestionnaireNotifications.CLE_NOTIFICATIONS not in st.session_state:
            st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = []

    @staticmethod
    def afficher(message: str, type: str = "info", duree: int = 3):
        """
        Affiche une notification

        Args:
            message: Message
            type: "success", "error", "warning", "info"
            duree: Durée en secondes
        """
        GestionnaireNotifications._init()

        notification = {
            "message": message,
            "type": type,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=duree),
        }

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS].append(notification)

    @staticmethod
    def rendre():
        """Affiche les notifications actives"""
        GestionnaireNotifications._init()

        notifications = st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS]
        maintenant = datetime.now()

        # Filtrer expirées
        notifications_actives = [n for n in notifications if n["expires_at"] > maintenant]

        st.session_state[GestionnaireNotifications.CLE_NOTIFICATIONS] = notifications_actives

        # Afficher (max 3)
        if notifications_actives:
            conteneur = st.container()

            with conteneur:
                for notification in notifications_actives[-3:]:
                    type_map = {
                        "success": st.success,
                        "error": st.error,
                        "warning": st.warning,
                        "info": st.info,
                    }

                    func_affichage = type_map.get(notification["type"], st.info)
                    func_affichage(notification["message"])


# ═══════════════════════════════════════════════════════════
# HELPERS RACCOURCIS
# ═══════════════════════════════════════════════════════════


def afficher_succes(message: str, duree: int = 3):
    """Raccourci pour notification succès"""
    GestionnaireNotifications.afficher(message, "success", duree)


def afficher_erreur(message: str, duree: int = 5):
    """Raccourci pour notification erreur"""
    GestionnaireNotifications.afficher(message, "error", duree)


def afficher_avertissement(message: str, duree: int = 4):
    """Raccourci pour notification avertissement"""
    GestionnaireNotifications.afficher(message, "warning", duree)


def afficher_info(message: str, duree: int = 3):
    """Raccourci pour notification info"""
    GestionnaireNotifications.afficher(message, "info", duree)
