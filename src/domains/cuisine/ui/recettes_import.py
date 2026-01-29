"""
Module pour l'import de recettes
"""

import streamlit as st
from src.utils.recipe_importer import RecipeImporter
from src.services.recettes import get_recette_service
from src.core.models import Recette, RecetteIngredient, Ingredient, EtapeRecette
from src.core.database import obtenir_contexte_db

# Logique métier pure
from src.domains.cuisine.logic.recettes_logic import (
    valider_recette
)


def render_importer():
    """Interface pour importer une recette"""
    st.subheader("📥 Importer une recette")
    st.write("Importez une recette depuis un site web, un PDF ou du texte")
    
    # Onglets pour différents types d'import
    import_tab1, import_tab2, import_tab3 = st.tabs(["🌐 URL/Site Web", "📄 Fichier PDF", "📝 Texte"])
    
    with import_tab1:
        _render_import_url()
    
    with import_tab2:
        _render_import_pdf()
    
    with import_tab3:
        _render_import_text()


def _render_import_url():
    """Import depuis une URL"""
    st.markdown("### 🌐 Importer depuis une URL")
    st.info("Entrez l'URL d'un site contenant une recette (recipetin, marmiton, cuisineaz, etc.)")
    
    url = st.text_input("URL du site", placeholder="https://www.marmiton.org/recettes/...")
    
    if st.button("🔍 Analyser le site", use_container_width=True):
        if not url:
            st.error("❌ Veuillez entrer une URL")
            return
        
        with st.spinner("⏳ Extraction de la recette..."):
            try:
                recipe_data = RecipeImporter.from_url(url)
                
                if recipe_data:
                    st.success("✅ Recette extraite!")
                    _show_import_preview(recipe_data)
                else:
                    st.error("❌ Impossible d'extraire la recette. Vérifiez l'URL.")
                    
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")


def _render_import_pdf():
    """Import depuis un PDF"""
    st.markdown("### 📄 Importer depuis un PDF")
    st.info("Téléchargez un fichier PDF contenant une recette")
    
    pdf_file = st.file_uploader("Choisissez un fichier PDF", type=["pdf"])
    
    if pdf_file:
        # Sauvegarder temporairement
        import tempfile
        import os
        
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


