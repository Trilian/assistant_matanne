"""
Module Comparatif ROI — Analyse comparative des stratégies

Fonctionnalités:
- Comparaison ROI cross-jeux (Loto vs Euromillions vs Paris)
- Radar chart multi-critères (ROI, variance, fréquence gains, espérance)
- Heatmap gains par mois / type
- Sharpe ratio adapté (performance ajustée au risque)
- Recommandation IA sur allocation optimale
"""

import logging
import math
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("comparatif_roi")


# ═══════════════════════════════════════════════════════════
# Chargement données
# ═══════════════════════════════════════════════════════════


@avec_session_db
def _charger_donnees_roi(jours: int = 365, db=None) -> dict[str, list[dict]]:
    """Charge les données par type de jeu."""
    from src.core.models.jeux import HistoriqueJeux

    date_debut = date.today() - timedelta(days=jours)
    rows = (
        db.query(HistoriqueJeux)
        .filter(HistoriqueJeux.date >= date_debut)
        .order_by(HistoriqueJeux.date.asc())
        .all()
    )

    resultats: dict[str, list[dict]] = {}
    for r in rows:
        type_jeu = r.type_jeu
        if type_jeu not in resultats:
            resultats[type_jeu] = []
        resultats[type_jeu].append(
            {
                "date": r.date,
                "mises": float(r.mises_totales),
                "gains": float(r.gains_totaux),
                "profit": float(r.gains_totaux - r.mises_totales),
                "nb_paris": r.nb_paris,
                "paris_gagnes": r.paris_gagnes,
            }
        )

    return resultats


# ═══════════════════════════════════════════════════════════
# Métriques de performance
# ═══════════════════════════════════════════════════════════


def _calculer_metriques(entries: list[dict]) -> dict:
    """Calcule les métriques de performance pour un type de jeu."""
    if not entries:
        return {
            "roi": 0,
            "sharpe": 0,
            "taux_reussite": 0,
            "variance": 0,
            "esperance": 0,
            "nb_sessions": 0,
            "total_mises": 0,
            "total_gains": 0,
            "profit": 0,
            "max_gain": 0,
            "max_perte": 0,
        }

    profits = [e["profit"] for e in entries]
    total_mises = sum(e["mises"] for e in entries)
    total_gains = sum(e["gains"] for e in entries)
    total_paris_gagnes = sum(e["paris_gagnes"] for e in entries)
    total_nb_paris = sum(e["nb_paris"] for e in entries)
    profit = total_gains - total_mises

    roi = (profit / total_mises * 100) if total_mises > 0 else 0
    esperance = sum(profits) / len(profits) if profits else 0
    variance = sum((p - esperance) ** 2 for p in profits) / len(profits) if profits else 0
    ecart_type = math.sqrt(variance) if variance > 0 else 0.001
    sharpe = esperance / ecart_type if ecart_type > 0 else 0
    taux = (total_paris_gagnes / total_nb_paris * 100) if total_nb_paris > 0 else 0

    return {
        "roi": round(roi, 2),
        "sharpe": round(sharpe, 3),
        "taux_reussite": round(taux, 1),
        "variance": round(variance, 2),
        "esperance": round(esperance, 2),
        "nb_sessions": len(entries),
        "total_mises": round(total_mises, 2),
        "total_gains": round(total_gains, 2),
        "profit": round(profit, 2),
        "max_gain": round(max(profits), 2) if profits else 0,
        "max_perte": round(min(profits), 2) if profits else 0,
    }


# ═══════════════════════════════════════════════════════════
# Visualisations
# ═══════════════════════════════════════════════════════════


def _afficher_radar(metriques_par_jeu: dict[str, dict]) -> None:
    """Radar chart multi-critères."""
    if not metriques_par_jeu:
        st.info("Aucune donnée pour le radar")
        return

    categories = ["ROI", "Sharpe Ratio", "Taux réussite", "Espérance", "Nb sessions"]
    fig = go.Figure()

    for type_jeu, m in metriques_par_jeu.items():
        values = [
            max(min(m["roi"], 100), -100),
            m["sharpe"] * 100,
            m["taux_reussite"],
            max(min(m["esperance"] * 10, 100), -100),
            min(m["nb_sessions"], 100),
        ]
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name=type_jeu.capitalize(),
            )
        )

    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [-100, 100]}},
        title="🎯 Comparaison multi-critères",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)


