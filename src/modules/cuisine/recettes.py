import streamlit as st
import asyncio
from typing import List, Dict

# Services optimisés
from src.services.recettes.recette_service import recette_service
from src.services.recettes.recette_ai_service import ai_recette_service

# UI Helpers (ZÉRO duplication)
from src.modules.ui_helpers import (
    render_module_header,
    render_module_tabs,
    render_quick_actions,
    render_filters_panel,
    render_items_list,
    confirm_delete,
    render_stats_header,
    render_ai_generation_form,
    render_export_section
)

# Core
from src.core.state import StateManager
from src.core.cache import Cache
from src.core.models import TypeVersionRecetteEnum, SaisonEnum, TypeRepasEnum
from src.ui import toast, item_card, empty_state
from src.utils import format_time, truncate


# ═══════════════════════════════════════════════════════════════
# TAB 1: MES RECETTES
# ═══════════════════════════════════════════════════════════════

def tab_mes_recettes():
    """Tab Mes Recettes - ULTRA-OPTIMISÉ"""

    # ✅ Filtres standardisés (helper)
    filters = render_filters_panel(
        filters_config={
            "search": {
                "type": "text",
                "label": "🔍 Rechercher",
                "default": ""
            },
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes"] + [s.value for s in SaisonEnum],
                "default": 0
            },
            "type_repas": {
                "type": "select",
                "label": "Type",
                "options": ["Tous"] + [t.value for t in TypeRepasEnum],
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
            "equilibre": {"type": "checkbox", "label": "🥗 Équilibrées", "default": False}
        },
        session_key="recettes_filters"
    )

    # ✅ Charger avec service optimisé
    @Cache.cached(ttl=60)
    def load_recettes():
        return recette_service.search_advanced(
            search_term=filters.get("search") or None,
            saison=filters["saison"] if filters["saison"] != "Toutes" else None,
            type_repas=filters["type_repas"] if filters["type_repas"] != "Tous" else None,
            temps_max=filters["temps_max"] if filters["temps_max"] < 180 else None,
            is_rapide=filters["rapide"] if filters["rapide"] else None,
            is_equilibre=filters["equilibre"] if filters["equilibre"] else None
        )

    recettes = load_recettes()

    if not recettes:
        empty_state("Aucune recette", icon="🔍")
        return

    # ✅ Stats header (helper)
    render_stats_header({
        "Total": {"value": len(recettes), "icon": "📚"},
        "Rapides": {"value": sum(1 for r in recettes if r.est_rapide), "icon": "⚡"},
        "IA": {"value": sum(1 for r in recettes if r.genere_par_ia), "icon": "🤖"}
    })

    st.markdown("---")

    # ✅ Affichage liste (helper)
    def render_recette_card(recette, key):
        metadata = [
            f"⏱️ {format_time(recette.temps_preparation + recette.temps_cuisson)}",
            f"🍽️ {recette.portions}p"
        ]

        tags = []
        if recette.est_rapide: tags.append("⚡ Rapide")
        if recette.compatible_bebe: tags.append("👶 Bébé")

        actions = [
            ("👁️ Voir", lambda: _view_recette(recette.id)),
            ("🗑️", lambda: confirm_delete(
                recette.id,
                recette.nom,
                lambda: recette_service.delete(recette.id),
                "recette",
                key=f"del_{recette.id}"
            ))
        ]

        item_card(
            title=recette.nom,
            metadata=metadata,
            tags=tags,
            image_url=recette.url_image,
            actions=actions,
            key=key
        )

    render_items_list(
        items=recettes[:20],  # Pagination simple
        card_renderer=render_recette_card,
        key="recettes_list"
    )


def _view_recette(recette_id: int):
    StateManager.get().viewing_recipe_id = recette_id
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# TAB 2: GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════════

def tab_generation_ia():
    """Tab Génération IA - ULTRA-OPTIMISÉ"""

    # ✅ Formulaire IA standardisé (helper)
    render_ai_generation_form(
        ai_service=ai_recette_service,
        generation_config={
            "info": "Mistral génère des recettes personnalisées",
            "params": {
                "count": {
                    "type": "slider",
                    "label": "Nombre",
                    "min": 1,
                    "max": 5,
                    "default": 3
                },
                "saison": {
                    "type": "select",
                    "label": "Saison",
                    "options": [s.value for s in SaisonEnum]
                },
                "is_quick": {
                    "type": "checkbox",
                    "label": "⚡ Rapide",
                    "default": False
                },
                "is_balanced": {
                    "type": "checkbox",
                    "label": "🥗 Équilibré",
                    "default": True
                }
            }
        },
        on_generated=lambda recipes: _save_generated_recipes(recipes),
        key="recettes_ai"
    )


def _save_generated_recipes(recipes):
    StateManager.get().generated_recipes = recipes


# ═══════════════════════════════════════════════════════════════
# TAB 3: EXPORT
# ═══════════════════════════════════════════════════════════════

def tab_export():
    """Tab Export - ULTRA-OPTIMISÉ"""

    # ✅ Export standardisé (helper)
    render_export_section(
        service=recette_service,
        filename="recettes",
        key="recettes_export"
    )


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - VERSION FINALE"""

# ✅ Header standardisé (helper)
render_module_header(
    title="Recettes Intelligentes",
    subtitle="IA • Versions multiples • Import/Export",
    icon="🍲"
)

# ✅ Tabs standardisés (helper)
render_module_tabs([
    {"label": "📚 Mes Recettes", "renderer": tab_mes_recettes},
    {"label": "✨ Générer IA", "renderer": tab_generation_ia},
    {"label": "📤 Export", "renderer": tab_export}
])