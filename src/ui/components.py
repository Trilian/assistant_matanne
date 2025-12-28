"""
Composants UI de Base
Composants simples et réutilisables pour toute l'application
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any, Union
from datetime import date, datetime
import pandas as pd


# ═══════════════════════════════════════════════════════════════
# AFFICHAGE DE BASE
# ═══════════════════════════════════════════════════════════════

def render_stat_row(stats: List[Dict], cols: int = None):
    """
    Ligne de statistiques avec métriques

    Args:
        stats: [{"label": str, "value": Any, "delta": Any, "delta_color": str}]
        cols: Nombre de colonnes (auto si None)

    Usage:
        render_stat_row([
            {"label": "Total", "value": 150},
            {"label": "Nouveaux", "value": 12, "delta": "+3", "delta_color": "normal"}
        ])
    """
    if not stats:
        return

    cols_count = cols or len(stats)
    columns = st.columns(cols_count)

    for idx, stat in enumerate(stats):
        if idx >= len(columns):
            break

        with columns[idx]:
            st.metric(
                label=stat.get("label", ""),
                value=stat.get("value", ""),
                delta=stat.get("delta"),
                delta_color=stat.get("delta_color", "normal")
            )


def render_badge(text: str, color: str = "#4CAF50"):
    """
    Badge coloré

    Usage:
        render_badge("✅ Actif", "#28a745")
    """
    st.markdown(
        f'<span style="background: {color}; color: white; '
        f'padding: 0.25rem 0.75rem; border-radius: 12px; '
        f'font-size: 0.875rem; font-weight: 600;">{text}</span>',
        unsafe_allow_html=True
    )


def render_progress_bar(
        value: float,
        max_value: float = 100,
        label: Optional[str] = None,
        color: str = "#4CAF50"
):
    """
    Barre de progression personnalisée

    Args:
        value: Valeur actuelle
        max_value: Valeur maximale
        label: Label optionnel
        color: Couleur de la barre

    Usage:
        render_progress_bar(75, 100, "Progression", "#2196F3")
    """
    percentage = min(100, (value / max_value) * 100)

    if label:
        st.caption(f"{label}: {value}/{max_value}")

    st.markdown(
        f"""
        <div style="background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
            <div style="background: {color}; width: {percentage}%; height: 100%; 
                        transition: width 0.3s; display: flex; align-items: center; 
                        justify-content: center; color: white; font-size: 0.75rem; font-weight: bold;">
                {percentage:.0f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_card(
        title: str,
        content: Callable,
        icon: Optional[str] = None,
        color: str = "#ffffff",
        border_color: str = "#e2e8e5"
):
    """
    Carte avec contenu personnalisé

    Args:
        title: Titre de la carte
        content: Fonction qui rend le contenu
        icon: Emoji ou icône optionnel
        color: Couleur de fond
        border_color: Couleur de la bordure

    Usage:
        render_card(
            "📊 Statistiques",
            lambda: st.write("Contenu..."),
            color="#f8f9fa"
        )
    """
    st.markdown(
        f"""
        <div style="background: {color}; border: 1px solid {border_color}; 
                    border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        title_display = f"{icon} {title}" if icon else title
        st.markdown(f"### {title_display}")
        content()


# ═══════════════════════════════════════════════════════════════
# RECHERCHE & FILTRES
# ═══════════════════════════════════════════════════════════════

def render_search_bar(
        placeholder: str = "Rechercher...",
        key: str = "search",
        icon: str = "🔍"
) -> str:
    """
    Barre de recherche simple

    Returns:
        Terme de recherche
    """
    return st.text_input(
        "",
        placeholder=f"{icon} {placeholder}",
        key=key,
        label_visibility="collapsed"
    )


def render_filter_panel(
        filters_config: Dict[str, Dict],
        key_prefix: str
) -> Dict:
    """
    Panneau de filtres dans expander

    Args:
        filters_config: {
            "filter_name": {
                "type": "select|checkbox|slider|text|date|multiselect",
                "label": str,
                "options": List (pour select/multiselect),
                "default": Any,
                "min/max/step": int (pour slider)
            }
        }
        key_prefix: Préfixe pour clés Streamlit

    Returns:
        Dict des valeurs de filtres
    """
    with st.expander("🔍 Filtres", expanded=False):
        results = {}

        for filter_name, config in filters_config.items():
            filter_type = config.get("type", "text")
            label = config.get("label", filter_name)
            key = f"{key_prefix}_filter_{filter_name}"

            if filter_type == "select":
                results[filter_name] = st.selectbox(
                    label,
                    options=config.get("options", []),
                    index=config.get("default", 0),
                    key=key
                )

            elif filter_type == "multiselect":
                results[filter_name] = st.multiselect(
                    label,
                    options=config.get("options", []),
                    default=config.get("default", []),
                    key=key
                )

            elif filter_type == "checkbox":
                results[filter_name] = st.checkbox(
                    label,
                    value=config.get("default", False),
                    key=key
                )

            elif filter_type == "slider":
                results[filter_name] = st.slider(
                    label,
                    min_value=config.get("min", 0),
                    max_value=config.get("max", 100),
                    value=config.get("default", 50),
                    step=config.get("step", 1),
                    key=key
                )

            elif filter_type == "date":
                results[filter_name] = st.date_input(
                    label,
                    value=config.get("default", date.today()),
                    key=key
                )

            elif filter_type == "text":
                results[filter_name] = st.text_input(
                    label,
                    value=config.get("default", ""),
                    key=key
                )

        return results


# ═══════════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════════

def render_pagination(
        total_items: int,
        items_per_page: int = 20,
        key: str = "pagination"
) -> tuple[int, int]:
    """
    Pagination simple

    Returns:
        (page_actuelle, items_per_page)
    """
    if total_items <= items_per_page:
        return 1, items_per_page

    total_pages = (total_items + items_per_page - 1) // items_per_page

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Préc", key=f"{key}_prev", disabled=st.session_state.get(f"{key}_page", 1) <= 1):
            st.session_state[f"{key}_page"] = max(1, st.session_state.get(f"{key}_page", 1) - 1)
            st.rerun()

    with col2:
        page = st.selectbox(
            "Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state.get(f"{key}_page", 1) - 1,
            key=f"{key}_select",
            label_visibility="collapsed"
        )

        if page != st.session_state.get(f"{key}_page", 1):
            st.session_state[f"{key}_page"] = page
            st.rerun()

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next", disabled=page >= total_pages):
            st.session_state[f"{key}_page"] = min(total_pages, page + 1)
            st.rerun()

    current_page = st.session_state.get(f"{key}_page", 1)
    st.caption(f"Page {current_page}/{total_pages} • {total_items} élément(s)")

    return current_page, items_per_page


# ═══════════════════════════════════════════════════════════════
# ÉTATS VIDES
# ═══════════════════════════════════════════════════════════════

def render_empty_state(
        message: str,
        icon: str = "📭",
        action_label: Optional[str] = None,
        action_callback: Optional[Callable] = None,
        key: str = "empty"
):
    """
    État vide avec action optionnelle

    Usage:
        render_empty_state(
            "Aucune recette",
            "🍽️",
            "➕ Ajouter",
            lambda: navigate("recettes.ajout")
        )
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 3rem; color: #6c757d;">
            <div style="font-size: 4rem;">{icon}</div>
            <div style="font-size: 1.5rem; margin-top: 1rem;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, key=f"{key}_action", type="primary", use_container_width=True):
                action_callback()


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS & FEEDBACK
# ═══════════════════════════════════════════════════════════════

def render_toast(message: str, type: str = "success", duration: int = 3):
    """
    Toast notification

    Args:
        message: Message à afficher
        type: success|error|warning|info
        duration: Durée en secondes (non utilisé avec st standard)
    """
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def render_confirmation_dialog(
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_label: str = "✅ Confirmer",
        cancel_label: str = "❌ Annuler",
        key: str = "confirm"
) -> bool:
    """
    Dialogue de confirmation

    Returns:
        True si confirmé

    Usage:
        if render_confirmation_dialog(
            "Supprimer cette recette ?",
            on_confirm=lambda: delete_recipe(id)
        ):
            st.success("Supprimé !")
    """
    st.warning(message)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(confirm_label, key=f"{key}_yes", type="primary", use_container_width=True):
            on_confirm()
            return True

    with col2:
        if st.button(cancel_label, key=f"{key}_no", use_container_width=True):
            if on_cancel:
                on_cancel()
            return False

    return False


# ═══════════════════════════════════════════════════════════════
# ACTIONS RAPIDES
# ═══════════════════════════════════════════════════════════════

def quick_action_bar(actions: List[tuple[str, Callable]], key_prefix: str = "action"):
    """
    Barre d'actions horizontale

    Args:
        actions: [(label, callback)]
        key_prefix: Préfixe pour clés

    Usage:
        quick_action_bar([
            ("🗑️ Nettoyer", cleanup),
            ("📤 Exporter", export)
        ])
    """
    if not actions:
        return

    cols = st.columns(len(actions))

    for idx, (label, callback) in enumerate(actions):
        with cols[idx]:
            if st.button(label, key=f"{key_prefix}_{idx}", use_container_width=True):
                callback()


def render_action_buttons(
        actions: List[Dict[str, Any]],
        layout: str = "horizontal",
        key_prefix: str = "btn"
):
    """
    Boutons d'action configurables

    Args:
        actions: [
            {
                "label": str,
                "callback": Callable,
                "type": "primary|secondary",
                "icon": str,
                "disabled": bool
            }
        ]
        layout: "horizontal" ou "vertical"
        key_prefix: Préfixe pour clés

    Usage:
        render_action_buttons([
            {
                "label": "Enregistrer",
                "callback": save,
                "type": "primary",
                "icon": "💾"
            },
            {
                "label": "Annuler",
                "callback": cancel
            }
        ])
    """
    if layout == "horizontal":
        cols = st.columns(len(actions))
        containers = cols
    else:
        containers = [st.container() for _ in actions]

    for idx, (container, action) in enumerate(zip(containers, actions)):
        with container:
            label = action.get("label", "Action")
            icon = action.get("icon", "")
            display_label = f"{icon} {label}" if icon else label

            if st.button(
                    display_label,
                    key=f"{key_prefix}_{idx}",
                    type=action.get("type", "secondary"),
                    disabled=action.get("disabled", False),
                    use_container_width=True
            ):
                callback = action.get("callback")
                if callback:
                    callback()


# ═══════════════════════════════════════════════════════════════
# HELPERS AFFICHAGE
# ═══════════════════════════════════════════════════════════════

def render_collapsible_section(
        title: str,
        content: Callable,
        icon: str = "📋",
        expanded: bool = False,
        key: Optional[str] = None
):
    """
    Section collapsible standardisée

    Usage:
        render_collapsible_section(
            "Détails",
            lambda: st.write("Contenu..."),
            icon="👁️"
        )
    """
    with st.expander(f"{icon} {title}", expanded=expanded):
        content()


def render_info_box(
        message: str,
        type: str = "info",
        icon: Optional[str] = None,
        dismissible: bool = False,
        key: str = "info"
):
    """
    Boîte d'information

    Args:
        message: Message
        type: info|success|warning|error
        icon: Icône personnalisée
        dismissible: Peut être fermée
        key: Clé unique
    """
    if dismissible and st.session_state.get(f"{key}_dismissed"):
        return

    icon_map = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }

    display_icon = icon or icon_map.get(type, "ℹ️")

    if type == "success":
        container = st.success
    elif type == "warning":
        container = st.warning
    elif type == "error":
        container = st.error
    else:
        container = st.info

    col1, col2 = st.columns([10, 1]) if dismissible else (st.container(), None)

    with col1:
        container(f"{display_icon} {message}")

    if dismissible and col2:
        with col2:
            if st.button("✕", key=f"{key}_dismiss"):
                st.session_state[f"{key}_dismissed"] = True
                st.rerun()


def render_divider(text: Optional[str] = None, color: str = "#e0e0e0"):
    """
    Séparateur avec texte optionnel

    Usage:
        render_divider("OU")
    """
    if text:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin: 1rem 0;">
                <div style="flex: 1; height: 1px; background: {color};"></div>
                <div style="padding: 0 1rem; color: #6c757d; font-weight: 500;">{text}</div>
                <div style="flex: 1; height: 1px; background: {color};"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(f'<hr style="border: none; border-top: 1px solid {color}; margin: 1rem 0;">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# FORMULAIRES
# ═══════════════════════════════════════════════════════════════

def render_form_field(
        field_config: Dict,
        key_prefix: str
) -> Any:
    """
    Champ de formulaire générique

    Args:
        field_config: {
            "type": "text|number|select|checkbox|textarea|date",
            "label": str,
            "default": Any,
            "required": bool,
            "help": str,
            "options": List (pour select)
        }
        key_prefix: Préfixe pour la clé

    Returns:
        Valeur du champ
    """
    field_type = field_config.get("type", "text")
    label = field_config.get("label", "Champ")
    required = field_config.get("required", False)
    help_text = field_config.get("help")
    key = f"{key_prefix}_{field_config.get('name', 'field')}"

    if required:
        label = f"{label} *"

    if field_type == "text":
        return st.text_input(
            label,
            value=field_config.get("default", ""),
            help=help_text,
            key=key
        )

    elif field_type == "number":
        return st.number_input(
            label,
            value=field_config.get("default", 0),
            min_value=field_config.get("min"),
            max_value=field_config.get("max"),
            step=field_config.get("step", 1),
            help=help_text,
            key=key
        )

    elif field_type == "select":
        return st.selectbox(
            label,
            options=field_config.get("options", []),
            index=field_config.get("default", 0),
            help=help_text,
            key=key
        )

    elif field_type == "checkbox":
        return st.checkbox(
            label,
            value=field_config.get("default", False),
            help=help_text,
            key=key
        )

    elif field_type == "textarea":
        return st.text_area(
            label,
            value=field_config.get("default", ""),
            height=field_config.get("height", 100),
            help=help_text,
            key=key
        )

    elif field_type == "date":
        return st.date_input(
            label,
            value=field_config.get("default", date.today()),
            help=help_text,
            key=key
        )


# ═══════════════════════════════════════════════════════════════
# TABLEAUX
# ═══════════════════════════════════════════════════════════════

def render_data_table(
        data: Union[List[Dict], pd.DataFrame],
        columns: Optional[List[str]] = None,
        sortable: bool = True,
        searchable: bool = True,
        actions: Optional[List[Dict]] = None,
        key: str = "table"
):
    """
    Tableau de données avec recherche et actions

    Args:
        data: Données (liste de dicts ou DataFrame)
        columns: Colonnes à afficher (None = toutes)
        sortable: Permet le tri
        searchable: Barre de recherche
        actions: Actions par ligne [{
            "label": str,
            "callback": Callable(row),
            "icon": str
        }]
        key: Clé unique
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    if df.empty:
        st.info("Aucune donnée")
        return

    # Recherche
    if searchable:
        search = st.text_input("🔍 Rechercher", key=f"{key}_search")
        if search:
            # Recherche dans toutes les colonnes string
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]

    # Colonnes à afficher
    if columns:
        df = df[columns]

    # Affichage
    if sortable:
        st.dataframe(df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    # Actions
    if actions:
        st.markdown("**Actions disponibles:**")
        for idx, row in df.iterrows():
            cols = st.columns(len(actions) + 1)

            with cols[0]:
                st.write(f"Ligne {idx + 1}")

            for action_idx, action in enumerate(actions):
                with cols[action_idx + 1]:
                    icon = action.get("icon", "")
                    label = f"{icon} {action['label']}" if icon else action['label']

                    if st.button(label, key=f"{key}_action_{idx}_{action_idx}"):
                        action["callback"](row)


# ═══════════════════════════════════════════════════════════════
# IMAGES
# ═══════════════════════════════════════════════════════════════

def render_image_with_fallback(
        image_url: Optional[str],
        fallback_icon: str = "🖼️",
        width: Optional[int] = None,
        caption: Optional[str] = None
):
    """
    Image avec fallback si URL invalide

    Args:
        image_url: URL de l'image
        fallback_icon: Emoji si pas d'image
        width: Largeur en pixels
        caption: Légende
    """
    if image_url:
        try:
            st.image(image_url, width=width, caption=caption, use_container_width=not width)
        except:
            st.markdown(
                f'<div style="text-align: center; font-size: 3rem; padding: 2rem; '
                f'background: #f5f5f5; border-radius: 8px;">{fallback_icon}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f'<div style="text-align: center; font-size: 3rem; padding: 2rem; '
            f'background: #f5f5f5; border-radius: 8px;">{fallback_icon}</div>',
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════
# DATES & TEMPS
# ═══════════════════════════════════════════════════════════════

def render_date_selector(
        label: str,
        default: Optional[date] = None,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        key: str = "date"
) -> date:
    """
    Sélecteur de date avec contraintes

    Returns:
        Date sélectionnée
    """
    return st.date_input(
        label,
        value=default or date.today(),
        min_value=min_date,
        max_value=max_date,
        key=key
    )


def render_time_range_selector(
        label: str,
        default_start: str = "08:00",
        default_end: str = "18:00",
        key: str = "time"
) -> tuple[str, str]:
    """
    Sélecteur de plage horaire

    Returns:
        (heure_debut, heure_fin)
    """
    st.markdown(f"**{label}**")

    col1, col2 = st.columns(2)

    with col1:
        start = st.time_input("Début", value=datetime.strptime(default_start, "%H:%M").time(), key=f"{key}_start")

    with col2:
        end = st.time_input("Fin", value=datetime.strptime(default_end, "%H:%M").time(), key=f"{key}_end")

    return start.strftime("%H:%M"), end.strftime("%H:%M")


# ═══════════════════════════════════════════════════════════════
# NAVIGATION & TABS
# ═══════════════════════════════════════════════════════════════

def render_breadcrumb(
        path: List[str],
        icons: Optional[List[str]] = None,
        on_click: Optional[List[Callable]] = None
):
    """
    Fil d'Ariane

    Args:
        path: ["Accueil", "Recettes", "Détails"]
        icons: ["🏠", "🍽️", "👁️"]
        on_click: [home_callback, recipes_callback, None]

    Usage:
        render_breadcrumb(
            ["Accueil", "Recettes", "Pizza"],
            ["🏠", "🍽️", "🍕"]
        )
    """
    breadcrumb_html = []

    for idx, item in enumerate(path):
        icon = icons[idx] if icons and idx < len(icons) else ""
        display = f"{icon} {item}" if icon else item

        if on_click and idx < len(on_click) and on_click[idx]:
            # Clickable (pas implémenté directement car st.markdown ne supporte pas onClick)
            breadcrumb_html.append(f'<span style="color: #2196F3; cursor: pointer;">{display}</span>')
        else:
            breadcrumb_html.append(f'<span>{display}</span>')

        if idx < len(path) - 1:
            breadcrumb_html.append('<span style="color: #6c757d; margin: 0 0.5rem;">→</span>')

    st.markdown(
        f'<div style="font-size: 0.875rem; color: #6c757d; margin-bottom: 1rem;">'
        f'{"".join(breadcrumb_html)}</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# LOADING & SPINNERS
# ═══════════════════════════════════════════════════════════════

def render_loading_spinner(
        message: str = "Chargement...",
        icon: str = "⏳"
):
    """
    Spinner de chargement

    Usage:
        render_loading_spinner("Génération en cours...")
    """
    st.markdown(
        f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 2rem; animation: pulse 2s infinite;">{icon}</div>
            <div style="margin-top: 1rem; color: #6c757d;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# HELPERS UTILITAIRES
# ═══════════════════════════════════════════════════════════════

def render_key_value_list(
        items: Dict[str, Any],
        title: Optional[str] = None,
        icon: Optional[str] = None
):
    """
    Liste clé-valeur

    Args:
        items: {"Nom": "Pizza", "Prix": "12€"}
        title: Titre optionnel
        icon: Icône optionnelle

    Usage:
        render_key_value_list({
            "Nom": "Pizza Margherita",
            "Prix": "12€",
            "Temps": "30min"
        }, "Informations", "📋")
    """
    if title:
        title_display = f"{icon} {title}" if icon else title
        st.markdown(f"**{title_display}**")

    for key, value in items.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.caption(key)
        with col2:
            st.write(value)


def render_countdown(
        target_date: date,
        label: str = "Jours restants",
        icon: str = "⏰"
):
    """
    Compte à rebours

    Args:
        target_date: Date cible
        label: Label
        icon: Icône

    Usage:
        render_countdown(date(2025, 12, 31), "Jours avant Noël", "🎄")
    """
    today = date.today()
    delta = (target_date - today).days

    if delta > 0:
        st.info(f"{icon} {label}: **{delta} jour(s)**")
    elif delta == 0:
        st.success(f"{icon} {label}: **Aujourd'hui !**")
    else:
        st.warning(f"{icon} {label}: **Dépassé de {abs(delta)} jour(s)**")