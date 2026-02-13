"""
Gestion des notifications - Onglet notifications de l'inventaire.
Affiche et gère les notifications d'alerte.
"""

import streamlit as st

from src.services.inventaire import get_inventaire_service
from src.services.notifications import obtenir_service_notifications_inventaire

# Alias pour rétrocompatibilité
obtenir_service_notifications = obtenir_service_notifications_inventaire


def render_notifications_widget():
    """Widget affichant les notifications actives (à utiliser en sidebar)"""
    service_notifs = obtenir_service_notifications()
    notifs = service_notifs.obtenir_notifications(non_lues_seulement=True)

    if not notifs:
        return

    # Affiche le badge de notification
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.metric("ðŸ”” Notifications", len(notifs), delta="À traiter")

    with col2:
        if st.button("ðŸ”„ Actualiser", key="refresh_notifs", width="stretch"):
            st.rerun()

    with col3:
        if st.button("⏰ Tout lire", key="mark_all_read", width="stretch"):
            for notif in notifs:
                service_notifs.marquer_lue(notif.id)
            st.rerun()

    # Affiche les notifications groupées par priorité
    st.divider()

    # Critiques
    critiques = [n for n in notifs if n.priorite == "haute"]
    if critiques:
        st.markdown("### ðŸš¨ CRITIQUES")
        for notif in critiques:
            with st.container(border=True):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(f"**{notif.icone} {notif.titre}**")
                    st.caption(notif.message)
                with col2:
                    if st.button("âœ“", key=f"mark_read_{notif.id}", help="Marquer comme lu"):
                        service_notifs.marquer_lue(notif.id)
                        st.rerun()

    # Moyennes
    moyennes = [n for n in notifs if n.priorite == "moyenne"]
    if moyennes:
        st.markdown("### âš ï¸ MOYENNES")
        for notif in moyennes[:3]:  # Affiche seulement les 3 premières
            with st.container(border=True):
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    st.write(f"**{notif.icone} {notif.titre}**")
                    st.caption(notif.message)
                with col2:
                    if st.button("âœ“", key=f"mark_read_{notif.id}", help="Marquer comme lu"):
                        service_notifs.marquer_lue(notif.id)
                        st.rerun()

        if len(moyennes) > 3:
            st.caption(f"... et {len(moyennes) - 3} autres")


