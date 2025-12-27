"""
Composants Recettes Ultra-Optimisés
Utilise les nouveaux composants génériques → -40% de code
"""
import streamlit as st
from typing import List, Dict, Optional, Callable

# Import des composants génériques
from src.ui.components import (
    render_item_card,
    render_unified_preview,
    DynamicList,
    SimpleModal,
    quick_action_bar
)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

INGREDIENT_FIELDS = [
    {"name": "nom", "type": "text", "label": "Nom", "required": True, "placeholder": "Ex: Tomates"},
    {"name": "quantite", "type": "number", "label": "Qté", "min": 0, "max": 10000, "step": 0.1, "default": 1.0},
    {"name": "unite", "type": "text", "label": "Unité", "default": "g"},
    {"name": "optionnel", "type": "checkbox", "label": "Opt."}
]

ETAPE_FIELDS = [
    {"name": "description", "type": "textarea", "label": "Description", "required": True, "height": 100},
    {"name": "duree", "type": "number", "label": "Durée (min)", "min": 0, "max": 300, "step": 5, "default": 0}
]


# ═══════════════════════════════════════════════════════════════
# COMPOSANTS INGRÉDIENTS/ÉTAPES (Nouvelle Version)
# ═══════════════════════════════════════════════════════════════

def render_ingredients_form_v2(
        initial_ingredients: Optional[List[Dict]] = None,
        key_prefix: str = "ing"
) -> List[Dict]:
    """
    Formulaire ingrédients V2 - Utilise DynamicList

    AVANT : 80 lignes de code custom
    APRÈS : 15 lignes avec DynamicList
    """
    st.markdown("### 🥕 Ingrédients")

    ingredient_list = DynamicList(
        key=f"{key_prefix}_ingredients",
        fields=INGREDIENT_FIELDS,
        initial_items=initial_ingredients,
        sortable=False,
        add_button_label="➕ Ajouter un ingrédient",
        empty_message="Aucun ingrédient ajouté"
    )

    return ingredient_list.render()


def render_etapes_form_v2(
        initial_etapes: Optional[List[Dict]] = None,
        key_prefix: str = "step"
) -> List[Dict]:
    """
    Formulaire étapes V2 - Utilise DynamicList avec tri

    AVANT : 100 lignes avec logique de tri custom
    APRÈS : 20 lignes avec DynamicList
    """
    st.markdown("### 📝 Étapes de Préparation")

    etape_list = DynamicList(
        key=f"{key_prefix}_etapes",
        fields=ETAPE_FIELDS,
        initial_items=initial_etapes,
        sortable=True,  # ✅ Tri activé
        add_button_label="➕ Ajouter une étape",
        empty_message="Aucune étape ajoutée"
    )

    items = etape_list.render()

    # Auto-numérotation
    for i, item in enumerate(items):
        item["ordre"] = i + 1

    return items


# ═══════════════════════════════════════════════════════════════
# CARTE RECETTE OPTIMISÉE
# ═══════════════════════════════════════════════════════════════

def render_recipe_card_v2(
        recette: Dict,
        on_view: Callable,
        on_edit: Callable,
        on_duplicate: Callable,
        on_delete: Callable,
        key: str
):
    """
    Carte recette V2 - Utilise render_item_card

    """
    # Préparer métadonnées
    metadata = [
        f"⏱️ {recette['temps_total']}min",
        f"🍽️ {recette['portions']} pers.",
        f"{'😊' if recette['difficulte'] == 'facile' else '😐' if recette['difficulte'] == 'moyen' else '😰'} {recette['difficulte'].capitalize()}"
    ]

    # Préparer tags
    tags = []
    if recette.get("est_rapide"):
        tags.append("⚡ Rapide")
    if recette.get("est_equilibre"):
        tags.append("🥗 Équilibré")
    if recette.get("compatible_bebe"):
        tags.append("👶 Bébé")
    if recette.get("compatible_batch"):
        tags.append("🍳 Batch")
    if recette.get("genere_par_ia"):
        tags.append(f"🤖 IA ({recette.get('score_ia', 0):.0f}%)")

    # Actions avec modals intégrées
    modal_delete = SimpleModal(f"delete_{key}")

    def handle_delete():
        if not modal_delete.is_showing():
            modal_delete.show()
            st.rerun()
        else:
            st.warning(f"⚠️ Supprimer '{recette['nom']}' définitivement ?")

            col1, col2 = st.columns(2)
            with col1:
                if modal_delete.confirm("🗑️ Supprimer"):
                    on_delete()
                    modal_delete.close()
            with col2:
                modal_delete.cancel()

    actions = [
        ("Détails", "👁️", on_view),
        ("Éditer", "✏️", on_edit),
        ("Dupliquer", "📋", on_duplicate),
        ("Supprimer", "🗑️", handle_delete)
    ]

    # Rendu
    render_item_card(
        title=recette["nom"],
        metadata=metadata,
        tags=tags,
        image_url=recette.get("url_image"),
        actions=actions,
        key=key,
        expandable_content=lambda: st.caption(recette.get("description", ""))
    )


# ═══════════════════════════════════════════════════════════════
# PREVIEW RECETTE OPTIMISÉE
# ═══════════════════════════════════════════════════════════════

