"""
Module Saisonnalité — Calendrier des fruits et légumes de saison.

Affiche les fruits et légumes de saison mois par mois,
avec conseils de conservation et idées recettes.
"""

import logging
from datetime import date

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("saisonnalite")

# Base de données fruits & légumes par mois (France métropolitaine)
SAISONS = {
    1: {
        "fruits": [
            "🍊 Orange",
            "🍋 Citron",
            "🍐 Poire",
            "🍎 Pomme",
            "🥝 Kiwi",
            "🍊 Clémentine",
            "🍊 Mandarine",
        ],
        "legumes": [
            "🥕 Carotte",
            "🥬 Poireau",
            "🥦 Chou",
            "🥔 Pomme de terre",
            "🧅 Oignon",
            "🧄 Ail",
            "🫛 Endive",
            "🥬 Mâche",
            "🎃 Courge",
            "🥬 Épinard",
        ],
    },
    2: {
        "fruits": ["🍊 Orange", "🍋 Citron", "🍐 Poire", "🍎 Pomme", "🥝 Kiwi"],
        "legumes": [
            "🥕 Carotte",
            "🥬 Poireau",
            "🥦 Chou",
            "🥔 Pomme de terre",
            "🫛 Endive",
            "🥬 Mâche",
            "🧅 Navet",
            "🥬 Épinard",
        ],
    },
    3: {
        "fruits": ["🍊 Orange", "🍋 Citron", "🍎 Pomme", "🥝 Kiwi"],
        "legumes": [
            "🥕 Carotte",
            "🥬 Poireau",
            "🥦 Chou-fleur",
            "🥬 Épinard",
            "🫛 Radis",
            "🥬 Cresson",
            "🥬 Oseille",
        ],
    },
    4: {
        "fruits": ["🍓 Fraise", "🍋 Citron", "🍎 Pomme"],
        "legumes": [
            "🥕 Carotte",
            "🫛 Radis",
            "🥬 Épinard",
            "🥦 Artichaut",
            "🫛 Asperge",
            "🥬 Cresson",
            "🧅 Oignon nouveau",
            "🥬 Roquette",
        ],
    },
    5: {
        "fruits": ["🍓 Fraise", "🍒 Cerise", "🍋 Citron"],
        "legumes": [
            "🫛 Asperge",
            "🥦 Artichaut",
            "🫛 Radis",
            "🥬 Épinard",
            "🥬 Laitue",
            "🫛 Petit pois",
            "🫘 Fève",
            "🥒 Concombre",
        ],
    },
    6: {
        "fruits": ["🍓 Fraise", "🍒 Cerise", "🍑 Abricot", "🫐 Framboise", "🍈 Melon"],
        "legumes": [
            "🥒 Courgette",
            "🫑 Poivron",
            "🍅 Tomate",
            "🥒 Concombre",
            "🫛 Petit pois",
            "🫘 Haricot vert",
            "🥦 Artichaut",
            "🥬 Laitue",
        ],
    },
    7: {
        "fruits": [
            "🍑 Pêche",
            "🍑 Abricot",
            "🫐 Framboise",
            "🫐 Myrtille",
            "🍈 Melon",
            "🍓 Fraise",
            "🍇 Raisin",
            "🍑 Nectarine",
        ],
        "legumes": [
            "🍅 Tomate",
            "🥒 Courgette",
            "🫑 Poivron",
            "🍆 Aubergine",
            "🥒 Concombre",
            "🫘 Haricot vert",
            "🧅 Oignon",
            "🌽 Maïs",
        ],
    },
    8: {
        "fruits": [
            "🍑 Pêche",
            "🍑 Nectarine",
            "🍇 Raisin",
            "🍑 Abricot",
            "🫐 Myrtille",
            "🍈 Melon",
            "🍉 Pastèque",
            "🫐 Mûre",
            "🍐 Poire",
        ],
        "legumes": [
            "🍅 Tomate",
            "🥒 Courgette",
            "🫑 Poivron",
            "🍆 Aubergine",
            "🫘 Haricot vert",
            "🌽 Maïs",
            "🥕 Carotte",
            "🥬 Laitue",
        ],
    },
    9: {
        "fruits": [
            "🍇 Raisin",
            "🍐 Poire",
            "🍎 Pomme",
            "🍑 Pêche",
            "🍈 Melon",
            "🫐 Mûre",
            "🍑 Prune",
        ],
        "legumes": [
            "🍅 Tomate",
            "🥒 Courgette",
            "🫑 Poivron",
            "🍆 Aubergine",
            "🎃 Potiron",
            "🥬 Poireau",
            "🥦 Chou",
            "🥕 Carotte",
            "🫘 Haricot vert",
        ],
    },
    10: {
        "fruits": ["🍎 Pomme", "🍐 Poire", "🍇 Raisin", "🌰 Châtaigne", "🥜 Noix", "🍊 Coing"],
        "legumes": [
            "🎃 Potiron",
            "🎃 Courge",
            "🥬 Poireau",
            "🥕 Carotte",
            "🥦 Chou",
            "🥦 Brocoli",
            "🫛 Endive",
            "🧅 Navet",
            "🥔 Pomme de terre",
        ],
    },
    11: {
        "fruits": ["🍎 Pomme", "🍐 Poire", "🍊 Clémentine", "🍊 Orange", "🥝 Kiwi", "🌰 Châtaigne"],
        "legumes": [
            "🎃 Courge",
            "🥬 Poireau",
            "🥕 Carotte",
            "🥦 Chou",
            "🫛 Endive",
            "🧅 Navet",
            "🥬 Mâche",
            "🥬 Épinard",
            "🥔 Pomme de terre",
        ],
    },
    12: {
        "fruits": [
            "🍊 Orange",
            "🍊 Clémentine",
            "🍊 Mandarine",
            "🍎 Pomme",
            "🍐 Poire",
            "🥝 Kiwi",
            "🍋 Citron",
        ],
        "legumes": [
            "🥬 Poireau",
            "🥕 Carotte",
            "🎃 Courge",
            "🥦 Chou",
            "🫛 Endive",
            "🥬 Mâche",
            "🧅 Navet",
            "🥔 Pomme de terre",
            "🥬 Épinard",
        ],
    },
}

