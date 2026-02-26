"""
UI Générateur de grilles Euromillions
"""

import logging

import streamlit as st

from src.ui.keys import KeyNamespace

from .crud import charger_grilles_utilisateur, enregistrer_grille
from .frequences import analyser_patterns_tirages, calculer_frequences_numeros
from .generation import (
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_ecart,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)

logger = logging.getLogger(__name__)
_keys = KeyNamespace("euromillions_gen")


def afficher_generateur_grilles(tirages: list[dict]) -> None:
    """Interface de génération de grilles Euromillions."""
    st.subheader("🎲 Générateur de grilles Euromillions")

    st.info(
        "⚠️ Ces stratégies ne modifient **PAS** vos chances de gagner. "
        "L'Euromillions est un jeu de hasard pur (~1/140M pour le jackpot)."
    )

    strategies = {
        "🎲 Aléatoire": "aleatoire",
        "🚫 Éviter populaires": "eviter_populaires",
        "⚖️ Équilibrée": "equilibree",
        "🔥 Numéros chauds": "chauds",
        "❄️ Numéros froids": "froids",
        "🔄 Mixte chauds/froids": "mixte",
        "⏰ En retard": "ecart",
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        strategie_label = st.selectbox(
            "Stratégie",
            list(strategies.keys()),
            key=_keys("strategie"),
        )
    with col2:
        nb_grilles = st.number_input(
            "Nombre de grilles",
            min_value=1,
            max_value=10,
            value=3,
            key=_keys("nb_grilles"),
        )

    strategie = strategies[strategie_label]

    if st.button("🎟️ Générer", type="primary", key=_keys("generer")):
        freq_data = calculer_frequences_numeros(tirages) if tirages else {}
        freq_numeros = freq_data.get("frequences_numeros", {})
        patterns = analyser_patterns_tirages(tirages) if tirages else {}

        grilles = []
        for _ in range(nb_grilles):
            if strategie == "aleatoire":
                grille = generer_grille_aleatoire()
            elif strategie == "eviter_populaires":
                grille = generer_grille_eviter_populaires()
            elif strategie == "equilibree":
                grille = generer_grille_equilibree(patterns)
            elif strategie in ("chauds", "froids", "mixte"):
                grille = generer_grille_chauds_froids(freq_numeros, strategie)
            elif strategie == "ecart":
                grille = generer_grille_ecart(freq_numeros)
            else:
                grille = generer_grille_aleatoire()
            grilles.append(grille)

        st.session_state[_keys("grilles_generees")] = grilles

    # Afficher les grilles générées
    grilles_gen = st.session_state.get(_keys("grilles_generees"), [])
    if grilles_gen:
        st.divider()
        for i, grille in enumerate(grilles_gen):
            numeros = grille.get("numeros", [])
            etoiles = grille.get("etoiles", [])
            source = grille.get("source", "?")
            note = grille.get("note", "")

            cols = st.columns([3, 2, 1])
            with cols[0]:
                nums_str = " - ".join(str(n) for n in numeros)
                stars_str = " ".join(f"★{e}" for e in etoiles)
                st.markdown(f"**Grille {i + 1}:** {nums_str} {stars_str}")
            with cols[1]:
                if note:
                    st.caption(note)
            with cols[2]:
                if st.button("💾", key=_keys(f"save_{i}"), help="Enregistrer"):
                    enregistrer_grille(
                        numeros=numeros,
                        etoiles=etoiles,
                        source=source,
                        est_virtuelle=True,
                    )
                    st.success("Grille enregistrée !")


def afficher_mes_grilles() -> None:
    """Affiche les grilles sauvegardées de l'utilisateur."""
    st.subheader("🎟️ Mes grilles Euromillions")

    grilles = charger_grilles_utilisateur(limite=50)
    if not grilles:
        st.info("Aucune grille enregistrée. Générez-en depuis l'onglet Générer !")
        return

    for grille in grilles:
        numeros = grille.get("numeros", [])
        etoiles = grille.get("etoiles", [])
        nums_str = " - ".join(str(n) for n in numeros)
        stars_str = " ".join(f"★{e}" for e in etoiles)
        gain = grille.get("gain")
        rang = grille.get("rang")
        source = grille.get("source", "?")
        date_str = str(grille.get("date_creation", ""))[:10]

        status = ""
        if gain is not None:
            status = f" → Rang {rang}, Gain: {gain:.2f}€" if rang else " → Aucun gain"
        elif grille.get("est_virtuelle"):
            status = " (virtuelle)"

        st.write(f"**{nums_str} {stars_str}** — {source} ({date_str}){status}")
