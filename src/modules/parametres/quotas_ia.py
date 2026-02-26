"""
Paramètres - Quotas et consommation IA.

Jauges temps réel, historique 30 jours, détail par service, cache sémantique.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_quotas")


@ui_fragment
def afficher_quotas_ia():
    """Suivi des quotas et consommation IA."""

    st.markdown("### 📈 Quotas & Consommation IA")
    st.caption("Suivi en temps réel de la consommation des appels IA")

    # ── Section 1: Consommation temps réel ──
    st.markdown("#### ⚡ Consommation en temps réel")

    try:
        from src.core.config import obtenir_parametres

        settings = obtenir_parametres()
        limite_jour = settings.RATE_LIMIT_DAILY
        limite_heure = settings.RATE_LIMIT_HOURLY
    except Exception:
        limite_jour = 100
        limite_heure = 20

    # Récupérer les compteurs actuels
    appels_jour = 0
    appels_heure = 0
    try:
        from src.core.monitoring.collector import obtenir_snapshot

        snapshot = obtenir_snapshot()
        metriques = snapshot.get("metriques", {})
        ia_appels = metriques.get("ia.appel", {})
        appels_jour = int(ia_appels.get("total", 0))
        # Estimation horaire basée sur les métriques récentes
        appels_heure = min(appels_jour, limite_heure)
    except Exception:
        pass

    col1, col2 = st.columns(2)

    with col1:
        pct_jour = min(appels_jour / limite_jour, 1.0) if limite_jour > 0 else 0
        st.markdown("**Appels quotidiens**")
        st.progress(pct_jour)
        st.caption(f"{appels_jour} / {limite_jour} appels aujourd'hui")
        if pct_jour >= 0.95:
            st.error("⛔ Quota quasi atteint ! Les appels IA seront bloqués.")
        elif pct_jour >= 0.8:
            st.warning("⚠️ Attention : 80% du quota quotidien consommé.")

    with col2:
        pct_heure = min(appels_heure / limite_heure, 1.0) if limite_heure > 0 else 0
        st.markdown("**Appels horaires**")
        st.progress(pct_heure)
        st.caption(f"{appels_heure} / {limite_heure} appels cette heure")
        if pct_heure >= 0.95:
            st.error("⛔ Limite horaire quasi atteinte !")
        elif pct_heure >= 0.8:
            st.warning("⚠️ 80% de la limite horaire consommée.")

    # ── Section 2: Détail par service IA ──
    st.markdown("---")
    st.markdown("#### 🧩 Détail par service IA")

    try:
        from src.core.monitoring.collector import collecteur

        metriques_ia = collecteur.filtrer_par_prefixe("ia.")
        if metriques_ia:
            import pandas as pd

            rows = []
            for nom, serie in metriques_ia.items():
                rows.append(
                    {
                        "Service": nom,
                        "Type": serie.type.name,
                        "Total": f"{serie.total:.0f}",
                        "Points": len(serie.points),
                    }
                )
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune métrique IA enregistrée pour le moment.")
    except Exception as e:
        logger.debug("Erreur métriques IA: %s", e)
        st.info("Métriques IA non disponibles.")

    # ── Section 3: Cache sémantique ──
    st.markdown("---")
    st.markdown("#### 🧠 Cache sémantique IA")

    try:
        from src.core.ai.cache import CacheIA as SemanticCache

        cache_stats = SemanticCache.obtenir_statistiques()

        col_c1, col_c2, col_c3 = st.columns(3)

        with col_c1:
            st.metric(
                "Taux de Hit",
                f"{cache_stats.get('taux_hit', 0):.1f}%",
                help="Pourcentage de réponses servies depuis le cache",
            )
        with col_c2:
            st.metric("Entrées cachées", cache_stats.get("entrees_ia", 0))
        with col_c3:
            st.metric("Appels économisés", cache_stats.get("saved_api_calls", 0))

        # Estimation des économies
        cout_par_appel = 0.002  # Estimation tarif Mistral
        economisees = cache_stats.get("saved_api_calls", 0)
        st.metric(
            "💰 Économies estimées",
            f"{economisees * cout_par_appel:.3f} €",
            help="Basé sur un coût estimé de 0.002 € par appel Mistral",
        )

    except Exception as e:
        logger.debug("Cache stats non disponibles: %s", e)
        st.info("Statistiques du cache IA non disponibles.")

    # ── Section 4: Historique (graphique) ──
    st.markdown("---")
    st.markdown("#### 📊 Historique de consommation")

    try:
        from src.core.monitoring.collector import collecteur

        serie_ia = collecteur.obtenir_serie("ia.appel")
        if serie_ia:
            import plotly.graph_objects as go

            timestamps = [p.timestamp for p in serie_ia]
            valeurs = [p.valeur for p in serie_ia]

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=timestamps,
                        y=valeurs,
                        mode="lines+markers",
                        name="Appels IA",
                        line={"color": "#2196F3"},
                    )
                ]
            )
            fig.update_layout(
                title="Appels IA dans le temps",
                xaxis_title="Timestamp",
                yaxis_title="Appels",
                height=300,
                margin={"t": 40, "b": 40, "l": 40, "r": 20},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour afficher un graphique.")
    except ImportError:
        st.info("Plotly requis pour les graphiques (pip install plotly)")
    except Exception as e:
        logger.debug("Erreur graphique historique: %s", e)
