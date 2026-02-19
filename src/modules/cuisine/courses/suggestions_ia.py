"""
Suggestions IA pour les courses.
"""

import time

from ._common import (
    get_courses_service,
    get_inventaire_service,
    logger,
    obtenir_contexte_db,
    obtenir_service_recettes,
    pd,
    st,
)


def render_suggestions_ia():
    """Suggestions IA depuis inventaire & recettes"""
    service = get_courses_service()
    _inventaire_service = get_inventaire_service()
    recettes_service = obtenir_service_recettes()

    st.subheader("⏰ Suggestions intelligentes")

    tab_inventaire, tab_recettes = st.tabs(["📦 Depuis inventaire", "🍽️ Par recettes"])

    with tab_inventaire:
        st.write("**Générer suggestions depuis stock bas**")

        if st.button("🤖 Analyser inventaire & générer suggestions"):
            with st.spinner("⏳ Analyse en cours..."):
                try:
                    suggestions = service.generer_suggestions_ia_depuis_inventaire()

                    if suggestions:
                        st.success(f"✅ {len(suggestions)} suggestions générées!")

                        # Afficher suggestions
                        df = pd.DataFrame(
                            [
                                {
                                    "Article": s.nom,
                                    "Quantité": f"{s.quantite} {s.unite}",
                                    "Priorité": s.priorite,
                                    "Rayon": s.rayon,
                                }
                                for s in suggestions
                            ]
                        )

                        st.dataframe(df, width="stretch")

                        if st.button("✅ Ajouter toutes les suggestions"):
                            try:
                                from src.core.models import Ingredient

                                db = next(obtenir_contexte_db())
                                count = 0

                                for suggestion in suggestions:
                                    # Trouver ou créer ingrédient
                                    ingredient = (
                                        db.query(Ingredient)
                                        .filter(Ingredient.nom == suggestion.nom)
                                        .first()
                                    )

                                    if not ingredient:
                                        ingredient = Ingredient(
                                            nom=suggestion.nom, unite=suggestion.unite
                                        )
                                        db.add(ingredient)
                                        db.commit()

                                    # Ajouter à la liste
                                    data = {
                                        "ingredient_id": ingredient.id,
                                        "quantite_necessaire": suggestion.quantite,
                                        "priorite": suggestion.priorite,
                                        "rayon_magasin": suggestion.rayon,
                                        "suggere_par_ia": True,
                                    }
                                    service.create(data)
                                    count += 1

                                st.success(f"✅ {count} articles ajoutés!")
                                st.session_state.courses_refresh += 1
                                # Pas de rerun pour rester sur cet onglet
                                time.sleep(0.5)
                            except Exception as e:
                                st.error(f"❌ Erreur sauvegarde: {str(e)}")
                    else:
                        st.info("Aucune suggestion (inventaire OK)")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    with tab_recettes:
        st.write("**Ajouter ingrédients manquants pour recettes**")

        if recettes_service is None:
            st.warning("⚠️ Service recettes indisponible")
        else:
            # Lister recettes
            try:
                recettes = recettes_service.get_all()

                if not recettes:
                    st.info("Aucune recette disponible")
                else:
                    recette_names = {r.id: r.nom for r in recettes}
                    selected_recette_id = st.selectbox(
                        "Sélectionner une recette",
                        options=list(recette_names.keys()),
                        format_func=lambda x: recette_names[x],
                        key="select_recette_courses",
                    )

                    if selected_recette_id:
                        recette = recettes_service.get_by_id_full(selected_recette_id)

                        if recette:
                            # Afficher ingrédients de la recette
                            nb_ingredients = len(recette.ingredients) if recette.ingredients else 0
                            st.caption(f"📝 {nb_ingredients} ingrédients")

                            if st.button(
                                "🔍 Ajouter ingrédients manquants",
                                key="btn_add_missing_ingredients",
                            ):
                                try:
                                    from src.core.db import obtenir_contexte_db
                                    from src.core.models import Ingredient

                                    # Récupérer ingrédients de la recette
                                    ingredients_recette = (
                                        recette.ingredients if recette.ingredients else []
                                    )

                                    if not ingredients_recette:
                                        st.warning("Aucun ingrédient dans cette recette")
                                    else:
                                        count_added = 0

                                        with obtenir_contexte_db() as db:
                                            for ing_obj in ingredients_recette:
                                                # Récupérer ingrédient
                                                ing_nom = (
                                                    ing_obj.ingredient.nom
                                                    if hasattr(ing_obj, "ingredient")
                                                    else ing_obj.nom
                                                )
                                                ing_quantite = (
                                                    ing_obj.quantite
                                                    if hasattr(ing_obj, "quantite")
                                                    else 1
                                                )
                                                ing_unite = (
                                                    ing_obj.ingredient.unite
                                                    if hasattr(ing_obj, "ingredient")
                                                    and hasattr(ing_obj.ingredient, "unite")
                                                    else "pièce"
                                                )

                                                if not ing_nom:
                                                    continue

                                                ingredient = (
                                                    db.query(Ingredient)
                                                    .filter(Ingredient.nom == ing_nom)
                                                    .first()
                                                )

                                                if not ingredient:
                                                    ingredient = Ingredient(
                                                        nom=ing_nom, unite=ing_unite
                                                    )
                                                    db.add(ingredient)
                                                    db.flush()
                                                    db.refresh(ingredient)

                                                # Ajouter à la liste courses
                                                data = {
                                                    "ingredient_id": ingredient.id,
                                                    "quantite_necessaire": ing_quantite,
                                                    "priorite": "moyenne",
                                                    "rayon_magasin": "Autre",
                                                    "notes": f"Pour {recette.nom}",
                                                }
                                                service.create(data)
                                                count_added += 1

                                        st.success(
                                            f"✅ {count_added} ingrédient(s) ajouté(s) à la liste!"
                                        )
                                        st.session_state.courses_refresh += 1
                                        # Pas de rerun pour rester sur cet onglet
                                        time.sleep(0.5)
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                                    logger.error(f"Erreur ajout ingrédients recette: {e}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur render tab recettes: {e}")


__all__ = ["render_suggestions_ia"]
