"""
UI Components - Data
Pagination, métriques, export
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    import pandas as pd


def pagination(
    total_items: int, items_per_page: int = 20, key: str = "pagination"
) -> tuple[int, int]:
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
            label_visibility="collapsed",
        )

    with col3:
        if st.button("Suiv ➡️", key=f"{key}_next"):
            st.session_state[f"{key}_page"] = min(total_pages, page + 1)
            st.rerun()

    current_page = st.session_state[f"{key}_page"]
    st.caption(f"Page {current_page}/{total_pages} • {total_items} élément(s)")

    return current_page, items_per_page


def ligne_metriques(stats: list[dict], cols: int | None = None):
    """
    Ligne de métriques

    Args:
        stats: Liste de stats [{label, value, delta}]
        cols: Nombre de colonnes (auto si None)

    Example:
        ligne_metriques([
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
                label=stat.get("label", ""), value=stat.get("value", ""), delta=stat.get("delta")
            )


def boutons_export(
    data: list[dict] | pd.DataFrame,
    nom_fichier: str = "export",
    formats: list[str] | None = None,
    cle: str = "export",
):
    """
    Boutons d'export

    Args:
        data: Données (list ou DataFrame)
        nom_fichier: Nom fichier (sans extension)
        formats: Formats disponibles
        cle: Clé unique

    Example:
        boutons_export(items, "recettes", ["csv", "json"], "recipes_export")
    """
    import pandas as pd  # Lazy load

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    formats = formats or ["csv", "json"]

    cols = st.columns(len(formats))

    for idx, fmt in enumerate(formats):
        with cols[idx]:
            if fmt == "csv":
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 CSV",
                    csv,
                    f"{nom_fichier}.csv",
                    "text/csv",
                    key=f"{cle}_csv",
                    use_container_width=True,
                )

            elif fmt == "json":
                json_str = df.to_json(orient="records", indent=2)
                st.download_button(
                    "📥 JSON",
                    json_str,
                    f"{nom_fichier}.json",
                    "application/json",
                    key=f"{cle}_json",
                    use_container_width=True,
                )


def tableau_donnees(data: list[dict] | pd.DataFrame, cle: str = "table"):
    """
    Tableau de données interactif

    Args:
        data: Données
        cle: Clé unique

    Example:
        tableau_donnees(recipes, "recipes_table")
    """
    import pandas as pd  # Lazy load

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data

    st.dataframe(df, width="stretch", key=cle)


def barre_progression(valeur: float, label: str = "", cle: str = "progress"):
    """
    Barre de progression

    Args:
        valeur: Valeur (0.0 - 1.0)
        label: Label
        cle: Clé unique

    Example:
        barre_progression(0.75, "Progression", "import_progress")
    """
    if label:
        st.markdown(f"**{label}**")

    st.progress(valeur, key=cle)
