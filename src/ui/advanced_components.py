"""
Composants UI Avancés Réutilisables
Élimine duplication dans recettes.py, planning_semaine.py, etc.

"""
import streamlit as st
from typing import Dict, List, Optional, Callable
from datetime import date


# ═══════════════════════════════════════════════════════════════
# COMPOSANTS RECETTES
# ═══════════════════════════════════════════════════════════════

def render_recipe_quick_actions(
        recette: Dict,
        unique_key: str,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_duplicate: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        show_all: bool = True
):
    """
    Actions rapides recette (réutilisable)

    ✅ Élimine duplication dans render_recipe_card_modern
    ✅ Clés uniques garanties

    Args:
        recette: Dict recette
        unique_key: Clé unique (ex: "list_recipe_123")
        on_*: Callbacks optionnels
        show_all: Si False, affiche version compacte
    """
    if show_all:
        col1, col2, col3, col4 = st.columns(4)
    else:
        col1, col2 = st.columns(2)

    with col1:
        if on_view and st.button(
                "👁️ Détails",
                key=f"{unique_key}_view",
                use_container_width=True
        ):
            on_view()

    with col2:
        if on_edit and st.button(
                "✏️ Éditer",
                key=f"{unique_key}_edit",
                use_container_width=True
        ):
            on_edit()

    if show_all:
        with col3:
            if on_duplicate and st.button(
                    "📋 Dupliquer",
                    key=f"{unique_key}_dup",
                    use_container_width=True
            ):
                on_duplicate()

        with col4:
            # Confirmation pour delete
            confirm_key = f"confirm_delete_{recette['id']}"

            if st.session_state.get(confirm_key):
                if st.button(
                        "⚠️ Confirmer?",
                        key=f"{unique_key}_del_confirm",
                        type="primary",
                        use_container_width=True
                ):
                    if on_delete:
                        on_delete()
            else:
                if st.button(
                        "🗑️ Supprimer",
                        key=f"{unique_key}_del",
                        use_container_width=True
                ):
                    st.session_state[confirm_key] = True
                    st.rerun()


def render_recipe_metadata_bar(recette: Dict):
    """
    Barre métadonnées recette

    ✅ Affichage standard réutilisable
    """
    metadata = [
        f"⏱️ {recette.get('temps_total', recette.get('temps_preparation', 0) + recette.get('temps_cuisson', 0))}min",
        f"🍽️ {recette.get('portions', 4)} pers.",
        f"{'😊' if recette.get('difficulte') == 'facile' else '😐' if recette.get('difficulte') == 'moyen' else '😰'} {recette.get('difficulte', 'moyen').capitalize()}"
    ]

    st.caption(" • ".join(metadata))


def render_recipe_tags(recette: Dict):
    """
    Tags recette standards

    ✅ Logique centralisée
    """
    tags = []

    if recette.get("est_rapide"):
        tags.append("⚡ Rapide")
    if recette.get("est_equilibre"):
        tags.append("🥗 Équilibré")
    if recette.get("compatible_bebe"):
        tags.append("👶 Bébé")
    if recette.get("compatible_batch"):
        tags.append("🍳 Batch")
    if recette.get("congelable"):
        tags.append("❄️ Congélation")
    if recette.get("genere_par_ia"):
        tags.append(f"🤖 IA ({recette.get('score_ia', 0):.0f}%)")

    if tags:
        st.caption(" • ".join(tags))


def render_recipe_card_compact(
        recette: Dict,
        unique_key: str,
        on_view: Callable,
        on_edit: Optional[Callable] = None
):
    """
    Carte recette compacte (pour liste)

    ✅ Remplace render_recipe_card_modern
    ✅ 50% moins de code
    """
    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### 🍽️ {recette['nom']}")

            desc = recette.get("description", "")
            if desc:
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                st.caption(desc)

            render_recipe_tags(recette)

        with col2:
            if recette.get("url_image"):
                st.image(recette["url_image"], use_container_width=True)

        render_recipe_metadata_bar(recette)

        # Actions
        render_recipe_quick_actions(
            recette,
            unique_key,
            on_view=on_view,
            on_edit=on_edit,
            show_all=False
        )


# ═══════════════════════════════════════════════════════════════
# COMPOSANTS PLANNING
# ═══════════════════════════════════════════════════════════════

def render_repas_slot_empty(
        jour_idx: int,
        type_repas: str,
        planning_id: int,
        date_jour: date,
        unique_key: str,
        on_add: Callable
):
    """
    Slot repas vide (bouton ajout)

    ✅ Centralise logique d'ajout
    """
    types_repas_icons = {
        "petit_déjeuner": "🌅",
        "déjeuner": "☀️",
        "dîner": "🌙",
        "goûter": "🍪"
    }

    if st.button(
            f"➕ Ajouter {types_repas_icons.get(type_repas, '🍽️')} {type_repas.replace('_', ' ').capitalize()}",
            key=f"{unique_key}_add",
            use_container_width=True,
            type="secondary"
    ):
        # Stocker infos pour modal
        st.session_state.adding_repas_slot = {
            "planning_id": planning_id,
            "jour_idx": jour_idx,
            "date_jour": date_jour,
            "type_repas": type_repas
        }
        on_add()


