"""
Module Recettes - VERSION 3.0 REFACTORISÉE
Intègre tous les refactoring core/ui/utils
"""
import streamlit as st
import asyncio
from typing import List, Dict, Optional

# ═══════════════════════════════════════════════════════════════
# IMPORTS REFACTORISÉS
# ═══════════════════════════════════════════════════════════════

# Core
from src.core.state import StateManager, get_state
from src.core.cache import Cache, RateLimit, render_cache_stats
from src.core.errors import handle_errors, ValidationError
from src.core.database import get_db_context
from src.core.models import Recette, TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum

# UI - Nouveau namespace unifié
from src.ui import (
    # Base
    empty_state, loading_spinner,
    # Forms
    search_bar, filter_panel,
    # Data
    pagination, metrics_row, export_buttons,
    # Feedback
    toast, Modal, confirmation_dialog,
    # Layouts
    grid_layout, item_card
)

# Services
from src.services.recettes import (
    recette_service,
    ai_recette_service,
    RecetteExporter,
    RecetteImporter,
    RecipeWebScraper,
    create_recette_version_service
)

# Utils
from src.utils import format_time, truncate


# ═══════════════════════════════════════════════════════════════
# TAB 1 : MES RECETTES
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True, fallback_value=None)
def tab_mes_recettes():
    """Tab Mes Recettes - VERSION REFACTORISÉE"""
    st.subheader("📚 Ma Collection")

    # ✅ Barre de recherche unifiée
    search = search_bar(placeholder="Rechercher une recette...", key="recipe_search")

    # ✅ Filtres unifiés
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
        "rapide": {"type": "checkbox", "label": "⚡ Rapides", "default": False},
        "equilibre": {"type": "checkbox", "label": "🥗 Équilibrées", "default": False},
        "bebe": {"type": "checkbox", "label": "👶 Bébé", "default": False},
        "ia": {"type": "checkbox", "label": "🤖 IA", "default": False}
    }

    filters = filter_panel(filters_config, key_prefix="recipe")

    st.markdown("---")

    # ✅ Charger recettes avec cache
    @Cache.cached(ttl=60)
    def load_recipes():
        return recette_service.search_advanced(
            search_term=search if search else None,
            saison=filters["saison"] if filters["saison"] != "Toutes" else None,
            type_repas=filters["type_repas"] if filters["type_repas"] != "Tous" else None,
            difficulte=filters["difficulte"] if filters["difficulte"] != "Toutes" else None,
            temps_max=filters["temps_max"] if filters["temps_max"] < 180 else None,
            is_rapide=filters["rapide"] if filters["rapide"] else None,
            is_equilibre=filters["equilibre"] if filters["equilibre"] else None,
            compatible_bebe=filters["bebe"] if filters["bebe"] else None,
            ia_only=filters["ia"] if filters["ia"] else None,
            limit=100
        )

    recettes = load_recipes()

    if not recettes:
        empty_state(
            message="Aucune recette trouvée",
            icon="🔍",
            subtext="Ajuste tes filtres ou ajoute une recette"
        )

        if st.button("➕ Ajouter une recette", type="primary"):
            StateManager.navigate_to("cuisine.recettes")
            st.rerun()
        return

    # ✅ Stats avec nouveau composant
    stats_data = [
        {"label": "Total", "value": len(recettes)},
        {"label": "Rapides", "value": sum(1 for r in recettes if r.est_rapide)},
        {"label": "IA", "value": sum(1 for r in recettes if r.genere_par_ia)},
    ]
    metrics_row(stats_data, cols=3)

    st.markdown("---")

    # ✅ Pagination
    page, per_page = pagination(
        total_items=len(recettes),
        items_per_page=12,
        key="recipes_pagination"
    )

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    recettes_page = recettes[start_idx:end_idx]

    # ✅ Affichage en grille avec item_card
    def render_recipe_card(recette: Recette, key: str):
        """Carte recette avec nouveau composant unifié"""
        # Métadonnées
        metadata = [
            f"⏱️ {format_time(recette.temps_preparation + recette.temps_cuisson)}",
            f"🍽️ {recette.portions}p",
            f"📊 {recette.difficulte}"
        ]

        # Tags
        tags = []
        if recette.est_rapide:
            tags.append("⚡ Rapide")
        if recette.est_equilibre:
            tags.append("🥗 Équilibré")
        if recette.compatible_bebe:
            tags.append("👶 Bébé")
        if recette.genere_par_ia:
            tags.append("🤖 IA")

        # Actions
        actions = [
            ("👁️ Voir", lambda: _view_recipe(recette.id)),
            ("✏️ Éditer", lambda: _edit_recipe(recette.id)),
            ("📋 Dupliquer", lambda: _duplicate_recipe(recette.id)),
            ("🗑️ Supprimer", lambda: _delete_recipe(recette.id))
        ]

        # ✅ Utilisation du composant unifié
        item_card(
            title=recette.nom,
            metadata=metadata,
            tags=tags,
            image_url=recette.url_image,
            actions=actions,
            key=key
        )

    # Grille
    grid_layout(
        items=recettes_page,
        cols_per_row=3,
        card_renderer=render_recipe_card,
        key="recipes_grid"
    )


