"""
Ajout manuel de recettes.
"""

import logging
import time

import streamlit as st

from src.core.errors_base import ErreurValidation
from src.services.recettes import get_recette_service

logger = logging.getLogger(__name__)


def render_ajouter_manuel():
    """Formulaire pour ajouter une recette manuellement"""
    st.subheader("➕ Ajouter une recette manuellement")

    # Initialiser session_state si nécessaire
    if "form_num_ingredients" not in st.session_state:
        st.session_state.form_num_ingredients = 3
    if "form_num_etapes" not in st.session_state:
        st.session_state.form_num_etapes = 3

    # Infos basiques (sans form pour réactivité)
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom de la recette *", max_chars=200, key="form_nom")
    with col2:
        type_repas = st.selectbox(
            "Type de repas *",
            ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"],
            key="form_type_repas",
        )

    # Upload d'image
    col_img, col_space = st.columns([2, 1])
    with col_img:
        image_file = st.file_uploader(
            "📷 Photo de la recette (optionnel)",
            type=["jpg", "jpeg", "png"],
            key="form_image_upload",
        )

    description = st.text_area("Description", height=100, key="form_description")

    col1, col2, col3 = st.columns(3)
    with col1:
        temps_prep = st.number_input(
            "Temps préparation (min)", min_value=0, max_value=300, value=15, key="form_temps_prep"
        )
    with col2:
        temps_cuisson = st.number_input(
            "Temps cuisson (min)", min_value=0, max_value=300, value=20, key="form_temps_cuisson"
        )
    with col3:
        portions = st.number_input(
            "Portions", min_value=1, max_value=20, value=4, key="form_portions"
        )

    col1, col2 = st.columns(2)
    with col1:
        difficulte = st.selectbox(
            "Difficulté", ["facile", "moyen", "difficile"], key="form_difficulte"
        )
    with col2:
        saison = st.selectbox(
            "Saison", ["toute_année", "printemps", "été", "automne", "hiver"], key="form_saison"
        )

    # Ingrédients
    st.markdown("### Ingrédients")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_ingredients = st.number_input(
            "Nombre d'ingrédients",
            min_value=1,
            max_value=20,
            value=st.session_state.form_num_ingredients,
            key="form_num_ing_selector",
        )
        st.session_state.form_num_ingredients = num_ingredients

    ingredients = []
    for i in range(int(num_ingredients)):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ing_nom = st.text_input(f"Ingrédient {i + 1}", key=f"form_ing_nom_{i}")
        with col2:
            ing_qty = st.number_input("Qté", value=1.0, key=f"form_ing_qty_{i}", step=0.25)
        with col3:
            ing_unit = st.text_input("Unité", value="g", key=f"form_ing_unit_{i}", max_chars=20)

        if ing_nom:
            ingredients.append({"nom": ing_nom, "quantite": ing_qty, "unite": ing_unit})

    # Étapes
    st.markdown("### Étapes de préparation")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_etapes = st.number_input(
            "Nombre d'étapes",
            min_value=1,
            max_value=15,
            value=st.session_state.form_num_etapes,
            key="form_num_etapes_selector",
        )
        st.session_state.form_num_etapes = num_etapes

    etapes = []
    for i in range(int(num_etapes)):
        etape_desc = st.text_area(f"Étape {i + 1}", height=80, key=f"form_etape_{i}")
        if etape_desc:
            etapes.append({"description": etape_desc, "duree": None})

    # Bouton créer
    if st.button("✅ Créer la recette", use_container_width=True, type="primary"):
        if not nom or not type_repas:
            st.error("❌ Nom et type de repas sont obligatoires")
        elif not ingredients:
            st.error("❌ Ajoutez au moins un ingrédient")
        elif not etapes:
            st.error("❌ Ajoutez au moins une étape")
        else:
            # Créer la recette
            service = get_recette_service()
            if service is None:
                st.error("❌ Service indisponible")
            else:
                try:
                    # Sauvegarder l'image si fournie
                    url_image = None
                    if image_file is not None:
                        import uuid
                        from pathlib import Path

                        # Créer dossier images s'il n'existe pas
                        images_dir = Path("data/recettes_images")
                        images_dir.mkdir(parents=True, exist_ok=True)

                        # Sauvegarder l'image avec un nom unique
                        ext = image_file.name.split(".")[-1]
                        unique_name = f"recette_{uuid.uuid4().hex[:8]}.{ext}"
                        image_path = images_dir / unique_name

                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())

                        url_image = str(image_path)

                    data = {
                        "nom": nom,
                        "description": description,
                        "type_repas": type_repas,
                        "temps_preparation": int(temps_prep),
                        "temps_cuisson": int(temps_cuisson),
                        "portions": int(portions),
                        "difficulte": difficulte,
                        "saison": saison,
                        "ingredients": ingredients,
                        "etapes": etapes,
                        "url_image": url_image,
                    }

                    # Créer la recette avec session BD
                    from src.core.db import obtenir_contexte_db

                    with obtenir_contexte_db() as db:
                        recette = service.create_complete(data, db=db)

                    # Réinitialiser le formulaire
                    st.session_state.form_num_ingredients = 3
                    st.session_state.form_num_etapes = 3
                    for key in list(st.session_state.keys()):
                        if key.startswith("form_"):
                            del st.session_state[key]

                    st.success(f"✅ Recette '{recette.nom}' créée avec succès!")
                    if image_file:
                        st.caption(f"📷 Image sauvegardée: {image_file.name}")
                    st.balloons()
                    time.sleep(1)

                except ErreurValidation as e:
                    st.error(f"❌ Erreur validation: {e}")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
                    logger.error(f"Erreur création recette: {e}")


__all__ = ["render_ajouter_manuel"]
