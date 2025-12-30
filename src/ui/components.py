"""
UI Components - Tout-en-un
Fusion de 5 fichiers en 1 (~800 lignes bien organisées)
"""
import streamlit as st
from typing import List, Dict, Optional, Callable, Any, Union
from datetime import date, time, datetime
import pandas as pd


# ═══════════════════════════════════════════════════════════════
# SECTION 1 : COMPOSANTS ATOMIQUES
# ═══════════════════════════════════════════════════════════════

def badge(text: str, color: str = "#4CAF50"):
    """Badge coloré"""
    st.markdown(
        f'<span style="background: {color}; color: white; '
        f'padding: 0.25rem 0.75rem; border-radius: 12px; '
        f'font-size: 0.875rem; font-weight: 600;">{text}</span>',
        unsafe_allow_html=True
    )

def metric_card(label: str, value: Any, delta: Optional[Any] = None, icon: Optional[str] = None):
    """Carte métrique"""
    display_label = f"{icon} {label}" if icon else label
    st.metric(label=display_label, value=value, delta=delta)

def empty_state(message: str, icon: str = "📭", subtext: Optional[str] = None):
    """État vide centré"""
    st.markdown(
        f'<div style="text-align: center; padding: 3rem; color: #6c757d;">'
        f'<div style="font-size: 4rem;">{icon}</div>'
        f'<div style="font-size: 1.5rem; margin-top: 1rem; font-weight: 500;">{message}</div>'
        f'{f"<div style=\"font-size: 1rem; margin-top: 0.5rem;\">{subtext}</div>" if subtext else ""}'
        f'</div>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
# SECTION 2 : FORMULAIRES
# ═══════════════════════════════════════════════════════════════

def form_field(field_config: Dict, key_prefix: str) -> Any:
    """Champ de formulaire générique"""
    field_type = field_config.get("type", "text")
    name = field_config.get("name", "field")
    label = field_config.get("label", name)
    required = field_config.get("required", False)
    key = f"{key_prefix}_{name}"

    if required:
        label = f"{label} *"

    if field_type == "text":
        return st.text_input(label, value=field_config.get("default", ""), key=key)
    elif field_type == "number":
        return st.number_input(
            label,
            value=float(field_config.get("default", 0)),
            min_value=field_config.get("min"),
            max_value=field_config.get("max"),
            step=field_config.get("step", 1),
            key=key
        )
    elif field_type == "select":
        return st.selectbox(label, field_config.get("options", []), key=key)
    elif field_type == "checkbox":
        return st.checkbox(label, value=field_config.get("default", False), key=key)
    elif field_type == "textarea":
        return st.text_area(label, value=field_config.get("default", ""), key=key)
    elif field_type == "date":
        return st.date_input(label, value=field_config.get("default", date.today()), key=key)
    else:
        return st.text_input(label, key=key)

def search_bar(placeholder: str = "Rechercher...", key: str = "search") -> str:
    """Barre de recherche"""
    return st.text_input("", placeholder=f"🔍 {placeholder}", key=key, label_visibility="collapsed")

def filter_panel(filters_config: Dict[str, Dict], key_prefix: str) -> Dict:
    """Panneau de filtres"""
    with st.expander("🔍 Filtres", expanded=False):
        results = {}
        for filter_name, config in filters_config.items():
            results[filter_name] = form_field({**config, "name": filter_name}, key_prefix)
        return results


# ═══════════════════════════════════════════════════════════════
# SECTION 3 : FEEDBACK
# ═══════════════════════════════════════════════════════════════

def toast(message: str, type: str = "success"):
    """Toast notification"""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)

class Modal:
    """Modal simple"""
    def __init__(self, key: str):
        self.key = f"modal_{key}"
        if self.key not in st.session_state:
            st.session_state[self.key] = False

    def show(self):
        st.session_state[self.key] = True

    def close(self):
        st.session_state[self.key] = False
        st.rerun()

    def is_showing(self) -> bool:
        return st.session_state.get(self.key, False)

    def confirm(self, label: str = "✅ Confirmer") -> bool:
        return st.button(label, key=f"{self.key}_yes", type="primary", use_container_width=True)

    def cancel(self, label: str = "❌ Annuler"):
        if st.button(label, key=f"{self.key}_no", use_container_width=True):
            self.close()


