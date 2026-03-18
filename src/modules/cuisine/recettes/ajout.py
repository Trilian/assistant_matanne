"""
Ajout manuel de recettes.
"""

import logging
import time

import streamlit as st

from src.core.exceptions import ErreurValidation
from src.services.cuisine.recettes import obtenir_service_recettes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("recettes_ajout")


@ui_fragment
def afficher_ajouter_manuel():
    """Formulaire pour ajouter une recette manuellement"""
    st.subheader("➕ Ajouter une recette manuellement")

    # Initialiser session_state si nécessaire
    if _keys("num_ingredients") not in st.session_state:
        st.session_state[_keys("num_ingredients")] = 3
    if _keys("num_etapes") not in st.session_state:
        st.session_state[_keys("num_etapes")] = 3

    # Infos basiques (sans form pour réactivité)
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom de la recette *", max_chars=200, key=_keys("nom"))
    with col2:
        type_repas = st.selectbox(
            "Type de repas *",
            ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"],
            key=_keys("type_repas"),
        )

    # Upload d'image
    col_img, col_space = st.columns([2, 1])
    with col_img:
        image_file = st.file_uploader(
            "📷 Photo de la recette (optionnel)",
            type=["jpg", "jpeg", "png"],
            key=_keys("image_upload"),
        )

    description = st.text_area("Description", height=100, key=_keys("description"))

    col1, col2, col3 = st.columns(3)
    with col1:
        temps_prep = st.number_input(
            "Temps préparation (min)", min_value=0, max_value=300, value=15, key=_keys("temps_prep")
        )
    with col2:
        temps_cuisson = st.number_input(
            "Temps cuisson (min)", min_value=0, max_value=300, value=20, key=_keys("temps_cuisson")
        )
    with col3:
        portions = st.number_input(
            "Portions", min_value=1, max_value=20, value=4, key=_keys("portions")
        )

    col1, col2 = st.columns(2)
    with col1:
        difficulte = st.selectbox(
            "Difficulté", ["facile", "moyen", "difficile"], key=_keys("difficulte")
        )
    with col2:
        saison = st.selectbox(
            "Saison", ["toute_année", "printemps", "été", "automne", "hiver"], key=_keys("saison")
        )

    col1, col2 = st.columns(2)
    with col1:
        categorie = st.selectbox(
            "Catégorie",
            ["Plat", "Entrée", "Dessert", "Accompagnement", "Apéritif", "Petit-déjeuner", "Goûter"],
            key=_keys("categorie"),
        )
    with col2:
        url_image_input = st.text_input(
            "URL image (optionnel)",
            key=_keys("url_image"),
            placeholder="https://...",
        )

    # Ingrédients
    st.markdown("### Ingrédients")
    col1, col2 = st.columns([3, 1])
    with col1:
        num_ingredients = st.number_input(
            "Nombre d'ingrédients",
            min_value=1,
            max_value=20,
            value=st.session_state[_keys("num_ingredients")],
            key=_keys("num_ing_selector"),
        )
        st.session_state[_keys("num_ingredients")] = num_ingredients

    ingredients = []
    for i in range(int(num_ingredients)):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ing_nom = st.text_input(f"Ingrédient {i + 1}", key=_keys("ing_nom", i))
        with col2:
            ing_qty = st.number_input("Qté", value=1.0, key=_keys("ing_qty", i), step=0.25)
        with col3:
            ing_unit = st.text_input("Unité", value="g", key=_keys("ing_unit", i), max_chars=20)

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
            value=st.session_state[_keys("num_etapes")],
            key=_keys("num_etapes_selector"),
        )
        st.session_state[_keys("num_etapes")] = num_etapes

    etapes = []
    for i in range(int(num_etapes)):
        etape_desc = st.text_area(f"Étape {i + 1}", height=80, key=_keys("etape", i))
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
            service = obtenir_service_recettes()
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
                    elif url_image_input and url_image_input.strip():
                        url_image = url_image_input.strip()

                    data = {
                        "nom": nom,
                        "description": description,
                        "type_repas": type_repas,
                        "temps_preparation": int(temps_prep),
                        "temps_cuisson": int(temps_cuisson),
                        "portions": int(portions),
                        "difficulte": difficulte,
                        "saison": saison,
                        "categorie": categorie,
                        "ingredients": ingredients,
                        "etapes": etapes,
                        "url_image": url_image,
                    }

                    # Créer la recette - service gère sa propre session
                    recette = service.create_complete(data)

                    # Réinitialiser le formulaire
                    st.session_state[_keys("num_ingredients")] = 3
                    st.session_state[_keys("num_etapes")] = 3
                    prefix = _keys.prefix + "__"
                    for key in list(st.session_state.keys()):
                        if key.startswith(prefix):
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


__all__ = ["afficher_ajouter_manuel"]
