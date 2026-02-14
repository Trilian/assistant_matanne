"""
Suggestions IA - Onglet suggestions IA de l'inventaire.
Affiche les suggestions d'achats basées sur l'IA.
"""

import logging

import streamlit as st

from src.services.inventaire import get_inventaire_service

logger = logging.getLogger(__name__)


def render_suggestions_ia():
    """Affiche les suggestions IA pour les courses"""
    service = get_inventaire_service()

    if service is None:
        st.error("❌ Service inventaire indisponible")
        return

    st.info("🤖 Suggestions IA basées sur l'état de votre inventaire")

    # Initialiser l'état
    if "suggestions_data" not in st.session_state:
        st.session_state.suggestions_data = None

    if st.button("🛒 Générer les suggestions", width="stretch"):
        try:
            with st.spinner("Génération des suggestions..."):
                suggestions = service.suggerer_courses_ia()

            if not suggestions:
                st.warning("⚠️ Aucune suggestion générée. Vérifiez votre inventaire.")
            else:
                st.session_state.suggestions_data = suggestions
                st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur suggestions IA: {e}", exc_info=True)

    # Afficher les suggestions stockées
    if st.session_state.get("suggestions_data"):
        suggestions = st.session_state.suggestions_data

        if suggestions:
            st.success(f"⏰ {len(suggestions)} suggestions générées")

            # Grouper par priorité
            by_priority = {}
            for sugg in suggestions:
                p = sugg.priorite
                if p not in by_priority:
                    by_priority[p] = []
                by_priority[p].append(sugg)

            # Afficher par priorité
            for priority in ["haute", "moyenne", "basse"]:
                if priority in by_priority:
                    icon = "❌" if priority == "haute" else "⚠️" if priority == "moyenne" else "✅"
                    with st.expander(
                        f"{icon} Priorité {priority.upper()} ({len(by_priority[priority])})"
                    ):
                        for sugg in by_priority[priority]:
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.write(f"**{sugg.nom}**")
                            with col2:
                                st.write(f"{sugg.quantite} {sugg.unite}")
                            with col3:
                                st.write(f"📝 {sugg.rayon}")
                            with col4:
                                if st.button("⏰ Ajouter", key=f"add_{sugg.nom}"):
                                    st.success(f"⏰ {sugg.nom} ajouté aux courses")
        else:
            st.warning("Aucune suggestion générée")


__all__ = ["render_suggestions_ia"]
