"""
Module pour l'import de recettes
"""

import streamlit as st

# Logique metier pure
from src.services.cuisine.recettes import get_recipe_import_service, obtenir_service_recettes
from src.services.cuisine.recettes.importer import RecipeImporter
from src.services.cuisine.recettes.parsers import ImportedRecipe


def afficher_importer():
    """Interface pour importer une recette"""
    st.subheader("📥 Importer une recette")
    st.write("Importez une recette depuis un site web, un PDF ou du texte")

    # Onglets pour differents types d'import
    import_tab1, import_tab2, import_tab3 = st.tabs(
        ["🌐 URL/Site Web", "📄 Fichier PDF", "📝 Texte"]
    )

    with import_tab1:
        _afficher_import_url()

    with import_tab2:
        _afficher_import_pdf()

    with import_tab3:
        _afficher_import_text()


def _imported_recipe_to_dict(recipe: ImportedRecipe) -> dict:
    """Convertit ImportedRecipe (Pydantic) en dict pour l'aperçu UI."""
    data = recipe.model_dump()
    # Convertir les ingrédients structurés en chaînes lisibles
    data["ingredients"] = [
        f"{ing.quantite:.0f} {ing.unite} {ing.nom}".strip() if ing.quantite else ing.nom
        for ing in recipe.ingredients
    ]
    return data


def _afficher_import_url():
    """Import depuis une URL via RecipeImportService."""
    st.markdown("### 🌐 Importer depuis une URL")
    st.info("Entrez l'URL d'un site contenant une recette (recipetin, marmiton, cuisineaz, etc.)")

    # État pour stocker les donnees extraites
    if "extracted_recipe" not in st.session_state:
        st.session_state.extracted_recipe = None

    url = st.text_input("URL du site", placeholder="https://www.marmiton.org/recettes/...")

    if st.button("📥 Extraire la recette du site", width="stretch", type="primary"):
        if not url:
            st.error("❌ Veuillez entrer une URL")
            return

        with st.spinner("⏳ Extraction du titre, image, ingredients, etapes, temps..."):
            try:
                service = get_recipe_import_service()
                result = service.import_from_url(url)

                if result and result.success and result.recipe:
                    recipe_data = _imported_recipe_to_dict(result.recipe)
                    st.session_state.extracted_recipe = recipe_data
                    st.success("✅ Recette extraite!")
                    st.rerun()
                else:
                    msg = result.message if result else "Erreur inconnue"
                    st.error(f"❌ {msg}")

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

    # Si une recette a ete extraite, afficher le formulaire d'edition
    if st.session_state.extracted_recipe:
        _show_import_preview(st.session_state.extracted_recipe)


def _afficher_import_pdf():
    """Import depuis un PDF"""
    st.markdown("### 📄 Importer depuis un PDF")
    st.info("Telechargez un fichier PDF contenant une recette")

    pdf_file = st.file_uploader("Choisissez un fichier PDF", type=["pdf"])

    if pdf_file:
        # Sauvegarder temporairement
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.getbuffer())
            tmp_path = tmp.name

        if st.button("🔍 Analyser le PDF", use_container_width=True):
            with st.spinner("⏳ Extraction de la recette..."):
                try:
                    recipe_data = RecipeImporter.from_pdf(tmp_path)

                    if recipe_data:
                        st.success("✅ Recette extraite!")
                        _show_import_preview(recipe_data)
                    else:
                        st.error("❌ Impossible d'extraire la recette du PDF.")

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
                finally:
                    os.unlink(tmp_path)


def _afficher_import_text():
    """Import depuis du texte"""
    st.markdown("### 📝 Importer depuis du texte")
    st.info("Collez le texte d'une recette (HTML, texte brut, etc.)")

    text = st.text_area(
        "Collez la recette ici",
        height=300,
        placeholder="""Pâtes à la Bolognaise

Ingredients:
- 400g de pâtes
- 500g de viande hachee
- 2 oignons

Étapes:
1. Cuire les pâtes
2. Preparer la sauce
...""",
    )

    if st.button("🔍 Analyser le texte", use_container_width=True):
        if not text:
            st.error("❌ Veuillez entrer du texte")
            return

        with st.spinner("⏳ Extraction de la recette..."):
            try:
                recipe_data = RecipeImporter.from_text(text)

                if recipe_data:
                    st.success("✅ Recette extraite!")
                    _show_import_preview(recipe_data)
                else:
                    st.error("❌ Impossible d'extraire la recette du texte.")

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")


