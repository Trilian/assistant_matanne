"""
Interface UI pour le module jeux (paris sportifs, loto).

Note: Ce fichier a été extrait depuis src/services/jeux/notification_service.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.jeux import (
    NotificationJeux,
    NotificationJeuxService,
    get_notification_jeux_service,
)
from src.ui.tokens import Couleur
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html


def afficher_badge_notifications_jeux(service: NotificationJeuxService | None = None) -> None:
    """Affiche un badge avec le nombre de notifications non lues."""
    if service is None:
        service = get_notification_jeux_service()

    non_lues = service.compter_non_lues()
    if non_lues > 0:
        st.markdown(
            f"""
            <span style="background-color: {Couleur.NOTIFICATIONS_BADGE}; color: {Sem.ON_INTERACTIVE};
                         padding: 2px 8px; border-radius: 10px;
                         font-size: 12px; font-weight: bold;">
                {echapper_html(str(non_lues))}
            </span>
            """,
            unsafe_allow_html=True,
        )


def afficher_notification_jeux(notification: NotificationJeux) -> None:
    """Affiche une notification dans l'UI."""
    with st.container():
        col1, col2 = st.columns([1, 10])

        with col1:
            st.markdown(f"### {notification.icone}")

        with col2:
            titre_style = "font-weight: normal;" if notification.lue else "font-weight: bold;"
            st.markdown(
                f"<span style='{titre_style}'>{echapper_html(notification.titre)}</span>",
                unsafe_allow_html=True,
            )
            st.caption(notification.message)
            st.caption(f"🕐 {notification.cree_le.strftime('%H:%M %d/%m')}")


def afficher_liste_notifications_jeux(
    service: NotificationJeuxService | None = None,
    limite: int = 10,
    type_jeu: str | None = None,
) -> None:
    """Affiche la liste des notifications."""
    if service is None:
        service = get_notification_jeux_service()

    notifications = service.notifications

    if type_jeu:
        notifications = [n for n in notifications if n.type_jeu == type_jeu]

    notifications = notifications[:limite]

    if not notifications:
        st.info("Aucune notification")
        return

    for notif in notifications:
        afficher_notification_jeux(notif)
        st.divider()


# Alias rétrocompatibilité
afficher_badge_notifications = afficher_badge_notifications_jeux
afficher_notification = afficher_notification_jeux
afficher_liste_notifications = afficher_liste_notifications_jeux


__all__ = [
    "afficher_badge_notifications_jeux",
    "afficher_notification_jeux",
    "afficher_liste_notifications_jeux",
    # Alias rétrocompatibilité
    "afficher_badge_notifications",
    "afficher_notification",
    "afficher_liste_notifications",
]
