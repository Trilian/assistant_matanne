"""
Module Annuaire Contacts — Répertoire des contacts utiles de la famille.

Médecins, artisans, urgences, écoles, voisins... avec catégories,
recherche et liens cliquables pour appeler directement.
"""

import logging

import streamlit as st

from src.core.models.utilitaires import CategorieContact
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_contacts_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("annuaire")

CATEGORIE_EMOJIS = {
    "sante": "🏥",
    "education": "🎓",
    "urgence": "🚨",
    "artisan": "🔧",
    "voisin": "🏘️",
    "administratif": "📄",
    "famille": "👨‍👩‍👧‍👦",
    "autre": "📇",
}


@profiler_rerun("annuaire_contacts")
def app():
    """Point d'entrée module Annuaire Contacts."""
    st.title("📇 Annuaire Contacts Utiles")
    st.caption("Répertoire familial : médecins, artisans, urgences...")

    with error_boundary(titre="Erreur annuaire"):
        service = get_contacts_service()

        # Barre de recherche et filtres
        col1, col2 = st.columns([3, 1])
        with col1:
            recherche = st.text_input(
                "🔍 Rechercher",
                placeholder="Nom, spécialité...",
                key=_keys("recherche"),
            )
        with col2:
            filtre_cat = st.selectbox(
                "Catégorie",
                options=["Toutes"] + [c.value for c in CategorieContact],
                key=_keys("filtre_cat"),
            )

        # Ajouter un contact
        with st.expander("➕ Nouveau contact", expanded=False):
            _formulaire_contact(service)

        st.divider()

        # Liste des contacts
        cat = None if filtre_cat == "Toutes" else filtre_cat
        contacts = service.lister(categorie=cat, recherche=recherche or None)

        if not contacts:
            st.info("📇 Aucun contact trouvé. Ajoutez votre premier contact ci-dessus !")
            return

        # Grouper par catégorie
        par_categorie = {}
        for c in contacts:
            cat_key = c.categorie or "autre"
            if cat_key not in par_categorie:
                par_categorie[cat_key] = []
            par_categorie[cat_key].append(c)

        for cat_key, items in sorted(par_categorie.items()):
            emoji = CATEGORIE_EMOJIS.get(cat_key, "📇")
            st.subheader(f"{emoji} {cat_key.replace('_', ' ').capitalize()}")

            for contact in items:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{contact.nom}**")
                        if contact.specialite:
                            st.caption(f"🏷️ {contact.specialite}")
                        if contact.adresse:
                            st.caption(f"📍 {contact.adresse}")
                    with col2:
                        if contact.telephone:
                            tel_clean = contact.telephone.replace(" ", "").replace(".", "")
                            st.markdown(f"📞 [{contact.telephone}](tel:{tel_clean})")
                        if contact.email:
                            st.markdown(f"✉️ [{contact.email}](mailto:{contact.email})")
                    with col3:
                        if contact.notes:
                            st.caption(f"📝 {contact.notes}")
                        if st.button("🗑️", key=_keys("del", str(contact.id)), help="Supprimer"):
                            service.supprimer(contact.id)
                            st.rerun()


def _formulaire_contact(service):
    """Formulaire d'ajout/édition de contact."""
    with st.form("form_contact", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom *", key=_keys("new_nom"))
            telephone = st.text_input(
                "Téléphone",
                placeholder="06 12 34 56 78",
                key=_keys("new_tel"),
            )
            email = st.text_input("Email", key=_keys("new_email"))
        with col2:
            categorie = st.selectbox(
                "Catégorie",
                options=[c.value for c in CategorieContact],
                key=_keys("new_cat"),
            )
            specialite = st.text_input(
                "Spécialité",
                placeholder="Pédiatre, Plombier...",
                key=_keys("new_spec"),
            )
            adresse = st.text_input("Adresse", key=_keys("new_adresse"))

        notes = st.text_input("Notes", key=_keys("new_notes"))

        if st.form_submit_button("💾 Enregistrer", use_container_width=True):
            if nom:
                service.creer(
                    nom=nom,
                    categorie=categorie,
                    telephone=telephone or None,
                    email=email or None,
                    specialite=specialite or None,
                    adresse=adresse or None,
                    notes=notes or None,
                )
                st.success(f"✅ Contact '{nom}' ajouté !")
                st.rerun()
            else:
                st.warning("Le nom est obligatoire.")