def _show_import_preview(recipe_data: dict):
    """Affiche l'aperçu et permet de modifier avant import"""
    # Initialiser l'etat de dernière recette importee
    if "last_imported_recipe_name" not in st.session_state:
        st.session_state.last_imported_recipe_name = None

    # Si une recette vient d'être importee, afficher un message de succès persistant
    if st.session_state.last_imported_recipe_name:
        col_success, col_action = st.columns([2, 1])
        with col_success:
            st.success(
                f"✅ Recette '{st.session_state.last_imported_recipe_name}' importee avec succès!"
            )
        with col_action:
            if st.button("✨ Voir la recette", use_container_width=True):
                st.rerun()
        st.divider()
        # Reinitialiser le message après l'affichage
        st.session_state.last_imported_recipe_name = None

    st.markdown("### 📋 Aperçu et modification")

    # Formulaire d'edition
    with st.form("form_import_recette"):
        # Infos de base
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de la recette *", value=recipe_data.get("nom", ""))
        with col2:
            # Detecter automatiquement le type de repas à partir du nom
            default_type = "dîner"  # Defaut le plus courant
            nom_lower = (nom + " " + recipe_data.get("description", "")).lower()

            if any(
                word in nom_lower
                for word in ["petit dej", "breakfast", "œuf", "pain", "tartine", "confiture"]
            ):
                default_type = "petit_dejeuner"
            elif any(
                word in nom_lower
                for word in ["gâteau", "dessert", "mousse", "tarte", "crème", "flan"]
            ):
                default_type = "dessert"
            elif any(
                word in nom_lower for word in ["apero", "appetizer", "canape", "amuse", "entree"]
            ):
                default_type = "aperitif"
            elif any(word in nom_lower for word in ["midi", "dejeuner", "lunch"]):
                default_type = "dejeuner"

            options = ["petit_dejeuner", "dejeuner", "dîner", "goûter", "aperitif", "dessert"]
            default_idx = options.index(default_type) if default_type in options else 2

            type_repas = st.selectbox("Type de repas *", options, index=default_idx)

        description = st.text_area(
            "Description", value=recipe_data.get("description", ""), height=100
        )

        # Image - D'abord essayer la URL extraite, sinon permet l'upload
        st.markdown("#### 🖼️ Image de la recette")
        extracted_image_url = recipe_data.get("image_url", "")

        image_url_input = st.text_input(
            "URL de l'image extraite",
            value=extracted_image_url,
            help="URL automatiquement extraite du site, vous pouvez la modifier",
        )

        st.markdown("**Ou telecharger une image:**")
        uploaded_image = st.file_uploader(
            "Choisissez une image", type=["jpg", "jpeg", "png", "webp"], key="import_image_uploader"
        )

        # Temps et portions
        col1, col2, col3 = st.columns(3)
        with col1:
            temps_prep = st.number_input(
                "Temps preparation (min)",
                min_value=0,
                max_value=300,
                value=recipe_data.get("temps_preparation", 15),
            )
        with col2:
            temps_cuisson = st.number_input(
                "Temps cuisson (min)",
                min_value=0,
                max_value=300,
                value=recipe_data.get("temps_cuisson", 20),
            )
        with col3:
            portions = st.number_input(
                "Portions", min_value=1, max_value=20, value=recipe_data.get("portions", 4)
            )

        difficulte = st.selectbox("Difficulte", ["facile", "moyen", "difficile"], index=0)

        # Ingredients
        st.markdown("#### 🛍 Ingredients")
        ingredients = recipe_data.get("ingredients", [])

        # Afficher et permettre l'edition
        edited_ingredients = []
        for idx, ing in enumerate(ingredients):
            ing_text = st.text_input(f"Ingredient {idx + 1}", value=ing, key=f"ing_{idx}")
            if ing_text:
                edited_ingredients.append(ing_text)

        # Ajouter un ingredient vierge pour en ajouter plus
        new_ing = st.text_input("Nouvel ingredient (optionnel)", key="new_ing")
        if new_ing:
            edited_ingredients.append(new_ing)

        # Étapes
        st.markdown("#### 👨‍🍳 Étapes de preparation")
        etapes = recipe_data.get("etapes", [])

        edited_etapes = []
        for idx, etape in enumerate(etapes):
            # Enlever le numero si present
            etape_text = etape.lstrip("0123456789.").strip()
            etape_input = st.text_area(
                f"Étape {idx + 1}", value=etape_text, height=60, key=f"step_{idx}"
            )
            if etape_input:
                edited_etapes.append(etape_input)

        # Ajouter une etape vierge
        new_step = st.text_area("Nouvelle etape (optionnel)", height=60, key="new_step")
        if new_step:
            edited_etapes.append(new_step)

        # Valider
        submitted = st.form_submit_button("✅ Importer cette recette", use_container_width=True)

        if submitted:
            # Afficher un container pour les messages
            validation_ok = True

            if not nom:
                st.error("❌ Le nom est obligatoire")
                validation_ok = False

            if not edited_ingredients:
                st.error("❌ Au moins un ingredient est obligatoire")
                validation_ok = False

            if not edited_etapes:
                st.error("❌ Au moins une etape est obligatoire")
                validation_ok = False

            if validation_ok:
                # Traiter l'image
                image_path = None
                if uploaded_image:
                    # Traiter le fichier uploade (même logique que la creation manuelle)
                    import os
                    import uuid

                    image_dir = "data/recettes_images"
                    os.makedirs(image_dir, exist_ok=True)

                    file_ext = uploaded_image.name.split(".")[-1].lower()
                    image_name = f"{uuid.uuid4()}.{file_ext}"
                    image_path = f"{image_dir}/{image_name}"

                    with open(image_path, "wb") as f:
                        f.write(uploaded_image.getbuffer())
                elif image_url_input:
                    # Utiliser l'URL extraite ou modifiee
                    image_path = image_url_input

                _save_imported_recipe(
                    nom=nom,
                    type_repas=type_repas,
                    description=description,
                    temps_preparation=temps_prep,
                    temps_cuisson=temps_cuisson,
                    portions=portions,
                    difficulte=difficulte,
                    ingredients=edited_ingredients,
                    etapes=edited_etapes,
                    image_path=image_path,
                )


