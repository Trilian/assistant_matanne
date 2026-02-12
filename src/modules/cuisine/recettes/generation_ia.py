"""
GÃenÃeration de recettes avec l'IA.
"""

import logging
import streamlit as st

from src.services.recettes import get_recette_service
from .utilitaires import formater_quantite

logger = logging.getLogger(__name__)


def render_generer_ia():
    """Interface pour gÃenÃerer des recettes avec l'IA"""
    # Marquer cet onglet comme actif
    st.session_state.recettes_selected_tab = 3
    
    st.subheader("âœ¨ GÃenÃerer des recettes avec l'IA")
    
    service = get_recette_service()
    if service is None:
        st.error("âŒ Service IA indisponible")
        return
    
    # SÃelection du mode de gÃenÃeration
    mode_gen = st.radio(
        "Mode de gÃenÃeration",
        ["PersonnalisÃe", "Recherche spÃecifique"],
        horizontal=True
    )
    
    if mode_gen == "Recherche spÃecifique":
        _render_recherche_specifique(service)
    else:
        _render_mode_personnalise(service)


def _render_recherche_specifique(service):
    """Mode recherche de variantes d'une recette spÃecifique"""
    st.info("ðŸ” GÃenÃerez plusieurs variantes d'une recette spÃecifique")
    with st.form("form_recette_specifique", border=True):
        recette_recherche = st.text_input(
            "Nom de la recette recherchÃee *",
            placeholder="Exemple: pâtes bolognaises, tarte tatin, pizza..."
        )
        nb_variantes = st.slider("Nombre de variantes", 1, 5, 3)
        submitted_spec = st.form_submit_button("ðŸ” Chercher des variantes", use_container_width=True)
    
    if submitted_spec and recette_recherche:
        with st.spinner(f"ðŸ¤– GÃenÃeration de variantes de '{recette_recherche}'..."):
            try:
                recettes_variantes = service.generer_variantes_recette_ia(
                    nom_recette=recette_recherche,
                    nb_variantes=nb_variantes,
                )
                
                if not recettes_variantes:
                    st.warning("âš ï¸ Aucune variante gÃenÃerÃee. RÃeessayez.")
                    return
                
                st.success(f"âœ… {len(recettes_variantes)} variante(s) de '{recette_recherche}' gÃenÃerÃee(s)!")
                st.divider()
                
                # Afficher les suggestions en cartes
                for idx, suggestion in enumerate(recettes_variantes, 1):
                    _render_suggestion_card(suggestion, idx, service, is_variant=True)
                
            except Exception as e:
                st.error(f"âŒ Erreur: {str(e)}")


