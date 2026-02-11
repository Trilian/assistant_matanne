"""
Interface Streamlit pour la synchronisation des calendriers externes.

Fonctionnalités:
- Export vers iCal
- Import depuis URL iCal
- Connexion Google Calendar
"""

from datetime import date, timedelta

import streamlit as st

from src.services.calendrier import get_calendar_sync_service


def render_calendar_sync_ui():
    """Interface Streamlit pour la synchronisation des calendriers."""
    st.subheader("📅 Synchronisation Calendriers")
    
    service = get_calendar_sync_service()
    
    # Tabs pour les différentes options
    tab1, tab2, tab3 = st.tabs(["📤 Exporter", "📥 Importer", "🔗 Connecter"])
    
    with tab1:
        _render_export_tab(service)
    
    with tab2:
        _render_import_tab(service)
    
    with tab3:
        _render_connect_tab(service)


def _render_export_tab(service):
    """Onglet d'export iCal."""
    st.markdown("### Exporter vers iCal")
    st.info("Téléchargez vos repas et activités au format iCal pour les importer dans votre application de calendrier préférée.")
    
    col1, col2 = st.columns(2)
    with col1:
        include_meals = st.checkbox("Inclure les repas", value=True, key="export_meals")
    with col2:
        include_activities = st.checkbox("Inclure les activités", value=True, key="export_activities")
    
    days_ahead = st.slider("Période (jours)", 7, 90, 30, key="export_days")
    
    if st.button("📥 Générer le fichier iCal", type="primary"):
        from src.services.utilisateur import get_auth_service
        auth = get_auth_service()
        user = auth.get_current_user()
        user_id = user.id if user else "anonymous"
        
        ical_content = service.export_to_ical(
            user_id=user_id,
            end_date=date.today() + timedelta(days=days_ahead),
            include_meals=include_meals,
            include_activities=include_activities,
        )
        
        if ical_content:
            st.download_button(
                label="💾 Télécharger le fichier .ics",
                data=ical_content,
                file_name="assistant_matanne_calendar.ics",
                mime="text/calendar",
            )
            st.success("✅ Fichier généré avec succès!")


def _render_import_tab(service):
    """Onglet d'import iCal."""
    st.markdown("### Importer depuis une URL iCal")
    st.info("Importez des événements depuis un calendrier partagé (Google Calendar, iCloud, etc.)")
    
    ical_url = st.text_input(
        "URL du calendrier iCal",
        placeholder="https://calendar.google.com/calendar/ical/...",
        key="import_ical_url"
    )
    
    calendar_name = st.text_input(
        "Nom du calendrier",
        value="Calendrier importé",
        key="import_calendar_name"
    )
    
    if st.button("📤 Importer", type="primary") and ical_url:
        from src.services.utilisateur import get_auth_service
        auth = get_auth_service()
        user = auth.get_current_user()
        user_id = user.id if user else "anonymous"
        
        with st.spinner("Import en cours..."):
            result = service.import_from_ical_url(
                user_id=user_id,
                ical_url=ical_url,
                calendar_name=calendar_name,
            )
        
        if result and result.success:
            st.success(f"✅ {result.message}")
        else:
            st.error(f"❌ {result.message if result else 'Erreur inconnue'}")


def _render_connect_tab(service):
    """Onglet de connexion des calendriers."""
    st.markdown("### Connecter un calendrier")
    
    st.markdown("#### Google Calendar")
    st.caption("Synchronisez automatiquement avec votre Google Calendar")
    
    from src.core.config import obtenir_parametres
    params = obtenir_parametres()
    
    if getattr(params, 'GOOGLE_CLIENT_ID', None):
        if st.button("🔗 Connecter Google Calendar", key="connect_google"):
            # Générer l'URL d'auth
            auth_url = service.get_google_auth_url(
                user_id="current_user",
                redirect_uri="http://localhost:8501/callback"
            )
            st.markdown(f"[Cliquez ici pour autoriser]({auth_url})")
    else:
        st.warning("Google Calendar non configuré (GOOGLE_CLIENT_ID manquant)")
    
    st.markdown("---")
    st.markdown("#### Apple iCloud Calendar")
    st.caption("Utilisez l'URL de partage iCal de votre calendrier iCloud")
    st.info("Dans iCloud Calendar: Partager → Calendrier public → Copier le lien")
