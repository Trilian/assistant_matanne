"""
Historique des courses.
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.services.cuisine.courses import obtenir_service_courses
from src.ui.components.atoms import etat_vide
from src.ui.fragments import ui_fragment

from .utils import PRIORITY_EMOJIS

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_historique():
    """Historique des listes de courses"""
    service = obtenir_service_courses()

    st.subheader("📋 Historique des courses")

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
            etat_vide("Aucun achat pendant cette période", "🛒")
            return

        # Statistiques
        total_articles = len(articles_achetes)
        rayons_utilises = set(
            a["rayon_magasin"] for a in articles_achetes if a.get("rayon_magasin")
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Articles achetés", total_articles)
        with col2:
            st.metric("🍪' Rayons différents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.get("priorite") == "haute"])
            st.metric("🔴 Haute priorité", priorite_haute)

        st.divider()

        # Tableau détaillé
        st.subheader("📋 Détail des achats")

        df = pd.DataFrame(
            [
                {
                    "Article": a.get("ingredient_nom", "N/A"),
                    "Quantité": f"{a.get('quantite_necessaire', '')} {a.get('unite', '')}",
                    "Priorité": PRIORITY_EMOJIS.get(a.get("priorite", ""), "⚫")
                    + " "
                    + a.get("priorite", ""),
                    "Rayon": a.get("rayon_magasin") or "N/A",
                    "Acheté le": a["achete_le"].strftime("%d/%m/%Y %H:%M")
                    if a.get("achete_le")
                    else "N/A",
                    "IA": "⏰" if a.get("suggere_par_ia") else "",
                }
                for a in articles_achetes
            ]
        )

        st.dataframe(df, width="stretch")

        # Export CSV
        if df is not None and not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"historique_courses_{date_debut}_{date_fin}.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur historique: {e}")


__all__ = ["afficher_historique"]
