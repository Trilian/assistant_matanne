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
        st.caption(f"💚 {parametres.APP_NAME} v{parametres.APP_VERSION} | Lazy Loading Active")

    with col2:
        if st.button("🐛 Bug"):
            st.info("GitHub Issues")

    with col3:
        if st.button("ℹ️ À propos"):
            with st.expander("À propos", expanded=True):
                st.markdown(
                    f"""
                ### {parametres.APP_NAME}
                **Version:** {parametres.APP_VERSION}

                **Stack:**
                - Frontend: Streamlit
                - Database: Supabase PostgreSQL
                - IA: Mistral AI
                - ⚡ Lazy Loading: Active
                """
                )
