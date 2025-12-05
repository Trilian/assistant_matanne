"""
Module Recettes - Compatible avec models.py en français
Architecture moderne avec génération IA, versions multiples, images
"""
import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, date
from typing import List, Dict, Optional
from src.core.database import get_db_context
from src.core.models import (
    Recette, RecetteIngredient, EtapeRecette, VersionRecette,
    Ingredient, TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum
)
from src.services.ai_recette_service import ai_recette_service

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
            if filters.get("is_quick"):
                query = query.filter(Recette.est_rapide == True)
            if filters.get("is_balanced"):
                query = query.filter(Recette.est_equilibre == True)
            if filters.get("is_baby_friendly"):
                query = query.filter(Recette.compatible_bebe == True)
            if filters.get("search"):
                query = query.filter(Recette.nom.ilike(f"%{filters['search']}%"))
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

def load_recipe_details(recette_id: int) -> Dict:
    """Charge les détails complets d'une recette"""
    with get_db_context() as db:
        recette = db.query(Recette).get(recette_id)
        if not recette:
            return None
        return {
            "recette": recette,
            "ingredients": [
                {
                    "nom": ing.ingredient.nom,
                    "quantite": ing.quantite,
                    "unite": ing.unite,
                    "optionnel": ing.optionnel
                }
                for ing in recette.ingredients
            ],
            "etapes": [
                {
                    "ordre": etape.ordre,
                    "description": etape.description,
                    "duree": etape.duree
                }
                for etape in sorted(recette.etapes, key=lambda x: x.ordre)
            ],
            "versions": [
                {
                    "type": v.type_version,
                    "instructions": v.instructions_modifiees,
                    "notes_bebe": v.notes_bebe,
                    "info_batch": {
                        "etapes_paralleles": v.etapes_paralleles_batch,
                        "temps_optimise": v.temps_optimise_batch
                    } if v.type_version == TypeVersionRecetteEnum.BATCH_COOKING else None
                }
                for v in recette.versions
            ]
        }

def save_recipe(recipe_data: Dict, version_data: Optional[Dict] = None) -> int:
    """Sauvegarde une recette avec ses ingrédients, étapes et versions"""
    with get_db_context() as db:
        recette = Recette(
            nom=recipe_data["nom"],
            description=recipe_data.get("description"),
            temps_preparation=recipe_data["temps_preparation"],
            temps_cuisson=recipe_data["temps_cuisson"],
            portions=recipe_data["portions"],
            difficulte=recipe_data.get("difficulte", "moyen"),
            type_repas=recipe_data.get("type_repas", TypeRepasEnum.DINER),
            saison=recipe_data.get("saison", SaisonEnum.TOUTE_ANNEE),
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

def delete_recipe(recette_id: int):
    """Supprime une recette"""
    with get_db_context() as db:
        db.query(Recette).filter(Recette.id == recette_id).delete()
        db.commit()

# ===================================
# UI COMPONENTS
# ===================================
def render_recipe_card(recette: pd.Series):
    """Affiche une carte recette moderne"""
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            if recette["url_image"]:
                st.image(recette["url_image"], use_container_width=True)
            else:
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                height: 150px; border-radius: 8px; display: flex;
                                align-items: center; justify-content: center; color: white;">
                        <span style="font-size: 3rem;">🍽️</span>
                    </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"### {recette['nom']}")
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
            if recette["description"]:
                desc = recette["description"]
                st.write(desc[:150] + "..." if len(desc) > 150 else desc)
            col_info1, col_info2, col_info3, col_info4 = st.columns(4)
            with col_info1:
                st.caption(f"⏱️ {recette['temps_total']}min")
            with col_info2:
                st.caption(f"🍽️ {recette['portions']} pers.")
            with col_info3:
                difficulty_emoji = {"facile": "😊", "moyen": "😐", "difficile": "😰"}
                st.caption(f"{difficulty_emoji.get(recette['difficulte'], '😐')} {recette['difficulte'].capitalize()}")
            with col_info4:
                saison = recette['saison'].replace('_', ' ') if recette['saison'] else "—"
                st.caption(f"📅 {saison.capitalize()}")