def _render_import_text():
    """Import depuis du texte"""
    st.markdown("### 📝 Importer depuis du texte")
    st.info("Collez le texte d'une recette (HTML, texte brut, etc.)")
    
    text = st.text_area(
        "Collez la recette ici",
        height=300,
        placeholder="""Pâtes à la Bolognaise

Ingrédients:
- 400g de pâtes
- 500g de viande hachée
- 2 oignons

Étapes:
1. Cuire les pâtes
2. Préparer la sauce
..."""
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
    st.markdown("### 📋 Aperçu et modification")
    
    # Formulaire d'édition
    with st.form("form_import_recette"):
        # Infos de base
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de la recette *", value=recipe_data.get('nom', ''))
        with col2:
            type_repas = st.selectbox(
                "Type de repas *",
                ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"]
            )
        
        description = st.text_area(
            "Description",
            value=recipe_data.get('description', ''),
            height=100
        )
        
        # Temps et portions
        col1, col2, col3 = st.columns(3)
        with col1:
            temps_prep = st.number_input(
                "Temps préparation (min)",
                min_value=0,
                max_value=300,
                value=recipe_data.get('temps_preparation', 15)
            )
        with col2:
            temps_cuisson = st.number_input(
                "Temps cuisson (min)",
                min_value=0,
                max_value=300,
                value=recipe_data.get('temps_cuisson', 20)
            )
        with col3:
            portions = st.number_input(
                "Portions",
                min_value=1,
                max_value=20,
                value=recipe_data.get('portions', 4)
            )
        
        difficulte = st.selectbox(
            "Difficulté",
            ["facile", "moyen", "difficile"],
            index=0
        )
        
        # Ingrédients
        st.markdown("#### 🛍 Ingrédients")
        ingredients = recipe_data.get('ingredients', [])
        
        # Afficher et permettre l'édition
        edited_ingredients = []
        for idx, ing in enumerate(ingredients):
            ing_text = st.text_input(f"Ingrédient {idx + 1}", value=ing, key=f"ing_{idx}")
            if ing_text:
                edited_ingredients.append(ing_text)
        
        # Ajouter un ingrédient vierge pour en ajouter plus
        new_ing = st.text_input("Nouvel ingrédient (optionnel)", key="new_ing")
        if new_ing:
            edited_ingredients.append(new_ing)
        
        # Étapes
        st.markdown("#### 👨‍🍳 Étapes de préparation")
        etapes = recipe_data.get('etapes', [])
        
        edited_etapes = []
        for idx, etape in enumerate(etapes):
            # Enlever le numéro si présent
            etape_text = etape.lstrip('0123456789.').strip()
            etape_input = st.text_area(f"Étape {idx + 1}", value=etape_text, height=60, key=f"step_{idx}")
            if etape_input:
                edited_etapes.append(etape_input)
        
        # Ajouter une étape vierge
        new_step = st.text_area("Nouvelle étape (optionnel)", height=60, key="new_step")
        if new_step:
            edited_etapes.append(new_step)
        
        # Valider
        submitted = st.form_submit_button("✅ Importer cette recette", use_container_width=True)
        
        if submitted:
            if not nom:
                st.error("❌ Le nom est obligatoire")
                return
            
            if not edited_ingredients:
                st.error("❌ Au moins un ingrédient est obligatoire")
                return
            
            if not edited_etapes:
                st.error("❌ Au moins une étape est obligatoire")
                return
            
            _save_imported_recipe(
                nom=nom,
                type_repas=type_repas,
                description=description,
                temps_preparation=temps_prep,
                temps_cuisson=temps_cuisson,
                portions=portions,
                difficulte=difficulte,
                ingredients=edited_ingredients,
                etapes=edited_etapes
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
    etapes: list
):
    """Sauvegarde la recette importée"""
    try:
        service = get_recette_service()
        if not service:
            st.error("❌ Service indisponible")
            return
        
        with st.spinner("💾 Sauvegarde en cours..."):
            # Créer la recette
            recette = Recette(
                nom=nom,
                type_repas=type_repas,
                description=description,
                temps_preparation=temps_preparation,
                temps_cuisson=temps_cuisson,
                portions=portions,
                difficulte=difficulte,
                source="import"  # Marquer comme importée
            )
            
            with obtenir_contexte_db() as db:
                # Sauvegarder la recette
                db.add(recette)
                db.flush()  # Pour avoir l'ID
                
                # Ajouter les ingrédients
                for idx, ing_text in enumerate(ingredients, 1):
                    # Parser "quantité unité nom"
                    parts = ing_text.split(maxsplit=2)
                    
                    if len(parts) >= 3:
                        quantite_str, unite, nom_ing = parts[0], parts[1], ' '.join(parts[2:])
                        quantite = float(quantite_str.replace(',', '.'))
                    elif len(parts) >= 2:
                        quantite_str, nom_ing = parts[0], parts[1]
                        quantite = float(quantite_str.replace(',', '.'))
                        unite = "g"
                    else:
                        quantite = 1
                        unite = ""
                        nom_ing = ing_text
                    
                    # Chercher ou créer l'ingrédient
                    ingredient = db.query(Ingredient).filter_by(nom=nom_ing).first()
                    if not ingredient:
                        ingredient = Ingredient(nom=nom_ing)
                        db.add(ingredient)
                        db.flush()
                    
                    ri = RecetteIngredient(
                        recette_id=recette.id,
                        ingredient_id=ingredient.id,
                        quantite=quantite,
                        unite=unite,
                        ordre=idx
                    )
                    db.add(ri)
                
                # Ajouter les étapes
                for idx, etape_text in enumerate(etapes, 1):
                    etape = EtapeRecette(
                        recette_id=recette.id,
                        description=etape_text,
                        ordre=idx
                    )
                    db.add(etape)
                
                db.commit()
            
            st.success(f"✅ Recette '{nom}' importée avec succès!")
            st.balloons()
            
            # Réinitialiser le formulaire
            import time
            time.sleep(1)
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erreur sauvegarde: {str(e)}")
        import logging
        logging.error(f"Erreur import recette: {e}")
