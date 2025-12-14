# src/modules/cuisine/recettes.py - PARTIE 1/2
"""
Module Recettes v3 - COMPLET
Toutes fonctionnalités intégrées : CRUD, IA, Import/Export, Édition, Versions
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
from src.ui.recette_components import (
    render_display_mode_toggle, render_recipe_card_grid,
    render_ingredients_form, render_etapes_form, render_recipe_preview
)
from src.services.recette_service import recette_service
from src.services.recette_edition_service import recette_edition_service
from src.services.recette_version_service import create_recette_version_service
from src.services.ai_recette_service import ai_recette_service
from src.services.import_export import RecetteExporter, RecetteImporter, render_export_ui, render_import_ui
from src.core.validators import RecetteInput, validate_model
from src.core.ai_cache import RateLimiter, render_cache_stats
from src.core.models import TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum


# ===================================
# HELPERS - AFFICHAGE
# ===================================

def render_recipe_card_modern(recette: Dict, key: str):
    """Carte recette moderne avec composants réutilisables"""

    metadata = [
        f"⏱️ {recette['temps_total']}min",
        f"🍽️ {recette['portions']} pers.",
        f"{'😊' if recette['difficulte'] == 'facile' else '😐' if recette['difficulte'] == 'moyen' else '😰'} {recette['difficulte'].capitalize()}"
    ]

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

    def view_details():
        StateManager.set_viewing_recipe(recette['id'])
        st.rerun()

    def edit_recipe():
        StateManager.set_editing_recipe(recette['id'])
        st.rerun()

    def duplicate_recipe():
        new_id = recette_edition_service.duplicate_recette(
            recette['id'],
            nouveau_nom=f"{recette['nom']} (copie)"
        )
        if new_id:
            render_toast(f"✅ Recette dupliquée", "success")
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
        ("✏️ Éditer", edit_recipe),
        ("📋 Dupliquer", duplicate_recipe),
        ("🗑️ Supprimer", delete_recipe)
    ]

    render_card(
        title=recette['nom'],
        content=recette.get('description', '')[:150] + "..." if len(recette.get('description', '')) > 150 else recette.get('description', ''),
        icon="🍽️",
        color="#4CAF50",
        actions=actions,
        footer=" • ".join(metadata),
        image_url=recette.get('url_image')
    )

    if tags:
        render_tags(tags)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)


def render_recipe_details_modern(recette_id: int):
    """Affiche les détails complets d'une recette"""

    recette = recette_service.get_by_id_full(recette_id)

    if not recette:
        st.error("Recette introuvable")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"# 🍽️ {recette.nom}")
        if recette.description:
            st.caption(recette.description)

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

    stats = [
        {"label": "Préparation", "value": f"{recette.temps_preparation}min"},
        {"label": "Cuisson", "value": f"{recette.temps_cuisson}min"},
        {"label": "Portions", "value": str(recette.portions)},
        {"label": "Difficulté", "value": recette.difficulte.capitalize()}
    ]

    render_stat_row(stats, cols=4)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Recette Standard",
        "👶 Version Bébé",
        "🍳 Version Batch",
        "🤖 Générer Versions IA"
    ])

    with tab1:
        st.markdown("### 🥕 Ingrédients")

        for ing_rec in sorted(recette.ingredients, key=lambda x: x.ingredient.nom):
            optional = " (optionnel)" if ing_rec.optionnel else ""
            st.write(f"• {ing_rec.quantite} {ing_rec.unite} de {ing_rec.ingredient.nom}{optional}")

        st.markdown("---")

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
                action_label="Générer avec l'IA →",
                action_callback=lambda: st.session_state.update({"active_version_tab": 3})
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
                icon="🍳",
                action_label="Générer avec l'IA →",
                action_callback=lambda: st.session_state.update({"active_version_tab": 3})
            )

    with tab4:
        render_generate_versions_ui(recette.id)

    st.markdown("---")

    col_action1, col_action2, col_action3, col_action4 = st.columns(4)

    with col_action1:
        if st.button("✏️ Modifier", use_container_width=True):
            StateManager.set_editing_recipe(recette_id)
            StateManager.set_viewing_recipe(None)
            st.rerun()

    with col_action2:
        if st.button("📋 Dupliquer", use_container_width=True):
            new_id = recette_edition_service.duplicate_recette(
                recette_id,
                nouveau_nom=f"{recette.nom} (copie)"
            )
            if new_id:
                render_toast("✅ Recette dupliquée", "success")
                st.balloons()
                st.rerun()

    with col_action3:
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

    with col_action4:
        if st.button("❌ Fermer", use_container_width=True):
            StateManager.set_viewing_recipe(None)
            st.rerun()


