"""
Module Recettes v2 - Refactorisé avec nouveaux composants
Remplace src/modules/cuisine/recettes.py
"""
import streamlit as st
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from src.core.state_manager import StateManager, get_state, navigate
from src.ui.components import (
    render_card, render_search_bar, render_filter_panel,
    render_stat_row, render_badge, render_tags, render_empty_state,
    render_pagination, render_confirmation_dialog, render_toast
)
from src.services.recette_service import recette_service
from src.services.ai_recette_service_v2 import ai_recette_service
from src.core.validators import RecetteInput, validate_model
from src.core.ai_cache import RateLimiter, render_cache_stats
from src.core.models import TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum


# ===================================
# HELPERS - AFFICHAGE
# ===================================

def render_recipe_card_modern(recette: Dict, key: str):
    """Carte recette moderne avec composants réutilisables"""

    # Construire métadonnées
    metadata = [
        f"⏱️ {recette['temps_total']}min",
        f"🍽️ {recette['portions']} pers.",
        f"{'😊' if recette['difficulte'] == 'facile' else '😐' if recette['difficulte'] == 'moyen' else '😰'} {recette['difficulte'].capitalize()}"
    ]

    # Tags
    tags = []
    if recette.get('est_rapide'):
        tags.append("⚡ Rapide")
    if recette.get('est_equilibre'):
        tags.append("🥗 Équilibré")
    if recette.get('compatible_bebe'):
        tags.append("👶 Bébé")
    if recette.get('compatible_batch'):
        tags.append("🍳 Batch")
    if recette.get('genere_par_ia'):
        tags.append(f"🤖 IA ({recette.get('score_ia', 0):.0f}%)")

    # Actions
    def view_details():
        StateManager.set_viewing_recipe(recette['id'])
        st.rerun()

    def delete_recipe():
        if f"confirm_delete_{recette['id']}" not in st.session_state:
            st.session_state[f"confirm_delete_{recette['id']}"] = True
        else:
            recette_service.delete(recette['id'])
            render_toast("Recette supprimée", "success")
            st.rerun()

    actions = [
        ("👁️ Détails", view_details),
        ("🗑️ Supprimer", delete_recipe)
    ]

    # Afficher la carte
    render_card(
        title=recette['nom'],
        content=recette.get('description', '')[:150] + "..." if len(recette.get('description', '')) > 150 else recette.get('description', ''),
        icon="🍽️",
        color="#4CAF50",
        actions=actions,
        footer=" • ".join(metadata),
        image_url=recette.get('url_image')
    )

    # Tags en dessous
    if tags:
        render_tags(tags)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)