def render_recipe_preview_v2(
        recette_data: Dict,
        ingredients: List[Dict],
        etapes: List[Dict],
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None
):
    """
    Preview recette V2 - Utilise render_unified_preview

    AVANT : 60 lignes de code custom
    APRÈS : 25 lignes avec composant générique
    """
    # Préparer sections
    sections = {
        "🥕 Ingrédients": [
            f"{ing['quantite']} {ing['unite']} {ing['nom']}"
            for ing in ingredients
        ],
        "📝 Étapes": [
            f"{etape['ordre']}. {etape['description'][:50]}..."
            for etape in etapes
        ]
    }

    # Métadonnées
    metadata = {
        "⏱️ Temps total": f"{recette_data.get('temps_preparation', 0) + recette_data.get('temps_cuisson', 0)}min",
        "🍽️ Portions": str(recette_data.get("portions", 4)),
        "Difficulté": recette_data.get("difficulte", "moyen").capitalize()
    }

    # Tags
    tags = []
    temps_total = recette_data.get("temps_preparation", 0) + recette_data.get("temps_cuisson", 0)
    if temps_total < 30:
        tags.append("⚡ Rapide")
    if recette_data.get("est_equilibre"):
        tags.append("🥗 Équilibré")
    if recette_data.get("compatible_bebe"):
        tags.append("👶 Bébé OK")

    # Actions
    actions = []
    if on_save:
        actions.append(("✅ Enregistrer", on_save))
    if on_cancel:
        actions.append(("❌ Annuler", on_cancel))

    # Rendu
    render_unified_preview(
        title=f"Preview : {recette_data.get('nom', 'Nouvelle recette')}",
        sections=sections,
        metadata=metadata,
        tags=tags,
        actions=actions if actions else None
    )


# ═══════════════════════════════════════════════════════════════
# DÉTAILS RECETTE OPTIMISÉS
# ═══════════════════════════════════════════════════════════════

def render_recipe_details_v2(
        recette: Dict,  # Recette complète avec ingrédients et étapes
        on_edit: Callable,
        on_duplicate: Callable,
        on_delete: Callable,
        on_close: Callable,
        key: str = "details"
):
    """
    Affichage détails recette V2

    AVANT : 100+ lignes
    APRÈS : 50 lignes avec composants génériques
    """
    # Header
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"# 🍽️ {recette['nom']}")
        if recette.get("description"):
            st.caption(recette["description"])

    with col2:
        if recette.get("url_image"):
            st.image(recette["url_image"], use_container_width=True)

    # Stats
    stats_data = [
        {"label": "Préparation", "value": f"{recette['temps_preparation']}min"},
        {"label": "Cuisson", "value": f"{recette['temps_cuisson']}min"},
        {"label": "Portions", "value": str(recette["portions"])},
        {"label": "Difficulté", "value": recette["difficulte"].capitalize()}
    ]

    from src.ui.components import render_stat_row
    render_stat_row(stats_data, cols=4)

    st.markdown("---")

    # Sections collapsibles
    from src.ui.components import render_collapsible_section

    render_collapsible_section(
        "Ingrédients",
        lambda: _render_ingredients_section(recette.get("ingredients", [])),
        icon="🥕",
        expanded=True
    )

    render_collapsible_section(
        "Étapes",
        lambda: _render_etapes_section(recette.get("etapes", [])),
        icon="📝",
        expanded=True
    )

    # Actions rapides
    st.markdown("---")
    quick_action_bar([
        ("✏️ Modifier", on_edit),
        ("📋 Dupliquer", on_duplicate),
        ("🗑️ Supprimer", on_delete),
        ("❌ Fermer", on_close)
    ], key_prefix=f"{key}_actions")


def _render_ingredients_section(ingredients: List[Dict]):
    """Helper pour section ingrédients"""
    for ing in ingredients:
        optional = " (optionnel)" if ing.get("optionnel") else ""
        st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}{optional}")


def _render_etapes_section(etapes: List[Dict]):
    """Helper pour section étapes"""
    for etape in sorted(etapes, key=lambda x: x.get("ordre", 0)):
        duration = f" *({etape.get('duree')}min)*" if etape.get("duree") else ""
        st.markdown(f"**{etape['ordre']}.** {etape['description']}{duration}")


# ═══════════════════════════════════════════════════════════════
# MODE GRILLE OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

def render_recipe_grid_v2(
        recettes: List[Dict],
        on_click: Callable,  # Prend recette_id en param
        cols_per_row: int = 3
):
    """
    Affichage grille recettes V2

    AVANT : 40 lignes avec logique de grid manuelle
    APRÈS : 20 lignes simplifiées
    """
    for row_start in range(0, len(recettes), cols_per_row):
        cols = st.columns(cols_per_row)

        for idx, recette in enumerate(recettes[row_start:row_start + cols_per_row]):
            with cols[idx]:
                _render_recipe_grid_card(recette, on_click)


def _render_recipe_grid_card(recette: Dict, on_click: Callable):
    """Carte compacte pour grille"""
    with st.container():
        # Image
        if recette.get("url_image"):
            st.image(recette["url_image"], use_container_width=True)
        else:
            st.markdown(
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'height: 150px; border-radius: 8px; display: flex; '
                'align-items: center; justify-content: center; color: white; '
                'font-size: 3rem;">🍽️</div>',
                unsafe_allow_html=True
            )

        # Titre
        st.markdown(f"**{recette['nom']}**")

        # Badges compacts
        badges = []
        if recette.get("est_rapide"):
            badges.append("⚡")
        if recette.get("compatible_bebe"):
            badges.append("👶")
        if recette.get("genere_par_ia"):
            badges.append("🤖")

        if badges:
            st.caption(" ".join(badges))

        # Métadonnées
        st.caption(f"⏱️ {recette.get('temps_total', 0)}min • {recette.get('difficulte', 'moyen')}")

        # Bouton
        if st.button("👁️ Voir", key=f"grid_{recette['id']}", use_container_width=True):
            on_click(recette['id'])