def _render_mode_personnalise(service):
    """Mode gÃenÃeration personnalisÃee"""
    st.info("ðŸ’¡ Laissez l'IA gÃenÃerer des recettes personnalisÃees basÃees sur vos prÃefÃerences")
    with st.form("form_recette_ia", border=True):
        col1, col2 = st.columns(2)
        with col1:
            type_repas = st.selectbox(
                "Type de repas *",
                ["petit_dÃejeuner", "dÃejeuner", "dîner", "goûter", "apÃeritif", "dessert"]
            )
        with col2:
            saison = st.selectbox(
                "Saison *",
                ["printemps", "ÃetÃe", "automne", "hiver", "toute_annÃee"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            difficulte = st.selectbox(
                "Niveau de difficultÃe",
                ["facile", "moyen", "difficile"]
            )
        with col2:
            nb_recettes = st.number_input(
                "Nombre de suggestions",
                min_value=1,
                max_value=10,
                value=3
            )
        
        ingredients_str = st.text_area(
            "IngrÃedients disponibles (optionnel)",
            placeholder="SÃeparez les ingrÃedients par des virgules\nEx: tomate, oignon, ail, riz",
            height=80
        )
        
        submitted = st.form_submit_button("ðŸ¤– GÃenÃerer avec l'IA", use_container_width=True)
    
    if submitted:
        if not type_repas or not saison:
            st.error("âŒ Type de repas et saison sont obligatoires")
        else:
            ingredients_dispo = None
            if ingredients_str:
                ingredients_dispo = [i.strip() for i in ingredients_str.split(",") if i.strip()]
            
            with st.spinner("ðŸ¤– L'IA gÃenère vos recettes..."):
                try:
                    recettes_suggestions = service.generer_recettes_ia(
                        type_repas=type_repas,
                        saison=saison,
                        difficulte=difficulte,
                        ingredients_dispo=ingredients_dispo,
                        nb_recettes=nb_recettes,
                    )
                    
                    if not recettes_suggestions:
                        st.warning("âš ï¸ Aucune recette gÃenÃerÃee. RÃeessayez.")
                        return
                    
                    st.success(f"âœ… {len(recettes_suggestions)} recette(s) gÃenÃerÃee(s)!")
                    st.divider()
                    
                    # Afficher les suggestions en cartes
                    for idx, suggestion in enumerate(recettes_suggestions, 1):
                        _render_suggestion_card(suggestion, idx, service, type_repas=type_repas, saison=saison)
                    
                except Exception as e:
                    st.error(f"âŒ Erreur gÃenÃeration: {str(e)}")
                    logger.error(f"Erreur IA recettes: {e}")


def _render_suggestion_card(suggestion, idx, service, is_variant=False, type_repas=None, saison=None):
    """Affiche une carte de suggestion de recette"""
    with st.container(border=True):
        # Titre + MÃetrique difficultÃe en ligne
        col_titre, col_diff = st.columns([4, 1])
        with col_titre:
            title_prefix = f"ðŸ³ Variante {idx}:" if is_variant else "ðŸ³"
            st.subheader(f"{title_prefix} {suggestion.nom}", anchor=False)
        with col_diff:
            difficulte_emoji = {"facile": "ðŸŸ¢", "moyen": "ðŸŸ¡", "difficile": "ðŸ”´"}.get(suggestion.difficulte, "")
            st.caption(f"{difficulte_emoji} {suggestion.difficulte}")
        
        # Description
        if suggestion.description:
            st.markdown(suggestion.description)
        
        # MÃetriques en ligne
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("â±ï¸ PrÃeparation", f"{suggestion.temps_preparation} min", label_visibility="collapsed")
        with col2:
            st.metric("ðŸ”¥ Cuisson", f"{suggestion.temps_cuisson} min", label_visibility="collapsed")
        with col3:
            st.metric("ðŸ½ï¸ Portions", suggestion.portions, label_visibility="collapsed")
        with col4:
            st.metric("â° Total", f"{suggestion.temps_preparation + suggestion.temps_cuisson} min", label_visibility="collapsed")
        
        st.divider()
        
        # IngrÃedients en deux colonnes
        if suggestion.ingredients:
            st.markdown("**IngrÃedients:**")
            col_ing1, col_ing2 = st.columns(2)
            with col_ing1:
                ing_list = suggestion.ingredients[:len(suggestion.ingredients)//2 + 1]
                for ing in ing_list:
                    if isinstance(ing, dict):
                        qty = formater_quantite(ing.get('quantite', ''))
                        st.write(f"â€¢ {ing.get('nom', 'N/A')}: {qty} {ing.get('unite', '')}")
                    else:
                        st.write(f"â€¢ {ing}")
            with col_ing2:
                ing_list = suggestion.ingredients[len(suggestion.ingredients)//2 + 1:]
                for ing in ing_list:
                    if isinstance(ing, dict):
                        qty = formater_quantite(ing.get('quantite', ''))
                        st.write(f"â€¢ {ing.get('nom', 'N/A')}: {qty} {ing.get('unite', '')}")
                    else:
                        st.write(f"â€¢ {ing}")
        
        # Étapes dans un expander
        if suggestion.etapes:
            with st.expander("ðŸ“‹ Étapes de prÃeparation"):
                for i, etape in enumerate(suggestion.etapes, 1):
                    if isinstance(etape, dict):
                        st.write(f"**{i}.** {etape.get('description', etape)}")
                    else:
                        st.write(f"**{i}.** {etape}")
        
        # Bouton d'ajout
        st.divider()
        col_btn_add, col_btn_space = st.columns([2, 1])
        with col_btn_add:
            button_key = f"add_variant_{idx}" if is_variant else f"add_suggestion_{idx}"
            if st.button(f"âœ… Ajouter Ã  mes recettes", key=button_key, use_container_width=True, type="primary"):
                try:
                    # PrÃeparer les donnÃees pour la crÃeation
                    data = {
                        "nom": suggestion.nom,
                        "description": suggestion.description,
                        "type_repas": getattr(suggestion, 'type_repas', type_repas),
                        "temps_preparation": suggestion.temps_preparation,
                        "temps_cuisson": suggestion.temps_cuisson,
                        "portions": suggestion.portions,
                        "difficulte": suggestion.difficulte,
                        "saison": getattr(suggestion, 'saison', saison),
                        "ingredients": suggestion.ingredients or [],
                        "etapes": suggestion.etapes or [],
                    }
                    
                    # CrÃeer la recette avec session BD
                    from src.core.database import obtenir_contexte_db
                    with obtenir_contexte_db() as db:
                        recette = service.create_complete(data, db=db)
                    st.success(f"âœ… '{recette.nom}' ajoutÃee Ã  vos recettes!")
                    st.toast(f"ðŸŽ‰ {recette.nom} sauvegardÃee!", icon="âœ…")
                    
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
                    logger.error(f"Erreur ajout suggestion: {e}")
        
        st.write("")  # Espacement


__all__ = ["render_generer_ia"]