def render_recipe_details_modern(recette_id: int):
    """Affiche les détails complets d'une recette"""

    # Charger avec eager loading
    recette = recette_service.get_by_id_full(recette_id)

    if not recette:
        st.error("Recette introuvable")
        return

    # Header
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"# 🍽️ {recette.nom}")
        if recette.description:
            st.caption(recette.description)

        # Tags
        tags = []
        if recette.est_rapide:
            tags.append("⚡ Rapide")
        if recette.est_equilibre:
            tags.append("🥗 Équilibré")
        if recette.compatible_bebe:
            tags.append("👶 Bébé")
        if recette.compatible_batch:
            tags.append("🍳 Batch")
        if recette.congelable:
            tags.append("❄️ Congélation")

        if tags:
            render_tags(tags)

    with col2:
        if recette.url_image:
            st.image(recette.url_image, use_container_width=True)

    # Stats
    stats = [
        {"label": "Préparation", "value": f"{recette.temps_preparation}min"},
        {"label": "Cuisson", "value": f"{recette.temps_cuisson}min"},
        {"label": "Portions", "value": str(recette.portions)},
        {"label": "Difficulté", "value": recette.difficulte.capitalize()}
    ]

    render_stat_row(stats, cols=4)

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Recette Standard", "👶 Version Bébé", "🍳 Version Batch"])

    with tab1:
        # Ingrédients
        st.markdown("### 🥕 Ingrédients")

        for ing_rec in sorted(recette.ingredients, key=lambda x: x.ingredient.nom):
            optional = " (optionnel)" if ing_rec.optionnel else ""
            st.write(f"• {ing_rec.quantite} {ing_rec.unite} de {ing_rec.ingredient.nom}{optional}")

        st.markdown("---")

        # Étapes
        st.markdown("### 📝 Étapes")

        for etape in sorted(recette.etapes, key=lambda x: x.ordre):
            duration = f" ({etape.duree}min)" if etape.duree else ""
            st.markdown(f"**{etape.ordre}.** {etape.description}{duration}")

    with tab2:
        version_bebe = next(
            (v for v in recette.versions if v.type_version == TypeVersionRecetteEnum.BEBE),
            None
        )

        if version_bebe:
            st.markdown("### 👶 Adaptation pour bébé")

            if version_bebe.instructions_modifiees:
                st.info(version_bebe.instructions_modifiees)

            if version_bebe.notes_bebe:
                st.warning(f"⚠️ **Précautions :** {version_bebe.notes_bebe}")
        else:
            render_empty_state(
                message="Aucune version bébé disponible",
                icon="👶",
                action_label="Générer avec l'IA",
                action_callback=lambda: st.info("Fonctionnalité à venir")
            )

    with tab3:
        version_batch = next(
            (v for v in recette.versions if v.type_version == TypeVersionRecetteEnum.BATCH_COOKING),
            None
        )

        if version_batch:
            st.markdown("### 🍳 Optimisation Batch Cooking")

            if version_batch.etapes_paralleles_batch:
                st.markdown("**Étapes parallélisables :**")
                for etape in version_batch.etapes_paralleles_batch:
                    st.write(f"• {etape}")

            if version_batch.temps_optimise_batch:
                temps_normal = recette.temps_preparation + recette.temps_cuisson
                st.metric(
                    "Temps optimisé",
                    f"{version_batch.temps_optimise_batch}min",
                    delta=f"-{temps_normal - version_batch.temps_optimise_batch}min"
                )
        else:
            render_empty_state(
                message="Aucune optimisation batch disponible",
                icon="🍳"
            )

    st.markdown("---")

    # Actions
    col_action1, col_action2, col_action3 = st.columns(3)

    with col_action1:
        if st.button("✏️ Modifier", use_container_width=True):
            StateManager.set_editing_recipe(recette_id)
            st.rerun()

    with col_action2:
        if st.button("🗑️ Supprimer", use_container_width=True, type="secondary"):
            result = render_confirmation_dialog(
                title="Confirmer la suppression",
                message=f"Supprimer définitivement '{recette.nom}' ?",
                key=f"delete_confirm_{recette_id}"
            )

            if result:
                recette_service.delete(recette_id)
                StateManager.set_viewing_recipe(None)
                render_toast("Recette supprimée", "success")
                st.rerun()

    with col_action3:
        if st.button("❌ Fermer", use_container_width=True):
            StateManager.set_viewing_recipe(None)
            st.rerun()


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Module Recettes v2 - Point d'entrée"""

    st.title("🍲 Recettes Intelligentes")
    st.caption("Génération IA, versions multiples, gestion complète")

    # Initialiser state
    state = get_state()

    # Vérifier si on affiche les détails d'une recette
    if state.viewing_recipe_id:
        render_recipe_details_modern(state.viewing_recipe_id)
        return

    # Stats cache IA (sidebar)
    with st.sidebar:
        render_cache_stats()

    # ===================================
    # TABS PRINCIPAUX
    # ===================================

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

        # Barre de recherche
        search = render_search_bar(
            placeholder="Rechercher une recette...",
            key="recipe_search"
        )

        # Filtres avancés
        filters_config = {
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes"] + [s.value for s in SaisonEnum],
                "default": 0
            },
            "type_repas": {
                "type": "select",
                "label": "Type de repas",
                "options": ["Tous"] + [t.value for t in TypeRepasEnum],
                "default": 0
            },
            "difficulte": {
                "type": "select",
                "label": "Difficulté",
                "options": ["Toutes", "facile", "moyen", "difficile"],
                "default": 0
            },
            "temps_max": {
                "type": "slider",
                "label": "Temps max (min)",
                "min": 0,
                "max": 180,
                "default": 180
            },
            "rapide": {
                "type": "checkbox",
                "label": "⚡ Rapides uniquement",
                "default": False
            },
            "equilibre": {
                "type": "checkbox",
                "label": "🥗 Équilibrées",
                "default": False
            },
            "bebe": {
                "type": "checkbox",
                "label": "👶 Compatible bébé",
                "default": False
            },
            "batch": {
                "type": "checkbox",
                "label": "🍳 Compatible batch",
                "default": False
            },
            "ia": {
                "type": "checkbox",
                "label": "🤖 Générées par IA",
                "default": False
            }
        }

        filters = render_filter_panel(filters_config, key_prefix="recipe")

        st.markdown("---")

        # Charger recettes avec filtres
        recettes = recette_service.search_advanced(
            search_term=search if search else None,
            saison=filters["saison"] if filters["saison"] != "Toutes" else None,
            type_repas=filters["type_repas"] if filters["type_repas"] != "Tous" else None,
            difficulte=filters["difficulte"] if filters["difficulte"] != "Toutes" else None,
            temps_max=filters["temps_max"] if filters["temps_max"] < 180 else None,
            is_rapide=filters["rapide"] if filters["rapide"] else None,
            is_equilibre=filters["equilibre"] if filters["equilibre"] else None,
            compatible_bebe=filters["bebe"] if filters["bebe"] else None,
            compatible_batch=filters["batch"] if filters["batch"] else None,
            ia_only=filters["ia"] if filters["ia"] else None,
            limit=100
        )

        if not recettes:
            render_empty_state(
                message="Aucune recette trouvée",
                icon="🔍",
                action_label="➕ Ajouter une recette",
                action_callback=lambda: st.session_state.update({"active_tab": 2})
            )
        else:
            # Stats rapides
            stats = recette_service.get_stats()

            stats_data = [
                {"label": "Total", "value": len(recettes)},
                {"label": "Rapides", "value": sum(1 for r in recettes if r.est_rapide)},
                {"label": "IA", "value": sum(1 for r in recettes if r.genere_par_ia)},
                {"label": "Temps moyen", "value": f"{int(stats['temps_moyen'])}min"}
            ]

            render_stat_row(stats_data, cols=4)

            st.markdown("---")

            # Pagination
            page, per_page = render_pagination(
                total_items=len(recettes),
                items_per_page=20,
                key="recipes_pagination"
            )

            # Afficher recettes paginées
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            for recette in recettes[start_idx:end_idx]:
                recette_dict = {
                    "id": recette.id,
                    "nom": recette.nom,
                    "description": recette.description,
                    "temps_total": recette.temps_preparation + recette.temps_cuisson,
                    "portions": recette.portions,
                    "difficulte": recette.difficulte,
                    "est_rapide": recette.est_rapide,
                    "est_equilibre": recette.est_equilibre,
                    "compatible_bebe": recette.compatible_bebe,
                    "compatible_batch": recette.compatible_batch,
                    "genere_par_ia": recette.genere_par_ia,
                    "score_ia": recette.score_ia,
                    "url_image": recette.url_image
                }

                render_recipe_card_modern(recette_dict, f"recipe_{recette.id}")

    # ===================================
    # TAB 2 : GÉNÉRATION IA
    # ===================================

    with tab2:
        st.subheader("✨ Générer des recettes avec l'IA")

        # Vérifier rate limit
        can_call, error_msg = RateLimiter.can_call()

        if not can_call:
            st.warning(error_msg)
            usage = RateLimiter.get_usage()
            st.caption(f"Utilisation: {usage['calls_today']}/{usage['limit_daily']} aujourd'hui")
            return

        st.info("💡 L'IA Mistral génère des recettes selon tes critères")

        with st.form("ai_generation"):
            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.markdown("**Critères de base**")
                count = st.slider("Nombre de recettes", 1, 5, 3)
                saison = st.selectbox("Saison", [s.value for s in SaisonEnum])
                type_repas = st.selectbox("Type de repas", [t.value for t in TypeRepasEnum])

            with col_g2:
                st.markdown("**Filtres**")
                is_quick = st.checkbox("⚡ Rapide (<30min)")
                is_balanced = st.checkbox("🥗 Équilibré", value=True)
                is_baby_friendly = st.checkbox("👶 Compatible bébé")
                is_batch_friendly = st.checkbox("🍳 Compatible batch cooking")

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

            submitted = st.form_submit_button(
                "✨ Générer les recettes",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if not gen_standard and not gen_baby and not gen_batch:
                st.error("Sélectionne au moins une version à générer")
            else:
                with st.spinner("🤖 L'IA génère les recettes..."):
                    try:
                        # Préparer filtres
                        filters_ai = {
                            "saison": saison,
                            "type_repas": type_repas,
                            "is_quick": is_quick,
                            "is_balanced": is_balanced,
                            "ingredients": [i.strip() for i in ingredients_input.split(",")] if ingredients_input else None
                        }

                        # Générer
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        recipes = loop.run_until_complete(
                            ai_recette_service.generate_recipes(
                                count=count,
                                filters=filters_ai,
                                version_type=TypeVersionRecetteEnum.STANDARD.value
                            )
                        )

                        # Ajouter images
                        for recipe in recipes:
                            recipe["url_image"] = ai_recette_service.generate_image_url(
                                recipe["nom"],
                                recipe["description"]
                            )

                        # Sauvegarder dans state
                        StateManager.save_generated_recipes(recipes)

                        render_toast(f"✅ {len(recipes)} recette(s) générée(s) !", "success")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")

        # Afficher recettes générées
        if state.generated_recipes:
            st.markdown("---")
            st.markdown("### 📋 Recettes Générées")

            selected_recipes = []

            for idx, recipe in enumerate(state.generated_recipes):
                with st.expander(f"🍽️ {recipe['nom']}", expanded=True):
                    col_r1, col_r2 = st.columns([1, 2])

                    with col_r1:
                        if recipe.get("url_image"):
                            st.image(recipe["url_image"], use_container_width=True)

                    with col_r2:
                        st.write(f"**{recipe['description']}**")

                        metadata = [
                            f"⏱️ {recipe['temps_preparation'] + recipe['temps_cuisson']}min",
                            f"🍽️ {recipe['portions']} portions",
                            f"{'😊' if recipe['difficulte'] == 'facile' else '😐'} {recipe['difficulte'].capitalize()}"
                        ]

                        st.caption(" • ".join(metadata))

                    st.markdown("**Ingrédients :**")
                    for ing in recipe["ingredients"]:
                        st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}")

                    st.markdown("**Étapes :**")
                    for step in recipe["etapes"]:
                        st.write(f"{step['ordre']}. {step['description']}")

                    if st.checkbox(f"✅ Sélectionner cette recette", key=f"select_{idx}"):
                        selected_recipes.append(recipe)

            if selected_recipes:
                if st.button(
                        f"➕ Ajouter {len(selected_recipes)} recette(s) sélectionnée(s)",
                        type="primary",
                        use_container_width=True
                ):
                    for recipe in selected_recipes:
                        # Extraire données pour service
                        recette_data = {
                            k: v for k, v in recipe.items()
                            if k not in ['ingredients', 'etapes', 'versions']
                        }

                        recette_data['genere_par_ia'] = True
                        recette_data['score_ia'] = 95.0  # Score par défaut

                        # Créer via service
                        recette_service.create_full(
                            recette_data=recette_data,
                            ingredients_data=recipe['ingredients'],
                            etapes_data=recipe['etapes'],
                            versions_data=recipe.get('versions')
                        )

                    StateManager.clear_generated_recipes()
                    render_toast(f"✅ {len(selected_recipes)} recette(s) ajoutée(s) !", "success")
                    st.balloons()
                    st.rerun()

    # ===================================
    # TAB 3 : AJOUT MANUEL
    # ===================================

    with tab3:
        st.subheader("➕ Ajouter une recette manuellement")

        # État pour ingrédients et étapes
        if "manual_ingredients" not in st.session_state:
            st.session_state.manual_ingredients = []
        if "manual_steps" not in st.session_state:
            st.session_state.manual_steps = []

        # Section ingrédients
        with st.expander("➕ Ajouter des ingrédients", expanded=True):
            col_ing1, col_ing2, col_ing3, col_ing4 = st.columns([2, 1, 1, 1])

            with col_ing1:
                ing_nom = st.text_input("Ingrédient", key="ing_nom", placeholder="Ex: Tomates")
            with col_ing2:
                ing_qty = st.number_input("Quantité", 0.0, 10000.0, 1.0, key="ing_qty")
            with col_ing3:
                ing_unit = st.text_input("Unité", key="ing_unit", placeholder="g, ml, etc.")
            with col_ing4:
                ing_opt = st.checkbox("Optionnel", key="ing_opt")

            if st.button("➕ Ajouter ingrédient"):
                if ing_nom:
                    st.session_state.manual_ingredients.append({
                        "nom": ing_nom,
                        "quantite": ing_qty,
                        "unite": ing_unit,
                        "optionnel": ing_opt
                    })
                    st.rerun()

        # Liste ingrédients
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

        # Section étapes
        with st.expander("➕ Ajouter des étapes", expanded=True):
            step_desc = st.text_area("Description", key="step_desc", height=80)

            if st.button("➕ Ajouter étape"):
                if step_desc:
                    st.session_state.manual_steps.append({
                        "ordre": len(st.session_state.manual_steps) + 1,
                        "description": step_desc,
                        "duree": None
                    })
                    st.rerun()

        # Liste étapes
        if st.session_state.manual_steps:
            st.markdown("**Étapes ajoutées :**")
            for idx, etape in enumerate(st.session_state.manual_steps):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{etape['ordre']}. {etape['description']}")
                with col2:
                    if st.button("❌", key=f"del_step_{idx}"):
                        st.session_state.manual_steps.pop(idx)
                        # Réordonner
                        for i, s in enumerate(st.session_state.manual_steps):
                            s['ordre'] = i + 1
                        st.rerun()

        # Formulaire principal
        st.markdown("---")

        with st.form("manual_recipe"):
            st.markdown("### 📝 Informations de la recette")

            col_m1, col_m2 = st.columns(2)

            with col_m1:
                nom = st.text_input("Nom *", placeholder="Ex: Gratin dauphinois")
                description = st.text_area("Description", height=100)
                temps_prep = st.number_input("Préparation (min)", 0, 300, 15, 5)
                temps_cuisson = st.number_input("Cuisson (min)", 0, 300, 30, 5)

            with col_m2:
                portions = st.number_input("Portions", 1, 20, 4)
                difficulte = st.selectbox("Difficulté", ["facile", "moyen", "difficile"])
                type_repas = st.selectbox("Type repas", [t.value for t in TypeRepasEnum])
                saison = st.selectbox("Saison", [s.value for s in SaisonEnum])

            submitted = st.form_submit_button("➕ Ajouter recette", type="primary")

            if submitted:
                # Validation
                if not nom:
                    st.error("Le nom est obligatoire")
                elif not st.session_state.manual_ingredients:
                    st.error("Ajoute au moins un ingrédient")
                elif not st.session_state.manual_steps:
                    st.error("Ajoute au moins une étape")
                else:
                    # Créer recette
                    recette_data = {
                        "nom": nom,
                        "description": description,
                        "temps_preparation": temps_prep,
                        "temps_cuisson": temps_cuisson,
                        "portions": portions,
                        "difficulte": difficulte,
                        "type_repas": type_repas,
                        "saison": saison,
                        "est_rapide": (temps_prep + temps_cuisson) < 30,
                        "est_equilibre": True,
                        "genere_par_ia": False
                    }

                    recette_id = recette_service.create_full(
                        recette_data=recette_data,
                        ingredients_data=st.session_state.manual_ingredients,
                        etapes_data=st.session_state.manual_steps
                    )

                    # Reset
                    del st.session_state.manual_ingredients
                    del st.session_state.manual_steps

                    render_toast(f"✅ Recette '{nom}' ajoutée !", "success")
                    st.balloons()
                    st.rerun()