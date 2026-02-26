"""
Paramètres - Sécurité & Confidentialité.

Verrouillage PIN, purge automatique, journal des connexions.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.core.state import obtenir_etat
from src.core.state.persistent import PersistentState, persistent_state
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_securite")


@persistent_state(key="securite_config", sync_interval=30, auto_commit=True)
def _obtenir_config_securite() -> dict:
    """Valeurs par défaut de la config sécurité (purge)."""
    return {
        "purge_automatique": False,
        "purge_delai_jours": 90,
        "derniere_purge": None,
    }


@ui_fragment
def afficher_securite_config():
    """Configuration sécurité et confidentialité."""
    from src.services.profils import SECTIONS_PROTEGER, ProfilService

    st.markdown("### 🔒 Sécurité & Confidentialité")
    st.caption("Verrouillage PIN, purge automatique, journal des connexions")

    etat = obtenir_etat()

    # Trouver le profil actif
    profils = ProfilService.obtenir_profils()
    profil_actif = None
    for p in profils:
        if p.display_name == etat.nom_utilisateur or p.username == etat.nom_utilisateur.lower():
            profil_actif = p
            break
    if not profil_actif and profils:
        profil_actif = profils[0]

    if not profil_actif:
        st.warning("Aucun profil trouvé.")
        return

    # ── Section 1: Verrouillage PIN ──
    st.markdown("#### 🔐 Verrouillage PIN")

    pin_actif = profil_actif.pin_hash is not None
    sections_protegees = profil_actif.sections_protegees or []

    st.write(
        f"**Statut :** {'🟢 Activé' if pin_actif else '🔴 Désactivé'} "
        f"pour **{profil_actif.display_name}**"
    )

    if pin_actif:
        # Gestion sections protégées
        nouvelles_sections = st.multiselect(
            "Sections protégées par PIN",
            SECTIONS_PROTEGER,
            default=sections_protegees,
            key=_keys("sections_protegees"),
        )

        col_pin1, col_pin2 = st.columns(2)
        with col_pin1:
            if st.button("💾 Sauvegarder sections", key=_keys("save_sections")):
                if ProfilService.definir_sections_protegees(
                    profil_actif.username, nouvelles_sections
                ):
                    afficher_succes("✅ Sections protégées mises à jour")
                else:
                    afficher_erreur("❌ Erreur")

        with col_pin2:
            if st.button("🗑️ Supprimer le PIN", key=_keys("del_pin"), type="secondary"):
                if ProfilService.supprimer_pin(profil_actif.username):
                    afficher_succes("✅ PIN supprimé")
                else:
                    afficher_erreur("❌ Erreur")

        # Changer le PIN
        with st.expander("🔄 Changer le PIN"):
            with st.form("change_pin_form"):
                ancien_pin = st.text_input(
                    "PIN actuel", type="password", max_chars=6, key=_keys("ancien_pin")
                )
                nouveau_pin = st.text_input(
                    "Nouveau PIN (4-6 chiffres)",
                    type="password",
                    max_chars=6,
                    key=_keys("nouveau_pin"),
                )
                confirmer_pin = st.text_input(
                    "Confirmer le nouveau PIN",
                    type="password",
                    max_chars=6,
                    key=_keys("confirm_pin"),
                )

                if st.form_submit_button("Changer le PIN"):
                    if not ProfilService.verifier_pin(profil_actif.username, ancien_pin):
                        afficher_erreur("❌ PIN actuel incorrect")
                    elif len(nouveau_pin) < 4 or not nouveau_pin.isdigit():
                        afficher_erreur("❌ Le PIN doit contenir 4-6 chiffres")
                    elif nouveau_pin != confirmer_pin:
                        afficher_erreur("❌ Les PINs ne correspondent pas")
                    else:
                        ProfilService.definir_pin(profil_actif.username, nouveau_pin)
                        afficher_succes("✅ PIN changé avec succès")
    else:
        # Définir un nouveau PIN
        with st.form("new_pin_form"):
            st.markdown("##### Définir un PIN")
            nouveau_pin = st.text_input(
                "PIN (4-6 chiffres)",
                type="password",
                max_chars=6,
                key=_keys("new_pin"),
            )
            confirmer_pin = st.text_input(
                "Confirmer le PIN",
                type="password",
                max_chars=6,
                key=_keys("new_confirm"),
            )

            if st.form_submit_button("🔐 Activer le PIN", type="primary"):
                if len(nouveau_pin) < 4 or not nouveau_pin.isdigit():
                    afficher_erreur("❌ Le PIN doit contenir 4-6 chiffres")
                elif nouveau_pin != confirmer_pin:
                    afficher_erreur("❌ Les PINs ne correspondent pas")
                else:
                    ProfilService.definir_pin(profil_actif.username, nouveau_pin)
                    afficher_succes("✅ PIN activé avec succès !")

    # ── Section 2: Purge automatique ──
    st.markdown("---")
    st.markdown("#### 🧹 Purge automatique des données")

    pstate: PersistentState = _obtenir_config_securite()
    config_purge = pstate.get_all()

    purge_active = st.toggle(
        "Activer la purge automatique",
        value=config_purge.get("purge_automatique", False),
        key=_keys("purge_toggle"),
    )

    if purge_active:
        delais = {30: "30 jours", 90: "90 jours", 180: "6 mois", 365: "1 an"}
        delai_actuel = config_purge.get("purge_delai_jours", 90)

        delai = st.selectbox(
            "Supprimer les données plus anciennes que",
            list(delais.keys()),
            format_func=lambda x: delais[x],
            index=list(delais.keys()).index(delai_actuel) if delai_actuel in delais else 1,
            key=_keys("purge_delai"),
        )

        derniere_purge = config_purge.get("derniere_purge")
        if derniere_purge:
            st.caption(f"📅 Dernière purge : {derniere_purge}")
        else:
            st.caption("📅 Aucune purge effectuée")

        # Sauvegarder config purge
        if st.button("💾 Sauvegarder", key=_keys("save_purge")):
            pstate.update(
                {
                    "purge_automatique": purge_active,
                    "purge_delai_jours": delai,
                }
            )
            pstate.commit()
            afficher_succes("✅ Configuration de purge sauvegardée")

        # Bouton purge manuelle
        st.markdown("---")
        st.warning(
            "⚠️ La purge manuelle supprimera définitivement les données "
            f"de plus de **{delais.get(delai, delai)} jours**."
        )
        if st.button("🗑️ Purger maintenant", type="primary", key=_keys("btn_purge")):
            st.info("🧹 Purge manuelle non encore implémentée (placeholder)")
            # TODO: Implémenter la purge réelle des tables
    else:
        if st.button("💾 Désactiver la purge", key=_keys("save_no_purge")):
            pstate.update({"purge_automatique": False})
            pstate.commit()
            afficher_succes("✅ Purge automatique désactivée")

    # ── Section 3: Journal des connexions ──
    st.markdown("---")
    st.markdown("#### 📋 Journal des connexions")

    try:
        from src.core.decorators import avec_session_db
        from src.core.models.systeme import HistoriqueAction

        @avec_session_db
        def _charger_connexions(*, db=None) -> list[dict]:
            actions = (
                db.query(HistoriqueAction)
                .filter(HistoriqueAction.action_type.in_(["connexion", "login", "profil.change"]))
                .order_by(HistoriqueAction.cree_le.desc())
                .limit(50)
                .all()
            )
            return [
                {
                    "Date": a.cree_le.strftime("%Y-%m-%d %H:%M") if a.cree_le else "—",
                    "Profil": a.user_name,
                    "Action": a.action_type,
                    "Description": a.description[:80] if a.description else "—",
                }
                for a in actions
            ]

        connexions = _charger_connexions()
        if connexions:
            import pandas as pd

            df = pd.DataFrame(connexions)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune connexion enregistrée.")
    except Exception as e:
        logger.debug("Journal connexions non disponible: %s", e)
        st.info("Journal des connexions non disponible.")