def render_notifications():
    """Gestion et affichage des notifications d'alerte"""
    st.subheader("ðŸ”” Notifications et Alertes")

    service = get_inventaire_service()
    service_notifs = obtenir_service_notifications()

    # Onglets
    tab_center, tab_config = st.tabs(["ðŸ“¬ Centre de notifications", "âš™ï¸ Configuration"])

    with tab_center:
        # Actualiser les notifications
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            if st.button("ðŸ”„ Actualiser les alertes", width="stretch", key="refresh_all_alerts"):
                try:
                    stats = service.generer_notifications_alertes()
                    total = sum(len(v) for v in stats.values())
                    st.toast(f"⏰ {total} alertes détectées", icon="ðŸ””")
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")

        with col2:
            stats_notifs = service_notifs.obtenir_stats()
            st.metric("ðŸ“¬ Non lues", stats_notifs["non_lues"])

        with col3:
            if st.button("⏰ Tout marquer comme lu", width="stretch"):
                service_notifs.effacer_toutes_lues()
                st.toast("⏰ Notifications marquées comme lues")
                st.rerun()

        st.divider()

        # Affiche les notifications groupées
        notifs = service_notifs.obtenir_notifications()

        if not notifs:
            st.info("⏰ Aucune notification pour le moment")
        else:
            # Grouper par priorité
            critiques = [n for n in notifs if n.priorite == "haute"]
            moyennes = [n for n in notifs if n.priorite == "moyenne"]
            basses = [n for n in notifs if n.priorite == "basse"]

            # Affiche les critiques
            if critiques:
                st.markdown("### ðŸš¨ Alertes Critiques")
                for notif in critiques:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"**{notif.icone} {notif.titre}**")
                            st.write(notif.message)
                            st.caption(
                                f"{'⏰ Lue' if notif.lue else 'ðŸ“Œ Non lue'} • {notif.date_creation.strftime('%d/%m %H:%M')}"
                            )
                        with col2:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button(
                                    "âœ“",
                                    key=f"mark_{notif.id}",
                                    help="Marquer comme lu",
                                    width="stretch",
                                ):
                                    service_notifs.marquer_lue(notif.id)
                                    st.rerun()
                            with col_b:
                                if st.button(
                                    "ðŸ—‘ï¸",
                                    key=f"delete_{notif.id}",
                                    help="Supprimer",
                                    width="stretch",
                                ):
                                    service_notifs.supprimer_notification(notif.id)
                                    st.rerun()

            # Affiche les moyennes
            if moyennes:
                st.markdown("### âš ï¸ Alertes Moyennes")
                for notif in moyennes:
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"**{notif.icone} {notif.titre}**")
                            st.write(notif.message)
                            st.caption(
                                f"{'⏰ Lue' if notif.lue else 'ðŸ“Œ Non lue'} • {notif.date_creation.strftime('%d/%m %H:%M')}"
                            )
                        with col2:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button(
                                    "âœ“",
                                    key=f"mark_{notif.id}",
                                    help="Marquer comme lu",
                                    width="stretch",
                                ):
                                    service_notifs.marquer_lue(notif.id)
                                    st.rerun()
                            with col_b:
                                if st.button(
                                    "ðŸ—‘ï¸",
                                    key=f"delete_{notif.id}",
                                    help="Supprimer",
                                    width="stretch",
                                ):
                                    service_notifs.supprimer_notification(notif.id)
                                    st.rerun()

            # Affiche les basses
            if basses:
                st.markdown("### â„¹ï¸ Informations")
                for notif in basses[:5]:  # Limit to 5
                    with st.container(border=True):
                        col1, col2 = st.columns([0.85, 0.15])
                        with col1:
                            st.write(f"**{notif.icone} {notif.titre}**")
                            st.write(notif.message)
                            st.caption(
                                f"{'⏰ Lue' if notif.lue else 'ðŸ“Œ Non lue'} • {notif.date_creation.strftime('%d/%m %H:%M')}"
                            )
                        with col2:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button(
                                    "âœ“",
                                    key=f"mark_{notif.id}",
                                    help="Marquer comme lu",
                                    width="stretch",
                                ):
                                    service_notifs.marquer_lue(notif.id)
                                    st.rerun()
                            with col_b:
                                if st.button(
                                    "ðŸ—‘ï¸",
                                    key=f"delete_{notif.id}",
                                    help="Supprimer",
                                    width="stretch",
                                ):
                                    service_notifs.supprimer_notification(notif.id)
                                    st.rerun()

                if len(basses) > 5:
                    st.caption(f"... et {len(basses) - 5} autres informations")

    with tab_config:
        st.write("**Configuration des notifications**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ðŸ”” Alertes actives")
            enable_stock = st.checkbox("Stock critique", value=True, key="alert_stock_crit")
            enable_stock_bas = st.checkbox("Stock bas", value=True, key="alert_stock_bas")
            enable_peremption = st.checkbox("Péremption", value=True, key="alert_peremption")

        with col2:
            st.markdown("### ðŸ“¤ Canaux")
            browser_notif = st.checkbox(
                "Notifications navigateur", value=True, help="Popup dans le navigateur"
            )
            email_notif = st.checkbox("Email (bientôt)", value=False, disabled=True)
            slack_notif = st.checkbox("Slack (bientôt)", value=False, disabled=True)

        st.divider()

        # Bouton pour générer les alertes
        if st.button("ðŸ”„ Générer les alertes maintenant", width="stretch", type="primary"):
            try:
                stats = service.generer_notifications_alertes()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("âŒ Critique", len(stats["stock_critique"]))
                with col2:
                    st.metric("âš  Bas", len(stats["stock_bas"]))
                with col3:
                    st.metric("â° Péremption", len(stats["peremption_proche"]))
                with col4:
                    st.metric("ðŸš¨ Expirés", len(stats["peremption_depassee"]))

                st.toast(f"⏰ {sum(len(v) for v in stats.values())} alertes créées", icon="ðŸ””")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")


__all__ = ["render_notifications", "render_notifications_widget"]
