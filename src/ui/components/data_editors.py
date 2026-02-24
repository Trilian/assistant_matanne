"""
Composants d'édition inline via st.data_editor.

Fournit des éditeurs de données tabulaires pour:
- Inventaire: édition quantités, dates de péremption, emplacements
- Courses: cocher/décocher articles, modifier quantités
- Budget: édition des montants directement dans le tableau

Usage:
    from src.ui.components.data_editors import (
        editeur_inventaire,
        editeur_courses,
        editeur_budget,
    )
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("data_editor")


# ═══════════════════════════════════════════════════════════
# ÉDITEUR INVENTAIRE
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "data-editor",
    exemple="editeur_inventaire(articles, on_save=save_fn)",
    tags=("inventaire", "data_editor", "inline"),
)
def editeur_inventaire(
    inventaire: list[dict[str, Any]],
    *,
    on_save: Any | None = None,
    key_suffix: str = "",
) -> pd.DataFrame | None:
    """
    Éditeur inline pour l'inventaire avec st.data_editor.

    Permet l'édition directe des quantités, dates de péremption,
    emplacements sans ouvrir de formulaire séparé.

    Args:
        inventaire: Liste de dicts d'articles d'inventaire
        on_save: Callback appelé avec les modifications (DataFrame)
        key_suffix: Suffixe pour les clés de widget (unicité)

    Returns:
        DataFrame modifié si des changements ont été faits, None sinon
    """
    if not inventaire:
        st.info("📦 Aucun article à éditer.")
        return None

    # Préparer le DataFrame pour l'édition
    df = pd.DataFrame(
        [
            {
                "id": article.get("id", idx),
                "Article": article.get("ingredient_nom", ""),
                "Catégorie": article.get("ingredient_categorie", "Autre"),
                "Quantité": float(article.get("quantite", 0)),
                "Unité": article.get("unite", "pce"),
                "Seuil min": float(article.get("quantite_min", 0)),
                "Emplacement": article.get("emplacement", ""),
                "Date péremption": (
                    pd.to_datetime(article["date_peremption"]).date()
                    if article.get("date_peremption")
                    else None
                ),
            }
            for idx, article in enumerate(inventaire)
        ]
    )

    # Configuration des colonnes
    column_config = {
        "id": None,  # Masquer l'ID
        "Article": st.column_config.TextColumn(
            "📦 Article",
            width="medium",
            disabled=True,  # Lecture seule
        ),
        "Catégorie": st.column_config.SelectboxColumn(
            "🏷️ Catégorie",
            options=[
                "Légumes",
                "Fruits",
                "Viandes",
                "Poissons",
                "Produits laitiers",
                "Épicerie",
                "Surgelés",
                "Boissons",
                "Condiments",
                "Autre",
            ],
            width="medium",
        ),
        "Quantité": st.column_config.NumberColumn(
            "📊 Quantité",
            min_value=0,
            max_value=9999,
            step=0.5,
            format="%.1f",
            width="small",
        ),
        "Unité": st.column_config.SelectboxColumn(
            "📐 Unité",
            options=["pce", "kg", "g", "L", "mL", "boîte", "sachet", "bouteille"],
            width="small",
        ),
        "Seuil min": st.column_config.NumberColumn(
            "⚠️ Seuil min",
            min_value=0,
            step=0.5,
            format="%.1f",
            width="small",
            help="Alerte quand la quantité passe sous ce seuil",
        ),
        "Emplacement": st.column_config.SelectboxColumn(
            "📍 Emplacement",
            options=["Frigo", "Congélateur", "Placard", "Cave", "Autre"],
            width="small",
        ),
        "Date péremption": st.column_config.DateColumn(
            "📅 Péremption",
            min_value=date.today(),
            format="DD/MM/YYYY",
            width="small",
        ),
    }

    # Afficher l'éditeur
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",  # Permet ajout/suppression de lignes
        key=_keys(f"inventaire_editor{key_suffix}"),
    )

    # Détecter les modifications
    if edited_df is not None and not df.equals(edited_df):
        col_save, col_cancel = st.columns([1, 4])

        with col_save:
            if st.button(
                "💾 Sauvegarder",
                type="primary",
                use_container_width=True,
                key=_keys(f"save_inventaire{key_suffix}"),
            ):
                if on_save:
                    on_save(edited_df)
                st.success("✅ Modifications sauvegardées!")
                return edited_df

        with col_cancel:
            if st.button(
                "↩️ Annuler",
                use_container_width=True,
                key=_keys(f"cancel_inventaire{key_suffix}"),
            ):
                st.rerun()

    return None


# ═══════════════════════════════════════════════════════════
# ÉDITEUR COURSES
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "data-editor",
    exemple="editeur_courses(articles, on_save=save_fn)",
    tags=("courses", "data_editor", "inline"),
)
def editeur_courses(
    articles: list[dict[str, Any]],
    *,
    on_save: Any | None = None,
    key_suffix: str = "",
) -> pd.DataFrame | None:
    """
    Éditeur inline pour la liste de courses.

    Permet de cocher/décocher les articles, modifier les quantités,
    changer les rayons et priorités directement dans le tableau.

    Args:
        articles: Liste de dicts d'articles de courses
        on_save: Callback avec les modifications
        key_suffix: Suffixe pour les clés de widget

    Returns:
        DataFrame modifié si sauvegardé, None sinon
    """
    if not articles:
        st.info("🛒 Aucun article dans la liste.")
        return None

    df = pd.DataFrame(
        [
            {
                "id": article.get("id", idx),
                "✅": article.get("achete", False),
                "Article": article.get("nom", article.get("ingredient_nom", "")),
                "Quantité": float(article.get("quantite", 1)),
                "Unité": article.get("unite", "pce"),
                "Rayon": article.get("rayon_magasin", "Autre"),
                "Priorité": article.get("priorite", "moyenne"),
                "Note": article.get("notes", ""),
            }
            for idx, article in enumerate(articles)
        ]
    )

    column_config = {
        "id": None,  # Masquer l'ID
        "✅": st.column_config.CheckboxColumn(
            "Acheté",
            default=False,
            width="small",
        ),
        "Article": st.column_config.TextColumn(
            "🛒 Article",
            width="medium",
        ),
        "Quantité": st.column_config.NumberColumn(
            "📊 Qté",
            min_value=0,
            max_value=999,
            step=1,
            format="%d",
            width="small",
        ),
        "Unité": st.column_config.SelectboxColumn(
            "📐 Unité",
            options=["pce", "kg", "g", "L", "mL", "boîte", "sachet", "bouteille", "lot"],
            width="small",
        ),
        "Rayon": st.column_config.SelectboxColumn(
            "🏪 Rayon",
            options=[
                "Fruits & Légumes",
                "Boucherie",
                "Poissonnerie",
                "Crémerie",
                "Épicerie",
                "Surgelés",
                "Boissons",
                "Hygiène",
                "Entretien",
                "Autre",
            ],
            width="small",
        ),
        "Priorité": st.column_config.SelectboxColumn(
            "🔔 Priorité",
            options=["haute", "moyenne", "basse"],
            width="small",
        ),
        "Note": st.column_config.TextColumn(
            "📝 Note",
            width="medium",
        ),
    }

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=_keys(f"courses_editor{key_suffix}"),
    )

    # Détecter les modifications
    if edited_df is not None and not df.equals(edited_df):
        col_save, col_info = st.columns([1, 4])

        with col_save:
            if st.button(
                "💾 Sauvegarder",
                type="primary",
                use_container_width=True,
                key=_keys(f"save_courses{key_suffix}"),
            ):
                if on_save:
                    on_save(edited_df)
                st.success("✅ Liste mise à jour!")
                return edited_df

        with col_info:
            nb_achetes = edited_df["✅"].sum()
            nb_total = len(edited_df)
            st.caption(f"✅ {nb_achetes}/{nb_total} articles cochés")

    return None


# ═══════════════════════════════════════════════════════════
# ÉDITEUR BUDGET
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "data-editor",
    exemple='editeur_budget(depenses, categories=["Alimentation"])',
    tags=("budget", "data_editor", "inline"),
)
def editeur_budget(
    depenses: list[dict[str, Any]],
    *,
    categories: list[str] | None = None,
    on_save: Any | None = None,
    key_suffix: str = "",
) -> pd.DataFrame | None:
    """
    Éditeur inline pour le budget familial.

    Permet l'édition des montants, catégories et descriptions
    directement dans le tableau récapitulatif.

    Args:
        depenses: Liste de dicts de dépenses
        categories: Liste des catégories disponibles
        on_save: Callback avec les modifications
        key_suffix: Suffixe pour les clés de widget

    Returns:
        DataFrame modifié si sauvegardé, None sinon
    """
    if not depenses:
        st.info("💰 Aucune dépense à afficher.")
        return None

    if categories is None:
        categories = [
            "Alimentation",
            "Courses",
            "Maison",
            "Santé",
            "Transport",
            "Loisirs",
            "Vêtements",
            "Enfant",
            "Services",
            "Autre",
        ]

    df = pd.DataFrame(
        [
            {
                "id": dep.get("id", idx),
                "Date": (pd.to_datetime(dep["date"]).date() if dep.get("date") else date.today()),
                "Montant (€)": float(dep.get("montant", 0)),
                "Catégorie": dep.get("categorie", "Autre"),
                "Description": dep.get("description", ""),
                "Magasin": dep.get("magasin", ""),
                "Récurrent": dep.get("est_recurrente", dep.get("est_recurrent", False)),
            }
            for idx, dep in enumerate(depenses)
        ]
    )

    column_config = {
        "id": None,  # Masquer
        "Date": st.column_config.DateColumn(
            "📅 Date",
            format="DD/MM/YYYY",
            width="small",
        ),
        "Montant (€)": st.column_config.NumberColumn(
            "💰 Montant (€)",
            min_value=0,
            max_value=99999,
            step=0.01,
            format="%.2f €",
            width="small",
        ),
        "Catégorie": st.column_config.SelectboxColumn(
            "🏷️ Catégorie",
            options=categories,
            width="small",
        ),
        "Description": st.column_config.TextColumn(
            "📝 Description",
            width="large",
        ),
        "Magasin": st.column_config.TextColumn(
            "🏪 Magasin",
            width="small",
        ),
        "Récurrent": st.column_config.CheckboxColumn(
            "🔄 Récurrent",
            default=False,
            width="small",
        ),
    }

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key=_keys(f"budget_editor{key_suffix}"),
    )

    # Statistiques et save
    if edited_df is not None:
        # Totaux
        total = edited_df["Montant (€)"].sum()
        st.markdown(f"**💰 Total: {total:.2f} €**")

        if not df.equals(edited_df):
            col_save, col_cancel = st.columns([1, 4])

            with col_save:
                if st.button(
                    "💾 Sauvegarder",
                    type="primary",
                    use_container_width=True,
                    key=_keys(f"save_budget{key_suffix}"),
                ):
                    if on_save:
                        on_save(edited_df)
                    st.success("✅ Budget mis à jour!")
                    return edited_df

            with col_cancel:
                if st.button(
                    "↩️ Annuler",
                    use_container_width=True,
                    key=_keys(f"cancel_budget{key_suffix}"),
                ):
                    st.rerun()

    return None


# ═══════════════════════════════════════════════════════════
# ÉDITEUR BUDGETS MENSUELS (enveloppes)
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "data-editor",
    exemple='editeur_budgets_mensuels({"Alimentation": 500})',
    tags=("budget", "mensuel", "data_editor"),
)
def editeur_budgets_mensuels(
    budgets: dict[str, float],
    *,
    on_save: Any | None = None,
    key_suffix: str = "",
) -> dict[str, float] | None:
    """
    Éditeur inline pour les enveloppes budgétaires mensuelles.

    Args:
        budgets: Dict catégorie → montant budget
        on_save: Callback avec le dict modifié
        key_suffix: Suffixe pour les clés

    Returns:
        Dict modifié si sauvegardé, None sinon
    """
    df = pd.DataFrame(
        [
            {"Catégorie": cat, "Budget mensuel (€)": float(montant)}
            for cat, montant in sorted(budgets.items())
        ]
    )

    column_config = {
        "Catégorie": st.column_config.TextColumn(
            "🏷️ Catégorie",
            width="medium",
            disabled=True,
        ),
        "Budget mensuel (€)": st.column_config.NumberColumn(
            "💰 Budget (€/mois)",
            min_value=0,
            max_value=99999,
            step=10,
            format="%.0f €",
            width="medium",
        ),
    }

    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",  # Pas d'ajout/suppression de catégories
        key=_keys(f"budgets_mensuels{key_suffix}"),
    )

    total = edited_df["Budget mensuel (€)"].sum()
    st.markdown(f"**💰 Budget total mensuel: {total:.0f} €**")

    if not df.equals(edited_df):
        if st.button(
            "💾 Sauvegarder les budgets",
            type="primary",
            use_container_width=True,
            key=_keys(f"save_budgets_mensuels{key_suffix}"),
        ):
            result = dict(
                zip(
                    edited_df["Catégorie"],
                    edited_df["Budget mensuel (€)"],
                    strict=False,
                )
            )
            if on_save:
                on_save(result)
            st.success("✅ Budgets mensuels mis à jour!")
            return result

    return None


__all__ = [
    "editeur_inventaire",
    "editeur_courses",
    "editeur_budget",
    "editeur_budgets_mensuels",
]
