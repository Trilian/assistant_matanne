"""Script to rewrite historique.py - removing direct DB access."""

import os

new_content = '''"""
Historique des courses.
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.services.cuisine.courses import obtenir_service_courses
from src.ui.components.atoms import etat_vide

from .utils import PRIORITY_EMOJIS

logger = logging.getLogger(__name__)


def afficher_historique():
    """Historique des listes de courses"""
    service = obtenir_service_courses()

    st.subheader("\U0001f4cb Historique des courses")

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=datetime.now() - timedelta(days=30))
    with col2:
        date_fin = st.date_input("Au", value=datetime.now())

    try:
        # Via service - plus de DB directe
        articles_achetes = service.obtenir_historique_achats(
            date_debut=date_debut,
            date_fin=date_fin,
        )

        if not articles_achetes:
            etat_vide("Aucun achat pendant cette p\u00e9riode", "\U0001f6d2")
            return

        # Statistiques
        total_articles = len(articles_achetes)
        rayons_utilises = set(
            a["rayon_magasin"] for a in articles_achetes if a.get("rayon_magasin")
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("\U0001f4ca Articles achet\u00e9s", total_articles)
        with col2:
            st.metric("\U0001f36a\\' Rayons diff\u00e9rents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.get("priorite") == "haute"])
            st.metric("\U0001f534 Haute priorit\u00e9", priorite_haute)

        st.divider()

        # Tableau d\u00e9taill\u00e9
        st.subheader("\U0001f4cb D\u00e9tail des achats")

        df = pd.DataFrame(
            [
                {
                    "Article": a.get("ingredient_nom", "N/A"),
                    "Quantit\u00e9": f"{a.get('quantite_necessaire', '')} {a.get('unite', '')}",
                    "Priorit\u00e9": PRIORITY_EMOJIS.get(a.get("priorite", ""), "\u26ab")
                    + " "
                    + a.get("priorite", ""),
                    "Rayon": a.get("rayon_magasin") or "N/A",
                    "Achet\u00e9 le": a["achete_le"].strftime("%d/%m/%Y %H:%M")
                    if a.get("achete_le")
                    else "N/A",
                    "IA": "\u23f0" if a.get("suggere_par_ia") else "",
                }
                for a in articles_achetes
            ]
        )

        st.dataframe(df, width="stretch")

        # Export CSV
        if df is not None and not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="\U0001f4e5 T\u00e9l\u00e9charger en CSV",
                data=csv,
                file_name=f"historique_courses_{date_debut}_{date_fin}.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"\u274c Erreur: {str(e)}")
        logger.error(f"Erreur historique: {e}")


__all__ = ["afficher_historique"]
'''

filepath = os.path.join("src", "modules", "cuisine", "courses", "historique.py")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
print(f"Rewrote {filepath}")
