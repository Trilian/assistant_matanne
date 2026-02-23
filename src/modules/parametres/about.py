"""
Paramètres - À Propos
Informations sur l'application et l'environnement
"""

import streamlit as st

from src.core.config import obtenir_parametres as get_settings
from src.core.state import GestionnaireEtat
from src.ui.fragments import ui_fragment


@ui_fragment
def afficher_about():
    """Informations sur l'application"""

    settings = get_settings()

    # Header avec logo/titre
    col_logo, col_info = st.columns([1, 3])

    with col_logo:
        st.markdown("# 🏠")

    with col_info:
        st.markdown(f"## {settings.APP_NAME}")
        st.caption(f"Version {settings.APP_VERSION}")

    st.markdown("---")

    # Description
    st.markdown("#### 📋 Description")
    st.markdown("""
Assistant familial intelligent pour gérer le quotidien :
- 🍳 **Recettes** et planning des repas
- 📦 **Inventaire** alimentaire
- 🛒 **Listes** de courses
- 📅 **Planning** hebdomadaire
- 👶 **Suivi** de Jules
- 💪 **Santé** et bien-être
""")

    st.markdown("---")

    # Stack technique en colonnes
    st.markdown("#### 🛠️ Stack Technique")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Frontend", "Streamlit", delta=None)
    with col2:
        st.metric("Database", "Supabase", delta=None)
    with col3:
        st.metric("IA", "Mistral AI", delta=None)
    with col4:
        lazy_status = "✅ Actif" if True else "❌"
        st.metric("Lazy Loading", lazy_status, delta=None)

    st.markdown("---")

    # Environnement
    st.markdown("#### 💻 Environnement")

    col1, col2 = st.columns(2)

    with col1:
        env_color = "🟢" if settings.ENV == "production" else "🟡"
        st.markdown(f"{env_color} **Mode:** {settings.ENV}")
        debug_icon = "🔧" if settings.DEBUG else "🔒"
        st.markdown(f"{debug_icon} **Debug:** {'Activé' if settings.DEBUG else 'Désactivé'}")

    with col2:
        db_ok = settings._verifier_db_configuree()
        ai_ok = settings._verifier_mistral_configure()
        st.markdown(f"{'✅' if db_ok else '❌'} **Base de données**")
        st.markdown(f"{'✅' if ai_ok else '❌'} **IA Mistral**")

    st.markdown("---")

    # Configuration (collapsible)
    with st.expander("🔐 Configuration (sans secrets)"):
        safe_config = settings.obtenir_config_publique()
        st.json(safe_config)

    # État système (collapsible)
    state_summary = GestionnaireEtat.obtenir_resume_etat()

    with st.expander("⚙️ État Système"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Module:** {state_summary.get('module_actuel', '—')}")
            st.markdown(f"**Utilisateur:** {state_summary.get('nom_utilisateur', '—')}")
            st.markdown(f"**Cache:** {'✅' if state_summary.get('cache_active') else '❌'}")
        with col2:
            st.markdown(f"**IA:** {'✅' if state_summary.get('ia_disponible') else '❌'}")
            st.markdown(f"**Debug:** {'✅' if state_summary.get('mode_debug') else '❌'}")
            notifs = state_summary.get("notifications_non_lues", 0)
            st.markdown(f"**Notifications:** {notifs}")
