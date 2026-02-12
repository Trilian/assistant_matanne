"""
Suggestions IA - Onglet suggestions IA de l'inventaire.
Affiche les suggestions d'achats basÃees sur l'IA.
"""

import logging
import streamlit as st

from src.services.inventaire import get_inventaire_service

logger = logging.getLogger(__name__)


def render_suggestions_ia():
    """Affiche les suggestions IA pour les courses"""
    service = get_inventaire_service()
    
    if service is None:
        st.error("âŒ Service inventaire indisponible")
        return
    
    st.info("ðŸ¤– Suggestions IA basÃees sur l'Ãetat de votre inventaire")
    
    # Initialiser l'Ãetat
    if "suggestions_data" not in st.session_state:
        st.session_state.suggestions_data = None
    
    if st.button("ðŸ›’ GÃenÃerer les suggestions", width='stretch'):
        try:
            with st.spinner("GÃenÃeration des suggestions..."):
                suggestions = service.suggerer_courses_ia()
            
            if not suggestions:
                st.warning("âš ï¸ Aucune suggestion gÃenÃerÃee. VÃerifiez votre inventaire.")
            else:
                st.session_state.suggestions_data = suggestions
                st.rerun()
        
        except Exception as e:
            st.error(f"âŒ Erreur: {str(e)}")
            logger.error(f"Erreur suggestions IA: {e}", exc_info=True)
    
    # Afficher les suggestions stockÃees
    if st.session_state.get("suggestions_data"):
        suggestions = st.session_state.suggestions_data
        
        if suggestions:
            st.success(f"âœ¨ {len(suggestions)} suggestions gÃenÃerÃees")
            
            # Grouper par prioritÃe
            by_priority = {}
            for sugg in suggestions:
                p = sugg.priorite
                if p not in by_priority:
                    by_priority[p] = []
                by_priority[p].append(sugg)
            
            # Afficher par prioritÃe
            for priority in ["haute", "moyenne", "basse"]:
                if priority in by_priority:
                    icon = "âŒ" if priority == "haute" else "âš ï¸" if priority == "moyenne" else "âœ…"
                    with st.expander(f"{icon} PrioritÃe {priority.upper()} ({len(by_priority[priority])})"):
                        for sugg in by_priority[priority]:
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.write(f"**{sugg.nom}**")
                            with col2:
                                st.write(f"{sugg.quantite} {sugg.unite}")
                            with col3:
                                st.write(f"ðŸ“ {sugg.rayon}")
                            with col4:
                                if st.button("âœ¨ Ajouter", key=f"add_{sugg.nom}"):
                                    st.success(f"âœ¨ {sugg.nom} ajoutÃe aux courses")
        else:
            st.warning("Aucune suggestion gÃenÃerÃee")


__all__ = ["render_suggestions_ia"]
