"""
Suggestions IA pour les courses.
"""

import logging
import time

import pandas as pd
import streamlit as st

from src.services.cuisine.courses import obtenir_service_courses
from src.services.cuisine.recettes import obtenir_service_recettes
from src.services.inventaire import obtenir_service_inventaire
from src.ui.components.atoms import etat_vide
from src.ui.fragments import ui_fragment

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_suggestions_ia():
    """Suggestions IA depuis inventaire & recettes"""
    service = obtenir_service_courses()
    _inventaire_service = obtenir_service_inventaire()
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
                                count = service.ajouter_suggestions_en_masse(suggestions)
                                st.success(f"✅ {count} articles ajoutés!")
                                st.session_state.courses_refresh += 1
                                time.sleep(0.5)
                            except Exception as e:
                                st.error(f"❌ Erreur sauvegarde: {str(e)}")
                    else:
                        etat_vide("Aucune suggestion", "✅", "Votre inventaire est complet")
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
                    etat_vide(
                        "Aucune recette disponible",
                        "🍳",
                        "Ajoutez des recettes pour générer des suggestions",
                    )
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
                                    # Récupérer ingrédients de la recette
                                    ingredients_recette = (
                                        recette.ingredients if recette.ingredients else []
                                    )

                                    if not ingredients_recette:
                                        st.warning("Aucun ingrédient dans cette recette")
                                    else:
                                        # Préparer les données d'ingrédients
                                        ingredients_data = []
                                        for ing_obj in ingredients_recette:
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
                                            if ing_nom:
                                                ingredients_data.append(
                                                    {
                                                        "nom": ing_nom,
                                                        "quantite": ing_quantite,
                                                        "unite": ing_unite,
                                                    }
                                                )

                                        count_added = service.ajouter_ingredients_recette(
                                            ingredients_data=ingredients_data,
                                            recette_nom=recette.nom,
                                        )

                                        st.success(
                                            f"✅ {count_added} ingrédient(s) ajouté(s) à la liste!"
                                        )
                                        st.session_state.courses_refresh += 1
                                        time.sleep(0.5)
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                                    logger.error(f"Erreur ajout ingrédients recette: {e}")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur render tab recettes: {e}")


__all__ = ["afficher_suggestions_ia"]
