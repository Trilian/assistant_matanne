"""
Interface UI pour l'import de recettes depuis le web.

Note: Ce fichier a été extrait depuis src/services/recettes/import_url.py
pour respecter la séparation UI/Services.
"""

import streamlit as st

from src.services.cuisine.recettes.import_url import get_recipe_import_service


def afficher_import_recette():  # pragma: no cover
    """Interface Streamlit pour l'import de recettes."""
    st.subheader("🌐 Importer une recette depuis le web")

    st.info(
        "📝 Collez l'URL d'une recette depuis Marmiton, CuisineAZ, ou tout autre site de cuisine."
    )

    # Import simple
    url = st.text_input(
        "URL de la recette",
        placeholder="https://www.marmiton.org/recettes/...",
        key="recipe_import_url",
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        use_ai = st.checkbox("Utiliser l'IA si nécessaire", value=True, key="use_ai_import")

    with col2:
        import_btn = st.button("📥 Importer", type="primary", use_container_width=True)

    if import_btn and url:
        service = get_recipe_import_service()

        with st.spinner("Import en cours..."):
            result = service.import_from_url(url, use_ai_fallback=use_ai)

        if result.success and result.recipe:
            st.success(f"✅ {result.message}")

            recipe = result.recipe

            # Afficher la prévisualisation
            st.markdown("---")
            st.markdown(f"### {recipe.nom}")

            if recipe.image_url:
                st.image(recipe.image_url, width=300)

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("⏱️ Préparation", f"{recipe.temps_preparation} min")
            with col_b:
                st.metric("🔥 Cuisson", f"{recipe.temps_cuisson} min")
            with col_c:
                st.metric("👥 Portions", recipe.portions)

            if recipe.description:
                st.markdown(f"*{recipe.description}*")

            # Ingrédients
            st.markdown("#### 🥕 Ingrédients")
            for ing in recipe.ingredients:
                qty = f"{ing.quantite} {ing.unite}" if ing.quantite else ""
                st.markdown(f"- {qty} {ing.nom}")

            # Étapes
            st.markdown("#### 📝 Préparation")
            for i, step in enumerate(recipe.etapes, 1):
                st.markdown(f"{i}. {step}")

            st.markdown("---")
            st.caption(f"🔗 Source: {recipe.source_site} | Confiance: {recipe.confiance_score:.0%}")

            # Bouton pour sauvegarder
            if st.button("💾 Ajouter à mes recettes", type="primary"):
                try:
                    from src.services.cuisine.recettes import obtenir_service_recettes

                    service = obtenir_service_recettes()

                    # Préparer les données
                    recette_data = {
                        "nom": recipe.nom,
                        "description": recipe.description,
                        "temps_preparation": recipe.temps_preparation,
                        "temps_cuisson": recipe.temps_cuisson,
                        "portions": recipe.portions,
                        "difficulte": recipe.difficulte,
                        "url_image": recipe.image_url,
                        "ingredients": [
                            {"nom": ing.nom, "quantite": ing.quantite or 1, "unite": ing.unite}
                            for ing in recipe.ingredients
                        ],
                        "etapes": [
                            {"ordre": i, "description": step}
                            for i, step in enumerate(recipe.etapes, 1)
                        ],
                    }

                    result = service.creer_complete(recette_data)
                    if result:
                        st.success(f"✅ Recette '{recipe.nom}' ajoutée avec succès!")
                        st.balloons()
                    else:
                        st.error("❌ Erreur lors de l'ajout")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")

        else:
            st.error(f"❌ {result.message}")
            if result.errors:
                for error in result.errors:
                    st.warning(f"⚠️ {error}")

            if result.recipe:
                st.markdown("---")
                st.markdown("### Extraction partielle:")
                st.json(result.recipe.model_dump())

    # Import en lot
    st.markdown("---")
    with st.expander("📋 Import en lot (plusieurs URLs)"):
        urls_text = st.text_area(
            "URLs (une par ligne)",
            height=150,
            key="batch_import_urls",
            placeholder="https://www.marmiton.org/recette1\nhttps://www.cuisineaz.com/recette2",
        )

        if st.button("📥 Importer tout", key="batch_import_btn"):
            urls = [u.strip() for u in urls_text.split("\n") if u.strip()]

            if urls:
                service = get_recipe_import_service()

                progress_bar = st.progress(0)
                status = st.empty()

                results = []
                for i, url in enumerate(urls):
                    status.text(f"Import {i + 1}/{len(urls)}: {url[:50]}...")
                    result = service.import_from_url(url, use_ai_fallback=True)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(urls))

                # Résumé
                success_count = sum(1 for r in results if r.success)
                st.markdown(f"### Résultat: {success_count}/{len(urls)} importées")

                for url, result in zip(urls, results, strict=False):
                    if result.success:
                        st.success(f"✅ {result.recipe.nom if result.recipe else url}")
                    else:
                        st.error(f"❌ {url}: {result.message}")


# Alias rétrocompatibilité
render_import_recipe_ui = afficher_import_recette


__all__ = [
    "afficher_import_recette",
    "render_import_recipe_ui",
]
