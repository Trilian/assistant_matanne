"""
Suggestions IA pour les courses.
"""

import time

from ._common import (
    st, pd, logger,
    get_courses_service, get_inventaire_service, get_recette_service,
    obtenir_contexte_db,
)


def render_suggestions_ia():
    """Suggestions IA depuis inventaire & recettes"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    recettes_service = get_recette_service()
    
    st.subheader("âœ¨ Suggestions intelligentes")
    
    tab_inventaire, tab_recettes = st.tabs(["ðŸ“¦ Depuis inventaire", "ðŸ½ï¸ Par recettes"])
    
    with tab_inventaire:
        st.write("**GÃenÃerer suggestions depuis stock bas**")
        
        if st.button("ðŸ¤– Analyser inventaire & gÃenÃerer suggestions"):
            with st.spinner("â³ Analyse en cours..."):
                try:
                    suggestions = service.generer_suggestions_ia_depuis_inventaire()
                    
                    if suggestions:
                        st.success(f"âœ… {len(suggestions)} suggestions gÃenÃerÃees!")
                        
                        # Afficher suggestions
                        df = pd.DataFrame([{
                            "Article": s.nom,
                            "QuantitÃe": f"{s.quantite} {s.unite}",
                            "PrioritÃe": s.priorite,
                            "Rayon": s.rayon
                        } for s in suggestions])
                        
                        st.dataframe(df, use_container_width=True)
                        
                        if st.button("âœ… Ajouter toutes les suggestions"):
                            try:
                                from src.core.models import Ingredient
                                
                                db = next(obtenir_contexte_db())
                                count = 0
                                
                                for suggestion in suggestions:
                                    # Trouver ou crÃeer ingrÃedient
                                    ingredient = db.query(Ingredient).filter(
                                        Ingredient.nom == suggestion.nom
                                    ).first()
                                    
                                    if not ingredient:
                                        ingredient = Ingredient(
                                            nom=suggestion.nom,
                                            unite=suggestion.unite
                                        )
                                        db.add(ingredient)
                                        db.commit()
                                    
                                    # Ajouter Ã  la liste
                                    data = {
                                        "ingredient_id": ingredient.id,
                                        "quantite_necessaire": suggestion.quantite,
                                        "priorite": suggestion.priorite,
                                        "rayon_magasin": suggestion.rayon,
                                        "suggere_par_ia": True
                                    }
                                    service.create(data)
                                    count += 1
                                
                                st.success(f"âœ… {count} articles ajoutÃes!")
                                st.session_state.courses_refresh += 1
                                # Pas de rerun pour rester sur cet onglet
                                time.sleep(0.5)
                            except Exception as e:
                                st.error(f"âŒ Erreur sauvegarde: {str(e)}")
                    else:
                        st.info("Aucune suggestion (inventaire OK)")
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
    
    with tab_recettes:
        st.write("**Ajouter ingrÃedients manquants pour recettes**")
        
        if recettes_service is None:
            st.warning("âš ï¸ Service recettes indisponible")
        else:
            # Lister recettes
            try:
                recettes = recettes_service.get_all()
                
                if not recettes:
                    st.info("Aucune recette disponible")
                else:
                    recette_names = {r.id: r.nom for r in recettes}
                    selected_recette_id = st.selectbox(
                        "SÃelectionner une recette",
                        options=list(recette_names.keys()),
                        format_func=lambda x: recette_names[x],
                        key="select_recette_courses"
                    )
                    
                    if selected_recette_id:
                        recette = recettes_service.get_by_id_full(selected_recette_id)
                        
                        if recette:
                            # Afficher ingrÃedients de la recette
                            nb_ingredients = len(recette.ingredients) if recette.ingredients else 0
                            st.caption(f"ðŸ“ {nb_ingredients} ingrÃedients")
                            
                            if st.button("ðŸ” Ajouter ingrÃedients manquants", key="btn_add_missing_ingredients"):
                                try:
                                    from src.core.models import Ingredient
                                    from src.core.database import obtenir_contexte_db
                                    
                                    # RÃecupÃerer ingrÃedients de la recette
                                    ingredients_recette = recette.ingredients if recette.ingredients else []
                                    
                                    if not ingredients_recette:
                                        st.warning("Aucun ingrÃedient dans cette recette")
                                    else:
                                        count_added = 0
                                        
                                        with obtenir_contexte_db() as db:
                                            for ing_obj in ingredients_recette:
                                                # RÃecupÃerer ingrÃedient
                                                ing_nom = ing_obj.ingredient.nom if hasattr(ing_obj, 'ingredient') else ing_obj.nom
                                                ing_quantite = ing_obj.quantite if hasattr(ing_obj, 'quantite') else 1
                                                ing_unite = ing_obj.ingredient.unite if hasattr(ing_obj, 'ingredient') and hasattr(ing_obj.ingredient, 'unite') else 'pièce'
                                                
                                                if not ing_nom:
                                                    continue
                                                
                                                ingredient = db.query(Ingredient).filter(
                                                    Ingredient.nom == ing_nom
                                                ).first()
                                                
                                                if not ingredient:
                                                    ingredient = Ingredient(
                                                        nom=ing_nom,
                                                        unite=ing_unite
                                                    )
                                                    db.add(ingredient)
                                                    db.flush()
                                                    db.refresh(ingredient)
                                                
                                                # Ajouter Ã  la liste courses
                                                data = {
                                                    "ingredient_id": ingredient.id,
                                                    "quantite_necessaire": ing_quantite,
                                                    "priorite": "moyenne",
                                                    "rayon_magasin": "Autre",
                                                    "notes": f"Pour {recette.nom}"
                                                }
                                                service.create(data)
                                                count_added += 1
                                        
                                        st.success(f"âœ… {count_added} ingrÃedient(s) ajoutÃe(s) Ã  la liste!")
                                        st.session_state.courses_refresh += 1
                                        # Pas de rerun pour rester sur cet onglet
                                        time.sleep(0.5)
                                except Exception as e:
                                    st.error(f"âŒ Erreur: {str(e)}")
                                    logger.error(f"Erreur ajout ingrÃedients recette: {e}")
            except Exception as e:
                st.error(f"âŒ Erreur: {str(e)}")
                logger.error(f"Erreur render tab recettes: {e}")


__all__ = ["render_suggestions_ia"]
