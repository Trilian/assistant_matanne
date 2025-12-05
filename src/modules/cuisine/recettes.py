"""
Module Recettes - Refait avec génération IA, versions multiples, images
Architecture moderne et flux optimisé
"""
import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, date
from typing import List, Dict, Optional
from src.core.database import get_db_context
from src.core.models import (
    Recette, RecetteIngredient, EtapeRecette, VersionRecette,
    Ingredient
)
from src.services.ai_recette_service import ai_recipe_service
# ===================================
# HELPERS - CRUD RECETTES
# ===================================
def load_recipes(filters: Optional[Dict] = None) -> pd.DataFrame:
    """Charge les recettes avec filtres"""
    with get_db_context() as db:
        query = db.query(Recette)

        if filters:
            if filters.get("saison"):
                query = query.filter(Recette.saison == filters["saison"])
            if filters.get("type_repas"):
                query = query.filter(Recette.type_repas == filters["type_repas"])
            if filters.get("est_rapide"):
                query = query.filter(Recette.est_rapide == True)
            if filters.get("est_equilibre"):
                query = query.filter(Recette.est_equilibre == True)
            if filters.get("compatible_bebe"):
                query = query.filter(Recette.compatible_bebe == True)
            if filters.get("recherche"):
                query = query.filter(Recette.nom.ilike(f"%{filters['recherche']}%"))

        recettes = query.order_by(Recette.cree_le.desc()).all()

        return pd.DataFrame([{
            "id": r.id,
            "nom": r.nom,
            "description": r.description,
            "temps_preparation": r.temps_preparation,
            "temps_cuisson": r.temps_cuisson,
            "temps_total": r.temps_preparation + r.temps_cuisson,
            "portions": r.portions,
            "difficulte": r.difficulte,
            "type_repas": r.type_repas,
            "saison": r.saison,
            "categorie": r.categorie or "—",
            "est_rapide": r.est_rapide,
            "est_equilibre": r.est_equilibre,
            "compatible_bebe": r.compatible_bebe,
            "compatible_batch": r.compatible_batch,
            "congelable": r.congelable,
            "genere_par_ia": r.genere_par_ia,
            "score_ia": r.score_ia or 0,
            "url_image": r.url_image,
            "cree_le": r.cree_le
        } for r in recettes])

def load_recipe_details(recipe_id: int) -> Dict:
    """Charge les détails complets d'une recette"""
    with get_db_context() as db:
        recette = db.query(Recette).get(recipe_id)
        if not recette:
            return None

        return {
            "recette": recette,
            "ingredients": [
                {
                    "nom": ri.ingredient.nom,
                    "quantite": ri.quantite,
                    "unite": ri.unite,
                    "optionnel": ri.optionnel
                }
                for ri in recette.ingredients
            ],
            "etapes": [
                {
                    "ordre": step.ordre,
                    "description": step.description,
                    "duree": step.duree
                }
                for step in sorted(recette.etapes, key=lambda x: x.ordre)
            ],
            "versions": [
                {
                    "type": v.type_version,
                    "instructions": v.instructions_modifiees,
                    "notes_bebe": v.notes_bebe,
                    "infos_batch": {
                        "etapes_paralleles": v.etapes_paralleles_batch,
                        "temps_optimise": v.temps_optimise_batch
                    } if v.type_version == "batch_cooking" else None
                }
                for v in recette.versions
            ]
        }
