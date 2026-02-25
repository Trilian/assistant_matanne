"""
Module Recettes - Gestion complète des recettes

Fonctionnalités:
- Liste des recettes avec filtres et pagination
- Détail recette avec badges, historique et versions
- Ajout manuel de recettes
- Génération de recettes avec l'IA
- Génération d'images pour les recettes
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

# Re-export public API (lazy-imported dans app())
from .utils import formater_quantite

_keys = KeyNamespace("recettes")


@profiler_rerun("recettes")
def app():
    """Point d'entrée module recettes"""
    from src.services.cuisine.recettes import obtenir_service_recettes

    # Import externe pour l'onglet import
    from ..recettes_import import afficher_importer
    from .ajout import afficher_ajouter_manuel
    from .detail import afficher_detail_recette
    from .generation_ia import afficher_generer_ia
    from .liste import afficher_liste

    st.title("🍽️ Mes Recettes")
    st.caption("Gestion complète de votre base de recettes")

    # Gérer l'état de la vue détails
    if _keys("detail_id") not in st.session_state:
        st.session_state[_keys("detail_id")] = None

    # Si une recette est sélectionnée, afficher son détail
    if st.session_state[_keys("detail_id")] is not None:
        service = obtenir_service_recettes()
        if service is not None:
            recette = service.get_by_id_full(st.session_state[_keys("detail_id")])
            if recette:
                # Bouton retour en haut avec icône visible
                col_retour, col_titre = st.columns([1, 10])
                with col_retour:
                    if st.button("⬅️", help="Retour à la liste", use_container_width=True):
                        st.session_state[_keys("detail_id")] = None
                        rerun()
                with col_titre:
                    st.write(f"**{recette.nom}**")
                st.divider()
                afficher_detail_recette(recette)
                return
        st.error("❌ Recette non trouvée")
        st.session_state[_keys("detail_id")] = None

    # Sous-tabs avec deep linking URL et persistence d'état
    TAB_LABELS = ["📋 Liste", "➕ Ajouter Manuel", "📥 Importer", "⏰ Générer IA", "💬 Assistant"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tab_liste, tab_ajout, tab_import, tab_ia, tab_chat = st.tabs(TAB_LABELS)

    with tab_liste:
        with error_boundary(titre="Erreur liste recettes"):
            afficher_liste()

    with tab_ajout:
        with error_boundary(titre="Erreur ajout recette"):
            afficher_ajouter_manuel()

    with tab_import:
        with error_boundary(titre="Erreur import recette"):
            afficher_importer()

    with tab_ia:
        with error_boundary(titre="Erreur génération IA"):
            afficher_generer_ia()

    with tab_chat:
        with error_boundary(titre="Erreur assistant cuisine"):
            from src.ui.components import afficher_chat_contextuel

            st.caption("Posez vos questions cuisine à l'assistant IA")
            afficher_chat_contextuel("recettes")


__all__ = [
    "app",
    "afficher_liste",
    "afficher_detail_recette",
    "afficher_ajouter_manuel",
    "afficher_generer_ia",
    "formater_quantite",
]
