"""
Footer de l'application.
"""

import streamlit as st

from src.core.config import obtenir_parametres


def afficher_footer():
    """Affiche le footer simplifié."""
    parametres = obtenir_parametres()
    
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.caption(f"ðŸ’š {parametres.APP_NAME} v{parametres.APP_VERSION} | Lazy Loading Active")

    with col2:
        if st.button("ðŸ› Bug"):
            st.info("GitHub Issues")

    with col3:
        if st.button("â„¹ï¸ Ã€ propos"):
            with st.expander("Ã€ propos", expanded=True):
                st.markdown(
                    f"""
                ### {parametres.APP_NAME}
                **Version:** {parametres.APP_VERSION}
                
                **Stack:**
                - Frontend: Streamlit
                - Database: Supabase PostgreSQL
                - IA: Mistral AI
                - âš¡ Lazy Loading: Active
                """
                )