def render_generate_versions_ui(recette_id: int):
    """UI pour générer les versions IA"""
    st.markdown("### 🤖 Générer les versions automatiquement")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    version_service = create_recette_version_service(agent)

    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("#### 👶 Version Bébé")
        st.caption("Adapte la recette pour les 6-18 mois")

        if st.button("✨ Générer Version Bébé", use_container_width=True, type="primary", key="gen_bebe"):
            with st.spinner("🤖 L'IA adapte pour bébé..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    version = loop.run_until_complete(
                        version_service.generer_version_bebe(recette_id)
                    )

                    if version:
                        version_service.sauvegarder_version(
                            recette_id,
                            version,
                            TypeVersionRecetteEnum.BEBE.value
                        )

                        render_toast("✅ Version bébé générée !", "success")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Impossible de générer la version")

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    with col_v2:
        st.markdown("#### 🍳 Version Batch")
        st.caption("Optimise pour plusieurs portions")

        if st.button("✨ Générer Version Batch", use_container_width=True, type="primary", key="gen_batch"):
            with st.spinner("🤖 L'IA optimise..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    version = loop.run_until_complete(
                        version_service.generer_version_batch(recette_id)
                    )

                    if version:
                        version_service.sauvegarder_version(
                            recette_id,
                            version,
                            TypeVersionRecetteEnum.BATCH_COOKING.value
                        )

                        render_toast("✅ Version batch générée !", "success")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Impossible de générer la version")

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")


def render_recipe_edit_form(recette_id: int):
    """Formulaire complet d'édition de recette"""

    recette = recette_service.get_by_id_full(recette_id)

    if not recette:
        st.error("Recette introuvable")
        return

    st.title(f"✏️ Éditer : {recette.nom}")

    with st.form("edit_recipe_form"):
        st.markdown("### 📝 Informations Générales")

        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *", value=recette.nom)
            description = st.text_area("Description", value=recette.description or "", height=100)
            temps_prep = st.number_input("Préparation (min)", 0, 300, recette.temps_preparation, 5)
            temps_cuisson = st.number_input("Cuisson (min)", 0, 300, recette.temps_cuisson, 5)

        with col2:
            portions = st.number_input("Portions", 1, 20, recette.portions)
            difficulte = st.selectbox("Difficulté", ["facile", "moyen", "difficile"],
                                      index=["facile", "moyen", "difficile"].index(recette.difficulte))
            type_repas = st.selectbox("Type repas", [t.value for t in TypeRepasEnum],
                                      index=[t.value for t in TypeRepasEnum].index(recette.type_repas))
            saison = st.selectbox("Saison", [s.value for s in SaisonEnum],
                                  index=[s.value for s in SaisonEnum].index(recette.saison))

        st.markdown("---")

        col_tag1, col_tag2 = st.columns(2)
        with col_tag1:
            est_equilibre = st.checkbox("🥗 Équilibré", value=recette.est_equilibre)
            compatible_bebe = st.checkbox("👶 Compatible bébé", value=recette.compatible_bebe)
        with col_tag2:
            compatible_batch = st.checkbox("🍳 Compatible batch", value=recette.compatible_batch)
            congelable = st.checkbox("❄️ Congelable", value=recette.congelable)

        submitted = st.form_submit_button("💾 Enregistrer les modifications", type="primary", use_container_width=True)

        if submitted:
            recette_data = {
                "nom": nom,
                "description": description,
                "temps_preparation": temps_prep,
                "temps_cuisson": temps_cuisson,
                "portions": portions,
                "difficulte": difficulte,
                "type_repas": type_repas,
                "saison": saison,
                "est_equilibre": est_equilibre,
                "compatible_bebe": compatible_bebe,
                "compatible_batch": compatible_batch,
                "congelable": congelable,
                "est_rapide": (temps_prep + temps_cuisson) < 30
            }

            success = recette_edition_service.update_recette_complete(
                recette_id,
                recette_data,
                [{"nom": ing.ingredient.nom, "quantite": ing.quantite, "unite": ing.unite, "optionnel": ing.optionnel}
                 for ing in recette.ingredients],
                [{"ordre": e.ordre, "description": e.description, "duree": e.duree}
                 for e in recette.etapes]
            )

            if success:
                StateManager.set_editing_recipe(None)
                render_toast("✅ Recette mise à jour", "success")
                st.rerun()

    if st.button("❌ Annuler", use_container_width=True):
        StateManager.set_editing_recipe(None)
        st.rerun()

    st.markdown("---")

    with st.expander("🔧 Modifier les ingrédients et étapes", expanded=False):
        st.info("💡 Fonctionnalité d'édition inline à venir")
        # PARTIE 2/2 - À COLLER APRÈS LA PARTIE 1

# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Module Recettes v3 - Point d'entrée"""

    st.title("🍲 Recettes Intelligentes")
    st.caption("Génération IA, versions multiples, import/export, gestion complète")

    state = get_state()

    if state.editing_recipe_id:
        render_recipe_edit_form(state.editing_recipe_id)
        return

    if state.viewing_recipe_id:
        render_recipe_details_modern(state.viewing_recipe_id)
        return

    with st.sidebar:
        render_cache_stats(key_prefix="recettes")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Mes Recettes",
        "✨ Générer avec l'IA",
        "➕ Ajouter Manuellement",
        "📤 Import / Export"
    ])

    with tab1:
        st.subheader("Ma collection de recettes")

        display_mode = render_display_mode_toggle(key="recipe_display")
        search = render_search_bar(placeholder="Rechercher une recette...", key="recipe_search")

        filters_config = {
            "saison": {"type": "select", "label": "Saison", "options": ["Toutes"] + [s.value for s in SaisonEnum], "default": 0},
            "type_repas": {"type": "select", "label": "Type de repas", "options": ["Tous"] + [t.value for t in TypeRepasEnum], "default": 0},
            "difficulte": {"type": "select", "label": "Difficulté", "options": ["Toutes", "facile", "moyen", "difficile"], "default": 0},
            "temps_max": {"type": "slider", "label": "Temps max (min)", "min": 0, "max": 180, "default": 180},
            "rapide": {"type": "checkbox", "label": "⚡ Rapides uniquement", "default": False},
            "equilibre": {"type": "checkbox", "label": "🥗 Équilibrées", "default": False},
            "bebe": {"type": "checkbox", "label": "👶 Compatible bébé", "default": False},
            "batch": {"type": "checkbox", "label": "🍳 Compatible batch", "default": False},
            "ia": {"type": "checkbox", "label": "🤖 Générées par IA", "default": False}
        }

        filters = render_filter_panel(filters_config, key_prefix="recipe")

        st.markdown("---")

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
            render_empty_state(message="Aucune recette trouvée", icon="🔍", action_label="➕ Ajouter une recette", action_callback=lambda: st.session_state.update({"active_tab": 2}))
        else:
            stats = recette_service.get_stats()
            stats_data = [
                {"label": "Total", "value": len(recettes)},
                {"label": "Rapides", "value": sum(1 for r in recettes if r.est_rapide)},
                {"label": "IA", "value": sum(1 for r in recettes if r.genere_par_ia)},
                {"label": "Temps moyen", "value": f"{int(stats['temps_moyen'])}min"}
            ]
            render_stat_row(stats_data, cols=4)

            st.markdown("---")

            page, per_page = render_pagination(
                total_items=len(recettes),
                items_per_page=20 if display_mode == "liste" else 12,
                key="recipes_pagination"
            )

            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            if display_mode == "grille":
                cols_per_row = 3
                recettes_page = recettes[start_idx:end_idx]

                for row_start in range(0, len(recettes_page), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for idx, recette in enumerate(recettes_page[row_start:row_start + cols_per_row]):
                        with cols[idx]:
                            recette_dict = {
                                "id": recette.id, "nom": recette.nom,
                                "temps_total": recette.temps_preparation + recette.temps_cuisson,
                                "difficulte": recette.difficulte, "est_rapide": recette.est_rapide,
                                "compatible_bebe": recette.compatible_bebe, "genere_par_ia": recette.genere_par_ia,
                                "url_image": recette.url_image
                            }
                            render_recipe_card_grid(recette_dict, f"grid_recipe_{recette.id}", lambda r_id=recette.id: (StateManager.set_viewing_recipe(r_id), st.rerun()))
            else:
                for recette in recettes[start_idx:end_idx]:
                    recette_dict = {
                        "id": recette.id, "nom": recette.nom, "description": recette.description,
                        "temps_total": recette.temps_preparation + recette.temps_cuisson, "portions": recette.portions,
                        "difficulte": recette.difficulte, "est_rapide": recette.est_rapide, "est_equilibre": recette.est_equilibre,
                        "compatible_bebe": recette.compatible_bebe, "compatible_batch": recette.compatible_batch,
                        "genere_par_ia": recette.genere_par_ia, "score_ia": recette.score_ia, "url_image": recette.url_image
                    }
                    render_recipe_card_modern(recette_dict, f"recipe_{recette.id}")

    with tab2:
        st.subheader("✨ Générer des recettes avec l'IA")

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
                ingredients_input = st.text_input("Ingrédients à utiliser (optionnel)", placeholder="tomate, basilic, mozzarella")

            submitted = st.form_submit_button("✨ Générer les recettes", type="primary", use_container_width=True)

        if submitted:
            with st.spinner("🤖 L'IA génère les recettes..."):
                try:
                    filters_ai = {
                        "saison": saison, "type_repas": type_repas, "is_quick": is_quick, "is_balanced": is_balanced,
                        "ingredients": [i.strip() for i in ingredients_input.split(",")] if ingredients_input else None
                    }

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    recipes = loop.run_until_complete(
                        ai_recette_service.generate_recipes(count=count, filters=filters_ai, version_type=TypeVersionRecetteEnum.STANDARD.value)
                    )

                    for recipe in recipes:
                        recipe["url_image"] = ai_recette_service.generate_image_url(recipe["nom"], recipe["description"])

                    StateManager.save_generated_recipes(recipes)
                    render_toast(f"✅ {len(recipes)} recette(s) générée(s) !", "success")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

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
                if st.button(f"➕ Ajouter {len(selected_recipes)} recette(s) sélectionnée(s)", type="primary", use_container_width=True):
                    for recipe in selected_recipes:
                        recette_data = {k: v for k, v in recipe.items() if k not in ['ingredients', 'etapes', 'versions']}
                        recette_data['genere_par_ia'] = True
                        recette_data['score_ia'] = 95.0

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

    with tab3:
        st.subheader("➕ Ajouter une recette manuellement")

        ingredients = render_ingredients_form(key_prefix="manual_ing")
        etapes = render_etapes_form(key_prefix="manual_step")

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
                if not nom:
                    st.error("Le nom est obligatoire")
                elif not ingredients:
                    st.error("Ajoute au moins un ingrédient")
                elif not etapes:
                    st.error("Ajoute au moins une étape")
                else:
                    recette_data = {
                        "nom": nom, "description": description, "temps_preparation": temps_prep,
                        "temps_cuisson": temps_cuisson, "portions": portions, "difficulte": difficulte,
                        "type_repas": type_repas, "saison": saison,
                        "est_rapide": (temps_prep + temps_cuisson) < 30,
                        "est_equilibre": True, "genere_par_ia": False
                    }

                    recette_id = recette_service.create_full(
                        recette_data=recette_data,
                        ingredients_data=ingredients,
                        etapes_data=etapes
                    )

                    if "manual_ing_list" in st.session_state:
                        del st.session_state["manual_ing_list"]
                    if "manual_step_list" in st.session_state:
                        del st.session_state["manual_step_list"]

                    render_toast(f"✅ Recette '{nom}' ajoutée !", "success")
                    st.balloons()
                    st.rerun()

    with tab4:
        st.subheader("📤 Import / Export de Recettes")

        tab_exp, tab_imp = st.tabs(["📤 Exporter", "📥 Importer"])

        with tab_exp:
            st.markdown("### Exporter tes recettes")

            recettes_all = recette_service.get_all(limit=1000)

            if not recettes_all:
                st.info("Aucune recette à exporter")
            else:
                st.info(f"💡 {len(recettes_all)} recette(s) disponible(s)")

                export_all = st.checkbox("Exporter toutes les recettes", value=True)

                if not export_all:
                    selected_ids = st.multiselect(
                        "Sélectionner les recettes",
                        options=[r.id for r in recettes_all],
                        format_func=lambda x: next(r.nom for r in recettes_all if r.id == x)
                    )
                else:
                    selected_ids = [r.id for r in recettes_all]

                if selected_ids:
                    render_export_ui(selected_ids)

        with tab_imp:
            st.markdown("### Importer des recettes")
            render_import_ui(recette_service)