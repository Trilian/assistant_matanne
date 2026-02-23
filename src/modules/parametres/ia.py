"""
Paramètres - Configuration IA
Gestion du service d'intelligence artificielle Mistral
"""

import streamlit as st

from src.core.ai.cache import CacheIA as SemanticCache
from src.core.config import obtenir_parametres as get_settings
from src.core.state import obtenir_etat
from src.ui.feedback import afficher_succes
from src.ui.fragments import ui_fragment


@ui_fragment
def afficher_ia_config():
    """Configuration IA"""

    st.markdown("### 🤖 Configuration IA")
    st.caption("Paramètres du service d'intelligence artificielle")

    settings = get_settings()

    # Infos modèle
    st.markdown("#### Modèle Actuel")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Modèle:** {settings.MISTRAL_MODEL}")
        st.info("**Provider:** Mistral AI")

    with col2:
        st.info("**Temperature:** 0.7 (defaut)")
        st.info("**Max Tokens:** 1000 (defaut)")

    st.markdown("---")

    # Rate Limiting
    st.markdown("#### ⚡ Rate Limiting")

    col3, col4 = st.columns(2)

    with col3:
        st.metric("Limite Quotidienne", f"{settings.RATE_LIMIT_DAILY} appels/jour")

    with col4:
        st.metric("Limite Horaire", f"{settings.RATE_LIMIT_HOURLY} appels/heure")

    # Utilisation actuelle
    _state = obtenir_etat()

    if "rate_limit" in st.session_state:
        rate_info = st.session_state.rate_limit

        st.markdown("**Utilisation Actuelle:**")

        col5, col6 = st.columns(2)

        with col5:
            calls_today = rate_info.get("calls_today", 0)
            progress_day = calls_today / settings.RATE_LIMIT_DAILY

            st.progress(progress_day)
            st.caption(f"{calls_today}/{settings.RATE_LIMIT_DAILY} appels aujourd'hui")

        with col6:
            calls_hour = rate_info.get("calls_hour", 0)
            progress_hour = calls_hour / settings.RATE_LIMIT_HOURLY

            st.progress(progress_hour)
            st.caption(f"{calls_hour}/{settings.RATE_LIMIT_HOURLY} appels cette heure")

    st.markdown("---")

    # Cache Semantique
    st.markdown("#### 🧠 Cache Sémantique")

    cache_stats = SemanticCache.obtenir_statistiques()

    col7, col8, col9 = st.columns(3)

    with col7:
        st.metric(
            "Taux de Hit",
            f"{cache_stats.get('taux_hit', 0):.1f}%",
            help="Pourcentage de reponses servies depuis le cache",
        )

    with col8:
        st.metric("Entrees Cachees", cache_stats.get("entrees_ia", 0))

    with col9:
        st.metric("Appels Économises", cache_stats.get("saved_api_calls", 0))

    mode = "🔑 Hachage MD5"
    st.info(f"**Mode:** {mode} (correspondance exacte des prompts)")

    # Actions cache IA
    col10, col11 = st.columns(2)

    with col10:
        if st.button("🗑️ Vider Cache IA", key="btn_clear_semantic_cache", use_container_width=True):
            SemanticCache.invalider_tout()
            afficher_succes("Cache IA vidé !")

    with col11:
        if st.button("📊 Détails Cache", key="btn_cache_details", use_container_width=True):
            with st.expander("📈 Statistiques Détaillées", expanded=True):
                st.json(cache_stats)
