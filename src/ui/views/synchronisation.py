"""
Interface UI pour la synchronisation temps réel et PWA.

Note: Ce fichier a été extrait depuis src/services/web/synchronisation.py et pwa.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.integrations.web.synchronisation import get_realtime_sync_service
from src.ui.tokens_semantic import Sem
from src.ui.utils import echapper_html


def afficher_indicateur_presence():
    """Affiche les utilisateurs connectés sur la liste."""
    sync = get_realtime_sync_service()
    users = sync.get_connected_users()

    if not users:
        return

    st.markdown("---")
    st.markdown("**👥 Connectés:**")

    cols = st.columns(min(len(users), 5))
    for i, user in enumerate(users[:5]):
        with cols[i]:
            # Avatar avec initiales
            initials = "".join([w[0].upper() for w in user.user_name.split()[:2]])
            st.markdown(
                f"""
                <div style="text-align: center;" role="listitem" aria-label="{echapper_html(user.user_name)} connecté">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, {Sem.INFO} 0%, {Sem.INTERACTIVE} 100%);
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        color: {Sem.ON_INTERACTIVE};
                        font-weight: bold;
                        font-size: 14px;
                    " aria-hidden="true">{echapper_html(initials)}</div>
                    <div style="font-size: 11px; margin-top: 4px;">{echapper_html(user.user_name)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if len(users) > 5:
        st.caption(f"... et {len(users) - 5} autre(s)")


def afficher_indicateur_frappe():
    """Affiche les indicateurs de frappe."""
    sync = get_realtime_sync_service()

    typing_users = [
        u
        for u in sync.get_connected_users()
        if u.is_typing and u.user_id != sync._get_current_user_id()
    ]

    if typing_users:
        names = ", ".join([u.user_name for u in typing_users[:3]])
        verb = "écrit" if len(typing_users) == 1 else "écrivent"
        st.caption(f"✏️ {names} {verb}...")


def afficher_statut_synchronisation():
    """Affiche le statut de synchronisation."""
    sync = get_realtime_sync_service()

    if sync.state.connected:
        users_count = len(sync.get_connected_users())
        st.success(f"🔄 Synchronisé • {users_count} connecté(s)")
    elif sync.state.pending_events:
        st.warning(f"⏳ {len(sync.state.pending_events)} modification(s) en attente")
    else:
        st.info("📴 Mode hors ligne")


def afficher_resolution_conflits():
    """Affiche l'interface de résolution de conflits de synchronisation.

    Permet à l'utilisateur de choisir quelle version garder
    quand deux modifications simultanées créent un conflit.
    """
    sync = get_realtime_sync_service()

    if sync.state.conflict_count == 0:
        return

    with st.expander(
        f"⚠️ {sync.state.conflict_count} conflit(s) détecté(s)", expanded=True
    ):
        st.markdown(
            "Des modifications simultanées ont été détectées. "
            "Choisissez la version à conserver."
        )

        pending = sync.state.pending_events
        conflicting = [e for e in pending if e.data.get("is_conflict")]

        for i, event in enumerate(conflicting):
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])

                item_name = event.data.get("nom", "Article inconnu")
                with col1:
                    st.markdown(f"**{item_name}**")
                    st.caption(
                        f"Modifié par {echapper_html(event.user_name)} "
                        f"à {event.timestamp.strftime('%H:%M')}"
                    )

                with col2:
                    if st.button(
                        "✅ Garder distant",
                        key=f"resolve_remote_{i}",
                    ):
                        sync.resolve_conflict(event, keep="remote")
                        st.rerun()

                with col3:
                    if st.button(
                        "🏠 Garder local",
                        key=f"resolve_local_{i}",
                    ):
                        sync.resolve_conflict(event, keep="local")
                        st.rerun()

        if st.button("🔄 Tout accepter (distant)", key="resolve_all"):
            for event in conflicting:
                sync.resolve_conflict(event, keep="remote")
            st.rerun()


def afficher_panneau_collaboratif():
    """Panneau complet de collaboration pour la sidebar.

    Combine statut, présence, frappe et conflits en un seul composant.
    À intégrer dans la sidebar du module courses.
    """
    sync = get_realtime_sync_service()

    if not sync.is_configured:
        return

    with st.sidebar:
        st.divider()
        st.markdown("### 👥 Mode Collaboratif")

        afficher_statut_synchronisation()
        afficher_indicateur_presence()
        afficher_indicateur_frappe()
        afficher_resolution_conflits()


__all__ = [
    "afficher_indicateur_presence",
    "afficher_indicateur_frappe",
    "afficher_statut_synchronisation",
    "afficher_resolution_conflits",
    "afficher_panneau_collaboratif",
]
