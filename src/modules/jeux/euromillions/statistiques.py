"""
UI Statistiques Euromillions - Affichage des fréquences et espérance
"""

import logging

import plotly.graph_objects as go
import streamlit as st

from src.ui.components.atoms import boule_loto_html
from src.ui.core.fragments import cached_fragment

from .calculs import calculer_esperance_mathematique
from .frequences import (
    analyser_patterns_tirages,
    calculer_frequences_numeros,
    identifier_numeros_chauds_froids,
)

logger = logging.getLogger(__name__)


def afficher_dernier_tirage(tirages: list[dict]) -> None:
    """Affiche le dernier tirage Euromillions."""
    if not tirages:
        st.info("Aucun tirage disponible")
        return

    dernier = tirages[0]
    st.subheader(f"🌟 Dernier tirage — {dernier.get('date_tirage', 'N/A')}")

    # Afficher les boules
    numeros = dernier.get("numeros", [])
    etoiles = dernier.get("etoiles", [])

    cols = st.columns(7)
    for i, num in enumerate(numeros):
        with cols[i]:
            st.markdown(boule_loto_html(num, is_chance=False, taille=60), unsafe_allow_html=True)
    for i, etoile in enumerate(etoiles):
        with cols[5 + i]:
            st.markdown(boule_loto_html(etoile, is_chance=True, taille=60), unsafe_allow_html=True)

    jackpot = dernier.get("jackpot_euros")
    if jackpot:
        st.metric("💰 Jackpot", f"{jackpot:,.0f} €")

    my_million = dernier.get("code_my_million")
    if my_million:
        st.info(f"🎟️ Code My Million: **{my_million}**")


@cached_fragment(ttl=300)
def _build_freq_chart(freq_data: dict, titre: str, max_num: int) -> go.Figure:
    """Construit un graphique de fréquences."""
    nums = sorted(freq_data.keys())
    counts = [freq_data[n]["count"] for n in nums]
    pcts = [freq_data[n]["pct"] for n in nums]

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(nums),
                y=counts,
                text=[f"{p:.1f}%" for p in pcts],
                textposition="auto",
                marker_color=["#FFD700" if n <= 25 else "#1E88E5" for n in nums],
            )
        ]
    )
    fig.update_layout(
        title=titre,
        xaxis_title="Numéro",
        yaxis_title="Fréquence",
        height=400,
        showlegend=False,
    )
    return fig


def afficher_statistiques_frequences(tirages: list[dict]) -> None:
    """Affiche les statistiques de fréquences Euromillions."""
    if len(tirages) < 5:
        st.warning("Pas assez de tirages pour les statistiques (minimum 5)")
        return

    freq_data = calculer_frequences_numeros(tirages)
    freq_numeros = freq_data.get("frequences_numeros", {})
    freq_etoiles = freq_data.get("frequences_etoiles", {})

    st.subheader("📊 Fréquences des numéros (1-50)")
    fig_nums = _build_freq_chart(freq_numeros, "Fréquence des numéros", 50)
    st.plotly_chart(fig_nums, use_container_width=True)

    st.subheader("⭐ Fréquences des étoiles (1-12)")
    fig_stars = _build_freq_chart(freq_etoiles, "Fréquence des étoiles", 12)
    st.plotly_chart(fig_stars, use_container_width=True)

    # Numéros chauds/froids
    analyse_nums = identifier_numeros_chauds_froids(freq_numeros, nb_top=10)
    analyse_stars = identifier_numeros_chauds_froids(freq_etoiles, nb_top=5)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔥 Numéros chauds**")
        for num, count, pct in analyse_nums.get("chauds", []):
            st.write(f"**{num}** — {count}× ({pct:.1f}%)")

    with col2:
        st.markdown("**❄️ Numéros froids**")
        for num, count, pct in analyse_nums.get("froids", []):
            st.write(f"**{num}** — {count}× ({pct:.1f}%)")

    with col3:
        st.markdown("**⏰ En retard**")
        for num, ecart in analyse_nums.get("retard", []):
            st.write(f"**{num}** — {ecart} tirages sans sortie")

    # Patterns
    patterns = analyser_patterns_tirages(tirages)
    if patterns:
        st.divider()
        st.subheader("📈 Patterns statistiques")
        m1, m2, m3 = st.columns(3)
        m1.metric("Somme moyenne", f"{patterns.get('somme_moyenne', 0):.1f}")
        m2.metric("Écart moyen", f"{patterns.get('ecart_moyen', 0):.1f}")
        m3.metric("Pairs en moyenne", f"{patterns.get('pairs_moyenne', 0):.1f}/5")


def afficher_esperance() -> None:
    """Affiche l'espérance mathématique de l'Euromillions."""
    st.subheader("📐 Espérance mathématique Euromillions")

    st.warning(
        "⚠️ Ces calculs démontrent que l'Euromillions est **défavorable au joueur**. "
        "L'espérance est **toujours négative**."
    )

    data = calculer_esperance_mathematique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Coût grille", f"{data['cout_grille']:.2f} €")
    col2.metric("Gain espéré", f"{data['gains_esperes']:.4f} €")
    col3.metric(
        "Espérance",
        f"{data['esperance']:.4f} €",
        delta=f"-{data['perte_moyenne_pct']:.1f}%",
        delta_color="inverse",
    )

    st.info(data["conclusion"])

    # Tableau des probabilités
    st.subheader("📋 Tableau des rangs")
    for rang_info in data["tableau"]:
        proba = rang_info["probabilite"]
        chance = f"1/{int(1 / proba):,}" if proba > 0 else "N/A"
        gain = rang_info["gain"]
        st.write(
            f"**Rang {rang_info['rang']}** — {rang_info['description']} | "
            f"Gain: {gain:,}€ | Chance: {chance}"
        )
