"""
Page Export Drive — Export de la liste vers La Fourche / Mon Petit Potager.

Génère des liens de recherche pour chaque article de la liste
vers les drives sélectionnés.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("export_drive")


def afficher_export_drive() -> None:
    """Affiche l'interface d'export drive."""
    st.subheader("🚗 Export vers Drive")
    st.caption("Exportez votre liste de courses vers La Fourche ou Mon Petit Potager")

    with error_boundary(titre="Erreur export drive"):
        _afficher_contenu()


def _afficher_contenu() -> None:
    """Contenu principal de l'export drive."""
    from src.services.cuisine.courses.export_drive import (
        DRIVES,
        exporter_multi_drives,
        generer_texte_partage,
    )

    # Sélection du drive
    drives_dispo = list(DRIVES.keys())
    drives_labels = {
        "la_fourche": "🌿 La Fourche (bio en ligne)",
        "mon_petit_potager": "🥕 Mon Petit Potager (local)",
    }

    selected = st.multiselect(
        "Drives cibles",
        options=drives_dispo,
        default=drives_dispo,
        format_func=lambda x: drives_labels.get(x, x),
        key=_keys("drives"),
    )

    if not selected:
        st.info("Sélectionnez au moins un drive.")
        return

    # Récupérer la liste active
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.courses import ArticleCourses, ListeCourses

        with obtenir_contexte_db() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.archivee == False).first()  # noqa: E712

            if not liste:
                st.info("Aucune liste de courses active.")
                return

            articles = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.achete == False,  # noqa: E712
                )
                .all()
            )

            noms_articles = [a.nom for a in articles if a.nom]
    except Exception as e:
        st.error(f"Erreur accès liste: {e}")
        return

    if not noms_articles:
        st.info("Tous les articles sont déjà cochés !")
        return

    st.markdown(f"**{len(noms_articles)} article(s)** à exporter")

    # Générer les exports
    exports = exporter_multi_drives(noms_articles, selected)

    for export in exports:
        drive_label = drives_labels.get(export.drive_id, export.drive_id)
        with st.expander(f"{drive_label}", expanded=True):
            st.markdown(f"**{len(export.articles)}** articles avec liens de recherche")

            for art in export.articles:
                st.markdown(f"- [{art.nom}]({art.url_recherche})")

    # Export texte partageable
    st.divider()
    if st.button("📋 Générer texte de partage", key=_keys("partage")):
        texte = generer_texte_partage(exports)
        st.code(texte, language=None)
        st.caption("Copiez ce texte pour le partager.")


__all__ = ["afficher_export_drive"]
