"""
Paramètres - Configuration Budget
Catégories de dépenses et sauvegarde des données
"""

import streamlit as st

from src.ui import etat_vide
from src.ui.feedback import afficher_erreur, afficher_succes, spinner_intelligent
from src.ui.fragments import ui_fragment


@ui_fragment
def afficher_budget_config():
    """Configuration du budget."""

    st.markdown("### 💰 Budget")

    # Section Budget
    st.markdown("#### 📈 Catégories de dépenses")

    try:
        from src.services.famille.budget import CategorieDepense

        # Mapping complet avec accents
        emoji_map = {
            "alimentation": "🍞",
            "courses": "🛒",
            "maison": "🏠",
            "santé": "🏥",
            "transport": "🚗",
            "loisirs": "🎮",
            "vêtements": "👕",
            "enfant": "👶",
            "éducation": "📚",
            "services": "🔧",
            "impôts": "📋",
            "épargne": "💰",
            "gaz": "🔥",
            "electricite": "⚡",
            "eau": "💧",
            "internet": "🌐",
            "loyer": "🏘️",
            "assurance": "🛡️",
            "taxe_fonciere": "🏛️",
            "creche": "🧒",
            "autre": "📦",
        }

        # Affichage en grille
        categories = list(CategorieDepense)
        cols = st.columns(4)
        for i, cat in enumerate(categories):
            with cols[i % 4]:
                emoji = emoji_map.get(cat.value, "📦")
                st.markdown(f"{emoji} {cat.value.replace('_', ' ').capitalize()}")

        st.info("👉 Accède au module **Budget** dans le menu Famille pour gérer tes dépenses")

    except ImportError:
        st.warning("Module budget non disponible")

    st.markdown("---")

    # Lien vers l'onglet Sauvegarde dédié
    st.caption("💾 Pour la gestion complète des sauvegardes, utilisez l'onglet **Sauvegarde**.")
