"""
UI Components - Data
Pagination, métriques, export
"""
import streamlit as st
from typing import List, Dict, Union, Optional
import pandas as pd


def pagination(total_items: int, items_per_page: int = 20, key: str = "pagination") -> tuple[int, int]:
    """
    Pagination simple

    Args:
        total_items: Nombre total d'items
        items_per_page: Items par page
        key: Clé unique

    Returns:
        (page_courante, items_per_page)

    Example:
        page, per_page = pagination(100, 20, "recipes")
    """
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
    """
    Ligne de métriques

    Args:
        stats: Liste de stats [{label, value, delta}]
        cols: Nombre de colonnes (auto si None)

    Example:
        metrics_row([
            {"label": "Total", "value": 42, "delta": "+5"},
            {"label": "Actifs", "value": 38}
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
                delta=stat.get("delta")
            )


def export_buttons(
        data: Union[List[Dict], pd.DataFrame],
        filename: str = "export",
        formats: List[str] = ["csv", "json"],
        key: str = "export"
):
    """
    Boutons d'export

    Args:
        data: Données (list ou DataFrame)
        filename: Nom fichier (sans extension)
        formats: Formats disponibles
        key: Clé unique

    Example:
        export_buttons(items, "recettes", ["csv", "json"], "recipes_export")
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    cols = st.columns(len(formats))

    for idx, fmt in enumerate(formats):
        with cols[idx]:
            if fmt == "csv":
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 CSV",
                    csv,
                    f"{filename}.csv",
                    "text/csv",
                    key=f"{key}_csv",
                    use_container_width=True
                )

            elif fmt == "json":
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(
                    "📥 JSON",
                    json_str,
                    f"{filename}.json",
                    "application/json",
                    key=f"{key}_json",
                    use_container_width=True
                )


def data_table(data: Union[List[Dict], pd.DataFrame], key: str = "table"):
    """
    Tableau de données interactif

    Args:
        data: Données
        key: Clé unique

    Example:
        data_table(recipes, "recipes_table")
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    st.dataframe(
        df,
        use_container_width=True,
        key=key
    )


def progress_bar(value: float, label: str = "", key: str = "progress"):
    """
    Barre de progression

    Args:
        value: Valeur (0.0 - 1.0)
        label: Label
        key: Clé unique

    Example:
        progress_bar(0.75, "Progression", "import_progress")
    """
    if label:
        st.markdown(f"**{label}**")

    st.progress(value, key=key)


def status_indicator(status: str, label: str = ""):
    """
    Indicateur de statut (LED)

    Args:
        status: "success", "warning", "error", "info"
        label: Label

    Example:
        status_indicator("success", "Connecté")
    """
    colors = {
        "success": "#4CAF50",
        "warning": "#FFC107",
        "error": "#f44336",
        "info": "#2196F3"
    }

    color = colors.get(status, "#gray")

    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 0.5rem;">'
        f'<div style="width: 12px; height: 12px; background: {color}; '
        f'border-radius: 50%; box-shadow: 0 0 8px {color};"></div>'
        f'<span>{label}</span>'
        f'</div>',
        unsafe_allow_html=True
    )