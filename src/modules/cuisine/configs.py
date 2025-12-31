"""
Configurations BaseModuleUI - Modules Cuisine
"""
from src.services.recettes import recette_service, RecetteExporter, RecetteImporter
from src.services.inventaire import inventaire_service, CATEGORIES, EMPLACEMENTS, InventaireExporter, InventaireImporter
from src.services.courses import courses_service, MAGASINS_CONFIG
from src.services.planning import planning_service, repas_service
from src.ui.base_module import ModuleConfig
from src.ui.base_io_service import IOConfig, create_io_service
from src.core.cache import Cache
from datetime import date


# ═══════════════════════════════════════════════════════════════
# 1. RECETTES CONFIG
# ═══════════════════════════════════════════════════════════════

def get_recettes_config() -> ModuleConfig:
    """Configuration complète module Recettes"""

    # IO Config
    io_config = IOConfig(
        field_mapping={
            "nom": "Nom",
            "description": "Description",
            "temps_preparation": "Temps préparation (min)",
            "temps_cuisson": "Temps cuisson (min)",
            "portions": "Portions",
            "difficulte": "Difficulté",
            "type_repas": "Type repas",
            "saison": "Saison"
        },
        required_fields=["nom", "temps_preparation", "temps_cuisson", "portions"]
    )

    return ModuleConfig(
        name="recettes",
        title="🍽️ Recettes Intelligentes",
        icon="🍽️",
        service=recette_service,

        # Champs d'affichage
        display_fields=[
            {"key": "nom", "label": "Nom", "type": "text"},
            {"key": "description", "label": "Description", "type": "textarea"},
            {"key": "temps_preparation", "label": "Temps préparation", "type": "number"},
            {"key": "portions", "label": "Portions", "type": "number"}
        ],

        # Recherche
        search_fields=["nom", "description"],

        # Filtres
        filters_config={
            "saison": {
                "type": "select",
                "label": "Saison",
                "options": ["Toutes", "printemps", "été", "automne", "hiver", "toute_année"],
                "default": "Toutes"
            },
            "difficulte": {
                "type": "select",
                "label": "Difficulté",
                "options": ["Toutes", "facile", "moyen", "difficile"],
                "default": "Toutes"
            },
            "type_repas": {
                "type": "select",
                "label": "Type repas",
                "options": ["Tous", "petit_déjeuner", "déjeuner", "dîner", "goûter"],
                "default": "Tous"
            },
            "rapide": {
                "type": "checkbox",
                "label": "⚡ Rapides uniquement",
                "default": False
            }
        },

        # Stats
        stats_config=[
            {"label": "Total", "value_key": "total"},
            {"label": "⚡ Rapides", "filter": {"est_rapide": True}},
            {"label": "👶 Bébé", "filter": {"compatible_bebe": True}},
            {"label": "🍳 Batch", "filter": {"compatible_batch": True}}
        ],

        # Actions
        actions=[
            {
                "label": "👁️ Voir",
                "callback": lambda item: _view_recette(item.id),
                "icon": "👁️"
            },
            {
                "label": "✏️ Éditer",
                "callback": lambda item: _edit_recette(item.id),
                "icon": "✏️"
            },
            {
                "label": "🗑️ Suppr.",
                "callback": lambda item: _delete_recette(item.id),
                "icon": "🗑️"
            }
        ],

        # Statut
        status_field="difficulte",
        status_colors={
            "facile": "#4CAF50",
            "moyen": "#FF9800",
            "difficile": "#f44336"
        },

        # Métadonnées carte
        metadata_fields=["temps_preparation", "temps_cuisson", "portions"],
        image_field="url_image",

        # Formulaire ajout
        form_fields=[
            {"name": "nom", "label": "Nom", "type": "text", "required": True},
            {"name": "description", "label": "Description", "type": "textarea"},
            {"name": "temps_preparation", "label": "Temps préparation (min)", "type": "number", "required": True, "min": 0, "max": 300},
            {"name": "temps_cuisson", "label": "Temps cuisson (min)", "type": "number", "required": True, "min": 0, "max": 300},
            {"name": "portions", "label": "Portions", "type": "number", "required": True, "min": 1, "max": 20},
            {"name": "difficulte", "label": "Difficulté", "type": "select", "options": ["facile", "moyen", "difficile"], "required": True},
            {"name": "type_repas", "label": "Type repas", "type": "select", "options": ["petit_déjeuner", "déjeuner", "dîner", "goûter"], "required": True},
            {"name": "saison", "label": "Saison", "type": "select", "options": ["printemps", "été", "automne", "hiver", "toute_année"], "required": True}
        ],

        # Import/Export
        io_service=create_io_service(io_config),
        export_formats=["csv", "json"],

        # Pagination
        items_per_page=12
    )


# ═══════════════════════════════════════════════════════════════
# 2. INVENTAIRE CONFIG
# ═══════════════════════════════════════════════════════════════

