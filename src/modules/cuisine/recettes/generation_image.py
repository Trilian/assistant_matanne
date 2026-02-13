"""
Génération d'images pour les recettes.
"""

import streamlit as st

from src.services.recettes import get_recette_service


def render_generer_image(recette):
    """Affiche l'interface pour générer une image pour la recette"""
    st.subheader("⏰ Générer une image pertinente")

    # Description du prompt - affichée complètement
    prompt = f"{recette.nom}"
    if recette.description:
        prompt += f": {recette.description}"
    st.caption(f"ðŸ“ {prompt}")

    # Bouton génération
    if st.button("ðŸŽ¨ Générer Image", use_container_width=True, key=f"gen_img_{recette.id}"):
        try:
            # Import et vérification des clés
            from src.utils.image_generator import (
                PEXELS_API_KEY,
                PIXABAY_API_KEY,
                UNSPLASH_API_KEY,
                generer_image_recette,
            )

            # Afficher le status
            status_placeholder = st.empty()

            with status_placeholder.container():
                st.info(f"â³ Génération de l'image pour: **{recette.nom}**")
                st.caption(
                    f"ðŸ”— Sources: Unsplash={'âœ…' if UNSPLASH_API_KEY else 'âŒ'} | Pexels={'âœ…' if PEXELS_API_KEY else 'âŒ'} | Pixabay={'âœ…' if PIXABAY_API_KEY else 'âŒ'}"
                )

            # Préparer la liste des ingrédients
            ingredients_list = []
            for ing in recette.ingredients:
                ingredients_list.append(
                    {"nom": ing.ingredient.nom, "quantite": ing.quantite, "unite": ing.unite}
                )

            # Générer l'image
            url_image = generer_image_recette(
                recette.nom,
                recette.description or "",
                ingredients_list=ingredients_list,
                type_plat=recette.type_repas,
            )

            # Mettre à jour le status
            if url_image:
                status_placeholder.empty()
                st.success(f"âœ… Image générée pour: **{recette.nom}**")
                # Stocker dans session state
                st.session_state[f"generated_image_{recette.id}"] = url_image

                # Afficher l'image en grande avec ratio maintenu
                st.image(url_image, caption=f"ðŸ½ï¸ {recette.nom}", use_column_width=True)
            else:
                status_placeholder.empty()
                st.error("âŒ Impossible de générer l'image - aucune source ne retourne d'image")
                st.info("ðŸ’¡ Assurez-vous qu'une clé API est configurée dans Settings > Secrets")

        except ImportError as e:
            st.error(f"âŒ Erreur d'import: {str(e)}")
        except Exception as e:
            import traceback

            st.error(f"âŒ Erreur: {str(e)}")
            with st.expander("ðŸ“‹ Détails erreur"):
                st.code(traceback.format_exc(), language="python")

    # Afficher l'image si elle existe en session state
    if f"generated_image_{recette.id}" in st.session_state:
        url_image = st.session_state[f"generated_image_{recette.id}"]
        st.image(url_image, caption=f"ðŸ½ï¸ {recette.nom}", use_column_width=True)

        # Proposer de sauvegarder
        if st.button(
            "ðŸ’¾ Sauvegarder cette image", use_container_width=True, key=f"save_img_{recette.id}"
        ):
            service = get_recette_service()
            if service:
                try:
                    recette.url_image = url_image
                    service.update(recette.id, {"url_image": url_image})
                    st.success("âœ… Image sauvegardée dans la recette!")
                    st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur sauvegarde: {str(e)}")


__all__ = ["render_generer_image"]
