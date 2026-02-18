"""
Dashboard - Tableau de bord de performance pour l'UI.

Fonctionnalités:
- Résumé des métriques de performance
- Score de santé global
- Composants UI pour affichage
"""

import logging

import streamlit as st

from .memory import MoniteurMemoire
from .profiler import ProfileurFonction
from .sql import OptimiseurSQL

logger = logging.getLogger(__name__)


class TableauBordPerformance:
    """
    Génère les métriques de performance pour l'UI.
    """

    @classmethod
    def obtenir_resume(cls) -> dict:
        """
        Retourne un résumé complet des performances.

        Returns:
            Dict avec toutes les métriques
        """
        from src.core.lazy_loader import ChargeurModuleDiffere

        # Stats lazy loading
        lazy_stats = ChargeurModuleDiffere.obtenir_statistiques()

        # Stats profiler
        profiler_stats = ProfileurFonction.obtenir_toutes_stats()
        slowest = ProfileurFonction.obtenir_plus_lentes(5)

        # Stats mémoire
        memory = MoniteurMemoire.obtenir_utilisation_courante()

        # Stats SQL
        sql_stats = OptimiseurSQL.obtenir_statistiques()

        return {
            "lazy_loading": {
                "modules_cached": lazy_stats["cached_modules"],
                "total_load_time_ms": round(lazy_stats["total_load_time"] * 1000, 0),
                "avg_load_time_ms": round(lazy_stats["average_load_time"] * 1000, 0),
            },
            "functions": {
                "tracked_count": len(profiler_stats),
                "slowest": [
                    {"name": name.split(".")[-1], "avg_ms": round(stats.avg_time_ms, 1)}
                    for name, stats in slowest
                ],
            },
            "memory": memory,
            "sql": {
                "total_queries": sql_stats["total_queries"],
                "avg_time_ms": sql_stats["avg_time_ms"],
                "slow_count": sql_stats["slow_query_count"],
            },
        }

    @classmethod
    def obtenir_score_sante(cls) -> tuple[int, str]:
        """
        Calcule un score de santé global (0-100).

        Returns:
            Tuple (score, status_emoji)
        """
        summary = cls.obtenir_resume()
        score = 100

        # Pénalités mémoire
        if summary["memory"]["current_mb"] > 500:
            score -= 20
        elif summary["memory"]["current_mb"] > 200:
            score -= 10

        # Pénalités SQL
        if summary["sql"]["slow_count"] > 10:
            score -= 15
        elif summary["sql"]["slow_count"] > 5:
            score -= 5

        # Pénalités chargement
        if summary["lazy_loading"]["avg_load_time_ms"] > 500:
            score -= 10
        elif summary["lazy_loading"]["avg_load_time_ms"] > 200:
            score -= 5

        # Status emoji
        if score >= 80:
            status = "🟢"
        elif score >= 60:
            status = "🟡"
        else:
            status = "🔴"

        return max(0, score), status


def afficher_panneau_performance():
    """Affiche le panneau de performance dans la sidebar."""

    summary = TableauBordPerformance.obtenir_resume()
    score, status = TableauBordPerformance.obtenir_score_sante()

    with st.expander(f"📊 Performance {status} {score}/100"):
        # Tabs pour différentes métriques
        tab1, tab2, tab3 = st.tabs(["⚡ Général", "🧠 Mémoire", "🗃️ SQL"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Modules chargés",
                    summary["lazy_loading"]["modules_cached"],
                )
            with col2:
                st.metric(
                    "Chargement moyen",
                    f"{summary['lazy_loading']['avg_load_time_ms']}ms",
                )

            # Top fonctions lentes
            if summary["functions"]["slowest"]:
                st.caption("🐌 Fonctions les plus lentes:")
                for f in summary["functions"]["slowest"][:3]:
                    st.caption(f"• {f['name']}: {f['avg_ms']}ms")

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Mémoire utilisée",
                    f"{summary['memory']['current_mb']}MB",
                )
            with col2:
                st.metric(
                    "Objets en mémoire",
                    f"{summary['memory']['total_objects']:,}",
                )

            if st.button("🧹 Nettoyer mémoire", key="cleanup_mem"):
                result = MoniteurMemoire.forcer_nettoyage()
                st.success(f"Libéré: {result['memory_freed_mb']}MB")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Requêtes totales",
                    summary["sql"]["total_queries"],
                )
            with col2:
                st.metric(
                    "Requêtes lentes",
                    summary["sql"]["slow_count"],
                    delta_color="inverse" if summary["sql"]["slow_count"] > 0 else "off",
                )

            if st.button("🗑️ Reset stats", key="reset_sql"):
                OptimiseurSQL.effacer()
                st.success("Stats SQL réinitialisées")


def afficher_badge_mini_performance():
    """Badge compact pour la barre latérale."""

    score, status = TableauBordPerformance.obtenir_score_sante()
    memory = MoniteurMemoire.obtenir_utilisation_courante()

    st.markdown(
        f'<div style="display: flex; justify-content: space-between; '
        f"padding: 0.25rem 0.5rem; background: #f0f2f6; border-radius: 4px; "
        f'font-size: 0.8rem;">'
        f"<span>{status} Perf: {score}%</span>"
        f"<span>💾 {memory['current_mb']}MB</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# WIDGETS CACHE & RATE LIMIT
# ═══════════════════════════════════════════════════════════


def afficher_statistiques_cache(prefixe_cle: str = "cache"):
    """
    Widget Streamlit pour afficher les stats cache dans la sidebar.

    Args:
        prefixe_cle: Préfixe pour les clés Streamlit (évite collisions)

    Example:
        >>> with st.sidebar:
        >>>     afficher_statistiques_cache()
    """
    from src.core.caching.cache import Cache

    stats = Cache.obtenir_statistiques()

    with st.expander("💾 Cache Stats"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Entrées", stats["entrees"], help="Nombre d'entrées en cache")
            st.metric("Taux Hit", f"{stats['taux_hit']:.1f}%", help="Taux de succès du cache")

        with col2:
            st.metric("Taille", f"{stats['taille_mo']:.2f} MB", help="Taille totale du cache")
            st.metric("Invalidations", stats["invalidations"], help="Nombre d'invalidations")

        # Actions
        col3, col4 = st.columns(2)

        with col3:
            if st.button("🧹 Nettoyer", key=f"{prefixe_cle}_nettoyer", use_container_width=True):
                Cache.nettoyer_expires()
                st.success("Nettoyage effectué !")
                st.rerun()

        with col4:
            if st.button("🗑️ Vider", key=f"{prefixe_cle}_vider", use_container_width=True):
                Cache.vider()
                st.success("Cache vidé !")
                st.rerun()


def afficher_statistiques_rate_limit():
    """
    Widget Streamlit pour afficher les stats de rate limiting.

    Example:
        >>> with st.sidebar:
        >>>     afficher_statistiques_rate_limit()
    """
    from src.core.ai import RateLimitIA

    stats = RateLimitIA.obtenir_statistiques()

    with st.expander("⏳ Rate Limit IA"):
        st.metric(
            "Appels aujourd'hui",
            f"{stats['appels_jour']} / {stats['limite_jour']}",
            delta=f"{stats['restant_jour']} restants",
        )

        st.metric(
            "Appels cette heure",
            f"{stats['appels_heure']} / {stats['limite_heure']}",
            delta=f"{stats['restant_heure']} restants",
        )

        # Progress bars
        st.progress(stats["appels_jour"] / stats["limite_jour"])
        st.caption("Quota journalier")
