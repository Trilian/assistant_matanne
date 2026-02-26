"""
Album Souvenirs – Albums photos et timeline des souvenirs familiaux.

Onglets:
  1. Timeline des souvenirs
  2. Albums
  3. Ajouter un souvenir
"""

from __future__ import annotations

import logging
from datetime import date

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("album_souvenirs")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.album import obtenir_service_album

        _service = obtenir_service_album()
    return _service


TYPES_ALBUM = ["general", "vacances", "fetes", "jules", "couple", "famille_elargie"]
EMOTIONS = ["joie", "fierte", "tendresse", "amusement", "nostalgie", "surprise", "emotion"]


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – TIMELINE
# ═══════════════════════════════════════════════════════════


def _onglet_timeline():
    """Timeline chronologique des souvenirs."""
    st.subheader("📅 Timeline Familiale")

    svc = _get_service()

    annee = st.selectbox(
        "Année",
        options=list(range(date.today().year, 2023, -1)),
        key=_keys("annee_filtre"),
    )

    try:
        souvenirs = svc.lister_souvenirs_timeline(annee=annee)
        if not souvenirs:
            etat_vide(f"Aucun souvenir en {annee}", icone="📸")
            return

        par_mois: dict[int, list] = {}
        for s in souvenirs:
            mois = s.date_souvenir.month if s.date_souvenir else 0
            par_mois.setdefault(mois, []).append(s)

        noms_mois = [
            "",
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]

        for mois in sorted(par_mois.keys(), reverse=True):
            st.markdown(f"### {noms_mois[mois]} {annee}")

            for s in par_mois[mois]:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        emoji_map = {
                            "joie": "😊",
                            "fierte": "🏆",
                            "tendresse": "💕",
                            "amusement": "😄",
                            "nostalgie": "🥹",
                            "surprise": "😲",
                            "emotion": "🥺",
                        }
                        emoji = emoji_map.get(s.emotion or "", "📸")
                        st.markdown(f"{emoji} **{s.titre}**")
                        if s.description:
                            st.write(s.description)
                        st.caption(
                            f"📅 {s.date_souvenir.strftime('%d/%m/%Y') if s.date_souvenir else '?'}"
                        )
                        if s.participants:
                            st.caption(f"👥 {', '.join(s.participants)}")
                    with col2:
                        if st.button("🗑️", key=_keys(f"del_s_{s.id}")):
                            try:
                                svc.supprimer_souvenir(s.id)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

    except Exception as e:
        st.error(f"Erreur timeline : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – ALBUMS
# ═══════════════════════════════════════════════════════════


def _onglet_albums():
    """Gestion des albums."""
    st.subheader("📚 Albums")

    svc = _get_service()

    with st.expander("➕ Créer un album", expanded=False):
        with st.form(_keys("form_album")):
            nom = st.text_input("Nom de l'album *", key=_keys("album_nom"))
            col1, col2 = st.columns(2)
            with col1:
                type_album = st.selectbox("Type", options=TYPES_ALBUM, key=_keys("album_type"))
            with col2:
                date_debut = st.date_input(
                    "Date début", value=date.today(), key=_keys("album_debut")
                )
            description = st.text_area("Description", key=_keys("album_desc"))

            if st.form_submit_button("💾 Créer", type="primary"):
                if not nom:
                    st.warning("Le nom est requis.")
                else:
                    try:
                        svc.create(
                            {
                                "nom": nom,
                                "type_album": type_album,
                                "date_debut": date_debut,
                                "description": description or None,
                            }
                        )
                        st.success(f"✅ Album « {nom} » créé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")

    try:
        albums = svc.list_all()
        if not albums:
            etat_vide("Aucun album créé", icone="📚")
        else:
            cols = st.columns(min(len(albums), 3))
            for i, album in enumerate(albums):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.markdown(f"📚 **{album.nom}**")
                        st.caption(f"Type : {album.type_album}")
                        if album.description:
                            st.caption(album.description[:100])
                        try:
                            stats = svc.obtenir_stats_album(album.id)
                            st.metric("Souvenirs", stats.get("nb_souvenirs", 0))
                        except Exception:
                            pass
                        if st.button("🗑️ Supprimer", key=_keys(f"del_a_{album.id}")):
                            try:
                                svc.delete(album.id)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
    except Exception as e:
        st.error(f"Erreur albums : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – AJOUTER SOUVENIR
# ═══════════════════════════════════════════════════════════


def _onglet_ajouter():
    """Formulaire d'ajout de souvenir."""
    st.subheader("📸 Ajouter un Souvenir")

    svc = _get_service()

    try:
        albums = svc.list_all()
        options_albums = {a.nom: a.id for a in albums} if albums else {}
    except Exception:
        options_albums = {}

    with st.form(_keys("form_souvenir")):
        titre = st.text_input("Titre *", key=_keys("sv_titre"))
        col1, col2 = st.columns(2)
        with col1:
            date_souvenir = st.date_input("Date", value=date.today(), key=_keys("sv_date"))
            emotion = st.selectbox("Émotion", options=EMOTIONS, key=_keys("sv_emotion"))
        with col2:
            if options_albums:
                album_choisi = st.selectbox(
                    "Album", options=list(options_albums.keys()), key=_keys("sv_album")
                )
            else:
                album_choisi = None
                st.info("Créez d'abord un album.")
            participants = st.multiselect(
                "Participants",
                options=["Jules", "Anne", "Mathieu", "Famille élargie", "Amis"],
                key=_keys("sv_participants"),
            )
        description = st.text_area("Description / anecdote", key=_keys("sv_desc"))

        if st.form_submit_button("💾 Enregistrer", type="primary"):
            if not titre:
                st.warning("Le titre est requis.")
            elif not album_choisi:
                st.warning("Sélectionnez un album.")
            else:
                try:
                    svc.ajouter_souvenir(
                        {
                            "titre": titre,
                            "date_souvenir": date_souvenir,
                            "emotion": emotion,
                            "description": description or None,
                            "participants": participants,
                            "album_id": options_albums[album_choisi],
                        }
                    )
                    st.success(f"✅ Souvenir « {titre} » ajouté !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("album_souvenirs")
def app():
    """Point d'entrée Album Souvenirs."""
    st.title("📸 Album & Souvenirs")
    st.caption("Gardez précieusement les moments familiaux")

    with error_boundary(titre="Erreur album souvenirs"):
        TAB_LABELS = ["📅 Timeline", "📚 Albums", "📸 Ajouter"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_timeline()
        with tabs[1]:
            _onglet_albums()
        with tabs[2]:
            _onglet_ajouter()
