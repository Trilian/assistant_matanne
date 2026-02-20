"""
Alertes - Composants d'affichage des alertes métier
Stock critique, péremption, notifications domaine
"""

import warnings
from typing import Any

import streamlit as st

from src.ui.registry import composant_ui


@composant_ui(
    "alertes",
    exemple='alerte_stock([{"nom": "Lait", "statut": "critique"}])',
    tags=["alert", "stock"],
)
def alerte_stock(articles: list[dict[str, Any]], cle: str = "alerte_stock") -> None:
    """
    Affiche une alerte de stock critique ou péremption

    Args:
        articles: Liste des articles en alerte
        cle: Déprécié, ignoré. Conservé pour rétrocompatibilité.
    """
    if cle != "alerte_stock":
        warnings.warn(
            "Le paramètre 'cle' de alerte_stock() est déprécié et ignoré.",
            DeprecationWarning,
            stacklevel=2,
        )
    if not articles:
        return

    with st.container():
        for _i, article in enumerate(articles):
            statut = article.get("statut", "unknown")
            nom = article.get("nom", "Article sans nom")

            if statut == "critique":
                st.warning(f"🔴 Stock critique: {nom}", icon="⚠️")
            elif statut == "peremption_proche":
                st.info(f"⏰ Péremption proche: {nom}", icon="ℹ️")
