"""
Module Loto - Composants UI de statistiques
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ui import etat_vide
from src.ui.fragments import cached_fragment, ui_fragment

from .calculs import calculer_esperance_mathematique
from .constants import GAINS_PAR_RANG, NUMERO_MAX, NUMERO_MIN
from .frequences import calculer_frequences_numeros, identifier_numeros_chauds_froids


@ui_fragment
def afficher_dernier_tirage(tirages: list):
    """Affiche le dernier tirage avec style"""
    if not tirages:
        etat_vide("Aucun tirage enregistré", "📊")
        return

    dernier = tirages[0]

    st.markdown("### 🎰 Dernier tirage")

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{dernier['date_tirage']}**")

            # Afficher les boules
            from src.ui import boule_loto

            cols_boules = st.columns(6)
            for i, num in enumerate(dernier["numeros"]):
                with cols_boules[i]:
                    boule_loto(num)

            with cols_boules[5]:
                boule_loto(dernier["numero_chance"], is_chance=True)

        with col2:
            if dernier.get("jackpot_euros"):
                st.metric("💰 Jackpot", f"{dernier['jackpot_euros']:,}€")


@cached_fragment(ttl=300)  # Cache 5 min (calculs lourds sur historique)
def afficher_statistiques_frequences(tirages: list):
    """Affiche les statistiques de fréquence"""
    if not tirages:
        st.warning("Pas assez de données pour les statistiques")
        return

    freq_data = calculer_frequences_numeros(tirages)
    frequences = freq_data.get("frequences", {})

    if not frequences:
        return

    chauds_froids = identifier_numeros_chauds_froids(frequences, nb_top=10)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔥 Numéros Chauds")
        st.caption("Les plus fréquents")
        for num in chauds_froids.get("chauds", [])[:5]:
            freq = frequences[num]["frequence"]
            pct = frequences[num]["pourcentage"]
            st.write(f"**{num}** - {freq} fois ({pct}%)")

    with col2:
        st.markdown("### â„ï¸ Numéros Froids")
        st.caption("Les moins fréquents")
        for num in chauds_froids.get("froids", [])[:5]:
            freq = frequences[num]["frequence"]
            pct = frequences[num]["pourcentage"]
            st.write(f"**{num}** - {freq} fois ({pct}%)")

    with col3:
        st.markdown("### ⏰ En Retard")
        st.caption("Pas sortis depuis longtemps")
        for num in chauds_froids.get("retard", [])[:5]:
            ecart = frequences[num]["ecart"]
            st.write(f"**{num}** - {ecart} tirages")

    st.divider()

    # Graphique de fréquence
    st.markdown("### 📊 Distribution des fréquences")

    nums = list(range(NUMERO_MIN, NUMERO_MAX + 1))
    freqs = [frequences.get(n, {}).get("frequence", 0) for n in nums]

    fig = go.Figure(
        data=[
            go.Bar(
                x=nums,
                y=freqs,
                marker_color=[
                    "#f5576c"
                    if n in chauds_froids.get("chauds", [])[:10]
                    else "#667eea"
                    if n in chauds_froids.get("froids", [])[:10]
                    else "#95a5a6"
                    for n in nums
                ],
                hovertemplate="Numéro %{x}<br>Fréquence: %{y}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis_title="Numéro",
        yaxis_title="Fréquence",
        height=300,
        margin=dict(l=20, r=20, t=20, b=40),
    )

    st.plotly_chart(fig, width="stretch", key="loto_freq_chart")

    # Avertissement
    st.warning(
        "⚠️ **Rappel**: Ces statistiques sont purement informatives. "
        "Chaque tirage est indépendant et aléatoire. "
        "Un numéro 'en retard' n'a pas plus de chances de sortir!"
    )


@cached_fragment(ttl=3600)  # Cache 1h (calculs mathématiques constants)
def afficher_esperance():
    """Affiche l'espérance mathématique du Loto"""

    esp = calculer_esperance_mathematique()

    st.markdown("### 📝 Mathématiques du Loto")

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("💸 Coût grille", f"{esp['cout_grille']:.2f}€")
            st.metric("📝‰ Espérance", f"{esp['esperance']:+.4f}€")

        with col2:
            st.metric("🎯 Gains espérés", f"{esp['gains_esperes']:.4f}€")
            st.metric("📊 Perte moyenne", f"{esp['perte_moyenne_pct']:.1f}%")

        st.info(esp["conclusion"])

    st.divider()

    st.markdown("### 🎲 Probabilités de gain")

    df_probas = pd.DataFrame(
        [
            {
                "Rang": rang,
                "Gains": f"{GAINS_PAR_RANG.get(rang, 'Jackpot'):,}€"
                if GAINS_PAR_RANG.get(rang)
                else "Jackpot",
                "Probabilité": proba,
            }
            for rang, proba in esp["probabilites"].items()
        ]
    )

    st.dataframe(df_probas, hide_index=True, width="stretch")

    st.warning(
        "⚠️ **Rappel**: Vous avez plus de chances de mourir d'une chute de météorite (1/700 000) "
        "que de gagner le jackpot du Loto (1/19 068 840)!"
    )