def render_recipe_details(recette_id: int):
    """Affiche les détails complets d'une recette"""
    details = load_recipe_details(recette_id)
    if not details:
        st.error("Recette introuvable")
        return
    recette = details["recette"]
    col_h1, col_h2 = st.columns([2, 1])
    with col_h1:
        st.markdown(f"# {recette.nom}")
        st.caption(recette.description or "")
    with col_h2:
        if recette.url_image:
            st.image(recette.url_image, use_container_width=True)
    tab1, tab2, tab3 = st.tabs(["📋 Recette", "👶 Version Bébé", "🍳 Version Batch"])
    with tab1:
        st.markdown("### 🥕 Ingrédients")
        for ing in details["ingredients"]:
            optional = " (optionnel)" if ing["optionnel"] else ""
            st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}{optional}")
        st.markdown("---")
        st.markdown("### 📝 Étapes")
        for etape in details["etapes"]:
            duration = f" ({etape['duree']}min)" if etape["duree"] else ""
            st.markdown(f"**{etape['ordre']}.** {etape['description']}{duration}")
    with tab2:
        version_bebe = next(
            (v for v in details["versions"] if v["type"] == TypeVersionRecetteEnum.BEBE),
            None
        )
        if version_bebe:
            st.markdown("### 👶 Adaptation pour bébé")
            st.info(version_bebe["instructions"] or "Pas d'instructions spécifiques")
            if version_bebe["notes_bebe"]:
                st.warning(f"⚠️ **Précautions :** {version_bebe['notes_bebe']}")
        else:
            st.info("Aucune version bébé disponible pour cette recette")
    with tab3:
        version_batch = next(
            (v for v in details["versions"] if v["type"] == TypeVersionRecetteEnum.BATCH_COOKING),
            None
        )
        if version_batch and version_batch["info_batch"]:
            info = version_batch["info_batch"]
            st.markdown("### 🍳 Optimisation Batch Cooking")
            if info.get("etapes_paralleles"):
                st.markdown("**Étapes parallélisables :**")
                for etape in info["etapes_paralleles"]:
                    st.write(f"• {etape}")
            if info.get("temps_optimise"):
                temps_normal = recette.temps_preparation + recette.temps_cuisson
                st.metric(
                    "Temps optimisé",
                    f"{info['temps_optimise']}min",
                    delta=f"-{temps_normal - info['temps_optimise']}min"
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

    # Initialise l'onglet actif si ce n'est pas déjà fait
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📚 Mes Recettes"  # Onglet par défaut

    tab1, tab2, tab3 = st.tabs(["📚 Mes Recettes", "✨ Générer avec l'IA", "➕ Ajouter Manuellement"])
    if st.session_state.active_tab == "📚 Mes Recettes":
        with tab1:
            st.subheader("Ma collection de recettes")
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                search = st.text_input("🔍 Rechercher", placeholder="Nom de recette...")
            with col_f2:
                saison_filter = st.selectbox(
                    "Saison",
                    ["Toutes"] + [s.value for s in SaisonEnum]
                )
            with col_f3:
                repas_filter = st.selectbox(
                    "Type de repas",
                    ["Tous"] + [m.value for m in TypeRepasEnum]
                )
            with col_f4:
                quick_only = st.checkbox("⚡ Rapides uniquement")
            with st.expander("🔧 Filtres avancés"):
                col_fa1, col_fa2 = st.columns(2)
                with col_fa1:
                    balanced_only = st.checkbox("🥗 Équilibrées")
                    baby_friendly_only = st.checkbox("👶 Compatible bébé")
                with col_fa2:
                    batch_friendly_only = st.checkbox("🍳 Compatible batch")
                    ai_only = st.checkbox("🤖 Générées par IA")
            filters = {}
            if search:
                filters["search"] = search
            if saison_filter != "Toutes":
                filters["saison"] = saison_filter
            if repas_filter != "Tous":
                filters["type_repas"] = repas_filter
            if quick_only:
                filters["is_quick"] = True
            if balanced_only:
                filters["is_balanced"] = True
            if baby_friendly_only:
                filters["is_baby_friendly"] = True
            df = load_recipes(filters)
            if df.empty:
                st.info("Aucune recette trouvée. Génère-en avec l'IA ou ajoute-en manuellement !")
            else:
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1:
                    st.metric("Total", len(df))
                with col_s2:
                    quick_count = len(df[df["est_rapide"] == True])
                    st.metric("Rapides", quick_count)
                with col_s3:
                    ai_count = len(df[df["genere_par_ia"] == True])
                    st.metric("Générées IA", ai_count)
                with col_s4:
                    avg_time = df["temps_total"].mean()
                    st.metric("Temps moyen", f"{avg_time:.0f}min")
                st.markdown("---")
                for idx, recette in df.iterrows():
                    render_recipe_card(recette)
                    col_a1, col_a2 = st.columns([1, 4])
                    with col_a1:
                        if st.button("👁️ Détails", key=f"view_{recette['id']}", use_container_width=True):
                            st.session_state[f"viewing_{recette['id']}"] = True
                            st.rerun()
                    with col_a2:
                        if st.button("🗑️ Supprimer", key=f"del_{recette['id']}", use_container_width=True):
                            delete_recipe(recette['id'])
                            st.success("Recette supprimée")
                            st.rerun()
                    if st.session_state.get(f"viewing_{recette['id']}", False):
                        with st.expander("Détails complets", expanded=True):
                            render_recipe_details(recette['id'])
                            if st.button("Fermer", key=f"close_{recette['id']}"):
                                del st.session_state[f"viewing_{recette['id']}"]
                                st.rerun()
                    st.markdown("---")
    elif st.session_state.active_tab == "✨ Générer avec l'IA":
        with tab2:
            st.subheader("✨ Générer des recettes avec l'IA")
            st.info("💡 L'IA génère des recettes selon tes critères")
            with st.form("ai_generation"):
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("**Critères de base**")
                    count = st.slider("Nombre de recettes", 1, 5, 3)
                    saison = st.selectbox("Saison", [s.value for s in SaisonEnum])
                    type_repas = st.selectbox("Type de repas", [m.value for m in TypeRepasEnum])
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
                            filters = {
                                "saison": saison,
                                "type_repas": type_repas,
                                "is_quick": is_quick,
                                "is_balanced": is_balanced,
                                "ingredients": [i.strip() for i in ingredients_input.split(",")] if ingredients_input else None
                            }
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            recipes = loop.run_until_complete(
                                ai_recette_service.generate_recipes(
                                    count=count,
                                    filters=filters,
                                    version_type=TypeVersionRecetteEnum.STANDARD.value
                                )
                            )
                            if gen_baby or gen_batch:
                                for recipe in recipes:
                                    versions = {}
                                    if gen_baby:
                                        baby_recipes = loop.run_until_complete(
                                            ai_recette_service.generate_recipes(
                                                count=1,
                                                filters={"nom": recipe["nom"]},
                                                version_type=TypeVersionRecetteEnum.BEBE.value
                                            )
                                        )
                                        if baby_recipes:
                                            versions[TypeVersionRecetteEnum.BEBE] = baby_recipes[0].get("version_bebe", {})
                                    if gen_batch:
                                        batch_recipes = loop.run_until_complete(
                                            ai_recette_service.generate_recipes(
                                                count=1,
                                                filters={"nom": recipe["nom"]},
                                                version_type=TypeVersionRecetteEnum.BATCH_COOKING.value
                                            )
                                        )
                                        if batch_recipes:
                                            versions[TypeVersionRecetteEnum.BATCH_COOKING] = batch_recipes[0].get("version_batch", {})
                                    recipe["versions"] = versions
                            for recipe in recipes:
                                recipe["url_image"] =  ai_recette_service.generate_image_url(
                                    recipe["nom"],
                                    recipe["description"]
                                )

                            st.session_state["generated_recipes"] = recipes
                            st.success(f"✅ {len(recipes)} recette(s) générée(s) !")
                        except Exception as e:
                            st.error(f"❌ Erreur : {str(e)}")
            if "generated_recipes" in st.session_state:
                st.markdown("---")
                st.markdown("### 📋 Recettes générées")
                recipes = st.session_state["generated_recipes"]
                selected_recipes = []
                for idx, recipe in enumerate(recipes):
                    with st.expander(f"🍽️ {recipe['nom']}", expanded=True):
                        col_r1, col_r2 = st.columns([1, 2])
                        with col_r1:
                            if recipe.get("url_image"):
                                st.image(recipe["url_image"], use_container_width=True)
                        with col_r2:
                            st.write(f"**{recipe['description']}**")
                            col_info1, col_info2, col_info3 = st.columns(3)
                            with col_info1:
                                st.caption(f"⏱️ {recipe['temps_preparation'] + recipe['temps_cuisson']}min")
                            with col_info2:
                                st.caption(f"🍽️ {recipe['portions']} portions")
                            with col_info3:
                                st.caption(f"😊 {recipe['difficulte'].capitalize()}")
                        st.markdown("**Ingrédients :**")
                        for ing in recipe["ingredients"]:
                            st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}")
                        st.markdown("**Étapes :**")
                        for step in recipe["etapes"]:
                            st.write(f"{step['ordre']}. {step['description']}")
                        if recipe.get("versions"):
                            st.markdown("**Versions disponibles :**")
                            versions_str = []
                            if TypeVersionRecetteEnum.BEBE in recipe["versions"]:
                                versions_str.append("👶 Bébé")
                            if TypeVersionRecetteEnum.BATCH_COOKING in recipe["versions"]:
                                versions_str.append("🍳 Batch")
                            st.caption(" • ".join(versions_str))
                        if st.checkbox(f"Sélectionner cette recette", key=f"select_{idx}"):
                            selected_recipes.append(recipe)
                if selected_recipes:
                    if st.button(f"➕ Ajouter {len(selected_recipes)} recette(s) sélectionnée(s)", type="primary"):
                        for recipe in selected_recipes:
                            version_data = None
                            if recipe.get("versions"):
                                version_data = {}
                                if TypeVersionRecetteEnum.BEBE in recipe["versions"]:
                                    version_data[TypeVersionRecetteEnum.BEBE] = recipe["versions"][TypeVersionRecetteEnum.BEBE]
                                if TypeVersionRecetteEnum.BATCH_COOKING in recipe["versions"]:
                                    version_data[TypeVersionRecetteEnum.BATCH_COOKING] = recipe["versions"][TypeVersionRecetteEnum.BATCH_COOKING]
                            save_recipe(recipe, version_data)
                        st.success(f"✅ {len(selected_recipes)} recette(s) ajoutée(s) !")
                        del st.session_state["generated_recipes"]
                        st.balloons()
                        st.rerun()
    elif st.session_state.active_tab == "➕ Ajouter Manuellement":
        with tab3:
            st.subheader("➕ Ajouter une recette manuellement")
            if "manual_ingredients" not in st.session_state:
                st.session_state.manual_ingredients = []
            if "manual_steps" not in st.session_state:
                st.session_state.manual_steps = []
            with st.expander("➕ Ajouter des ingrédients", expanded=True):
                col_ing1, col_ing2, col_ing3, col_ing4 = st.columns([2, 1, 1, 1])
                with col_ing1:
                    ing_nom = st.text_input("Ingrédient", key="ing_nom")
                with col_ing2:
                    ing_qty = st.number_input("Quantité", 0.0, 10000.0, 1.0, key="ing_qty")
                with col_ing3:
                    ing_unit = st.text_input("Unité", key="ing_unit", placeholder="g, ml, etc.")
                with col_ing4:
                    ing_opt = st.checkbox("Optionnel", key="ing_opt")
                if st.button("➕ Ajouter ingrédient", key="add_ing"):
                    if ing_nom:
                        st.session_state.manual_ingredients.append({
                            "nom": ing_nom,
                            "quantite": ing_qty,
                            "unite": ing_unit,
                            "optionnel": ing_opt
                        })
                        st.rerun()
            if st.session_state.manual_ingredients:
                st.markdown("**Ingrédients ajoutés :**")
                for idx, ing in enumerate(st.session_state.manual_ingredients):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{ing['quantite']} {ing['unite']} de {ing['nom']}")
                    with col2:
                        if st.button("❌", key=f"del_ing_{idx}"):
                            st.session_state.manual_ingredients.pop(idx)
                            st.rerun()
            with st.expander("➕ Ajouter des étapes", expanded=True):
                col_step1, col_step2 = st.columns([3, 1])
                with col_step1:
                    step_desc = st.text_area("Description", key="step_desc", height=80)
                with col_step2:
                    step_ordre = st.number_input("Ordre", 1, 20, len(st.session_state.manual_steps)+1, key="step_ordre")
                if st.button("➕ Ajouter étape", key="add_step"):
                    if step_desc:
                        st.session_state.manual_steps.append({
                            "ordre": step_ordre,
                            "description": step_desc,
                            "duree": None
                        })
                        st.rerun()
            if st.session_state.manual_steps:
                st.markdown("**Étapes ajoutées :**")
                for idx, etape in enumerate(sorted(st.session_state.manual_steps, key=lambda x: x['ordre'])):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{etape['ordre']}. {etape['description']}")
                    with col2:
                        if st.button("❌", key=f"del_step_{idx}"):
                            st.session_state.manual_steps = [s for i, s in enumerate(st.session_state.manual_steps) if i != idx]
                            st.rerun()
            with st.form("manual_recipe"):
                st.markdown("### 📝 Informations")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    nom = st.text_input("Nom *", placeholder="Ex: Pâtes carbonara")
                    description = st.text_area("Description", height=100)
                with col_m2:
                    temps_prep = st.number_input("Préparation (min)", 0, 300, 15, 5)
                    temps_cuisson = st.number_input("Cuisson (min)", 0, 300, 30, 5)
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    portions = st.number_input("Portions", 1, 20, 4)
                with col_t2:
                    difficulte = st.selectbox("Difficulté", ["facile", "moyen", "difficile"])
                with col_t3:
                    type_repas = st.selectbox("Type repas", [t.value for t in TypeRepasEnum])
                submitted = st.form_submit_button("➕ Ajouter recette", type="primary")
                if submitted:
                    if not nom:
                        st.error("Le nom est obligatoire")
                    elif not st.session_state.manual_ingredients:
                        st.error("Ajoute au moins un ingrédient")
                    elif not st.session_state.manual_steps:
                        st.error("Ajoute au moins une étape")
                    else:
                        recipe_data = {
                            "nom": nom,
                            "description": description,
                            "temps_preparation": temps_prep,
                            "temps_cuisson": temps_cuisson,
                            "portions": portions,
                            "difficulte": difficulte,
                            "type_repas": type_repas,
                            "saison": SaisonEnum.TOUTE_ANNEE,
                            "est_rapide": (temps_prep + temps_cuisson) < 30,
                            "est_equilibre": True,
                            "compatible_bebe": False,
                            "compatible_batch": False,
                            "congelable": False,
                            "genere_par_ia": False,
                            "ingredients": st.session_state.manual_ingredients,
                            "etapes": st.session_state.manual_steps
                        }
                        recette_id = save_recipe(recipe_data)
                        del st.session_state.manual_ingredients
                        del st.session_state.manual_steps
                        st.success(f"✅ Recette '{nom}' ajoutée !")
                        st.balloons()
                        st.rerun()
