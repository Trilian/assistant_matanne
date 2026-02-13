"""
Module Achats Famille - Wishlist centralisee.

Categories:
- Jules (vetements, jouets, equipement)
- Nous (jeux, loisirs, equipement)
- Wishlist & priorites
"""

import streamlit as st

from .components import (
    render_achat_card,
    render_add_form,
    render_dashboard,
    render_historique,
    render_liste_groupe,
    render_par_magasin,
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
            "💨â€👩â€💧 Nous",
            "🏪 Par magasin",
            "➕ Ajouter",
            "📝œ Historique",
        ]
    )

    with tabs[0]:
        render_dashboard()

    with tabs[1]:
        render_liste_groupe("jules", "👶 Achats pour Jules")

    with tabs[2]:
        render_liste_groupe("nous", "💨â€👩â€💧 Achats pour nous")

    with tabs[3]:
        render_par_magasin()

    with tabs[4]:
        render_add_form()

    with tabs[5]:
        render_historique()


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
    "render_dashboard",
    "render_liste_groupe",
    "render_achat_card",
    "render_add_form",
    "render_historique",
    "render_par_magasin",
]