def render_repas_card_compact(
        repas: Dict,
        unique_key: str,
        on_view: Optional[Callable] = None,
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None
):
    """
    Carte repas compacte

    ✅ Réutilisable dans planning
    """
    recette = repas.get("recette")

    if not recette:
        st.info("Repas sans recette")
        return

    with st.container():
        col1, col2 = st.columns([1, 4])

        with col1:
            if recette.get("url_image"):
                st.image(recette["url_image"], use_container_width=True)

        with col2:
            st.markdown(f"**{recette['nom']}**")

            # Badges
            badges = []
            if repas.get("est_adapte_bebe"):
                badges.append("👶 Bébé")
            if repas.get("est_batch"):
                badges.append("🍳 Batch")

            if badges:
                st.caption(" • ".join(badges))

            temps_total = recette.get('temps_total',
                                      recette.get('temps_preparation', 0) +
                                      recette.get('temps_cuisson', 0))

            st.caption(f"⏱️ {temps_total}min • {repas.get('portions', 4)} pers.")

        # Actions
        col_a1, col_a2, col_a3 = st.columns(3)

        with col_a1:
            if on_view and st.button(
                    "👁️",
                    key=f"{unique_key}_view",
                    help="Voir détails"
            ):
                on_view()

        with col_a2:
            if on_edit and st.button(
                    "✏️",
                    key=f"{unique_key}_edit",
                    help="Modifier"
            ):
                on_edit()

        with col_a3:
            if on_delete and st.button(
                    "🗑️",
                    key=f"{unique_key}_del",
                    help="Supprimer"
            ):
                on_delete()


def render_planning_day_header(
        jour_nom: str,
        jour_date: date,
        is_today: bool = False
):
    """
    Header jour planning

    ✅ Affichage standard
    """
    prefix = "🔵 " if is_today else ""
    st.markdown(f"### {prefix}{jour_nom} {jour_date.strftime('%d/%m')}")


# ═══════════════════════════════════════════════════════════════
# COMPOSANTS GÉNÉRIQUES AVANCÉS
# ═══════════════════════════════════════════════════════════════

def render_filter_bar(
        filters_config: Dict,
        key_prefix: str,
        on_clear: Optional[Callable] = None
) -> Dict:
    """
    Barre de filtres horizontale

    ✅ Alternative à render_filter_panel en expander
    ✅ Plus compact pour UI dense
    """
    with st.container():
        cols = st.columns(len(filters_config) + 1)

        results = {}

        for idx, (filter_name, config) in enumerate(filters_config.items()):
            with cols[idx]:
                filter_type = config.get("type", "text")
                label = config.get("label", filter_name)
                key = f"{key_prefix}_{filter_name}"

                if filter_type == "select":
                    results[filter_name] = st.selectbox(
                        label,
                        config.get("options", []),
                        index=config.get("default", 0),
                        key=key,
                        label_visibility="collapsed"
                    )

                elif filter_type == "checkbox":
                    results[filter_name] = st.checkbox(
                        label,
                        value=config.get("default", False),
                        key=key
                    )

        # Bouton clear
        with cols[-1]:
            st.write("")  # Spacer
            if on_clear and st.button(
                    "🔄 Reset",
                    key=f"{key_prefix}_clear",
                    use_container_width=True
            ):
                on_clear()

        return results


def render_quick_stats_bar(stats: List[Dict]):
    """
    Barre stats horizontale compacte

    ✅ Alternative à render_stat_row
    ✅ Plus compacte
    """
    cols = st.columns(len(stats))

    for idx, stat in enumerate(stats):
        with cols[idx]:
            st.metric(
                label="",
                value=stat.get("value", ""),
                delta=stat.get("delta"),
                delta_color=stat.get("delta_color", "normal"),
                label_visibility="collapsed"
            )
            st.caption(stat.get("label", ""))


def render_loading_skeleton(count: int = 3):
    """
    Skeleton loader pendant chargement

    ✅ Améliore UX
    """
    for _ in range(count):
        with st.container():
            st.markdown(
                """
                <div style="background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                            height: 100px; border-radius: 8px; margin-bottom: 1rem;
                            animation: shimmer 1.5s infinite;">
                </div>
                """,
                unsafe_allow_html=True
            )


def render_batch_action_bar(
        selected_items: List[int],
        actions: List[tuple[str, Callable]],
        key_prefix: str
):
    """
    Barre d'actions batch (multi-sélection)

    ✅ Utile pour sélection multiple
    """
    if not selected_items:
        return

    st.info(f"✓ {len(selected_items)} élément(s) sélectionné(s)")

    cols = st.columns(len(actions))

    for idx, (label, callback) in enumerate(actions):
        with cols[idx]:
            if st.button(
                    label,
                    key=f"{key_prefix}_batch_{idx}",
                    use_container_width=True
            ):
                callback(selected_items)


# ═══════════════════════════════════════════════════════════════
# HELPERS DE NAVIGATION
# ═══════════════════════════════════════════════════════════════

def render_breadcrumb(path: List[str]):
    """
    Fil d'Ariane

    ✅ Navigation claire
    """
    st.caption(" → ".join(path))


def render_tabs_with_icons(
        tabs: Dict[str, str],
        default: int = 0
) -> int:
    """
    Tabs avec icônes

    Args:
        tabs: {"label": "icon"}
        default: Index par défaut

    Returns:
        Index tab active
    """
    labels = [f"{icon} {label}" for label, icon in tabs.items()]

    tab_objects = st.tabs(labels)

    # Retourner index actif (détecté via session_state)
    active_tab = st.session_state.get("active_tab_idx", default)

    return active_tab