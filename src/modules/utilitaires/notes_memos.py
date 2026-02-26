"""
Module Notes & Mémos — Widget post-it pour la famille.

Notes rapides avec catégories, épinglage, couleurs, tags
et mode checklist. Archivage et recherche inclus.
"""

import logging

import streamlit as st

from src.core.models.utilitaires import CategorieNote
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_notes_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("notes_memos")

COULEURS = {
    "🟡 Jaune": "#fff9c4",
    "🔵 Bleu": "#bbdefb",
    "🟢 Vert": "#c8e6c9",
    "🟠 Orange": "#ffe0b2",
    "🟣 Violet": "#e1bee7",
    "⚪ Blanc": "#ffffff",
}


@profiler_rerun("notes_memos")
def app():
    """Point d'entrée module Notes & Mémos."""
    st.title("📝 Notes & Mémos")
    st.caption("Post-its numériques pour toute la famille")

    with error_boundary(titre="Erreur notes"):
        service = get_notes_service()

        # Barre d'actions
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            filtre_cat = st.selectbox(
                "Catégorie",
                options=["Toutes"] + [c.value for c in CategorieNote],
                key=_keys("filtre_cat"),
            )
        with col2:
            epingle_only = st.checkbox("📌 Épinglées", key=_keys("epingle_only"))
        with col3:
            voir_archives = st.checkbox("📦 Archives", key=_keys("archives"))

        # Formulaire de création
        with st.expander("➕ Nouvelle note", expanded=False):
            _formulaire_creation(service)

        st.divider()

        # Liste des notes
        cat_filtre = None if filtre_cat == "Toutes" else filtre_cat
        notes = service.lister(
            categorie=cat_filtre,
            epingle_seulement=epingle_only,
            inclure_archives=voir_archives,
        )

        if not notes:
            st.info("Aucune note. Créez votre première note ci-dessus ! 📝")
            return

        # Affichage en grille
        cols = st.columns(3)
        for i, note in enumerate(notes):
            with cols[i % 3]:
                _afficher_note(note, service)


def _formulaire_creation(service):
    """Formulaire de création d'une note."""
    with st.form("form_note", clear_on_submit=True):
        titre = st.text_input("Titre", key=_keys("new_titre"))
        contenu = st.text_area("Contenu", height=100, key=_keys("new_contenu"))

        col1, col2, col3 = st.columns(3)
        with col1:
            categorie = st.selectbox(
                "Catégorie",
                options=[c.value for c in CategorieNote],
                key=_keys("new_cat"),
            )
        with col2:
            couleur = st.selectbox(
                "Couleur",
                options=list(COULEURS.keys()),
                key=_keys("new_couleur"),
            )
        with col3:
            epingle = st.checkbox("📌 Épingler", key=_keys("new_epingle"))

        tags_str = st.text_input(
            "Tags (séparés par des virgules)",
            key=_keys("new_tags"),
        )

        submitted = st.form_submit_button("💾 Créer la note", use_container_width=True)

        if submitted and titre:
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
            service.creer(
                titre=titre,
                contenu=contenu,
                categorie=categorie,
                couleur=COULEURS[couleur],
                epingle=epingle,
                tags=tags,
            )
            st.success("Note créée !")
            st.rerun()


def _afficher_note(note, service):
    """Affiche une note sous forme de carte."""
    couleur = getattr(note, "couleur", "#ffffff") or "#ffffff"
    epingle_icon = "📌 " if note.epingle else ""

    with st.container(border=True):
        st.markdown(
            f"<div style='background-color:{couleur};padding:4px 8px;border-radius:4px;'>"
            f"<strong>{epingle_icon}{note.titre}</strong></div>",
            unsafe_allow_html=True,
        )

        if note.contenu:
            st.markdown(note.contenu[:200])

        # Tags
        tags = getattr(note, "tags", None) or []
        if tags:
            st.caption(" ".join(f"`{t}`" for t in tags))

        st.caption(f"📁 {note.categorie} • {note.modifie_le.strftime('%d/%m %H:%M')}")

        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📌", key=_keys("pin", str(note.id)), help="Épingler/Détacher"):
                service.basculer_epingle(note.id)
                st.rerun()
        with col2:
            if st.button("📦", key=_keys("arch", str(note.id)), help="Archiver"):
                service.archiver(note.id)
                st.rerun()
        with col3:
            if st.button("🗑️", key=_keys("del", str(note.id)), help="Supprimer"):
                service.supprimer(note.id)
                st.rerun()
