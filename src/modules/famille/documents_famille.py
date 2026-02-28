"""
Documents Famille – Coffre-fort numérique pour documents importants.

Onglets:
  1. Tous les documents (liste + recherche)
  2. Ajouter un document
  3. Alertes expiration
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
_keys = KeyNamespace("documents_famille")

_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.documents import obtenir_service_documents

        _service = obtenir_service_documents()
    return _service


TYPES_DOCUMENTS = [
    "carte_identite",
    "passeport",
    "carte_vitale",
    "mutuelle",
    "carnet_sante",
    "ordonnance",
    "certificat_naissance",
    "livret_famille",
    "contrat",
    "facture",
    "attestation",
    "assurance",
    "diplome",
    "autre",
]

EMOJIS_TYPE = {
    "carte_identite": "🪪",
    "passeport": "📘",
    "carte_vitale": "💚",
    "mutuelle": "🏥",
    "carnet_sante": "🩺",
    "ordonnance": "💊",
    "certificat_naissance": "👶",
    "livret_famille": "👨‍👩‍👧",
    "contrat": "📄",
    "facture": "🧾",
    "attestation": "📋",
    "assurance": "🛡️",
    "diplome": "🎓",
    "autre": "📎",
}


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – TOUS LES DOCUMENTS
# ═══════════════════════════════════════════════════════════


def _onglet_documents():
    """Liste et recherche de documents."""
    st.subheader("📁 Coffre-fort Documents")

    svc = _get_service()

    col1, col2 = st.columns(2)
    with col1:
        recherche = st.text_input("🔍 Rechercher", key=_keys("recherche"))
    with col2:
        filtre_type = st.selectbox(
            "Type",
            options=["Tous"] + TYPES_DOCUMENTS,
            key=_keys("filtre_type"),
        )

    try:
        documents = svc.list_all()

        if recherche:
            documents = [
                d
                for d in documents
                if recherche.lower() in (d.nom or "").lower()
                or recherche.lower() in (d.description or "").lower()
            ]

        if filtre_type != "Tous":
            documents = [d for d in documents if d.type_document == filtre_type]

        if not documents:
            etat_vide("Aucun document trouvé", icone="📁")
            return

        par_type: dict[str, list] = {}
        for d in documents:
            t = d.type_document or "autre"
            par_type.setdefault(t, []).append(d)

        for type_doc, docs in sorted(par_type.items()):
            emoji = EMOJIS_TYPE.get(type_doc, "📎")
            with st.expander(
                f"{emoji} {type_doc.replace('_', ' ').title()} ({len(docs)})",
                expanded=True,
            ):
                for doc in docs:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([4, 2, 1])
                        with col1:
                            st.markdown(f"**{doc.nom}**")
                            if doc.description:
                                st.caption(doc.description[:100])
                            if doc.membre_famille:
                                st.caption(f"👤 {doc.membre_famille}")
                        with col2:
                            if doc.date_expiration:
                                jours = doc.jours_avant_expiration
                                if jours is not None:
                                    if jours < 0:
                                        st.error(f"⛔ Expiré ({abs(jours)}j)")
                                    elif jours <= 30:
                                        st.warning(f"⚠️ Expire dans {jours}j")
                                    else:
                                        st.info(f"📅 {doc.date_expiration}")
                            if doc.tags:
                                st.caption(f"🏷️ {', '.join(doc.tags)}")
                        with col3:
                            if st.button("🗑️", key=_keys(f"del_{doc.id}")):
                                try:
                                    svc.delete(doc.id)
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))

    except Exception as e:
        st.error(f"Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – AJOUTER
# ═══════════════════════════════════════════════════════════


def _onglet_ajouter():
    """Formulaire d'ajout de document."""
    st.subheader("➕ Ajouter un Document")

    svc = _get_service()

    with st.form(_keys("form_doc")):
        nom = st.text_input("Nom du document *", key=_keys("doc_nom"))
        col1, col2 = st.columns(2)
        with col1:
            type_doc = st.selectbox("Type *", options=TYPES_DOCUMENTS, key=_keys("doc_type"))
            membre = st.selectbox(
                "Membre", ["Famille", "Jules", "Anne", "Mathieu"], key=_keys("doc_membre")
            )
            numero_document = st.text_input("N° de document", key=_keys("doc_numero"))
        with col2:
            date_emission = st.date_input(
                "Date d'émission", value=date.today(), key=_keys("doc_emission")
            )
            date_expiration = st.date_input(
                "Date d'expiration (optionnel)", value=None, key=_keys("doc_expiration")
            )
            organisme = st.text_input("Organisme émetteur", key=_keys("doc_organisme"))

        description = st.text_area("Description / notes", key=_keys("doc_desc"))
        tags = st.text_input("Tags (séparés par virgule)", key=_keys("doc_tags"))

        if st.form_submit_button("💾 Enregistrer", type="primary"):
            if not nom:
                st.warning("Le nom est requis.")
            else:
                try:
                    tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
                    svc.create(
                        {
                            "nom": nom,
                            "type_document": type_doc,
                            "membre_famille": membre,
                            "numero_document": numero_document or None,
                            "date_emission": date_emission,
                            "date_expiration": date_expiration,
                            "organisme_emetteur": organisme or None,
                            "description": description or None,
                            "tags": tags_list,
                        }
                    )
                    st.success(f"✅ Document « {nom} » ajouté !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – ALERTES EXPIRATION
# ═══════════════════════════════════════════════════════════


def _onglet_alertes():
    """Alertes documents expirant bientôt."""
    st.subheader("⚠️ Alertes Expiration")

    svc = _get_service()

    try:
        documents = svc.list_all()

        expires = [d for d in documents if d.est_expire]
        expirant = [
            d
            for d in documents
            if d.date_expiration
            and not d.est_expire
            and d.jours_avant_expiration is not None
            and d.jours_avant_expiration <= 90
        ]

        if not expires and not expirant:
            st.success("✅ Aucun document expiré ou expirant bientôt !")
            return

        if expires:
            st.markdown("#### ⛔ Documents expirés")
            for d in expires:
                emoji = EMOJIS_TYPE.get(d.type_document, "📎")
                st.error(
                    f"{emoji} **{d.nom}** — Expiré le {d.date_expiration} "
                    f"({abs(d.jours_avant_expiration)}j) • {d.membre_famille or ''}"
                )

        if expirant:
            st.markdown("#### ⚠️ Expiration prochaine")
            for d in sorted(expirant, key=lambda x: x.jours_avant_expiration or 0):
                emoji = EMOJIS_TYPE.get(d.type_document, "📎")
                jours = d.jours_avant_expiration
                if jours <= 30:
                    st.warning(
                        f"{emoji} **{d.nom}** — Expire dans {jours}j • {d.membre_famille or ''}"
                    )
                else:
                    st.info(
                        f"{emoji} **{d.nom}** — Expire dans {jours}j • {d.membre_famille or ''}"
                    )

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Total documents", len(documents))
        with col2:
            st.metric("⛔ Expirés", len(expires))
        with col3:
            st.metric("⚠️ Expirant < 90j", len(expirant))

    except Exception as e:
        st.error(f"Erreur alertes : {e}")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("documents_famille")
def app():
    """Point d'entrée Documents Famille."""
    st.title("📁 Documents Famille")
    st.caption("Coffre-fort numérique pour tous vos documents importants")

    with error_boundary(titre="Erreur documents famille"):
        TAB_LABELS = ["📁 Documents", "➕ Ajouter", "⚠️ Alertes"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_documents()
        with tabs[1]:
            _onglet_ajouter()
        with tabs[2]:
            _onglet_alertes()
