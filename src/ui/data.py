"""
Composants Données
Tables, pagination, recherche avancée
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Callable, Union, Any


# ═══════════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════════

def pagination(
        total_items: int,
        items_per_page: int = 20,
        key: str = "pagination"
) -> tuple[int, int]:
    """
    Pagination simple

    Args:
        total_items: Nombre total d'items
        items_per_page: Items par page
        key: Clé unique

    Returns:
        (page_actuelle, items_per_page)
    """
    if total_items <= items_per_page:
        return 1, items_per_page

    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Init page
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

        if page != st.session_state[f"{key}_page"]:
            st.session_state[f"{key}_page"] = page
            st.rerun()

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next"):
            st.session_state[f"{key}_page"] = min(total_pages, page + 1)
            st.rerun()

    current_page = st.session_state[f"{key}_page"]
    st.caption(f"Page {current_page}/{total_pages} • {total_items} élément(s)")

    return current_page, items_per_page


# ═══════════════════════════════════════════════════════════════
# TABLEAUX
# ═══════════════════════════════════════════════════════════════

def data_table(
        data: Union[List[Dict], pd.DataFrame],
        columns: Optional[List[str]] = None,
        sortable: bool = True,
        searchable: bool = True,
        actions: Optional[List[Dict]] = None,
        key: str = "table"
):
    """
    Tableau de données interactif

    Args:
        data: Données (liste dicts ou DataFrame)
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
    # Conversion en DataFrame
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
            mask = df.astype(str).apply(
                lambda x: x.str.contains(search, case=False, na=False)
            ).any(axis=1)
            df = df[mask]

    # Colonnes
    if columns:
        df = df[columns]

    # Affichage
    st.dataframe(df, use_container_width=True)

    # Actions
    if actions and not df.empty:
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


def simple_table(
        headers: List[str],
        rows: List[List[Any]],
        key: str = "simple_table"
):
    """
    Tableau simple (sans pandas)

    Args:
        headers: En-têtes
        rows: Lignes de données
        key: Clé unique
    """
    # Construction HTML
    table_html = '<table style="width:100%; border-collapse: collapse;">'

    # Headers
    table_html += '<tr style="background: #f5f5f5;">'
    for header in headers:
        table_html += f'<th style="padding: 0.5rem; border: 1px solid #ddd; text-align: left;">{header}</th>'
    table_html += '</tr>'

    # Rows
    for row in rows:
        table_html += '<tr>'
        for cell in row:
            table_html += f'<td style="padding: 0.5rem; border: 1px solid #ddd;">{cell}</td>'
        table_html += '</tr>'

    table_html += '</table>'

    st.markdown(table_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# METRICS & STATS
# ═══════════════════════════════════════════════════════════════

def metrics_row(stats: List[Dict], cols: Optional[int] = None):
    """
    Ligne de métriques

    Args:
        stats: [{"label": str, "value": Any, "delta": Any}]
        cols: Nombre de colonnes (auto si None)
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


def stat_cards(stats: List[Dict], cols: int = 3):
    """
    Cartes statistiques

    Args:
        stats: [{
            "label": str,
            "value": Any,
            "icon": str,
            "color": str
        }]
        cols: Nombre de colonnes
    """
    columns = st.columns(cols)

    for idx, stat in enumerate(stats):
        col_idx = idx % cols

        with columns[col_idx]:
            icon = stat.get("icon", "📊")
            color = stat.get("color", "#4CAF50")

            st.markdown(
                f"""
                <div style="background: {color}15; border-left: 4px solid {color}; 
                            padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="font-size: 2rem;">{icon}</div>
                    <div style="font-size: 2rem; font-weight: 600; margin-top: 0.5rem;">
                        {stat.get("value", "")}
                    </div>
                    <div style="color: #6c757d; font-size: 0.875rem;">
                        {stat.get("label", "")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════════════════
# RECHERCHE AVANCÉE
# ═══════════════════════════════════════════════════════════════

def advanced_search(
        data: Union[List[Dict], pd.DataFrame],
        search_fields: List[str],
        filters_config: Optional[Dict] = None,
        key: str = "adv_search"
) -> Union[List[Dict], pd.DataFrame]:
    """
    Recherche avancée avec filtres multiples

    Args:
        data: Données à rechercher
        search_fields: Champs de recherche
        filters_config: Config des filtres (voir filter_panel)
        key: Clé unique

    Returns:
        Données filtrées
    """
    # Conversion DataFrame si nécessaire
    is_list = isinstance(data, list)
    if is_list:
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    col1, col2 = st.columns([2, 1])

    with col1:
        # Recherche texte
        search = st.text_input("🔍 Rechercher", key=f"{key}_text")

        if search:
            mask = pd.Series([False] * len(df))
            for field in search_fields:
                if field in df.columns:
                    mask |= df[field].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]

    with col2:
        # Filtres
        if filters_config:
            with st.expander("🔧 Filtres"):
                for filter_name, config in filters_config.items():
                    field_type = config.get("type", "select")

                    if field_type == "select" and filter_name in df.columns:
                        options = ["Tous"] + sorted(df[filter_name].unique().tolist())
                        selected = st.selectbox(
                            config.get("label", filter_name),
                            options,
                            key=f"{key}_filter_{filter_name}"
                        )

                        if selected != "Tous":
                            df = df[df[filter_name] == selected]

    # Retour dans le format original
    if is_list:
        return df.to_dict('records')
    return df


# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════

def export_buttons(
        data: Union[List[Dict], pd.DataFrame],
        filename: str = "export",
        formats: List[str] = ["csv", "json"],
        key: str = "export"
):
    """
    Boutons d'export de données

    Args:
        data: Données à exporter
        filename: Nom du fichier (sans extension)
        formats: ["csv", "json", "excel"]
        key: Clé unique
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