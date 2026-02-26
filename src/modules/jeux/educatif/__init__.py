"""
Module Éducatif Probabilités — Comprendre les maths derrière les jeux

Fonctionnalités:
- Simulateur Monte Carlo interactif (X€/semaine pendant N ans)
- Distribution de Poisson pour pronostics sportifs
- Comparatif espérance Loto vs Euromillions vs Paris
- Loi des grands nombres interactive
"""

import logging
import math
import random

import plotly.graph_objects as go
import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("educatif_jeux")


# ═══════════════════════════════════════════════════════════
# Monte Carlo
# ═══════════════════════════════════════════════════════════


def _simuler_monte_carlo(
    mise_hebdo: float,
    nb_annees: int,
    type_jeu: str,
    nb_simulations: int = 1000,
) -> dict:
    """Simule N années de mises hebdomadaires."""
    nb_semaines = nb_annees * 52

    # Probabilités simplifiées par jeu
    if type_jeu == "Loto":
        proba_petit = 1 / 6
        gain_petit = 5.0
        proba_gros = 1 / 2000
        gain_gros = 1000.0
    elif type_jeu == "Euromillions":
        proba_petit = 1 / 13
        gain_petit = 4.0
        proba_gros = 1 / 10000
        gain_gros = 5000.0
    else:  # Paris sportifs
        proba_petit = 0.45
        gain_petit = mise_hebdo * 0.9
        proba_gros = 0.10
        gain_gros = mise_hebdo * 4.0

    resultats_finaux = []

    for _ in range(nb_simulations):
        solde = 0.0
        for _ in range(nb_semaines):
            solde -= mise_hebdo
            r = random.random()
            if r < proba_gros:
                solde += gain_gros
            elif r < proba_gros + proba_petit:
                solde += gain_petit

        resultats_finaux.append(solde)

    resultats_tries = sorted(resultats_finaux)
    return {
        "resultats": resultats_finaux,
        "total_mise": mise_hebdo * nb_semaines,
        "moyenne": sum(resultats_finaux) / len(resultats_finaux),
        "median": resultats_tries[len(resultats_tries) // 2],
        "pire": min(resultats_finaux),
        "meilleur": max(resultats_finaux),
        "pct_positif": sum(1 for r in resultats_finaux if r > 0) / len(resultats_finaux) * 100,
    }


def _afficher_monte_carlo() -> None:
    """Interface du simulateur Monte Carlo."""
    st.subheader("🎲 Simulateur Monte Carlo")
    st.caption("Que se passe-t-il si vous jouez X€/semaine pendant N années ?")

    col1, col2, col3 = st.columns(3)
    with col1:
        mise = st.number_input(
            "Mise hebdo (€)",
            1.0,
            100.0,
            10.0,
            step=1.0,
            key=_keys("mc_mise"),
        )
    with col2:
        annees = st.slider("Années", 1, 30, 10, key=_keys("mc_annees"))
    with col3:
        jeu = st.selectbox(
            "Type de jeu",
            ["Loto", "Euromillions", "Paris sportifs"],
            key=_keys("mc_jeu"),
        )

    nb_sim = st.slider(
        "Nombre de simulations",
        100,
        5000,
        1000,
        step=100,
        key=_keys("mc_nsim"),
    )

    if st.button("🚀 Lancer la simulation", key=_keys("mc_go")):
        with st.spinner(f"Simulation de {nb_sim} scénarios..."):
            result = _simuler_monte_carlo(mise, annees, jeu, nb_sim)

        # KPIs
        cols = st.columns(4)
        cols[0].metric("💰 Total misé", f"{result['total_mise']:,.0f} €")
        cols[1].metric("📊 Solde moyen", f"{result['moyenne']:+,.0f} €")
        cols[2].metric("📈 Meilleur cas", f"{result['meilleur']:+,.0f} €")
        cols[3].metric(
            "✅ Chance de profit",
            f"{result['pct_positif']:.1f}%",
            delta=f"Médiane: {result['median']:+,.0f}€",
        )

        # Histogramme
        fig = go.Figure(
            data=go.Histogram(
                x=result["resultats"],
                nbinsx=50,
                marker_color="steelblue",
            )
        )
        fig.add_vline(
            x=0,
            line_dash="dash",
            line_color="red",
            annotation_text="Break-even",
        )
        fig.update_layout(
            title=f"Distribution des résultats ({nb_sim} simulations, {annees} ans)",
            xaxis_title="Solde final (€)",
            yaxis_title="Fréquence",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.warning(
            f"⚠️ En jouant {mise:.0f}€/semaine pendant {annees} ans, vous dépenserez "
            f"**{result['total_mise']:,.0f}€**. En moyenne, vous perdrez "
            f"**{abs(result['moyenne']):,.0f}€**. "
            f"Seuls **{result['pct_positif']:.1f}%** des scénarios sont rentables."
        )


# ═══════════════════════════════════════════════════════════
# Comparatif espérance
# ═══════════════════════════════════════════════════════════


def _afficher_comparatif_esperance() -> None:
    """Comparatif d'espérance mathématique entre jeux."""
    st.subheader("📐 Espérance mathématique comparée")

    jeux = {
        "Loto (1 grille)": {"mise": 2.20, "esperance": -1.43, "retour": 0.35},
        "Euromillions (1 grille)": {"mise": 2.50, "esperance": -1.75, "retour": 0.30},
        "Paris sportif (cote 2.0)": {"mise": 2.00, "esperance": -0.10, "retour": 0.95},
        "Paris sportif (cote 5.0)": {"mise": 2.00, "esperance": -0.40, "retour": 0.80},
        "Roulette (rouge/noir)": {"mise": 2.00, "esperance": -0.054, "retour": 0.973},
    }

    noms = list(jeux.keys())
    retours = [j["retour"] * 100 for j in jeux.values()]
    colors = ["green" if r >= 90 else "orange" if r >= 50 else "red" for r in retours]

    fig = go.Figure(
        data=go.Bar(
            x=noms,
            y=retours,
            marker_color=colors,
            text=[f"{r:.1f}%" for r in retours],
            textposition="outside",
        )
    )
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="white",
        annotation_text="Seuil rentabilité",
    )
    fig.update_layout(
        title="Taux de retour joueur par type de jeu (%)",
        yaxis_title="Retour (%)",
        height=400,
        yaxis_range=[0, 110],
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé
    st.markdown("### Détail par jeu")
    for nom, j in jeux.items():
        col1, col2, col3 = st.columns(3)
        col1.write(f"**{nom}**")
        col2.write(f"Mise: {j['mise']:.2f}€ → Espérance: {j['esperance']:+.2f}€")
        col3.write(f"Retour: {j['retour'] * 100:.1f}%")

    st.info(
        "💡 **Conclusion**: Les paris sportifs offrent le meilleur retour (~95%), "
        "mais nécessitent une expertise. Le Loto et l'Euromillions sont des jeux "
        "de hasard pur avec un retour de ~30-35%. Ce sont des divertissements, "
        "pas des investissements."
    )


# ═══════════════════════════════════════════════════════════
# Loi des grands nombres
# ═══════════════════════════════════════════════════════════


def _afficher_loi_grands_nombres() -> None:
    """Visualisation interactive de la loi des grands nombres."""
    st.subheader("📊 Loi des grands nombres")
    st.caption("Plus on joue, plus le résultat converge vers l'espérance théorique")

    nb_lancers = st.slider(
        "Nombre de lancers",
        10,
        10000,
        1000,
        key=_keys("lgn_lancers"),
    )

    if st.button("🎲 Lancer la simulation", key=_keys("lgn_go")):
        proba_gain = 0.48  # Avantage maison de 4%
        gains = [1 if random.random() < proba_gain else -1 for _ in range(nb_lancers)]
        cumul = [sum(gains[: i + 1]) for i in range(nb_lancers)]
        moyenne_mobile = [sum(gains[: i + 1]) / (i + 1) for i in range(nb_lancers)]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=cumul,
                mode="lines",
                name="Solde cumulé",
                line={"color": "steelblue"},
            )
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(
            title=f"Solde cumulé sur {nb_lancers} paris (proba gain = {proba_gain * 100}%)",
            xaxis_title="Nombre de paris",
            yaxis_title="Solde",
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Moyenne mobile
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                y=moyenne_mobile,
                mode="lines",
                name="Moyenne mobile",
                line={"color": "orange"},
            )
        )
        esperance = proba_gain * 2 - 1
        fig2.add_hline(
            y=esperance,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Espérance = {esperance:+.3f}",
        )
        fig2.update_layout(
            title="Convergence de la moyenne vers l'espérance",
            xaxis_title="Nombre de paris",
            yaxis_title="Gain moyen par pari",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.info(
            f"La moyenne converge vers l'espérance théorique ({esperance * 100:+.1f}% "
            "par pari). Sur le long terme, la maison gagne toujours."
        )


# ═══════════════════════════════════════════════════════════
# Distribution de Poisson (football)
# ═══════════════════════════════════════════════════════════


def _afficher_poisson() -> None:
    """Distribution de Poisson pour les scores de football."""
    st.subheader("📈 Distribution de Poisson — Scores football")
    st.caption("Modèle probabiliste pour prédire les scores de matchs")

    col1, col2 = st.columns(2)
    with col1:
        lambda_dom = st.slider(
            "Buts attendus domicile (λ)",
            0.5,
            4.0,
            1.5,
            0.1,
            key=_keys("poi_dom"),
        )
    with col2:
        lambda_ext = st.slider(
            "Buts attendus extérieur (λ)",
            0.5,
            4.0,
            1.2,
            0.1,
            key=_keys("poi_ext"),
        )

    max_buts = 6
    probas: dict[str, float] = {}

    for i in range(max_buts + 1):
        for j in range(max_buts + 1):
            p_i = (lambda_dom**i * math.exp(-lambda_dom)) / math.factorial(i)
            p_j = (lambda_ext**j * math.exp(-lambda_ext)) / math.factorial(j)
            probas[f"{i}-{j}"] = p_i * p_j

    # Top 10 scores les plus probables
    top = sorted(probas.items(), key=lambda x: x[1], reverse=True)[:10]
    scores = [t[0] for t in top]
    probs = [t[1] * 100 for t in top]

    fig = go.Figure(
        data=go.Bar(
            x=scores,
            y=probs,
            marker_color="mediumpurple",
            text=[f"{p:.1f}%" for p in probs],
            textposition="outside",
        )
    )
    fig.update_layout(
        title=f"Scores les plus probables (λ_dom={lambda_dom}, λ_ext={lambda_ext})",
        xaxis_title="Score",
        yaxis_title="Probabilité (%)",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Marchés 1X2
    p_dom = sum(v for k, v in probas.items() if int(k.split("-")[0]) > int(k.split("-")[1]))
    p_nul = sum(v for k, v in probas.items() if int(k.split("-")[0]) == int(k.split("-")[1]))
    p_ext = sum(v for k, v in probas.items() if int(k.split("-")[0]) < int(k.split("-")[1]))

    cols = st.columns(3)
    cols[0].metric("🏠 Victoire domicile", f"{p_dom * 100:.1f}%")
    cols[1].metric("🤝 Match nul", f"{p_nul * 100:.1f}%")
    cols[2].metric("✈️ Victoire extérieur", f"{p_ext * 100:.1f}%")

    # Cotes justes
    st.markdown("### Cotes justes (sans marge)")
    cols2 = st.columns(3)
    cols2[0].metric("Dom.", f"{1 / p_dom:.2f}" if p_dom > 0 else "∞")
    cols2[1].metric("Nul", f"{1 / p_nul:.2f}" if p_nul > 0 else "∞")
    cols2[2].metric("Ext.", f"{1 / p_ext:.2f}" if p_ext > 0 else "∞")


# ═══════════════════════════════════════════════════════════
# Point d'entrée
# ═══════════════════════════════════════════════════════════


@profiler_rerun("educatif_jeux")
def app():
    """Point d'entrée du module Éducatif."""
    st.title("🎓 Module Éducatif — Probabilités & Jeux")
    st.caption("Comprenez les mathématiques derrière les jeux pour jouer en conscience")

    TAB_LABELS = ["🎲 Monte Carlo", "📐 Espérance", "📊 Grands nombres", "📈 Poisson"]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    with tabs[0]:
        with error_boundary("monte_carlo"):
            _afficher_monte_carlo()

    with tabs[1]:
        with error_boundary("esperance"):
            _afficher_comparatif_esperance()

    with tabs[2]:
        with error_boundary("grands_nombres"):
            _afficher_loi_grands_nombres()

    with tabs[3]:
        with error_boundary("poisson"):
            _afficher_poisson()


def main():
    app()


__all__ = ["app", "main"]
