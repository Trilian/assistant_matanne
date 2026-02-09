"""
Module Achats Famille - Wishlist centralisée.

Catégories:
- 👶 Jules (vêtements, jouets, équipement)
- 👨‍👩‍👧 Nous (jeux, loisirs, équipement)
- 📋 Wishlist & priorités
"""

from ._common import st

# Import des fonctions pour exposer l'API publique
from .helpers import (
    get_all_purchases, get_purchases_by_category, get_purchases_by_groupe,
    get_stats, mark_as_bought, delete_purchase
)
from .components import (
    render_dashboard, render_liste_groupe, render_achat_card,
    render_add_form, render_historique, render_par_magasin
)


def app():
    """Point d'entrée du module Achats Famille"""
    st.title("🛍️ Achats Famille")
    
    stats = get_stats()
    st.caption(f"📋 {stats['en_attente']} en attente • 💰 ~{stats['total_estime']:.0f}€")
    
    # Tabs
    tabs = st.tabs([
        "📊 Dashboard", 
        "👶 Jules", 
        "👨‍👩‍👧 Nous", 
        "🏪 Par magasin",
        "➕ Ajouter",
        "📜 Historique"
    ])
    
    with tabs[0]:
        render_dashboard()
    
    with tabs[1]:
        render_liste_groupe("jules", "👶 Achats pour Jules")
    
    with tabs[2]:
        render_liste_groupe("nous", "👨‍👩‍👧 Achats pour nous")
    
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
