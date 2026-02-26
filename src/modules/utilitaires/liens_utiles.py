"""
Module Liens Utiles — Gestionnaire de favoris/bookmarks familial.

Sauvegardez et organisez les liens utiles pour la famille :
recettes, activités enfants, bons plans, administratif...
"""

import logging

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_liens_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("liens_utiles")

CATEGORIES_LIENS = [
    "🍽️ Cuisine & Recettes",
    "👶 Enfants & Famille",
    "🏠 Maison & Bricolage",
    "🎭 Activités & Sorties",
    "📚 Éducation",
    "🏥 Santé",
    "💰 Bons Plans",
    "📄 Administratif",
    "💻 Tech & Outils",
    "🎮 Loisirs",
    "🌍 Voyage",
    "📦 Autre",
]


@profiler_rerun("liens_utiles")
def app():
    """Point d'entrée module Liens Utiles."""
    st.title("🔗 Liens Utiles")
    st.caption("Favoris et bookmarks de la famille")

    with error_boundary(titre="Erreur liens"):
        service = get_liens_service()

        # Barre de filtres
        col1, col2 = st.columns([3, 1])
        with col1:
            recherche = st.text_input(
                "🔍 Rechercher",
                placeholder="Mot-clé dans le titre ou description...",
                key=_keys("recherche"),
            )
        with col2:
            filtre_cat = st.selectbox(
                "Catégorie",
                options=["Toutes"] + CATEGORIES_LIENS,
                key=_keys("filtre_cat"),
            )

        # Formulaire d'ajout
        with st.expander("➕ Nouveau lien", expanded=False):
            _formulaire_lien(service)

        st.divider()

        # Liste des liens
        liens = service.lister()

        # Filtrage côté UI
        if recherche:
            liens = [
                l
                for l in liens
                if recherche.lower() in (l.titre or "").lower()
                or recherche.lower() in (l.description or "").lower()
            ]
        if filtre_cat != "Toutes":
            liens = [l for l in liens if l.categorie == filtre_cat]

        if not liens:
            st.info("🔗 Aucun lien trouvé. Ajoutez votre premier favori !")
            return

        # Grouper par catégorie
        par_cat = {}
        for l in liens:
            cat = l.categorie or "📦 Autre"
            if cat not in par_cat:
                par_cat[cat] = []
            par_cat[cat].append(l)

        for cat, items in sorted(par_cat.items()):
            st.subheader(cat)
            for lien in items:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        st.markdown(f"**[{lien.titre}]({lien.url})**")
                        if lien.description:
                            st.caption(lien.description)
                    with col2:
                        tags = lien.tags or []
                        if tags:
                            st.caption(" ".join(f"`{t}`" for t in tags))
                    with col3:
                        if st.button("🗑️", key=_keys("del", str(lien.id)), help="Supprimer"):
                            service.supprimer(lien.id)
                            st.rerun()


def _formulaire_lien(service):
    """Formulaire d'ajout de lien."""
    with st.form("form_lien", clear_on_submit=True):
        titre = st.text_input("Titre *", key=_keys("new_titre"))
        url = st.text_input(
            "URL *",
            placeholder="https://...",
            key=_keys("new_url"),
        )

        col1, col2 = st.columns(2)
        with col1:
            categorie = st.selectbox(
                "Catégorie",
                options=CATEGORIES_LIENS,
                key=_keys("new_cat"),
            )
        with col2:
            tags_str = st.text_input(
                "Tags (séparés par virgules)",
                key=_keys("new_tags"),
            )
        description = st.text_input("Description", key=_keys("new_desc"))

        if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
            if titre and url:
                tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
                service.creer(
                    titre=titre,
                    url=url,
                    categorie=categorie,
                    description=description or None,
                    tags=tags,
                )
                st.success(f"🔗 '{titre}' ajouté aux favoris !")
                st.rerun()
            else:
                st.warning("Titre et URL sont obligatoires.")
