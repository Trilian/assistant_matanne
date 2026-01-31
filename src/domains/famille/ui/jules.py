"""
Module Jules - Suivi développement et jalons

Affiche:
- Profil Jules
- Jalons atteints
- Apprentissages
- Activités adaptées à l'âge
"""

import streamlit as st
from src.core.database import get_db_context
from src.core.models import ChildProfile


def app():
    """Point d'entrée module jules"""
    st.title("👶 Jules - Suivi Développement")
    
    try:
        with get_db_context() as db:
            # Récupérer profil Jules
            profil = db.query(ChildProfile).filter_by(is_active=True).first()
            
            if profil:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📅 Âge", f"{profil.age_months} mois")
                
                with col2:
                    st.metric("👶 Prénom", profil.name)
                
                with col3:
                    st.metric("🎂 Anniversaire", profil.birth_date.strftime("%d/%m/%Y"))
                
                st.divider()
                st.info("📌 Module en cours de développement - Jalons et activités à venir")
            else:
                st.warning("⚠️ Profil Jules non configuré")
                if st.button("➕ Créer le profil"):
                    st.info("Redirection vers configuration...")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
