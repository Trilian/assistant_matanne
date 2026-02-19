"""
Génération d'images pour les recettes.
"""

import streamlit as st

from src.services.cuisine.recettes import get_recette_service


def render_generer_image(recette):
    """Affiche l'interface pour générer une image pour la recette"""
    st.subheader("⏰ Générer une image pertinente")

    # Description du prompt - affichée complètement
    prompt = f"{recette.nom}"
    if recette.description:
        prompt += f": {recette.description}"
    st.caption(f"📝 {prompt}")

    # Bouton génération
    if st.button("🎨 Générer Image", use_container_width=True, key=f"gen_img_{recette.id}"):
        try:
            # Import et vérification des clés
            from src.services.integrations.images import (
                PEXELS_API_KEY,
                PIXABAY_API_KEY,
                UNSPLASH_API_KEY,
                generer_image_recette,
            )

            # Afficher le status
            status_placeholder = st.empty()

            with status_placeholder.container():
                st.info(f"⏳ Génération de l'image pour: **{recette.nom}**")
                st.caption(
                    f"🔗 Sources: Unsplash={'✅' if UNSPLASH_API_KEY else '❌'} | Pexels={'✅' if PEXELS_API_KEY else '❌'} | Pixabay={'✅' if PIXABAY_API_KEY else '❌'}"
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
                st.success(f"✅ Image générée pour: **{recette.nom}**")
                # Stocker dans session state
                st.session_state[f"generated_image_{recette.id}"] = url_image

                # Afficher l'image en grande avec ratio maintenu
                st.image(url_image, caption=f"🍽️ {recette.nom}", use_column_width=True)
            else:
                status_placeholder.empty()
                st.error("❌ Impossible de générer l'image - aucune source ne retourne d'image")
                st.info("💡 Assurez-vous qu'une clé API est configurée dans Settings > Secrets")

        except ImportError as e:
            st.error(f"❌ Erreur d'import: {str(e)}")
        except Exception as e:
            import traceback

            st.error(f"❌ Erreur: {str(e)}")
            with st.expander("📋 Détails erreur"):
                st.code(traceback.format_exc(), language="python")

    # Afficher l'image si elle existe en session state
    if f"generated_image_{recette.id}" in st.session_state:
        url_image = st.session_state[f"generated_image_{recette.id}"]
        st.image(url_image, caption=f"🍽️ {recette.nom}", use_column_width=True)

        # Proposer de sauvegarder
        if st.button(
            "💾 Sauvegarder cette image", use_container_width=True, key=f"save_img_{recette.id}"
        ):
            service = get_recette_service()
            if service:
                try:
                    recette.url_image = url_image
                    service.update(recette.id, {"url_image": url_image})
                    st.success("✅ Image sauvegardée dans la recette!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur sauvegarde: {str(e)}")


__all__ = ["render_generer_image"]