# ═══════════════════════════════════════════════════════════════
# SECTION 4 : DATA & TABLES
# ═══════════════════════════════════════════════════════════════

def pagination(total_items: int, items_per_page: int = 20, key: str = "pagination") -> tuple[int, int]:
    """Pagination simple"""
    if total_items <= items_per_page:
        return 1, items_per_page

    total_pages = (total_items + items_per_page - 1) // items_per_page

    if f"{key}_page" not in st.session_state:
        st.session_state[f"{key}_page"] = 1

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Préc", key=f"{key}_prev"):
            st.session_state[f"{key}_page"] = max(1, st.session_state[f"{key}_page"] - 1)
            st.rerun()

    with col2:
        page = st.selectbox(
            "Page",
            options=list(range(1, total_pages + 1)),
            index=st.session_state[f"{key}_page"] - 1,
            key=f"{key}_select",
            label_visibility="collapsed"
        )

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next"):
            st.session_state[f"{key}_page"] = min(total_pages, page + 1)
            st.rerun()

    current_page = st.session_state[f"{key}_page"]
    st.caption(f"Page {current_page}/{total_pages} • {total_items} élément(s)")
    return current_page, items_per_page

def metrics_row(stats: List[Dict], cols: Optional[int] = None):
    """Ligne de métriques"""
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
                delta=stat.get("delta")
            )

def export_buttons(data: Union[List[Dict], pd.DataFrame], filename: str = "export",
                   formats: List[str] = ["csv", "json"], key: str = "export"):
    """Boutons d'export"""
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    cols = st.columns(len(formats))

    for idx, fmt in enumerate(formats):
        with cols[idx]:
            if fmt == "csv":
                csv = df.to_csv(index=False)
                st.download_button("📥 CSV", csv, f"{filename}.csv", "text/csv", key=f"{key}_csv", use_container_width=True)
            elif fmt == "json":
                json_str = df.to_json(orient='records', indent=2)
                st.download_button("📥 JSON", json_str, f"{filename}.json", "application/json", key=f"{key}_json", use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 5 : LAYOUTS
# ═══════════════════════════════════════════════════════════════

def grid_layout(items: List[Dict], cols_per_row: int = 3, card_renderer: Callable[[Dict, str], None] = None, key: str = "grid"):
    """Layout en grille"""
    if not items:
        st.info("Aucun élément")
        return

    for row_idx in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            item_idx = row_idx + col_idx
            if item_idx < len(items):
                with cols[col_idx]:
                    if card_renderer:
                        card_renderer(items[item_idx], f"{key}_{item_idx}")
                    else:
                        st.write(items[item_idx])

def item_card(title: str, metadata: List[str], status: Optional[str] = None,
              status_color: Optional[str] = None, tags: Optional[List[str]] = None,
              image_url: Optional[str] = None, actions: Optional[List[tuple]] = None, key: str = "item"):
    """Carte item universelle"""
    border_color = status_color or "#e2e8e5"

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {border_color}; padding: 1rem; '
            f'background: #f8f9fa; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        if image_url:
            col_img, col_content = st.columns([1, 4])
            with col_img:
                st.image(image_url, use_container_width=True)
            content_col = col_content
        else:
            content_col = st.container()

        with content_col:
            if status:
                col_title, col_status = st.columns([3, 1])
                with col_title:
                    st.markdown(f"### {title}")
                with col_status:
                    st.markdown(
                        f'<div style="text-align: right; color: {status_color or "#6c757d"}; '
                        f'font-weight: 600;">{status}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f"### {title}")

            if metadata:
                st.caption(" • ".join(metadata))

            if tags:
                tag_html = " ".join([
                    f'<span style="background: #e7f3ff; padding: 0.25rem 0.5rem; '
                    f'border-radius: 12px; font-size: 0.875rem;">{tag}</span>'
                    for tag in tags
                ])
                st.markdown(tag_html, unsafe_allow_html=True)

        if actions:
            cols = st.columns(len(actions))
            for idx, (label, callback) in enumerate(actions):
                with cols[idx]:
                    if st.button(label, key=f"{key}_action_{idx}", use_container_width=True):
                        callback()