def _afficher_heatmap(donnees: dict[str, list[dict]]) -> None:
    """Heatmap gains par mois / type."""
    all_data = []
    for type_jeu, entries in donnees.items():
        for e in entries:
            all_data.append(
                {
                    "type_jeu": type_jeu.capitalize(),
                    "mois": pd.Timestamp(e["date"]).to_period("M").strftime("%Y-%m"),
                    "profit": e["profit"],
                }
            )

    if not all_data:
        st.info("Pas assez de données pour la heatmap")
        return

    df = pd.DataFrame(all_data)
    pivot = df.pivot_table(
        values="profit",
        index="type_jeu",
        columns="mois",
        aggfunc="sum",
        fill_value=0,
    )

    fig = px.imshow(
        pivot,
        labels={"x": "Mois", "y": "Type de jeu", "color": "Profit (€)"},
        title="🗓️ Heatmap profit mensuel par jeu",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        aspect="auto",
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def _afficher_tableau_comparatif(metriques_par_jeu: dict[str, dict]) -> None:
    """Tableau comparatif détaillé."""
    rows = []
    for type_jeu, m in metriques_par_jeu.items():
        rows.append(
            {
                "Jeu": type_jeu.capitalize(),
                "Mises (€)": m["total_mises"],
                "Gains (€)": m["total_gains"],
                "Profit (€)": m["profit"],
                "ROI (%)": m["roi"],
                "Sharpe": m["sharpe"],
                "Taux réussite (%)": m["taux_reussite"],
                "Sessions": m["nb_sessions"],
                "Max gain (€)": m["max_gain"],
                "Max perte (€)": m["max_perte"],
            }
        )

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée à comparer")


def _afficher_recommandation_ia(metriques_par_jeu: dict[str, dict]) -> None:
    """Recommandation IA sur allocation optimale."""
    if not metriques_par_jeu:
        return

    if st.button("🤖 Obtenir recommandation IA", key=_keys("reco_ia")):
        with st.spinner("Analyse en cours..."):
            try:
                from src.services.jeux import get_jeux_ai_service

                service = get_jeux_ai_service()
                context = "Voici mes métriques par type de jeu:\n"
                for type_jeu, m in metriques_par_jeu.items():
                    context += (
                        f"- {type_jeu}: ROI={m['roi']}%, Sharpe={m['sharpe']}, "
                        f"Taux={m['taux_reussite']}%, Profit={m['profit']}€, "
                        f"Sessions={m['nb_sessions']}\n"
                    )

                result = service.call_with_cache(
                    prompt=(
                        f"{context}\nAnalyse ces performances et recommande "
                        "l'allocation optimale du budget jeux entre ces types. "
                        "Donne des conseils concrets pour améliorer la rentabilité."
                    ),
                    system_prompt=(
                        "Tu es un expert en analyse de jeux d'argent. "
                        "Donne des conseils objectifs et responsables. "
                        "Rappelle toujours que le jeu comporte des risques."
                    ),
                )
                st.markdown(result)
            except Exception as e:
                logger.warning(f"Recommandation IA indisponible: {e}")
                st.warning("Recommandation IA indisponible.")


# ═══════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════


@profiler_rerun("comparatif_roi")
def app():
    """Point d'entrée du module Comparatif ROI."""
    st.title("📊 Comparatif ROI — Stratégies de jeu")
    st.caption("Analysez la performance relative de vos différents types de jeux")

    TAB_LABELS = ["🎯 Radar", "📊 Détails", "🗓️ Heatmap", "🤖 IA"]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    jours = st.selectbox(
        "Période",
        [30, 90, 180, 365],
        index=3,
        format_func=lambda x: f"{x} jours",
        key=_keys("periode"),
    )

    donnees = _charger_donnees_roi(jours=jours)
    metriques = {t: _calculer_metriques(e) for t, e in donnees.items()}

    with tabs[0]:
        with error_boundary("radar_roi"):
            _afficher_radar(metriques)

    with tabs[1]:
        with error_boundary("details_roi"):
            _afficher_tableau_comparatif(metriques)

    with tabs[2]:
        with error_boundary("heatmap_roi"):
            _afficher_heatmap(donnees)

    with tabs[3]:
        with error_boundary("ia_roi"):
            _afficher_recommandation_ia(metriques)


def main():
    app()


__all__ = ["app", "main"]
