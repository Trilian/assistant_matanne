"""
Composant UI pour la synchronisation Google Calendar.

Interface utilisateur pour:
- Connecter son compte Google
- Importer les événements depuis Google
- Exporter le planning familial vers Google
"""

import logging
from datetime import datetime, timedelta

import streamlit as st

from src.core.config import obtenir_parametres
from src.services.famille.calendrier import (
    get_calendar_sync_service,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",  # Lecture + Écriture
    "https://www.googleapis.com/auth/calendar.events",
]

REDIRECT_URI_LOCAL = "http://localhost:8501/callback/google"


# ═══════════════════════════════════════════════════════════
# FONCTIONS UI
# ═══════════════════════════════════════════════════════════


def verifier_config_google() -> tuple[bool, str]:
    """Vérifie si la configuration Google est présente."""
    params = obtenir_parametres()

    client_id = getattr(params, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(params, "GOOGLE_CLIENT_SECRET", "")

    if not client_id:
        return False, "GOOGLE_CLIENT_ID non configuré dans .env.local"
    if not client_secret:
        return False, "GOOGLE_CLIENT_SECRET non configuré dans .env.local"

    return True, "Configuration OK"


def afficher_config_google_calendar():
    """Affiche le panneau de configuration Google Calendar."""

    st.markdown("### 📅 Google Calendar")

    # Vérifier la configuration
    config_ok, message = verifier_config_google()

    if not config_ok:
        st.warning(f"⚠️ {message}")

        with st.expander("ℹ️ Comment configurer Google Calendar"):
            st.markdown("""
            **Étapes pour activer Google Calendar:**

            1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
            2. Créez un nouveau projet ou sélectionnez-en un existant
            3. Activez l'API Google Calendar
            4. Allez dans "Identifiants" → "Créer des identifiants" → "ID client OAuth 2.0"
            5. Type d'application: "Application Web"
            6. Ajoutez `http://localhost:8501/callback/google` aux URIs de redirection autorisées
            7. Copiez le Client ID et Client Secret
            8. Ajoutez-les dans votre fichier `.env.local`:

            ```
            GOOGLE_CLIENT_ID=votre_client_id
            GOOGLE_CLIENT_SECRET=votre_client_secret
            ```

            9. Redémarrez l'application
            """)
        return

    # Configuration présente
    st.success("✅ Google Calendar configuré")

    # État de la connexion
    if "google_calendar_config" not in st.session_state:
        st.session_state.google_calendar_config = None

    config = st.session_state.google_calendar_config

    if config:
        # Connecté
        st.markdown(f"**Calendrier connecté:** {config.name}")
        st.caption(
            f"Dernière sync: {config.last_sync.strftime('%d/%m/%Y %H:%M') if config.last_sync else 'Jamais'}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Synchroniser", use_container_width=True):
                with st.spinner("Synchronisation en cours..."):
                    service = get_calendar_sync_service()
                    result = service.sync_google_calendar(config)

                    if result.success:
                        st.success(f"✅ {result.events_imported} événements importés")
                    else:
                        st.error(f"❌ {result.message}")

        with col2:
            if st.button("📤 Exporter vers Google", use_container_width=True):
                st.info("🚧 Export vers Google Calendar - En développement")

        with col3:
            if st.button("🔌 Déconnecter", use_container_width=True):
                st.session_state.google_calendar_config = None
                st.rerun()

    else:
        # Non connecté
        st.info("📅 Connectez votre Google Calendar pour synchroniser vos événements")

        if st.button("🔗 Connecter Google Calendar", type="primary"):
            # Générer l'URL d'auth
            service = get_calendar_sync_service()
            try:
                auth_url = service.get_google_auth_url(
                    user_id="default_user",
                    redirect_uri=REDIRECT_URI_LOCAL,
                )

                st.markdown(f"""
                **Cliquez sur le lien ci-dessous pour autoriser l'accès:**

                [🔗 Autoriser Google Calendar]({auth_url})

                Après autorisation, copiez le code fourni ci-dessous:
                """)

                # Champ pour le code
                auth_code = st.text_input(
                    "Code d'autorisation Google",
                    placeholder="4/0AY0e-g7...",
                    help="Collez le code reçu après avoir autorisé l'accès",
                )

                if auth_code and st.button("✅ Valider le code"):
                    with st.spinner("Connexion en cours..."):
                        config = service.handle_google_callback(
                            user_id="default_user",
                            code=auth_code,
                            redirect_uri=REDIRECT_URI_LOCAL,
                        )

                        if config:
                            st.session_state.google_calendar_config = config
                            st.success("✅ Google Calendar connecté!")
                            st.rerun()
                        else:
                            st.error("❌ Échec de la connexion")

            except ValueError as e:
                st.error(f"❌ {str(e)}")


def afficher_statut_sync_google():
    """Affiche le statut de synchronisation Google Calendar."""

    config = st.session_state.get("google_calendar_config")

    if not config:
        return

    # Calculer le temps depuis la dernière sync
    if config.last_sync:
        delta = datetime.now() - config.last_sync
        if delta < timedelta(minutes=5):
            st.success("🟢 Synchronisé à l'instant")
        elif delta < timedelta(hours=1):
            st.info(f"🟡 Synchronisé il y a {delta.seconds // 60} min")
        elif delta < timedelta(days=1):
            st.warning(f"🟠 Synchronisé il y a {delta.seconds // 3600}h")
        else:
            st.error(f"🔴 Dernière sync: {config.last_sync.strftime('%d/%m')}")


def afficher_bouton_sync_rapide():
    """Bouton de sync rapide Google Calendar pour la sidebar."""

    config = st.session_state.get("google_calendar_config")

    if config:
        if st.button("🔄 Sync Google", use_container_width=True):
            service = get_calendar_sync_service()
            result = service.sync_google_calendar(config)

            if result.success:
                st.toast(f"✅ {result.events_imported} événements synchronisés")
            else:
                st.toast(f"❌ Erreur sync: {result.message}")
