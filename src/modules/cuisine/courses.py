"""
Module Courses - Gestion de la liste de courses
"""

import streamlit as st
from src.services.courses import get_courses_service


def app():
    """Point d'entrée module courses"""
    st.title("🛒 Courses")
    st.caption("Gestion de votre liste de courses")

    tab_liste, tab_historique, tab_suggestions = st.tabs(["📋 Liste", "📚 Historique", "✨ Suggestions"])

    with tab_liste:
        render_liste()

    with tab_historique:
        st.info("📚 Historique des listes - À implémenter")

    with tab_suggestions:
        st.info("✨ Suggestions intelligentes - À implémenter")


def render_liste():
    """Affiche la liste de courses"""
    service = get_courses_service()
    
    if service is None:
        st.error("❌ Service courses indisponible")
        return
    
    liste = service.get_liste_courses()
    
    if not liste:
        st.info("Liste de courses vide")
        return
    
    # Filtrer par statut
    col1, col2 = st.columns(2)
    
    with col1:
        # Non achetés
        non_achetes = [a for a in liste if not a.get("achete")]
        st.subheader(f"📝 À acheter ({len(non_achetes)})")
        
        for article in non_achetes:
            priorite = article.get("priorite", "moyenne")
            emoji = "🔴" if priorite == "haute" else "🟡" if priorite == "moyenne" else "🟢"
            st.write(f"{emoji} {article.get('ingredient_nom')} - {article.get('quantite_necessaire')}")
    
    with col2:
        # Achetés
        achetes = [a for a in liste if a.get("achete")]
        st.subheader(f"✅ Acheté ({len(achetes)})")
        
        for article in achetes[:5]:
            st.write(f"✓ {article.get('ingredient_nom')}")