def save_recipe(recipe_data: Dict, version_data: Optional[Dict] = None) -> int:
    """Sauvegarde une recette avec ses ingrédients, étapes et versions"""
    with get_db_context() as db:
        # Créer la recette
        recette = Recette(
            nom=recipe_data["nom"],
            description=recipe_data.get("description"),
            temps_preparation=recipe_data["temps_preparation"],
            temps_cuisson=recipe_data["temps_cuisson"],
            portions=recipe_data["portions"],
            difficulte=recipe_data.get("difficulte", "moyen"),
            type_repas=recipe_data.get("type_repas", "dîner"),
            saison=recipe_data.get("saison", "toute_année"),
            categorie=recipe_data.get("categorie"),
            est_rapide=recipe_data.get("est_rapide", False),
            est_equilibre=recipe_data.get("est_equilibre", False),
            compatible_bebe=recipe_data.get("compatible_bebe", False),
            compatible_batch=recipe_data.get("compatible_batch", False),
            congelable=recipe_data.get("congelable", False),
            genere_par_ia=recipe_data.get("genere_par_ia", False),
            score_ia=recipe_data.get("score_ia"),
            url_image=recipe_data.get("url_image")
        )
        db.add(recette)
        db.flush()

        # Ajouter ingrédients
        for ing_data in recipe_data.get("ingredients", []):
            ingredient = db.query(Ingredient).filter(
                Ingredient.nom == ing_data["nom"]
            ).first()

            if not ingredient:
                ingredient = Ingredient(
                    nom=ing_data["nom"],
                    unite=ing_data["unite"],
                    categorie=ing_data.get("categorie")
                )
                db.add(ingredient)
                db.flush()

            recette_ing = RecetteIngredient(
                recette_id=recette.id,
                ingredient_id=ingredient.id,
                quantite=ing_data["quantite"],
                unite=ing_data["unite"],
                optionnel=ing_data.get("optionnel", False)
            )
            db.add(recette_ing)

        # Ajouter étapes
        for step_data in recipe_data.get("etapes", []):
            etape = EtapeRecette(
                recette_id=recette.id,
                ordre=step_data["ordre"],
                description=step_data["description"],
                duree=step_data.get("duree")
            )
            db.add(etape)

        # Ajouter versions
        if version_data:
            for v_type, v_data in version_data.items():
                version = VersionRecette(
                    recette_base_id=recette.id,
                    type_version=v_type,
                    instructions_modifiees=v_data.get("instructions_modifiees"),
                    ingredients_modifies=v_data.get("ingredients_modifies"),
                    notes_bebe=v_data.get("notes_bebe"),
                    etapes_paralleles_batch=v_data.get("etapes_paralleles"),
                    temps_optimise_batch=v_data.get("temps_optimise")
                )
                db.add(version)

        db.commit()
        return recette.id

def delete_recipe(recipe_id: int):
    """Supprime une recette"""
    with get_db_context() as db:
        db.query(Recette).filter(Recette.id == recipe_id).delete()
        db.commit()
# ===================================
# UI COMPONENTS
# ===================================
def render_recipe_card(recette: pd.Series):
    """Affiche une carte recette moderne"""
    with st.container():
        col1, col2 = st.columns([1, 3])

        with col1:
            # Image - FIX
            if pd.notna(recette["url_image"]) and recette["url_image"]:
                try:
                    st.image(recette["url_image"], use_container_width=True)
                except:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    height: 150px; border-radius: 8px; display: flex; 
                                    align-items: center; justify-content: center; color: white;">
                            <span style="font-size: 3rem;">🍽️</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                height: 150px; border-radius: 8px; display: flex; 
                                align-items: center; justify-content: center; color: white;">
                        <span style="font-size: 3rem;">🍽️</span>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            # Titre et tags
            st.markdown(f"### {recette['nom']}")

            # Tags
            tags = []
            if recette["est_rapide"]:
                tags.append("⚡ Rapide")
            if recette["est_equilibre"]:
                tags.append("🥗 Équilibré")
            if recette["compatible_bebe"]:
                tags.append("👶 Bébé OK")
            if recette["compatible_batch"]:
                tags.append("🍳 Batch")
            if recette["congelable"]:
                tags.append("❄️ Congélation")
            if recette["genere_par_ia"]:
                tags.append(f"🤖 IA ({recette['score_ia']:.0f}%)")

            st.caption(" • ".join(tags) if tags else "—")

            # Description
            if recette["description"]:
                desc = recette["description"]
                st.write(desc[:150] + "..." if len(desc) > 150 else desc)

            # Infos
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)

            with col_info1:
                st.caption(f"⏱️ {recette['temps_total']}min")
            with col_info2:
                st.caption(f"🍽️ {recette['portions']} pers.")
            with col_info3:
                difficulty_emoji = {"facile": "😊", "moyen": "😐", "difficile": "😰"}
                st.caption(f"{difficulty_emoji.get(recette['difficulte'], '😐')} {recette['difficulte'].capitalize()}")
            with col_info4:
                st.caption(f"📅 {recette['saison'].replace('_', ' ').capitalize()}")

