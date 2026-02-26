"""
Module Mots de Passe Maison — Coffre-fort familial sécurisé.

Stocke les mots de passe WiFi, codes d'alarme, digicodes, etc.
avec chiffrement Fernet. Protection par code PIN à 4 chiffres.
"""

import logging

import streamlit as st

from src.core.models.utilitaires import CategorieMotDePasse
from src.core.monitoring import profiler_rerun
from src.modules._framework import error_boundary
from src.services.utilitaires.service import get_mots_de_passe_service
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("mots_de_passe")


def _verifier_pin() -> bool:
    """Vérifie si l'utilisateur a entré le bon PIN."""
    if st.session_state.get("mdp_deverrouille"):
        return True
    return False


@profiler_rerun("mots_de_passe")
def app():
    """Point d'entrée module Mots de Passe."""
    st.title("🔐 Coffre-fort Mots de Passe")
    st.caption("Mots de passe WiFi, codes d'alarme, digicodes...")

    with error_boundary(titre="Erreur mots de passe"):
        service = get_mots_de_passe_service()

        # Écran de verrouillage
        if not _verifier_pin():
            _ecran_verrouillage()
            return

        # Interface principale
        col_header1, col_header2 = st.columns([3, 1])
        with col_header2:
            if st.button("🔒 Verrouiller", key=_keys("lock"), use_container_width=True):
                st.session_state["mdp_deverrouille"] = False
                st.rerun()

        # Ajouter un mot de passe
        with st.expander("➕ Ajouter un mot de passe", expanded=False):
            _formulaire_ajout(service)

        st.divider()

        # Liste des mots de passe
        mdps = service.lister()

        if not mdps:
            st.info("🔐 Aucun mot de passe enregistré. Ajoutez-en un ci-dessus.")
            return

        # Grouper par catégorie
        categories = {}
        for mdp in mdps:
            cat = mdp.categorie or "autre"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(mdp)

        for cat, items in sorted(categories.items()):
            cat_label = cat.replace("_", " ").capitalize()
            st.subheader(f"📁 {cat_label}")

            for mdp in items:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{mdp.nom}**")
                        if mdp.identifiant:
                            st.caption(f"👤 {mdp.identifiant}")
                    with col2:
                        # Affichage masqué par défaut
                        show_key = f"show_{mdp.id}"
                        if st.session_state.get(show_key, False):
                            try:
                                pin = st.session_state.get("mdp_pin", "1234")
                                mdp_clair = service.dechiffrer(mdp.valeur_chiffree, pin)
                                if mdp_clair:
                                    st.code(mdp_clair)
                                else:
                                    st.error("Déchiffrement impossible (PIN incorrect ?)")
                            except Exception:
                                st.error("Déchiffrement impossible")
                            if st.button(
                                "🙈 Masquer",
                                key=_keys("hide", str(mdp.id)),
                            ):
                                st.session_state[show_key] = False
                                st.rerun()
                        else:
                            st.markdown("••••••••")
                            if st.button(
                                "👁️ Voir",
                                key=_keys("show", str(mdp.id)),
                            ):
                                st.session_state[show_key] = True
                                st.rerun()
                    with col3:
                        if mdp.notes:
                            st.caption(f"📝 {mdp.notes}")
                        if st.button("🗑️", key=_keys("del", str(mdp.id)), help="Supprimer"):
                            service.supprimer(mdp.id)
                            st.rerun()


def _ecran_verrouillage():
    """Écran de saisie du PIN."""
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔒 Coffre verrouillé")
        st.caption("Entrez votre code PIN pour accéder aux mots de passe")

        pin = st.text_input(
            "Code PIN (4 chiffres)",
            type="password",
            max_chars=4,
            key=_keys("pin"),
        )

        if st.button("🔓 Déverrouiller", key=_keys("unlock"), use_container_width=True):
            # PIN par défaut: 1234 — à personnaliser
            pin_attendu = st.session_state.get("mdp_pin", "1234")
            if pin == pin_attendu:
                st.session_state["mdp_deverrouille"] = True
                st.rerun()
            else:
                st.error("❌ Code PIN incorrect")

        with st.expander("⚙️ Définir/Changer le PIN"):
            new_pin = st.text_input(
                "Nouveau PIN (4 chiffres)",
                type="password",
                max_chars=4,
                key=_keys("new_pin"),
            )
            if st.button("💾 Sauvegarder PIN", key=_keys("save_pin")):
                if new_pin and len(new_pin) == 4 and new_pin.isdigit():
                    st.session_state["mdp_pin"] = new_pin
                    st.success("PIN mis à jour !")
                else:
                    st.error("Le PIN doit être composé de 4 chiffres")


def _formulaire_ajout(service):
    """Formulaire d'ajout d'un mot de passe."""
    with st.form("form_mdp", clear_on_submit=True):
        nom = st.text_input("Nom", placeholder="WiFi maison, Alarme...", key=_keys("new_nom"))
        categorie = st.selectbox(
            "Catégorie",
            options=[c.value for c in CategorieMotDePasse],
            key=_keys("new_cat"),
        )
        identifiant = st.text_input(
            "Identifiant (optionnel)",
            placeholder="admin, user...",
            key=_keys("new_id"),
        )
        mot_de_passe = st.text_input(
            "Mot de passe",
            type="password",
            key=_keys("new_mdp"),
        )
        notes = st.text_input(
            "Notes",
            placeholder="Étage, emplacement...",
            key=_keys("new_notes"),
        )

        if st.form_submit_button("💾 Enregistrer", use_container_width=True):
            if nom and mot_de_passe:
                try:
                    pin = st.session_state.get("mdp_pin", "1234")
                    service.creer(
                        pin=pin,
                        valeur_claire=mot_de_passe,
                        nom=nom,
                        categorie=categorie,
                        identifiant=identifiant or None,
                        notes=notes or None,
                    )
                    st.success(f"🔐 '{nom}' enregistré !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            else:
                st.warning("Nom et mot de passe requis.")
