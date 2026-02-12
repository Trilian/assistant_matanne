"""
Gestion des alertes - Onglet alertes de l'inventaire.
Affiche les articles en alerte avec actions rapides.
"""

import streamlit as st

from src.services.inventaire import get_inventaire_service
from .utilitaires import _prepare_alert_dataframe


def render_alertes():
    """Affiche les articles en alerte avec actions rapides"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("âŒ Service inventaire indisponible")
        return
    
    try:
        alertes = service.get_alertes()
        
        if not any(alertes.values()):
            st.success("âœ¨ Aucune alerte! Votre inventaire est en bon Ãetat.")
            return
        
        # ARTICLES CRITIQUES
        if alertes["critique"]:
            st.error(f"âŒ {len(alertes['critique'])} articles en stock critique")
            df = _prepare_alert_dataframe(alertes["critique"])
            st.dataframe(df, width='stretch', hide_index=True)
        
        st.divider()
        
        # STOCK BAS
        if alertes["stock_bas"]:
            st.warning(f"âš  {len(alertes['stock_bas'])} articles avec stock faible")
            df = _prepare_alert_dataframe(alertes["stock_bas"])
            st.dataframe(df, width='stretch', hide_index=True)
        
        st.divider()
        
        # PÉREMPTION PROCHE
        if alertes["peremption_proche"]:
            st.warning(f"â° {len(alertes['peremption_proche'])} articles proche pÃeremption")
            df = _prepare_alert_dataframe(alertes["peremption_proche"])
            st.dataframe(df, width='stretch', hide_index=True)
    
    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")


__all__ = ["render_alertes"]