def render_recipe_details(recipe_id: int):
    """Affiche les détails complets d'une recette"""
    details = load_recipe_details(recipe_id)
    if not details:
        st.error("Recette introuvable")
        return

    recette = details["recette"]

    # Header
    col_h1, col_h2 = st.columns([2, 1])

    with col_h1:
        st.markdown(f"# {recette.nom}")
        st.caption(recette.description or "")

    with col_h2:
        if recette.url_image:
            st.image(recette.url_image, use_container_width=True)

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📋 Recette", "👶 Version Bébé", "🍳 Version Batch"])

    with tab1:
        # Ingrédients
        st.markdown("### 🥕 Ingrédients")
        for ing in details["ingredients"]:
            optionnel = " (optionnel)" if ing["optionnel"] else ""
            st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}{optionnel}")

        st.markdown("---")

        # Étapes
        st.markdown("### 📝 Étapes")
        for step in details["etapes"]:
            duree = f" ({step['duree']}min)" if step["duree"] else ""
            st.markdown(f"**{step['ordre']}.** {step['description']}{duree}")

    with tab2:
        baby_version = next(
            (v for v in details["versions"] if v["type"] == "bébé"),
            None
        )
        if baby_version:
            st.markdown("### 👶 Adaptation pour bébé")
            st.info(baby_version["instructions"] or "Pas d'instructions spécifiques")
            if baby_version["notes_bebe"]:
                st.warning(f"⚠️ **Précautions :** {baby_version['notes_bebe']}")
        else:
            st.info("Aucune version bébé disponible pour cette recette")

    with tab3:
        batch_version = next(
            (v for v in details["versions"] if v["type"] == "batch_cooking"),
            None
        )
        if batch_version and batch_version["infos_batch"]:
            info = batch_version["infos_batch"]
            st.markdown("### 🍳 Optimisation Batch Cooking")

            if info.get("etapes_paralleles"):
                st.markdown("**Étapes parallélisables :**")
                for step in info["etapes_paralleles"]:
                    st.write(f"• {step}")

            if info.get("temps_optimise"):
                st.metric(
                    "Temps optimisé",
                    f"{info['temps_optimise']}min",
                    delta=f"-{(recette.temps_preparation + recette.temps_cuisson) - info['temps_optimise']}min"
                )
        else:
            st.info("Aucune optimisation batch cooking disponible")