def _save_imported_recipe(
    nom: str,
    type_repas: str,
    description: str,
    temps_preparation: int,
    temps_cuisson: int,
    portions: int,
    difficulte: str,
    ingredients: list,
    etapes: list,
    image_path: str = None,
):
    """Sauvegarde la recette importee via ServiceRecettes"""
    try:
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"🔄 Tentative sauvegarde recette: {nom}")

        service = obtenir_service_recettes()
        if not service:
            st.error("❌ Service indisponible")
            logger.error("Service recette indisponible")
            return

        with st.spinner("💾 Sauvegarde en cours..."):
            recette = service.create_from_import(
                nom=nom,
                type_repas=type_repas,
                description=description,
                temps_preparation=temps_preparation,
                temps_cuisson=temps_cuisson,
                portions=portions,
                difficulte=difficulte,
                ingredients_textes=ingredients,
                etapes_textes=etapes,
                image_path=image_path,
            )

            if recette:
                # Stocker le succès dans session_state pour affichage persistant
                st.session_state.last_imported_recipe_name = nom
                # Effacer les donnees extraites
                st.session_state.extracted_recipe = None

                st.success(f"✅ Recette '{nom}' importee avec succès!")
                logger.info(f"✅ Recette '{nom}' importee avec succès")
                st.balloons()
            else:
                st.error("❌ Erreur lors de la sauvegarde")

    except Exception as e:
        st.error(f"❌ Erreur sauvegarde: {str(e)}")
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Erreur import recette: {e}", exc_info=True)
