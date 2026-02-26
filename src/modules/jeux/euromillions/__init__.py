"""
Module Euromillions - Analyse statistique et simulation de stratégies

⚠️ DISCLAIMER: L'Euromillions est un jeu de hasard pur.
Aucune stratégie ne peut prédire les résultats.
Ce module est à but éducatif et de divertissement.

Fonctionnalités:
- Historique des tirages avec statistiques (1-50 + étoiles 1-12)
- Analyse des fréquences numéros et étoiles
- Génération de grilles selon différentes stratégies
- Suivi des grilles virtuelles
- Simulation et backtesting (6 stratégies)
- Espérance mathématique et probabilités
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

from .crud import (
    ajouter_tirage,
    charger_grilles_utilisateur,
    charger_tirages_db,
    enregistrer_grille,
)
from .generateur import afficher_generateur_grilles, afficher_mes_grilles
from .scraper import charger_tirages_euromillions
from .simulation import afficher_gestion_tirages, afficher_simulation
from .statistiques import (
    afficher_dernier_tirage,
    afficher_esperance,
    afficher_statistiques_frequences,
)

_keys = KeyNamespace("euromillions")


def _charger_tirages(limite: int = 200) -> list[dict]:
    """Charge les tirages: BD d'abord, puis scraper en fallback."""
    tirages = charger_tirages_db(limite=limite)
    if not tirages:
        tirages = charger_tirages_euromillions(limite=limite)
    return tirages


@profiler_rerun("euromillions")
def app():
    """Point d'entrée du module Euromillions"""

    st.title("🌟 Euromillions - Analyse & Simulation")
    st.caption("5 numéros (1-50) + 2 étoiles (1-12) — Tirages mardi et vendredi")

    # Avertissement
    with st.expander("⚠️ Avertissement important", expanded=False):
        st.markdown("""
        **L'Euromillions est un jeu de hasard pur.**

        - Probabilité de jackpot: **1 sur 139 838 160**
        - Chaque tirage est **totalement indépendant** des précédents
        - L'espérance mathématique est **très négative** (~-60%)
        - C'est environ **7× pire** que le Loto français

        Ce module est à but **éducatif et de divertissement**.
        Ne jouez que ce que vous pouvez vous permettre de perdre.
        """)

    # Charger données
    tirages = _charger_tirages(limite=200)

    # Tabs principaux avec deep linking URL
    TAB_LABELS = [
        "📊 Statistiques",
        "🎲 Générer Grille",
        "🎟️ Mes Grilles",
        "🔬 Simulation",
        "📐 Maths",
        "⚙️ Tirages",
    ]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    # TAB 1: STATISTIQUES
    with tabs[0]:
        with error_boundary("euro_statistiques"):
            afficher_dernier_tirage(tirages)
            st.divider()
            afficher_statistiques_frequences(tirages)

    # TAB 2: GÉNÉRATION
    with tabs[1]:
        with error_boundary("euro_generateur"):
            afficher_generateur_grilles(tirages)

    # TAB 3: MES GRILLES
    with tabs[2]:
        with error_boundary("euro_mes_grilles"):
            afficher_mes_grilles()

    # TAB 4: SIMULATION
    with tabs[3]:
        with error_boundary("euro_simulation"):
            afficher_simulation()

    # TAB 5: MATHÉMATIQUES
    with tabs[4]:
        with error_boundary("euro_maths"):
            afficher_esperance()

    # TAB 6: GESTION TIRAGES
    with tabs[5]:
        with error_boundary("euro_tirages"):
            afficher_gestion_tirages()


def main():
    app()


__all__ = [
    "app",
    "main",
    "charger_tirages_db",
    "charger_tirages_euromillions",
    "charger_grilles_utilisateur",
    "enregistrer_grille",
    "ajouter_tirage",
]