# ===================================
# MODULE PRINCIPAL
# ===================================
def app():
    """Module Recettes - Point d'entrée"""
    st.title("🍲 Recettes Intelligentes")
    st.caption("Génération IA, versions multiples, gestion complète")
    # Tabs principaux
    tab1, tab2, tab3 = st.tabs([
        "📚 Mes Recettes",
        "✨ Générer avec l'IA",
        "➕ Ajouter Manuellement"
    ])
    # ===================================
    # TAB 1 : MES RECETTES
    # ===================================
    with tab1:
        st.subheader("Ma collection de recettes")
        # Filtres
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            search = st.text_input("🔍 Rechercher", placeholder="Nom de recette...")
        with col_f2:
            season_filter = st.selectbox(
                "Saison",
                ["Toutes"] + [s.value for s in SeasonEnum]
            )
        with col_f3:
            meal_filter = st.selectbox(
                "Type de repas",
                ["Tous"] + [m.value for m in MealTypeEnum]
            )
        with col_f4:
            quick_only = st.checkbox("⚡ Rapides uniquement")
        # Filtres avancés (collapsible)
        with st.expander("🔧 Filtres avancés"):
            col_fa1, col_fa2, col_fa3 = st.columns(3)
            with col_fa1:
                balanced_only = st.checkbox("🥗 Équilibrées")
                baby_friendly_only = st.checkbox("👶 Compatible bébé")
            with col_fa2:
                batch_friendly_only = st.checkbox("🍳 Compatible batch")
                freezable_only = st.checkbox("❄️ Congélable")
            with col_fa3:
                ai_only = st.checkbox("🤖 Générées par IA")

        # Construire les filtres
        filtres = {}
        if recherche:
            filtres["recherche"] = recherche
        if filtre_saison != "Toutes":
            filtres["saison"] = filtre_saison
        if filtre_repas != "Tous":
            filtres["type_repas"] = filtre_repas
        if rapide_uniquement:
            filtres["est_rapide"] = True
        if equilibre_uniquement:
            filtres["est_equilibre"] = True
        if bebe_uniquement:
            filtres["compatible_bebe"] = True

        # Charger recettes
        df = load_recipes(filters)
        if df.empty:
            st.info("Aucune recette trouvée. Génère-en avec l'IA ou ajoute-en manuellement !")
        else:
            # Statistiques
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)

            with col_s1:
                st.metric("Total", len(df))
            with col_s2:
                rapides = len(df[df["est_rapide"] == True])
                st.metric("Rapides", rapides)
            with col_s3:
                ia_count = len(df[df["genere_par_ia"] == True])
                st.metric("Générées IA", ia_count)
            with col_s4:
                temps_moyen = df["temps_total"].mean()
                st.metric("Temps moyen", f"{temps_moyen:.0f}min")
            st.markdown("---")

            # Afficher les recettes
            for idx, recette in df.iterrows():
                render_recipe_card(recette)

                # Actions
                col_a1, col_a2, col_a3 = st.columns([1, 1, 3])

                with col_a1:
                    if st.button("👁️ Détails", key=f"view_{recette['id']}", use_container_width=True):
                        st.session_state[f"viewing_{recette['id']}"] = True
                        st.rerun()

                with col_a2:
                    if st.button("🗑️ Supprimer", key=f"del_{recette['id']}", use_container_width=True):
                        delete_recipe(recette['id'])
                        st.success("Recette supprimée")
                        st.rerun()

                # Afficher détails si demandé
                if st.session_state.get(f"viewing_{recette['id']}", False):
                    with st.expander("Détails complets", expanded=True):
                        render_recipe_details(recette['id'])
                        if st.button("Fermer", key=f"close_{recette['id']}"):
                            del st.session_state[f"viewing_{recette['id']}"]
                            st.rerun()

                st.markdown("---")
    # ===================================
    # TAB 2 : GÉNÉRATION IA
    # ===================================
    with tab2:
        st.subheader("✨ Générer des recettes avec l'IA")
        st.info("💡 L'IA génère des recettes selon tes critères, avec images et versions multiples")
        # Formulaire de génération
        with st.form("ai_generation"):
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("**Critères de base**")
                count = st.slider("Nombre de recettes", 1, 5, 3)
                season = st.selectbox(
                    "Saison",
                    ["all_year"] + [s.value for s in SeasonEnum if s != SeasonEnum.ALL_YEAR]
                )
                meal_type = st.selectbox(
                    "Type de repas",
                    [m.value for m in MealTypeEnum]
                )
                category = st.text_input(
                    "Catégorie (optionnel)",
                    placeholder="Végétarien, Italien, etc."
                )
            with col_g2:
                st.markdown("**Filtres**")
                is_quick = st.checkbox("⚡ Rapide (<30min)")
                is_balanced = st.checkbox("🥗 Équilibré", value=True)
                is_baby_friendly = st.checkbox("👶 Compatible bébé")
                is_batch_friendly = st.checkbox("🍳 Compatible batch cooking")
                is_freezable = st.checkbox("❄️ Congélable")
                ingredients_input = st.text_input(
                    "Ingrédients à utiliser (optionnel)",
                    placeholder="tomate, basilic, mozzarella"
                )
            st.markdown("**Versions à générer**")
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1:
                gen_standard = st.checkbox("📋 Standard", value=True)
            with col_v2:
                gen_baby = st.checkbox("👶 Bébé")
            with col_v3:
                gen_batch = st.checkbox("🍳 Batch Cooking")
            submitted = st.form_submit_button("✨ Générer les recettes", type="primary", use_container_width=True)
        if submitted:
            if not gen_standard and not gen_baby and not gen_batch:
                st.error("Sélectionne au moins une version à générer")
            else:
                with st.spinner("🤖 L'IA génère les recettes..."):
                    try:
                        # Préparer filtres
                        filters = {
                            "season": season,
                            "meal_type": meal_type,
                            "is_quick": is_quick,
                            "is_balanced": is_balanced,
                            "category": category if category else None,
                            "ingredients": [i.strip() for i in ingredients_input.split(",")] if ingredients_input else None
                        }
                        # Générer recettes
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        recipes = loop.run_until_complete(
                            ai_recipe_service.generate_recipes(
                                count=count,
                                filters=filters,
                                version_type="standard"
                            )
                        )
                        # Générer versions supplémentaires si demandé
                        if gen_baby or gen_batch:
                            for recipe in recipes:
                                versions = {}
                                if gen_baby:
                                    baby_recipes = loop.run_until_complete(
                                        ai_recipe_service.generate_recipes(
                                            count=1,
                                            filters={"name": recipe["name"]},
                                            version_type="baby"
                                        )
                                    )
                                    if baby_recipes:
                                        versions["baby"] = baby_recipes[0].get("baby_version", {})
                                if gen_batch:
                                    batch_recipes = loop.run_until_complete(
                                        ai_recipe_service.generate_recipes(
                                            count=1,
                                            filters={"name": recipe["name"]},
                                            version_type="batch_cooking"
                                        )
                                    )
                                    if batch_recipes:
                                        versions["batch"] = batch_recipes[0].get("batch_version", {})
                                recipe["versions"] = versions
                        # Générer images
                        for recipe in recipes:
                            image_url = loop.run_until_complete(
                                ai_recipe_service.generate_image_url(
                                    recipe["name"],
                                    recipe["description"]
                                )
                            )
                            recipe["image_url"] = image_url
                        st.session_state["generated_recipes"] = recipes
                        st.success(f"✅ {len(recipes)} recette(s) générée(s) !")
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        # Afficher recettes générées
        if "generated_recipes" in st.session_state:
            st.markdown("---")
            st.markdown("### 📋 Recettes générées")
            recipes = st.session_state["generated_recipes"]
            selected_recipes = []
            for idx, recipe in enumerate(recipes):
                with st.expander(f"🍽️ {recipe['name']}", expanded=True):
                    col_r1, col_r2 = st.columns([1, 2])
                    with col_r1:
                        if recipe.get("image_url"):
                            st.image(recipe["image_url"], use_container_width=True)
                    with col_r2:
                        st.write(f"**{recipe['description']}**")
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.caption(f"⏱️ {recipe['prep_time'] + recipe['cook_time']}min")
                        with col_info2:
                            st.caption(f"🍽️ {recipe['servings']} portions")
                        with col_info3:
                            st.caption(f"😊 {recipe['difficulty'].capitalize()}")
                    # Ingrédients
                    st.markdown("**Ingrédients :**")
                    for ing in recipe["ingredients"]:
                        st.write(f"• {ing['quantity']} {ing['unit']} de {ing['name']}")
                    # Étapes
                    st.markdown("**Étapes :**")
                    for step in recipe["steps"]:
                        st.write(f"{step['order']}. {step['description']}")
                    # Versions
                    if recipe.get("versions"):
                        st.markdown("**Versions disponibles :**")
                        versions_str = []
                        if "baby" in recipe["versions"]:
                            versions_str.append("👶 Bébé")
                        if "batch" in recipe["versions"]:
                            versions_str.append("🍳 Batch")
                        st.caption(" • ".join(versions_str))
                    # Sélection
                    if st.checkbox(f"Sélectionner cette recette", key=f"select_{idx}"):
                        selected_recipes.append(recipe)
            # Bouton ajout
            if selected_recipes:
                if st.button(f"➕ Ajouter {len(selected_recipes)} recette(s) sélectionnée(s)", type="primary"):
                    for recipe in selected_recipes:
                        # Préparer versions
                        version_data = None
                        if recipe.get("versions"):
                            version_data = {}
                            if "baby" in recipe["versions"]:
                                version_data[RecipeVersionEnum.BABY] = recipe["versions"]["baby"]
                            if "batch" in recipe["versions"]:
                                version_data[RecipeVersionEnum.BATCH_COOKING] = recipe["versions"]["batch"]
                        # Sauvegarder
                        save_recipe(recipe, version_data)
                    st.success(f"✅ {len(selected_recipes)} recette(s) ajoutée(s) !")
                    del st.session_state["generated_recipes"]
                    st.balloons()
                    st.rerun()
    # ===================================
    # TAB 3 : AJOUT MANUEL
    # ===================================
    with tab3:
        st.subheader("➕ Ajouter une recette manuellement")

        # ============================================================
        # SECTION 1 : INGRÉDIENTS
        # ============================================================
        st.markdown("### 🥕 Ingrédients")

        if "manual_ingredients" not in st.session_state:
            st.session_state.manual_ingredients = []

        with st.expander("➕ Ajouter des ingrédients", expanded=True):
            col_ing1, col_ing2, col_ing3, col_ing4 = st.columns([2, 1, 1, 1])

            with col_ing1:
                ing_name = st.text_input("Ingrédient", key="ing_name")
            with col_ing2:
                ing_qty = st.number_input("Quantité", 0.0, 10000.0, 1.0, key="ing_qty")
            with col_ing3:
                ing_unit = st.text_input("Unité", key="ing_unit", placeholder="g, ml, etc.")
            with col_ing4:
                ing_optional = st.checkbox("Optionnel", key="ing_optional")

            if st.button("➕ Ajouter l'ingrédient", key="add_ingredient"):
                if ing_name:
                    st.session_state.manual_ingredients.append({
                        "name": ing_name,
                        "quantity": ing_qty,
                        "unit": ing_unit,
                        "optional": ing_optional
                    })
                    st.rerun()

        # Afficher les ingrédients ajoutés
        if st.session_state.manual_ingredients:
            st.markdown("**Ingrédients ajoutés :**")
            for idx, ing in enumerate(st.session_state.manual_ingredients):
                col_ing_d1, col_ing_d2, col_ing_d3 = st.columns([4, 1, 1])
                with col_ing_d1:
                    st.write(f"{ing['quantity']} {ing['unit']} de {ing['name']}")
                with col_ing_d2:
                    if ing['optional']:
                        st.caption("Optionnel")
                with col_ing_d3:
                    if st.button("❌", key=f"del_ing_{idx}"):
                        st.session_state.manual_ingredients.pop(idx)
                        st.rerun()

        st.markdown("---")

        # ============================================================
        # SECTION 2 : ÉTAPES
        # ============================================================
        st.markdown("### 📝 Étapes de préparation")

        if "manual_steps" not in st.session_state:
            st.session_state.manual_steps = []

        with st.expander("➕ Ajouter des étapes", expanded=True):
            col_step1, col_step2, col_step3 = st.columns([3, 1, 1])

            with col_step1:
                step_desc = st.text_area("Description de l'étape", key="step_desc", height=80)
            with col_step2:
                step_order = st.number_input("Ordre", 1, 20, len(st.session_state.manual_steps)+1, key="step_order")
            with col_step3:
                step_duration = st.number_input("Durée (min)", 0, 120, 0, key="step_duration")

            if st.button("➕ Ajouter l'étape", key="add_step"):
                if step_desc:
                    st.session_state.manual_steps.append({
                        "order": step_order,
                        "description": step_desc,
                        "duration": step_duration
                    })
                    st.rerun()

        # Afficher les étapes ajoutées
        if st.session_state.manual_steps:
            st.markdown("**Étapes ajoutées :**")
            for idx, step in enumerate(sorted(st.session_state.manual_steps, key=lambda x: x['order'])):
                col_step_d1, col_step_d2, col_step_d3 = st.columns([4, 1, 1])
                with col_step_d1:
                    st.write(f"{step['order']}. {step['description']}")
                with col_step_d2:
                    if step['duration']:
                        st.caption(f"{step['duration']}min")
                with col_step_d3:
                    if st.button("❌", key=f"del_step_{idx}"):
                        st.session_state.manual_steps = [s for i, s in enumerate(st.session_state.manual_steps) if i != idx]
                        st.rerun()

        st.markdown("---")

        # ============================================================
        # SECTION 3 : FORMULAIRE PRINCIPAL (INFOS DE BASE + VERSIONS)
        # ============================================================
        with st.form("manual_recipe"):
            # Infos de base
            st.markdown("### 📝 Informations de base")

            col_m1, col_m2 = st.columns(2)

            with col_m1:
                name = st.text_input("Nom de la recette *", placeholder="Ex: Pâtes à la carbonara")
                description = st.text_area(
                    "Description",
                    placeholder="Décris brièvement la recette...",
                    height=100
                )

            with col_m2:
                image_url = st.text_input(
                    "URL de l'image (optionnel)",
                    placeholder="https://..."
                )
                if image_url:
                    st.image(image_url, width=200)

            # Temps et portions
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)

            with col_t1:
                prep_time = st.number_input("Préparation (min)", 0, 300, 15, 5)
            with col_t2:
                cook_time = st.number_input("Cuisson (min)", 0, 300, 30, 5)
            with col_t3:
                servings = st.number_input("Portions", 1, 20, 4)
            with col_t4:
                difficulty = st.selectbox("Difficulté", ["easy", "medium", "hard"])

            # Catégories
            st.markdown("### 🏷️ Catégories et tags")

            col_c1, col_c2 = st.columns(2)

            with col_c1:
                meal_type = st.selectbox("Type de repas", ["breakfast", "lunch", "dinner", "snack"])
                season = st.selectbox("Saison", ["spring", "summer", "fall", "winter", "all_year"])
                category = st.text_input("Catégorie", placeholder="Végétarien, Italien, etc.")

            with col_c2:
                is_quick = st.checkbox("⚡ Rapide")
                is_balanced = st.checkbox("🥗 Équilibré")
                is_baby_friendly = st.checkbox("👶 Compatible bébé")
                is_batch_friendly = st.checkbox("🍳 Compatible batch")
                is_freezable = st.checkbox("❄️ Congélable")

            # Versions spéciales
            st.markdown("### 🔄 Versions spéciales (optionnel)")

            with st.expander("👶 Version bébé"):
                baby_instructions = st.text_area(
                    "Instructions spécifiques pour bébé",
                    placeholder="Ex: Mixer finement, éviter le sel...",
                    height=100,
                    key="baby_instructions"
                )
                baby_notes = st.text_input(
                    "Précautions pour bébé",
                    placeholder="Ex: Pas avant 12 mois, risque d'étouffement...",
                    key="baby_notes"
                )

            with st.expander("🍳 Version batch cooking"):
                batch_parallel = st.text_area(
                    "Étapes parallélisables (une par ligne)",
                    placeholder="Ex: Éplucher les légumes\nPréchauffer le four...",
                    height=100,
                    key="batch_parallel"
                )
                batch_time = st.number_input(
                    "Temps optimisé (min)",
                    0,
                    600,
                    0,
                    key="batch_time"
                )

            # Soumission
            st.markdown("---")
            submitted = st.form_submit_button("➕ Ajouter la recette", type="primary")

            if submitted:
                if not name:
                    st.error("Le nom de la recette est obligatoire")
                elif not st.session_state.manual_ingredients:
                    st.error("Ajoute au moins un ingrédient")
                elif not st.session_state.manual_steps:
                    st.error("Ajoute au moins une étape")
                else:
                    # Préparer les données de la recette
                    recipe_data = {
                        "name": name,
                        "description": description,
                        "prep_time": prep_time,
                        "cook_time": cook_time,
                        "servings": servings,
                        "difficulty": difficulty,
                        "meal_type": meal_type,
                        "season": season,
                        "category": category,
                        "is_quick": is_quick,
                        "is_balanced": is_balanced,
                        "is_baby_friendly": is_baby_friendly,
                        "is_batch_friendly": is_batch_friendly,
                        "is_freezable": is_freezable,
                        "ai_generated": False,
                        "image_url": image_url,
                        "ingredients": st.session_state.manual_ingredients,
                        "steps": st.session_state.manual_steps
                    }

                    # Préparer les versions
                    version_data = None
                    if baby_instructions or baby_notes:
                        version_data = {
                            RecipeVersionEnum.BABY: {
                                "modified_instructions": baby_instructions,
                                "baby_notes": baby_notes
                            }
                        }

                    if batch_parallel or batch_time:
                        if version_data is None:
                            version_data = {}
                        version_data[RecipeVersionEnum.BATCH_COOKING] = {
                            "parallel_steps": [s.strip() for s in batch_parallel.split('\n') if s.strip()],
                            "optimized_time": batch_time if batch_time > 0 else None
                        }

                    # Sauvegarder
                    recipe_id = save_recipe(recipe_data, version_data)

                    # Nettoyer le formulaire
                    del st.session_state.manual_ingredients
                    del st.session_state.manual_steps

                    st.success(f"✅ Recette '{name}' ajoutée avec succès !")
                    st.balloons()
                    st.rerun()