def get_inventaire_config() -> ModuleConfig:
    """Configuration complète module Inventaire"""

    # IO Config
    io_config = IOConfig(
        field_mapping={
            "nom": "Nom",
            "categorie": "Catégorie",
            "quantite": "Quantité",
            "unite": "Unité",
            "quantite_min": "Seuil",
            "emplacement": "Emplacement",
            "date_peremption": "Péremption"
        },
        required_fields=["nom", "quantite"]
    )

    return ModuleConfig(
        name="inventaire",
        title="📦 Inventaire Intelligent",
        icon="📦",
        service=inventaire_service,

        # Champs
        display_fields=[
            {"key": "nom", "label": "Nom", "type": "text"},
            {"key": "categorie", "label": "Catégorie", "type": "select"},
            {"key": "quantite", "label": "Quantité", "type": "number"},
            {"key": "unite", "label": "Unité", "type": "text"}
        ],

        # Recherche
        search_fields=["nom"],

        # Filtres
        filters_config={
            "categorie": {
                "type": "select",
                "label": "Catégorie",
                "options": ["Toutes"] + CATEGORIES,
                "default": "Toutes"
            },
            "emplacement": {
                "type": "select",
                "label": "Emplacement",
                "options": ["Tous"] + EMPLACEMENTS,
                "default": "Tous"
            },
            "statut": {
                "type": "select",
                "label": "Statut",
                "options": ["Tous", "ok", "sous_seuil", "peremption_proche", "critique"],
                "default": "Tous"
            }
        },

        # Stats
        stats_config=[
            {"label": "Articles", "value_key": "total"},
            {"label": "Stock Bas", "filter": {"statut": "sous_seuil"}},
            {"label": "⚠️ Critiques", "filter": {"statut": "critique"}},
            {"label": "⏳ Péremption", "filter": {"statut": "peremption_proche"}}
        ],

        # Actions
        actions=[
            {
                "label": "➕",
                "callback": lambda item: _adjust_stock(item.id, 1.0),
                "icon": "➕"
            },
            {
                "label": "➖",
                "callback": lambda item: _adjust_stock(item.id, -1.0),
                "icon": "➖"
            },
            {
                "label": "🛒",
                "callback": lambda item: _add_to_cart(item.id),
                "icon": "🛒"
            }
        ],

        # Statut
        status_field="statut",
        status_colors={
            "ok": "#4CAF50",
            "sous_seuil": "#FFC107",
            "peremption_proche": "#FF9800",
            "critique": "#f44336"
        },

        # Métadonnées
        metadata_fields=["categorie", "quantite", "unite", "emplacement"],

        # Formulaire
        form_fields=[
            {"name": "nom", "label": "Nom", "type": "text", "required": True},
            {"name": "categorie", "label": "Catégorie", "type": "select", "options": CATEGORIES, "required": True},
            {"name": "quantite", "label": "Quantité", "type": "number", "required": True, "min": 0, "step": 0.1},
            {"name": "unite", "label": "Unité", "type": "select", "options": ["pcs", "kg", "g", "L", "mL"], "required": True},
            {"name": "quantite_min", "label": "Seuil", "type": "number", "min": 0, "step": 0.1},
            {"name": "emplacement", "label": "Emplacement", "type": "select", "options": EMPLACEMENTS},
            {"name": "date_peremption", "label": "Péremption", "type": "date"}
        ],

        # IO
        io_service=create_io_service(io_config),
        export_formats=["csv", "json"],

        items_per_page=20
    )


# ═══════════════════════════════════════════════════════════════
# 3. COURSES CONFIG
# ═══════════════════════════════════════════════════════════════

def get_courses_config() -> ModuleConfig:
    """Configuration complète module Courses"""

    # IO Config
    io_config = IOConfig(
        field_mapping={
            "nom": "Article",
            "quantite": "Quantité",
            "unite": "Unité",
            "priorite": "Priorité",
            "magasin": "Magasin",
            "rayon": "Rayon"
        },
        required_fields=["nom", "quantite"]
    )

    return ModuleConfig(
        name="courses",
        title="🛒 Courses Intelligentes",
        icon="🛒",
        service=courses_service,

        display_fields=[
            {"key": "nom", "label": "Article", "type": "text"},
            {"key": "quantite", "label": "Quantité", "type": "number"},
            {"key": "priorite", "label": "Priorité", "type": "select"}
        ],

        search_fields=["nom"],

        filters_config={
            "priorite": {
                "type": "select",
                "label": "Priorité",
                "options": ["Toutes", "haute", "moyenne", "basse"],
                "default": "Toutes"
            },
            "magasin": {
                "type": "select",
                "label": "Magasin",
                "options": ["Tous"] + list(MAGASINS_CONFIG.keys()),
                "default": "Tous"
            },
            "achete": {
                "type": "checkbox",
                "label": "Afficher achetés",
                "default": False
            }
        },

        stats_config=[
            {"label": "Total", "value_key": "total"},
            {"label": "🔴 Haute", "filter": {"priorite": "haute"}},
            {"label": "🟡 Moyenne", "filter": {"priorite": "moyenne"}},
            {"label": "🟢 Basse", "filter": {"priorite": "basse"}}
        ],

        actions=[
            {
                "label": "✅ Acheté",
                "callback": lambda item: _mark_bought(item.id),
                "icon": "✅"
            },
            {
                "label": "🗑️ Suppr.",
                "callback": lambda item: _delete_course(item.id),
                "icon": "🗑️"
            }
        ],

        status_field="priorite",
        status_colors={
            "haute": "#f44336",
            "moyenne": "#FFC107",
            "basse": "#4CAF50"
        },

        metadata_fields=["quantite", "unite", "magasin", "priorite"],

        form_fields=[
            {"name": "nom", "label": "Article", "type": "text", "required": True},
            {"name": "quantite", "label": "Quantité", "type": "number", "required": True, "min": 0.1, "step": 0.1},
            {"name": "unite", "label": "Unité", "type": "select", "options": ["pcs", "kg", "g", "L", "mL"], "required": True},
            {"name": "priorite", "label": "Priorité", "type": "select", "options": ["haute", "moyenne", "basse"], "default": "moyenne"},
            {"name": "magasin", "label": "Magasin", "type": "select", "options": list(MAGASINS_CONFIG.keys())},
            {"name": "rayon", "label": "Rayon", "type": "text"}
        ],

        io_service=create_io_service(io_config),
        export_formats=["csv", "json"],

        items_per_page=30
    )


