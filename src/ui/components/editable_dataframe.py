"""
Editable DataFrames — Innovation v11: st.dataframe avec édition inline.

Composants pour l'édition directe de données dans des tableaux interactifs.
Utilisé pour:
- Inventaire (modifier quantités, dates péremption)
- Listes de courses (cocher, modifier quantités)
- Planning repas (drag-drop, édition)

Usage:
    from src.ui.components.editable_dataframe import (
        inventaire_editable,
        courses_editable,
        planning_editable,
        DataFrameEditor,
    )

    # Inventaire avec édition quantités
    df_modifie = inventaire_editable(df_inventaire)
    if df_modifie is not None:
        sauvegarder_inventaire(df_modifie)

    # Liste de courses avec checkboxes
    df_courses = courses_editable(df_courses)

    # Éditeur générique
    editor = DataFrameEditor(
        df,
        editable_columns=["quantite", "prix"],
        column_config={"prix": st.column_config.NumberColumn("Prix €", format="%.2f")}
    )
    result = editor.render()
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Callable

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

__all__ = [
    "DataFrameEditor",
    "inventaire_editable",
    "courses_editable",
    "planning_editable",
    "table_editable_simple",
]


# ═══════════════════════════════════════════════════════════
# DATAFRAME EDITOR — Classe générique
# ═══════════════════════════════════════════════════════════


class DataFrameEditor:
    """Éditeur de DataFrame avancé avec st.data_editor.

    Fonctionnalités:
    - Configuration des colonnes (types, formats, validation)
    - Colonnes en lecture seule
    - Ajout/suppression de lignes
    - Callbacks sur modifications
    - Historique des changements
    - Validation avant sauvegarde

    Usage:
        editor = DataFrameEditor(
            df,
            editable_columns=["quantite", "prix"],
            key="mon_editeur"
        )
        editor.on_change(lambda df: save_to_db(df))
        result = editor.render()
    """

    def __init__(
        self,
        data: pd.DataFrame,
        *,
        key: str = "df_editor",
        editable_columns: list[str] | None = None,
        readonly_columns: list[str] | None = None,
        column_config: dict[str, Any] | None = None,
        hide_columns: list[str] | None = None,
        num_rows: str = "dynamic",  # "dynamic" ou "fixed"
        height: int | None = None,
        use_container_width: bool = True,
    ):
        """
        Args:
            data: DataFrame source
            key: Clé unique
            editable_columns: Colonnes éditables (None = toutes)
            readonly_columns: Colonnes en lecture seule
            column_config: Config des colonnes (st.column_config)
            hide_columns: Colonnes à masquer
            num_rows: "dynamic" permet ajout/suppression
            height: Hauteur fixe (pixels)
            use_container_width: Utiliser toute la largeur
        """
        self.data = data.copy()
        self.key = key
        self.editable_columns = editable_columns
        self.readonly_columns = readonly_columns or []
        self.column_config = column_config or {}
        self.hide_columns = hide_columns or []
        self.num_rows = num_rows
        self.height = height
        self.use_container_width = use_container_width

        self._on_change_callbacks: list[Callable[[pd.DataFrame], None]] = []
        self._validators: list[Callable[[pd.DataFrame], tuple[bool, str]]] = []

    def on_change(self, callback: Callable[[pd.DataFrame], None]) -> DataFrameEditor:
        """Ajoute un callback sur modification.

        Args:
            callback: Fonction appelée avec le DataFrame modifié

        Returns:
            self pour chaînage
        """
        self._on_change_callbacks.append(callback)
        return self

    def add_validator(
        self, validator: Callable[[pd.DataFrame], tuple[bool, str]]
    ) -> DataFrameEditor:
        """Ajoute un validateur.

        Args:
            validator: Fonction(df) -> (is_valid, message)

        Returns:
            self pour chaînage
        """
        self._validators.append(validator)
        return self

    def _build_column_config(self) -> dict[str, Any]:
        """Construit la configuration des colonnes."""
        config = {}

        for col in self.data.columns:
            # Colonnes cachées
            if col in self.hide_columns:
                config[col] = None
                continue

            # Colonnes en lecture seule
            if col in self.readonly_columns:
                config[col] = st.column_config.Column(
                    col,
                    disabled=True,
                )
                continue

            # Config personnalisée
            if col in self.column_config:
                config[col] = self.column_config[col]
                continue

            # Auto-config selon le type
            dtype = self.data[col].dtype

            if pd.api.types.is_bool_dtype(dtype):
                config[col] = st.column_config.CheckboxColumn(col)

            elif pd.api.types.is_datetime64_any_dtype(dtype):
                config[col] = st.column_config.DatetimeColumn(
                    col,
                    format="DD/MM/YYYY HH:mm",
                )

            elif pd.api.types.is_numeric_dtype(dtype):
                if "prix" in col.lower() or "cout" in col.lower():
                    config[col] = st.column_config.NumberColumn(
                        col,
                        format="%.2f €",
                    )
                elif "quantite" in col.lower() or "qte" in col.lower():
                    config[col] = st.column_config.NumberColumn(
                        col,
                        min_value=0,
                        step=1,
                    )
                else:
                    config[col] = st.column_config.NumberColumn(col)

        return config

    def render(self) -> pd.DataFrame | None:
        """Affiche l'éditeur et retourne le DataFrame modifié.

        Returns:
            DataFrame modifié ou None si pas de changement
        """
        # Construire la config
        col_config = self._build_column_config()

        # Déterminer les colonnes éditables
        disabled_cols = self.readonly_columns + self.hide_columns
        if self.editable_columns:
            # Désactiver toutes sauf celles listées
            for col in self.data.columns:
                if col not in self.editable_columns and col not in disabled_cols:
                    if col not in col_config or not isinstance(col_config.get(col), type(None)):
                        col_config[col] = st.column_config.Column(col, disabled=True)

        # Afficher l'éditeur
        edited_df = st.data_editor(
            self.data,
            key=self.key,
            column_config=col_config,
            num_rows=self.num_rows,
            height=self.height,
            use_container_width=self.use_container_width,
            hide_index=True,
        )

        # Détecter les changements
        has_changes = not edited_df.equals(self.data)

        if has_changes:
            # Validation
            for validator in self._validators:
                is_valid, message = validator(edited_df)
                if not is_valid:
                    st.error(f"❌ {message}")
                    return None

            # Callbacks
            for callback in self._on_change_callbacks:
                try:
                    callback(edited_df)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

            return edited_df

        return None


# ═══════════════════════════════════════════════════════════
# ÉDITEURS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════


def inventaire_editable(
    df: pd.DataFrame,
    *,
    key: str = "inventaire_editor",
    on_save: Callable[[pd.DataFrame], None] | None = None,
) -> pd.DataFrame | None:
    """Éditeur d'inventaire avec quantités et dates de péremption.

    Colonnes attendues:
    - nom: Nom du produit (lecture seule)
    - quantite: Quantité (éditable, number)
    - unite: Unité (éditable, selectbox)
    - date_peremption: Date (éditable, date picker)
    - emplacement: Emplacement (éditable, selectbox)

    Args:
        df: DataFrame inventaire
        key: Clé unique
        on_save: Callback de sauvegarde

    Returns:
        DataFrame modifié ou None
    """
    st.markdown("### 📦 Inventaire")

    # Configuration des colonnes
    column_config = {
        "nom": st.column_config.TextColumn(
            "Produit",
            disabled=True,
            width="large",
        ),
        "quantite": st.column_config.NumberColumn(
            "Quantité",
            min_value=0,
            step=1,
            default=1,
        ),
        "unite": st.column_config.SelectboxColumn(
            "Unité",
            options=["pièce", "kg", "g", "L", "mL", "paquet", "boîte", "bouteille"],
            default="pièce",
        ),
        "date_peremption": st.column_config.DateColumn(
            "Péremption",
            format="DD/MM/YYYY",
            min_value=date.today(),
        ),
        "emplacement": st.column_config.SelectboxColumn(
            "Emplacement",
            options=["Réfrigérateur", "Congélateur", "Placard", "Cave", "Autre"],
            default="Placard",
        ),
    }

    # Indicateurs visuels pour péremption proche
    if "date_peremption" in df.columns:
        today = pd.Timestamp.now().normalize()
        df_display = df.copy()

        # Ajouter colonne statut
        def get_status(row):
            if pd.isna(row.get("date_peremption")):
                return "⚪"
            peremption = pd.Timestamp(row["date_peremption"])
            delta = (peremption - today).days
            if delta < 0:
                return "🔴 Périmé"
            elif delta <= 3:
                return "🟠 Urgent"
            elif delta <= 7:
                return "🟡 Bientôt"
            return "🟢 OK"

        df_display["statut"] = df.apply(get_status, axis=1)
        column_config["statut"] = st.column_config.TextColumn(
            "Statut",
            disabled=True,
            width="small",
        )
    else:
        df_display = df

    editor = DataFrameEditor(
        df_display,
        key=key,
        column_config=column_config,
        readonly_columns=["nom", "statut"] if "statut" in df_display.columns else ["nom"],
        num_rows="dynamic",
    )

    # Validateur: quantités positives
    def validate_quantities(df_new: pd.DataFrame) -> tuple[bool, str]:
        if "quantite" in df_new.columns:
            if (df_new["quantite"] < 0).any():
                return False, "Les quantités doivent être positives"
        return True, ""

    editor.add_validator(validate_quantities)

    # Callback de sauvegarde
    if on_save:
        editor.on_change(on_save)

    result = editor.render()

    # Bouton de sauvegarde explicite
    if result is not None:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Sauvegarder", key=f"{key}_save", type="primary"):
                if on_save:
                    # Retirer la colonne statut avant sauvegarde
                    save_df = result.drop(columns=["statut"], errors="ignore")
                    on_save(save_df)
                st.success("✅ Inventaire sauvegardé!")
                st.rerun()

    return result


def courses_editable(
    df: pd.DataFrame,
    *,
    key: str = "courses_editor",
    on_check: Callable[[str, bool], None] | None = None,
    on_save: Callable[[pd.DataFrame], None] | None = None,
) -> pd.DataFrame | None:
    """Éditeur de liste de courses avec checkboxes.

    Colonnes attendues:
    - nom: Nom du produit
    - quantite: Quantité
    - unite: Unité
    - fait: Checkbox coché/non coché
    - categorie: Catégorie (fruits, légumes, etc.)

    Args:
        df: DataFrame courses
        key: Clé unique
        on_check: Callback quand un item est coché
        on_save: Callback de sauvegarde

    Returns:
        DataFrame modifié ou None
    """
    st.markdown("### 🛒 Liste de courses")

    # S'assurer que la colonne 'fait' existe
    if "fait" not in df.columns:
        df = df.copy()
        df["fait"] = False

    # Configuration des colonnes
    column_config = {
        "fait": st.column_config.CheckboxColumn(
            "✓",
            default=False,
            width="small",
        ),
        "nom": st.column_config.TextColumn(
            "Article",
            width="large",
        ),
        "quantite": st.column_config.NumberColumn(
            "Qté",
            min_value=1,
            step=1,
            default=1,
            width="small",
        ),
        "unite": st.column_config.SelectboxColumn(
            "Unité",
            options=["", "kg", "g", "L", "mL", "pièce(s)", "paquet", "boîte"],
            width="small",
        ),
        "categorie": st.column_config.SelectboxColumn(
            "Catégorie",
            options=[
                "Fruits & Légumes",
                "Viandes & Poissons",
                "Produits laitiers",
                "Épicerie",
                "Surgelés",
                "Boissons",
                "Hygiène",
                "Autre",
            ],
            width="medium",
        ),
    }

    # Réorganiser colonnes (fait en premier)
    cols_order = ["fait"] + [c for c in df.columns if c != "fait"]
    df_display = df[cols_order]

    # Stats
    total = len(df_display)
    done = df_display["fait"].sum() if "fait" in df_display.columns else 0

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.progress(done / max(total, 1), text=f"{done}/{total} articles cochés")
    with col2:
        if st.button("☑️ Tout cocher", key=f"{key}_check_all"):
            df_display["fait"] = True
            st.rerun()
    with col3:
        if st.button("☐ Tout décocher", key=f"{key}_uncheck_all"):
            df_display["fait"] = False
            st.rerun()

    editor = DataFrameEditor(
        df_display,
        key=key,
        column_config=column_config,
        num_rows="dynamic",
    )

    if on_save:
        editor.on_change(on_save)

    result = editor.render()

    # Détecter les changements de checkbox
    if result is not None and on_check:
        for idx in result.index:
            old_val = df_display.loc[idx, "fait"] if idx in df_display.index else False
            new_val = result.loc[idx, "fait"]
            if old_val != new_val:
                nom = result.loc[idx, "nom"]
                on_check(nom, new_val)

    return result


def planning_editable(
    df: pd.DataFrame,
    *,
    key: str = "planning_editor",
    jours: list[str] | None = None,
    repas_types: list[str] | None = None,
    on_save: Callable[[pd.DataFrame], None] | None = None,
) -> pd.DataFrame | None:
    """Éditeur de planning repas de la semaine.

    Format DataFrame:
    - Index: jours de la semaine
    - Colonnes: types de repas (petit_dejeuner, dejeuner, diner, etc.)
    - Valeurs: noms des recettes

    Args:
        df: DataFrame planning (jours x repas)
        key: Clé unique
        jours: Liste des jours
        repas_types: Types de repas
        on_save: Callback sauvegarde

    Returns:
        DataFrame modifié ou None
    """
    st.markdown("### 📅 Planning des repas")

    if jours is None:
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    if repas_types is None:
        repas_types = ["Petit-déjeuner", "Déjeuner", "Goûter", "Dîner"]

    # S'assurer que le DataFrame a le bon format
    if df.empty:
        df = pd.DataFrame(index=jours, columns=repas_types, data="")

    # Configuration colonnes (tout éditable)
    column_config = {
        col: st.column_config.TextColumn(
            col,
            width="medium",
            help="Cliquer pour éditer",
        )
        for col in df.columns
    }

    # Ajouter colonne jour si pas en index
    if df.index.name != "jour" and "jour" not in df.columns:
        df_display = df.reset_index()
        if "index" in df_display.columns:
            df_display = df_display.rename(columns={"index": "jour"})
        column_config["jour"] = st.column_config.TextColumn(
            "Jour",
            disabled=True,
            width="small",
        )
    else:
        df_display = df

    edited = st.data_editor(
        df_display,
        key=key,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
    )

    # Détecter changements
    has_changes = not edited.equals(df_display)

    if has_changes:
        # Stats
        filled = (edited != "").sum().sum() - (1 if "jour" in edited.columns else 0) * len(edited)
        total_slots = len(jours) * len(repas_types)
        st.info(f"📊 {filled}/{total_slots} repas planifiés")

        if st.button("💾 Sauvegarder le planning", key=f"{key}_save", type="primary"):
            if on_save:
                # Remettre en format original (jour en index)
                save_df = edited.set_index("jour") if "jour" in edited.columns else edited
                on_save(save_df)
            st.success("✅ Planning sauvegardé!")
            return edited

    return None


def table_editable_simple(
    data: list[dict] | pd.DataFrame,
    *,
    key: str = "simple_editor",
    columns: list[str] | None = None,
    column_labels: dict[str, str] | None = None,
    editable: list[str] | None = None,
    height: int = 400,
) -> pd.DataFrame | None:
    """Table éditable simple pour données génériques.

    Args:
        data: Données (liste de dicts ou DataFrame)
        key: Clé unique
        columns: Colonnes à afficher
        column_labels: Labels des colonnes
        editable: Colonnes éditables
        height: Hauteur

    Returns:
        DataFrame modifié ou None
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    if columns:
        df = df[columns]

    # Config avec labels
    col_config = {}
    if column_labels:
        for col, label in column_labels.items():
            if col in df.columns:
                col_config[col] = st.column_config.Column(label)

    # Colonnes non-éditables
    if editable:
        for col in df.columns:
            if col not in editable and col not in col_config:
                col_config[col] = st.column_config.Column(col, disabled=True)

    result = st.data_editor(
        df,
        key=key,
        column_config=col_config,
        height=height,
        use_container_width=True,
        hide_index=True,
    )

    if not result.equals(df):
        return result
    return None
