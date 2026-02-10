"""
Module Domain - Composants métier pour les domaines (cuisine, inventaire, etc.)
Affichage d'alertes spécifiques au domaine
"""

import streamlit as st
from typing import List, Dict, Any


def stock_alert(articles: List[Dict[str, Any]], key: str = "stock_alert") -> None:
    """
    Affiche une alerte de stock critique ou péremption
    
    Args:
        articles: Liste des articles en alerte
        key: Clé unique Streamlit pour le widget
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
