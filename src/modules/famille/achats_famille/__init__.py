"""
Module Achats Famille - Wishlist centralisee.

Categories:
- Jules (vetements, jouets, equipement)
- Nous (jeux, loisirs, equipement)
- Wishlist & priorites
"""

import streamlit as st

from .components import (
    afficher_achat_card,
    afficher_add_form,
    afficher_dashboard,
    afficher_historique,
    afficher_liste_groupe,
    afficher_par_magasin,
)

# Import des fonctions pour exposer l'API publique
from .utils import (
    delete_purchase,
    get_all_purchases,
    get_purchases_by_category,
    get_purchases_by_groupe,
    get_stats,
    mark_as_bought,
)


def app():
    """Point d'entrée du module Achats Famille"""
    st.title("🛍️ Achats Famille")

    stats = get_stats()
    st.caption(f"📋 {stats['en_attente']} en attente • 💰 ~{stats['total_estime']:.0f}€")

    # Tabs
    tabs = st.tabs(
        [
            "📊 Dashboard",
            "👶 Jules",
            "👨‍👩‍👦 Nous",
            "🏪 Par magasin",
            "➕ Ajouter",
            "📜 Historique",
        ]
    )

    with tabs[0]:
        afficher_dashboard()

    with tabs[1]:
        afficher_liste_groupe("jules", "👶 Achats pour Jules")

    with tabs[2]:
        afficher_liste_groupe("nous", "👨‍👩‍👦 Achats pour nous")

    with tabs[3]:
        afficher_par_magasin()

    with tabs[4]:
        afficher_add_form()

    with tabs[5]:
        afficher_historique()


__all__ = [
    # Entry point
    "app",
    # Helpers
    "get_all_purchases",
    "get_purchases_by_category",
    "get_purchases_by_groupe",
    "get_stats",
    "mark_as_bought",
    "delete_purchase",
    # UI
    "afficher_dashboard",
    "afficher_liste_groupe",
    "afficher_achat_card",
    "afficher_add_form",
    "afficher_historique",
    "afficher_par_magasin",
]