# ═══════════════════════════════════════════════════════════════
# 4. PLANNING CONFIG
# ═══════════════════════════════════════════════════════════════

def get_planning_config() -> ModuleConfig:
    """Configuration complète module Planning"""

    # Note: Planning a une structure différente (jours + repas)
    # On garde une config minimale pour BaseModuleUI

    return ModuleConfig(
        name="planning",
        title="🗓️ Planning Hebdomadaire",
        icon="🗓️",
        service=planning_service,

        display_fields=[
            {"key": "nom", "label": "Nom", "type": "text"},
            {"key": "semaine_debut", "label": "Semaine", "type": "date"}
        ],

        search_fields=["nom"],

        filters_config={},

        stats_config=[
            {"label": "Plannings", "value_key": "total"}
        ],

        actions=[
            {
                "label": "👁️ Voir",
                "callback": lambda item: _view_planning(item.id),
                "icon": "👁️"
            },
            {
                "label": "🗑️ Suppr.",
                "callback": lambda item: _delete_planning(item.id),
                "icon": "🗑️"
            }
        ],

        metadata_fields=["semaine_debut"],

        form_fields=[
            {"name": "nom", "label": "Nom", "type": "text", "required": True},
            {"name": "semaine_debut", "label": "Semaine", "type": "date", "required": True}
        ],

        io_service=None,  # Planning a sa propre logique d'export

        items_per_page=10
    )


# ═══════════════════════════════════════════════════════════════
# CALLBACKS (Actions communes)
# ═══════════════════════════════════════════════════════════════

import streamlit as st
from src.ui import toast, Modal

def _view_recette(recette_id: int):
    """Affiche détails recette"""
    st.session_state.viewing_recipe_id = recette_id
    st.rerun()

def _edit_recette(recette_id: int):
    """Édite recette"""
    st.session_state.editing_recipe_id = recette_id
    st.rerun()

def _delete_recette(recette_id: int):
    """Supprime recette avec confirmation"""
    modal = Modal(f"delete_recette_{recette_id}")

    if not modal.is_showing():
        modal.show()
    else:
        st.warning("⚠️ Confirmer la suppression ?")

        if modal.confirm():
            recette_service.delete(recette_id)
            toast("🗑️ Recette supprimée", "success")
            Cache.invalidate("recettes")
            modal.close()

        modal.cancel()

def _adjust_stock(article_id: int, delta: float):
    """Ajuste stock inventaire"""
    article = inventaire_service.get_by_id(article_id)
    if article:
        new_qty = max(0, article.quantite + delta)
        inventaire_service.update(article_id, {"quantite": new_qty})

        icon = "➕" if delta > 0 else "➖"
        toast(f"{icon} Stock ajusté", "success")
        Cache.invalidate("inventaire")
        st.rerun()

def _add_to_cart(article_id: int):
    """Ajoute article aux courses"""
    article = inventaire_service.get_by_id(article_id)
    if article:
        courses_service.create({
            "ingredient_id": article.ingredient_id,
            "quantite_necessaire": article.quantite_min,
            "priorite": "haute"
        })
        toast("🛒 Ajouté aux courses", "success")
        st.rerun()

def _mark_bought(article_id: int):
    """Marque article comme acheté"""
    courses_service.update(article_id, {"achete": True, "achete_le": date.today()})
    toast("✅ Marqué acheté", "success")
    Cache.invalidate("courses")
    st.rerun()

def _delete_course(article_id: int):
    """Supprime article courses"""
    courses_service.delete(article_id)
    toast("🗑️ Supprimé", "success")
    Cache.invalidate("courses")
    st.rerun()

def _view_planning(planning_id: int):
    """Affiche planning"""
    st.session_state.viewing_planning_id = planning_id
    st.rerun()

def _delete_planning(planning_id: int):
    """Supprime planning"""
    planning_service.delete(planning_id)
    toast("🗑️ Planning supprimé", "success")
    Cache.invalidate("planning")
    st.rerun()