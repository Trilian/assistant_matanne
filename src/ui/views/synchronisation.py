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


__all__ = [
    "afficher_indicateur_presence",
    "afficher_indicateur_frappe",
    "afficher_statut_synchronisation",
]
