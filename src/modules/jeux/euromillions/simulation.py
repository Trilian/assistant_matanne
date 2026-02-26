"""
UI Simulation Euromillions - Backtesting de stratégies
"""

import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ui.core.fragments import cached_fragment
from src.ui.keys import KeyNamespace

from .scraper import charger_tirages_euromillions
from .strategies import comparer_strategies, simuler_strategie

logger = logging.getLogger(__name__)
_keys = KeyNamespace("euromillions_sim")


@cached_fragment(ttl=300)
def _build_roi_chart(resultats: list[dict]) -> go.Figure:
    """Graphique comparatif ROI des stratégies."""
    noms = [r["strategie"] for r in resultats]
    rois = [r["roi"] for r in resultats]
    colors = ["#4CAF50" if r >= 0 else "#F44336" for r in rois]

    fig = go.Figure(
        data=[
            go.Bar(
                x=noms,
                y=rois,
                text=[f"{r:.2f}%" for r in rois],
                textposition="auto",
                marker_color=colors,
            )
        ]
    )
    fig.update_layout(
        title="Comparaison ROI par stratégie",
        yaxis_title="ROI (%)",
        height=400,
    )
    return fig


def afficher_simulation() -> None:
    """Interface de simulation et backtesting Euromillions."""
    st.subheader("🔬 Simulation de stratégies Euromillions")

    st.warning(
        "⚠️ La simulation utilise les tirages passés. "
        "Les résultats **ne prédisent pas** les performances futures."
    )

    tirages = charger_tirages_euromillions(limite=500)
    if len(tirages) < 10:
        st.error("Pas assez de tirages pour la simulation (minimum 10)")
        return

    col1, col2 = st.columns(2)
    with col1:
        nb_tirages = st.slider(
            "Tirages à analyser",
            min_value=10,
            max_value=len(tirages),
            value=min(100, len(tirages)),
            key=_keys("nb_tirages"),
        )
    with col2:
        grilles_par_tirage = st.slider(
            "Grilles par tirage",
            min_value=1,
            max_value=5,
            value=1,
            key=_keys("grilles"),
        )

    if st.button("🚀 Lancer la simulation", type="primary", key=_keys("lancer")):
        tirages_sim = tirages[:nb_tirages]

        progress = st.progress(0, text="Simulation en cours...")
        strategies = ["aleatoire", "eviter_populaires", "equilibree", "chauds", "froids", "ecart"]
        resultats = []

        for i, strat in enumerate(strategies):
            res = simuler_strategie(tirages_sim, strat, grilles_par_tirage)
            resultats.append(res)
            progress.progress((i + 1) / len(strategies), text=f"Stratégie: {strat}")

        progress.empty()

        # Résultats triés par ROI
        resultats.sort(key=lambda r: r.get("roi", 0), reverse=True)

        # Tableau
        df = pd.DataFrame(
            [
                {
                    "Stratégie": r["strategie"],
                    "Grilles": r["nb_grilles"],
                    "Mise (€)": f"{r['mise_totale']:.2f}",
                    "Gains (€)": f"{r['gains_totaux']:.2f}",
                    "Profit (€)": f"{r['profit']:.2f}",
                    "ROI (%)": f"{r['roi']:.2f}",
                    "Gagnants": r["nb_gagnants"],
                    "Taux (%)": f"{r['taux_gain']:.2f}",
                }
                for r in resultats
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Graphique ROI
        fig = _build_roi_chart(resultats)
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "📊 **Conclusion**: Toutes les stratégies convergent vers un ROI négatif "
            "sur le long terme. L'Euromillions a une espérance de ~-60%."
        )


def afficher_gestion_tirages() -> None:
    """Gestion des tirages: sync et ajout manuel."""
    st.subheader("⚙️ Gestion des tirages Euromillions")

    from .crud import ajouter_tirage

    # Sync automatique
    if st.button("🔄 Synchroniser les tirages", key=_keys("sync")):
        tirages = charger_tirages_euromillions(limite=50)
        nb_ajoutes = 0
        for t in tirages:
            from datetime import date as date_type

            date_str = t.get("date_tirage", "")
            try:
                if isinstance(date_str, str):
                    date_t = date_type.fromisoformat(date_str)
                else:
                    date_t = date_str
                ok = ajouter_tirage(
                    date_tirage=date_t,
                    numeros=t["numeros"],
                    etoiles=t["etoiles"],
                    jackpot=t.get("jackpot_euros"),
                    code_my_million=t.get("code_my_million"),
                )
                if ok:
                    nb_ajoutes += 1
            except Exception as e:
                logger.debug(f"Erreur ajout tirage: {e}")
        st.success(f"✅ {nb_ajoutes} tirage(s) ajouté(s)")

    # Ajout manuel
    st.divider()
    st.markdown("**Ajouter un tirage manuellement**")

    with st.form(key=_keys("form_tirage")):
        date_tirage = st.date_input("Date du tirage", key=_keys("date"))

        cols = st.columns(5)
        numeros = []
        for i in range(5):
            with cols[i]:
                n = st.number_input(f"N°{i + 1}", min_value=1, max_value=50, key=_keys(f"num_{i}"))
                numeros.append(n)

        cols_e = st.columns(2)
        etoiles = []
        for i in range(2):
            with cols_e[i]:
                e = st.number_input(f"★{i + 1}", min_value=1, max_value=12, key=_keys(f"star_{i}"))
                etoiles.append(e)

        jackpot = st.number_input(
            "Jackpot (€)", min_value=0, value=17_000_000, key=_keys("jackpot")
        )

        if st.form_submit_button("Ajouter"):
            if len(set(numeros)) == 5 and len(set(etoiles)) == 2:
                ok = ajouter_tirage(
                    date_tirage=date_tirage,
                    numeros=sorted(numeros),
                    etoiles=sorted(etoiles),
                    jackpot=jackpot,
                )
                if ok:
                    st.success("✅ Tirage ajouté")
                else:
                    st.warning("Tirage déjà existant pour cette date")
            else:
                st.error("Les numéros et étoiles doivent être uniques")