# ═══════════════════════════════════════════════════════════════
# TAB 2 : GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Tab Génération IA - REFACTORISÉ"""
    st.subheader("✨ Génération IA")

    # ✅ Vérifier rate limit
    can_call, error_msg = RateLimit.can_call()

    if not can_call:
        st.warning(error_msg)
        usage = RateLimit.get_usage()
        st.caption(f"Utilisation: {usage['calls_today']}/{usage['daily_limit']}")
        return

    st.info("💡 Mistral génère des recettes personnalisées")

    with st.form("ai_generation"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Critères**")
            count = st.slider("Nombre", 1, 5, 3)
            saison = st.selectbox("Saison", [s.value for s in SaisonEnum])
            type_repas = st.selectbox("Type", [t.value for t in TypeRepasEnum])

        with col2:
            st.markdown("**Filtres**")
            is_quick = st.checkbox("⚡ Rapide")
            is_balanced = st.checkbox("🥗 Équilibré", value=True)
            is_baby = st.checkbox("👶 Bébé")
            ingredients = st.text_input("Ingrédients", placeholder="tomate, basilic")

        submitted = st.form_submit_button("✨ Générer", type="primary", use_container_width=True)

    if submitted:
        with st.spinner("🤖 Génération..."):
            try:
                filters = {
                    "saison": saison,
                    "type_repas": type_repas,
                    "is_quick": is_quick,
                    "is_balanced": is_balanced,
                    "ingredients": [i.strip() for i in ingredients.split(",")] if ingredients else None
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

                StateManager.get().generated_recipes = recipes
                toast("✅ Recettes générées !", "success")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")

    # Afficher recettes générées
    _render_generated_recipes()


# ═══════════════════════════════════════════════════════════════
# TAB 3 : AJOUT MANUEL
# ═══════════════════════════════════════════════════════════════

def tab_ajout_manuel():
    """Tab Ajout Manuel"""
    st.subheader("➕ Nouvelle Recette")

    st.info("🚧 Utilise le formulaire simple ou import depuis web")

    # À implémenter avec les nouveaux composants forms
    st.write("Formulaire à venir...")


# ═══════════════════════════════════════════════════════════════
# TAB 4 : IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════════

def tab_import_export():
    """Tab Import/Export"""
    st.subheader("📤 Import/Export")

    tab_exp, tab_imp_file, tab_imp_web = st.tabs([
        "📤 Exporter",
        "📥 Importer",
        "🌐 Web"
    ])

    with tab_exp:
        recettes = recette_service.get_all(limit=1000)

        if not recettes:
            st.info("Aucune recette")
        else:
            st.info(f"💡 {len(recettes)} recette(s)")

            # ✅ Utiliser le nouveau composant export
            export_buttons(
                data=[{"id": r.id, "nom": r.nom} for r in recettes],
                filename="recettes",
                formats=["csv", "json"],
                key="recipes_export"
            )

    with tab_imp_file:
        st.markdown("### Importer")
        uploaded = st.file_uploader("Fichier", type=["json", "csv"])

        if uploaded:
            st.info("Import à implémenter")

    with tab_imp_web:
        st.markdown("### Depuis Web")
        url = st.text_input("URL", placeholder="https://marmiton.org/...")

        if st.button("🌐 Importer", type="primary"):
            with st.spinner("Scraping..."):
                try:
                    recipe_data = RecipeWebScraper.scrape_url(url)

                    if recipe_data:
                        st.success("✅ Recette extraite")
                        st.json(recipe_data)
                    else:
                        st.error("Extraction échouée")

                except Exception as e:
                    st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS PRIVÉS
# ═══════════════════════════════════════════════════════════════

def _view_recipe(recette_id: int):
    """Affiche détails recette"""
    StateManager.get().viewing_recipe_id = recette_id
    st.rerun()


def _edit_recipe(recette_id: int):
    """Édite recette"""
    StateManager.get().editing_recipe_id = recette_id
    st.rerun()


def _duplicate_recipe(recette_id: int):
    """Duplique recette"""
    try:
        recette = recette_service.get_by_id_full(recette_id)
        new_id = recette_service.duplicate(
            recette_id,
            nouveau_nom=f"{recette.nom} (copie)"
        )

        if new_id:
            toast("✅ Recette dupliquée", "success")
            st.balloons()
            Cache.invalidate("recette")
            st.rerun()

    except Exception as e:
        st.error(f"❌ {str(e)}")


def _delete_recipe(recette_id: int):
    """Supprime recette avec confirmation"""
    modal = Modal("delete_recipe")

    if st.button("🗑️ Supprimer", key=f"del_{recette_id}"):
        modal.show()

    if modal.is_showing():
        st.warning("⚠️ Supprimer cette recette ?")

        if modal.confirm("✅ Confirmer"):
            try:
                recette_service.delete(recette_id)
                toast("🗑️ Supprimée", "success")
                Cache.invalidate("recette")
                modal.close()
            except Exception as e:
                st.error(f"❌ {str(e)}")

        modal.cancel()


def _render_generated_recipes():
    """Affiche recettes générées"""
    state = get_state()

    if not state.generated_recipes:
        return

    st.markdown("---")
    st.markdown("### 📋 Recettes Générées")

    selected = []

    for idx, recipe in enumerate(state.generated_recipes):
        with st.expander(f"🍽️ {recipe['nom']}", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Description:** {truncate(recipe['description'], 100)}")
                st.caption(f"⏱️ {format_time(recipe['temps_preparation'] + recipe['temps_cuisson'])}")

            with col2:
                st.caption(f"🍽️ {recipe['portions']} portions")
                st.caption(f"📊 {recipe['difficulte']}")

            if st.checkbox("✅ Sélectionner", key=f"sel_{idx}"):
                selected.append(recipe)

    if selected:
        if st.button(
                f"➕ Ajouter {len(selected)} recette(s)",
                type="primary",
                use_container_width=True
        ):
            try:
                for recipe in selected:
                    recette_data = {k: v for k, v in recipe.items()
                                    if k not in ["ingredients", "etapes"]}
                    recette_data["genere_par_ia"] = True

                    recette_service.create_full(
                        recette_data=recette_data,
                        ingredients_data=recipe["ingredients"],
                        etapes_data=recipe["etapes"]
                    )

                StateManager.get().generated_recipes = []
                toast(f"✅ {len(selected)} ajoutée(s) !", "success")
                Cache.invalidate("recette")
                st.balloons()
                st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - VERSION REFACTORISÉE"""
    st.title("🍲 Recettes Intelligentes")
    st.caption("IA • Versions multiples • Import/Export")

    # ✅ Cache stats dans sidebar
    with st.sidebar:
        render_cache_stats(key_prefix="recettes")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Mes Recettes",
        "✨ Générer IA",
        "➕ Ajouter",
        "📤 Import/Export"
    ])

    with tab1:
        tab_mes_recettes()

    with tab2:
        tab_generation_ia()

    with tab3:
        tab_ajout_manuel()

    with tab4:
        tab_import_export()