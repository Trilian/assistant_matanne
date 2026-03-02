"""
Contacts Famille – Répertoire familial par catégorie.

Catégories: médical, garde, éducation, administration, famille, urgence.
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
_keys = KeyNamespace("contacts_famille")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.contacts import obtenir_service_contacts

        _service = obtenir_service_contacts()
    return _service


CATEGORIES = ["medical", "garde", "education", "administration", "famille", "urgence"]
EMOJIS_CAT = {
    "medical": "🏥",
    "garde": "👶",
    "education": "📚",
    "administration": "🏛️",
    "famille": "👨‍👩‍👧",
    "urgence": "🚨",
}


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – RÉPERTOIRE
# ═══════════════════════════════════════════════════════════


def _onglet_repertoire():
    """Répertoire contacts par catégorie."""
    st.subheader("📇 Répertoire Familial")

    svc = _get_service()

    # Recherche
    recherche = st.text_input("🔍 Rechercher un contact", key=_keys("recherche"))

    try:
        if recherche:
            contacts = svc.rechercher(recherche)
        else:
            contacts = svc.list_all()

        if not contacts:
            etat_vide("Aucun contact enregistré", icone="📇")
            return

        # Grouper par catégorie
        par_categorie: dict[str, list[object]] = {}
        for c in contacts:
            cat = c.categorie or "autre"
            par_categorie.setdefault(cat, []).append(c)

        for cat in CATEGORIES:
            contacts_cat = par_categorie.get(cat, [])
            if not contacts_cat:
                continue

            emoji = EMOJIS_CAT.get(cat, "📋")
            with st.expander(
                f"{emoji} {cat.replace('_', ' ').title()} ({len(contacts_cat)})", expanded=True
            ):
                for c in sorted(contacts_cat, key=lambda x: x.nom):
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            urgence = "🚨 " if c.est_urgence else ""
                            st.markdown(f"{urgence}**{c.nom_complet}**")
                            if c.specialite:
                                st.caption(f"🔬 {c.specialite}")
                        with col2:
                            if c.telephone:
                                st.write(f"📞 {c.telephone}")
                            if c.email:
                                st.write(f"📧 {c.email}")
                            if c.adresse:
                                st.caption(f"📍 {c.adresse}")
                        with col3:
                            if st.button("🗑️", key=_keys(f"del_{c.id}")):
                                try:
                                    svc.delete(c.id)
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – AJOUT/ÉDITION
# ═══════════════════════════════════════════════════════════


def _onglet_ajout():
    """Formulaire d'ajout de contact."""
    st.subheader("➕ Ajouter un contact")

    svc = _get_service()

    with st.form(_keys("form_contact")):
        col1, col2 = st.columns(2)
        with col1:
            prenom = st.text_input("Prénom *", key=_keys("c_prenom"))
            nom = st.text_input("Nom *", key=_keys("c_nom"))
            categorie = st.selectbox("Catégorie *", options=CATEGORIES, key=_keys("c_cat"))
            specialite = st.text_input("Spécialité", key=_keys("c_spe"))
        with col2:
            telephone = st.text_input("Téléphone", key=_keys("c_tel"))
            email = st.text_input("Email", key=_keys("c_email"))
            adresse = st.text_input("Adresse", key=_keys("c_adresse"))
            est_urgence = st.checkbox("Contact d'urgence", key=_keys("c_urgence"))

        notes = st.text_area("Notes", key=_keys("c_notes"))

        if st.form_submit_button("💾 Enregistrer", type="primary"):
            if not prenom or not nom:
                st.warning("Prénom et nom sont requis.")
            else:
                try:
                    svc.create(
                        {
                            "prenom": prenom,
                            "nom": nom,
                            "categorie": categorie,
                            "specialite": specialite or None,
                            "telephone": telephone or None,
                            "email": email or None,
                            "adresse": adresse or None,
                            "est_urgence": est_urgence,
                            "notes": notes or None,
                        }
                    )
                    st.success(f"✅ Contact {prenom} {nom} ajouté !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – URGENCES
# ═══════════════════════════════════════════════════════════


def _onglet_urgences():
    """Vue rapide contacts d'urgence."""
    st.subheader("🚨 Contacts d'Urgence")

    svc = _get_service()

    try:
        contacts = svc.list_all()
        urgences = [c for c in contacts if c.est_urgence]

        if not urgences:
            etat_vide("Aucun contact d'urgence défini", icone="🚨")
            st.info("Marquez des contacts comme 'urgence' dans l'onglet Ajout.")
            return

        # Numéros essentiels
        st.markdown("#### 📞 Numéros rapides")
        for c in urgences:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"🚨 **{c.nom_complet}**")
                    if c.specialite:
                        st.caption(c.specialite)
                with col2:
                    if c.telephone:
                        st.markdown(f"📞 **{c.telephone}**")

        # Numéros nationaux
        st.markdown("---")
        st.markdown("#### 📞 Numéros nationaux")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("SAMU", "15")
        with col2:
            st.metric("Pompiers", "18")
        with col3:
            st.metric("Urgences EU", "112")

        col4, col5 = st.columns(2)
        with col4:
            st.metric("Centre antipoison", "01 40 05 48 48")
        with col5:
            st.metric("SOS Médecins", "3624")

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("contacts_famille")
def app():
    """Point d'entrée Contacts Famille."""
    st.title("📇 Contacts Famille")
    st.caption("Répertoire familial centralisé avec accès rapide urgences")

    with error_boundary(titre="Erreur contacts famille"):
        TAB_LABELS = ["📇 Répertoire", "➕ Ajouter", "🚨 Urgences"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_repertoire()
        with tabs[1]:
            _onglet_ajout()
        with tabs[2]:
            _onglet_urgences()
