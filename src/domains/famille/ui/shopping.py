"""
Module Shopping - Achats centralisés (Jules, famille, maison)

Affiche:
- Listes de courses
- Articles à acheter
- Budgets par catégorie
"""

import streamlit as st
from src.core.database import get_db_context


def app():
    """Point d'entrée module shopping"""
    st.title("🛍️ Achats Centralisés")
    
    try:
        tab1, tab2, tab3 = st.tabs(["📑 Listes", "📄 Historique", "📊 Budget"])
        
        with tab1:
            st.subheader("📑 Listes de courses")
            st.info("📌 Module en cours de développement")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Nouvelle liste"):
                    st.info("Création nouvelle liste")
            
            with col2:
                if st.button("🤖 Suggérer avec IA"):
                    st.info("Génération suggestions IA")
        
        with tab2:
            st.subheader("📄 Historique achats")
            st.caption("Vos achats récents apparaissent ici")
        
        with tab3:
            st.subheader("📊 Budget courses")
            st.caption("Analyse budgétaire par catégorie")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
