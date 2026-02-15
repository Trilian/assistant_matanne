"""
Module Loto - Analyse statistique et simulation de stratégies

⚠️ DISCLAIMER: Le Loto est un jeu de hasard pur.
Aucune stratégie ne peut prédire les résultats.
Ce module est à but éducatif et de divertissement.

Fonctionnalités:
- Historique des tirages avec statistiques
- Analyse des fréquences (curiosité mathématique)
- Génération de grilles selon différentes stratégies
- Suivi des "paris virtuels" pour tester les stratégies
- Simulation et backtesting
"""

from ._common import st
from .crud import ajouter_tirage, enregistrer_grille
from .generateur import afficher_generateur_grilles, afficher_mes_grilles
from .simulation import afficher_gestion_tirages, afficher_simulation
from .statistiques import (
    afficher_dernier_tirage,
    afficher_esperance,
    afficher_statistiques_frequences,
)

# Import des fonctions pour exposer l'API publique
from .sync import sync_tirages_loto
from .utils import charger_grilles_utilisateur, charger_tirages


def app():
    """Point d'entrée du module Loto"""

    st.title("🎰 Loto - Analyse & Simulation")
    st.caption("Analysez les statistiques et testez vos stratégies (virtuellement)")

    # Avertissement
    with st.expander("⚠️ Avertissement important", expanded=False):
        st.markdown("""
        **Le Loto est un jeu de hasard pur.**

        - Chaque tirage est **totalement indépendant** des précédents
        - Un numéro "en retard" n'a **pas plus de chances** de sortir
        - Aucune stratégie ne peut **prédire** les résultats
        - L'espérance mathématique est **négative** (vous perdez en moyenne)

        Ce module est à but **éducatif et de divertissement**.
        Ne jouez que ce que vous pouvez vous permettre de perdre.
        """)

    # Charger données
    tirages = charger_tirages(limite=200)

    # Tabs principaux
    tabs = st.tabs(
        [
            "📊 Statistiques",
            "🎲 Générer Grille",
            "🎫 Mes Grilles",
            "🔬 Simulation",
            "📊 Maths",
            "⚙️ Tirages",
        ]
    )

    # TAB 1: STATISTIQUES
    with tabs[0]:
        afficher_dernier_tirage(tirages)
        st.divider()
        afficher_statistiques_frequences(tirages)

    # TAB 2: GÉNÉRATION
    with tabs[1]:
        afficher_generateur_grilles(tirages)

    # TAB 3: MES GRILLES
    with tabs[2]:
        afficher_mes_grilles()

    # TAB 4: SIMULATION
    with tabs[3]:
        afficher_simulation()

    # TAB 5: MATHÉMATIQUES
    with tabs[4]:
        afficher_esperance()

    # TAB 6: GESTION TIRAGES
    with tabs[5]:
        afficher_gestion_tirages()


# Alias
def main():
    app()


__all__ = [
    # Entry point
    "app",
    "main",
    # Sync
    "sync_tirages_loto",
    # Helpers
    "charger_tirages",
    "charger_grilles_utilisateur",
    # CRUD
    "ajouter_tirage",
    "enregistrer_grille",
    # UI
    "afficher_dernier_tirage",
    "afficher_statistiques_frequences",
    "afficher_esperance",
    "afficher_generateur_grilles",
    "afficher_mes_grilles",
    "afficher_simulation",
    "afficher_gestion_tirages",
]