MOIS_NOMS = [
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


@profiler_rerun("saisonnalite")
def app():
    """Point d'entrée module Saisonnalité."""
    st.title("🥕 Fruits & Légumes de Saison")
    st.caption("Mangez local et de saison toute l'année")

    with error_boundary(titre="Erreur saisonnalité"):
        mois_actuel = date.today().month

        tab1, tab2 = st.tabs(["📅 Ce mois-ci", "📊 Calendrier complet"])

        with tab1:
            _afficher_mois(mois_actuel)

        with tab2:
            _calendrier_complet(mois_actuel)


def _afficher_mois(mois: int):
    """Affiche les produits de saison pour un mois donné."""
    mois_select = st.selectbox(
        "Mois",
        options=range(1, 13),
        format_func=lambda m: f"{MOIS_NOMS[m]} {'📍' if m == date.today().month else ''}",
        index=mois - 1,
        key=_keys("mois_select"),
    )

    saison = SAISONS.get(mois_select, {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍎 Fruits")
        fruits = saison.get("fruits", [])
        if fruits:
            for f in fruits:
                st.markdown(f"- {f}")
        else:
            st.info("Pas de données pour ce mois")

        st.metric("Total fruits", len(fruits))

    with col2:
        st.subheader("🥬 Légumes")
        legumes = saison.get("legumes", [])
        if legumes:
            for l in legumes:
                st.markdown(f"- {l}")
        else:
            st.info("Pas de données pour ce mois")

        st.metric("Total légumes", len(legumes))


def _calendrier_complet(mois_actuel: int):
    """Vue calendrier avec tous les mois."""
    st.subheader("📊 Vue annuelle")

    # Tableau récapitulatif
    type_affichage = st.radio(
        "Afficher",
        options=["Fruits", "Légumes", "Les deux"],
        horizontal=True,
        key=_keys("type_cal"),
    )

    for mois_num in range(1, 13):
        saison = SAISONS.get(mois_num, {})
        est_actuel = mois_num == mois_actuel
        label = f"{'📍 ' if est_actuel else ''}{MOIS_NOMS[mois_num]}"

        with st.expander(label, expanded=est_actuel):
            items = []
            if type_affichage in ("Fruits", "Les deux"):
                items.extend(saison.get("fruits", []))
            if type_affichage in ("Légumes", "Les deux"):
                items.extend(saison.get("legumes", []))

            if items:
                # Affichage en colonnes
                nb_cols = 4
                cols = st.columns(nb_cols)
                for i, item in enumerate(items):
                    with cols[i % nb_cols]:
                        st.markdown(item)
            else:
                st.caption("Aucun produit")
