"""
Interface UI pour la synchronisation temps réel et PWA.

Note: Ce fichier a été extrait depuis src/services/web/synchronisation.py et pwa.py
pour respecter la séparation UI/Services.
"""

import streamlit as st
import streamlit.components.v1 as components

from src.services.web.synchronisation import get_realtime_sync_service


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
                <div style="text-align: center;">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                    ">{initials}</div>
                    <div style="font-size: 11px; margin-top: 4px;">{user.user_name}</div>
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


def afficher_invite_installation_pwa():
    """Affiche un bouton d'installation PWA si disponible."""
    install_script = """
    <div id="pwa-install-container" style="display: none;">
        <button id="pwa-install-btn" onclick="installPWA()" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            📲 Installer l'application
        </button>
    </div>

    <script>
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('pwa-install-container').style.display = 'block';
        });

        async function installPWA() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('Install outcome:', outcome);
                deferredPrompt = null;
                document.getElementById('pwa-install-container').style.display = 'none';
            }
        }
    </script>
    """

    components.html(install_script, height=60)


# Alias rétrocompatibilité
render_presence_indicator = afficher_indicateur_presence
render_typing_indicator = afficher_indicateur_frappe
render_sync_status = afficher_statut_synchronisation
render_install_prompt = afficher_invite_installation_pwa


__all__ = [
    "afficher_indicateur_presence",
    "afficher_indicateur_frappe",
    "afficher_statut_synchronisation",
    "afficher_invite_installation_pwa",
    # Alias rétrocompatibilité
    "render_presence_indicator",
    "render_typing_indicator",
    "render_sync_status",
    "render_install_prompt",
]
