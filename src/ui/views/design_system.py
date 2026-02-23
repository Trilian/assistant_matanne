"""
Page Design System auto-générée depuis le registre @composant_ui.

Cette page documente automatiquement tous les composants UI enregistrés
avec leurs signatures, exemples et métadonnées.

Usage:
    Appeler `afficher_design_system()` depuis un module Streamlit
    ou accéder via le menu Paramètres > Design System.
"""

from __future__ import annotations

import streamlit as st

from src.ui.a11y import A11y
from src.ui.components.atoms import badge, separateur
from src.ui.registry import ComponentMeta, obtenir_catalogue, rechercher_composants
from src.ui.tokens import Couleur, Espacement, Rayon, Variante


def afficher_design_system():
    """Affiche la page Design System avec tous les composants enregistrés."""
    st.title("🎨 Design System")
    st.caption("Documentation auto-générée depuis le registre `@composant_ui`")

    # Inject a11y CSS
    A11y.injecter_css()

    # Recherche
    col_search, col_stats = st.columns([3, 1])
    with col_search:
        recherche = st.text_input(
            "🔍 Rechercher un composant",
            placeholder="badge, metric, form...",
            key="ds_search",
        )

    catalogue = obtenir_catalogue()
    total_composants = sum(len(comps) for comps in catalogue.values())

    with col_stats:
        st.metric("Composants", total_composants)

    separateur()

    if recherche:
        _afficher_resultats_recherche(recherche)
    else:
        _afficher_catalogue_par_categorie(catalogue)


def _afficher_resultats_recherche(terme: str):
    """Affiche les résultats de recherche."""
    resultats = rechercher_composants(terme)

    if not resultats:
        st.info(f"Aucun composant trouvé pour « {terme} »")
        return

    st.subheader(f"🔍 {len(resultats)} résultat(s) pour « {terme} »")

    for meta in resultats:
        _afficher_carte_composant(meta)


def _afficher_catalogue_par_categorie(catalogue: dict[str, list[ComponentMeta]]):
    """Affiche le catalogue groupé par catégorie."""
    # Ordre des catégories
    ordre_categories = ["atoms", "forms", "data", "layouts", "metrics", "feedback", "system"]

    categories_triees = sorted(
        catalogue.keys(), key=lambda c: ordre_categories.index(c) if c in ordre_categories else 99
    )

    # Tabs par catégorie
    if categories_triees:
        tabs = st.tabs([f"{_icone_categorie(cat)} {cat.title()}" for cat in categories_triees])

        for tab, categorie in zip(tabs, categories_triees, strict=False):
            with tab:
                composants = catalogue[categorie]
                st.caption(f"{len(composants)} composant(s)")

                for meta in sorted(composants, key=lambda m: m.nom):
                    _afficher_carte_composant(meta)


def _icone_categorie(categorie: str) -> str:
    """Retourne l'icône emoji pour une catégorie."""
    icones = {
        "atoms": "⚛️",
        "forms": "📝",
        "data": "📊",
        "layouts": "🏗️",
        "metrics": "📈",
        "feedback": "💬",
        "system": "⚙️",
    }
    return icones.get(categorie, "📦")


def _afficher_carte_composant(meta: ComponentMeta):
    """Affiche une carte détaillée pour un composant."""
    with st.expander(f"**{meta.nom}**`{meta.signature}`", expanded=False):
        # Description
        if meta.description:
            st.markdown(meta.description)

        # Tags
        if meta.tags:
            cols = st.columns(len(meta.tags))
            for col, tag in zip(cols, meta.tags, strict=False):
                with col:
                    badge(tag, variante=Variante.INFO)

        # Exemple
        if meta.exemple:
            st.markdown("**Exemple:**")
            st.code(meta.exemple, language="python")

        # Source
        st.caption(f"📁 `{meta.fichier}` ligne {meta.ligne}")


def generer_markdown_api() -> str:
    """Génère la documentation Markdown du Design System.

    Returns:
        Documentation formatée en Markdown.
    """
    catalogue = obtenir_catalogue()
    lignes = [
        "# Design System - API Reference",
        "",
        "Documentation auto-générée des composants UI.",
        "",
        f"**Total: {sum(len(c) for c in catalogue.values())} composants**",
        "",
    ]

    for categorie in sorted(catalogue.keys()):
        composants = catalogue[categorie]
        lignes.append(f"## {categorie.title()}")
        lignes.append("")

        for meta in sorted(composants, key=lambda m: m.nom):
            lignes.append(f"### `{meta.nom}{meta.signature}`")
            lignes.append("")

            if meta.description:
                # Première ligne de la docstring
                premiere_ligne = meta.description.split("\n")[0].strip()
                lignes.append(premiere_ligne)
                lignes.append("")

            if meta.exemple:
                lignes.append("**Exemple:**")
                lignes.append(f"```python\n{meta.exemple}\n```")
                lignes.append("")

            if meta.tags:
                lignes.append(f"Tags: {', '.join(f'`{t}`' for t in meta.tags)}")
                lignes.append("")

            lignes.append("---")
            lignes.append("")

    return "\n".join(lignes)


def exporter_design_system_json() -> dict:
    """Exporte le Design System au format JSON.

    Returns:
        Dict avec toutes les métadonnées des composants.
    """
    catalogue = obtenir_catalogue()
    export = {}

    for categorie, composants in catalogue.items():
        export[categorie] = [
            {
                "nom": m.nom,
                "signature": m.signature,
                "description": m.description,
                "exemple": m.exemple,
                "tags": list(m.tags),
                "fichier": m.fichier,
                "ligne": m.ligne,
            }
            for m in composants
        ]

    return export


__all__ = [
    "afficher_design_system",
    "generer_markdown_api",
    "exporter_design_system_json",
]
