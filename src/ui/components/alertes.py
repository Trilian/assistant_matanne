"""
Alertes - Composants d'affichage des alertes métier
Stock critique, péremption, notifications domaine
"""

from typing import Any

import streamlit as st


def alerte_stock(articles: list[dict[str, Any]], cle: str = "alerte_stock") -> None:
    """
    Affiche une alerte de stock critique ou péremption

    Args:
        articles: Liste des articles en alerte
        cle: Clé unique Streamlit pour le widget
    """
    if not articles:
        return

    with st.container():
        for i, article in enumerate(articles):
            statut = article.get("statut", "unknown")
            nom = article.get("nom", "Article sans nom")

            if statut == "critique":
                st.warning(f"🔴 Stock critique: {nom}", icon="⚠️")
            elif statut == "peremption_proche":
                st.info(f"⏰ Péremption proche: {nom}", icon="ℹ️")
