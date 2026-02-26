"""
Paramètres - Configuration Cache
Gestion du cache applicatif et cache IA
"""

import streamlit as st

from src.core.ai.cache import CacheIA as SemanticCache
from src.core.caching import obtenir_cache
from src.ui.feedback import afficher_succes
from src.ui.fragments import lazy, ui_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("param_cache")


@lazy(condition=lambda: st.session_state.get(_keys("show_details"), False), show_skeleton=True)
def _afficher_cache_details():
    """Détails du cache (chargé conditionnellement)."""
    from src.core.caching import obtenir_cache

    cache = obtenir_cache()
    stats = cache.obtenir_statistiques() if hasattr(cache, "obtenir_statistiques") else {}

    st.markdown("##### 📊 Statistiques détaillées")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taille mémoire", stats.get("taille_memoire", "N/A"))
    with col2:
        st.metric("Entrées L1", stats.get("entrees_l1", 0))
    with col3:
        st.metric("Entrées L2", stats.get("entrees_l2", 0))

    # Détails par niveau de cache
    with st.expander("🔍 Détails par niveau"):
        st.json(stats)


@ui_fragment
def afficher_cache_config():
    """Configuration cache"""

    st.markdown("### 💾 Gestion du Cache")
    st.caption("Cache applicatif et cache IA")

    # Cache applicatif
    st.markdown("#### 📦 Cache Applicatif")

    if _keys("data") in st.session_state:
        cache_size = len(st.session_state[_keys("data")])

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Entrees", cache_size)

        with col2:
            if _keys("stats") in st.session_state:
                stats = st.session_state[_keys("stats")]
                total = stats.get("hits", 0) + stats.get("misses", 0)
                hit_rate = (stats.get("hits", 0) / total * 100) if total > 0 else 0

                st.metric("Taux de Hit", f"{hit_rate:.1f}%")

            if st.button(
                "🗑️ Vider Cache Applicatif", key="btn_clear_cache_app", use_container_width=True
            ):
                obtenir_cache().clear()
                afficher_succes("Cache applicatif vidé !")

    else:
        st.info("Cache vide")

    st.markdown("---")

    # Cache IA
    st.markdown("#### 🤖 Cache IA")

    cache_stats = SemanticCache.obtenir_statistiques()

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Entrees", cache_stats.get("entrees_ia", 0))

    with col4:
        st.metric("Hits", cache_stats.get("entrees_ia", 0))

    with col5:
        st.metric("Misses", 0)

    if st.button("🗑️ Vider Cache IA", key="btn_clear_cache_ia", use_container_width=True):
        SemanticCache.invalider_tout()
        afficher_succes("Cache IA vidé !")

    st.markdown("---")

    # Section détails (lazy-loaded)
    show_details = st.checkbox(
        "📊 Afficher statistiques détaillées",
        key=_keys("show_details"),
        help="Charge les statistiques avancées du cache",
    )
    if show_details:
        _afficher_cache_details()

    st.markdown("---")

    # Actions groupees
    st.markdown("#### ⚡ Actions Groupées")

    if st.button(
        "🗑️ TOUT Vider (Cache App + IA)",
        key="btn_clear_all",
        type="primary",
        use_container_width=True,
    ):
        obtenir_cache().clear()
        SemanticCache.invalider_tout()
        afficher_succes("✅ Tous les caches vidés !")
