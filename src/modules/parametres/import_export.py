"""
Paramètres - Import / Export de configuration.

Export JSON, import avec validation et preview, réinitialisation par section.
"""

from __future__ import annotations

import json
import logging

import streamlit as st

from src.core.state import obtenir_etat
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_io")

_SECTIONS_REINIT = {
    "preferences_modules": "🎯 Préférences par module",
    "securite": "🔒 Sécurité (PIN + sections protégées)",
    "notifications": "🔔 Notifications",
}


@ui_fragment
def afficher_import_export():
    """Import / Export de configuration."""
    from src.services.profils import ProfilService

    st.markdown("### 📦 Import / Export")
    st.caption("Sauvegarde et restauration de la configuration du profil")

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

    # ── Section 1: Export ──
    st.markdown("#### 📤 Exporter la configuration")
    st.write(f"Profil actif : **{profil_actif.avatar_emoji} {profil_actif.display_name}**")

    sections_export = st.multiselect(
        "Sections à exporter",
        ["profil", "sante", "notifications"],
        default=["profil", "sante", "notifications"],
        key=_keys("sections_export"),
    )

    if st.button("📥 Générer l'export", key=_keys("btn_export")):
        try:
            export = ProfilService.exporter_configuration(profil_actif.username)
            if export:
                # Filtrer les sections non demandées
                export_filtre = {"version": export["version"], "timestamp": export["timestamp"]}
                for section in sections_export:
                    if section in export:
                        export_filtre[section] = export[section]

                json_str = json.dumps(export_filtre, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ Télécharger le fichier JSON",
                    json_str.encode("utf-8"),
                    f"config_{profil_actif.username}_{export['timestamp'][:10]}.json",
                    "application/json",
                    key=_keys("dl_export"),
                )
                with st.expander("👁️ Aperçu de l'export"):
                    st.json(export_filtre)
            else:
                afficher_erreur("❌ Erreur lors de la génération de l'export")
        except Exception as e:
            logger.error("Erreur export: %s", e)
            afficher_erreur(f"❌ Erreur: {e}")

    # ── Section 2: Import ──
    st.markdown("---")
    st.markdown("#### 📥 Importer une configuration")

    fichier = st.file_uploader(
        "Fichier JSON de configuration",
        type=["json"],
        key=_keys("file_upload"),
    )

    if fichier is not None:
        try:
            data = json.loads(fichier.read().decode("utf-8"))

            # Validation basique
            if "version" not in data:
                st.error("❌ Fichier invalide : pas de champ 'version'")
                return

            st.success(f"✅ Fichier valide (version {data['version']})")

            # Preview des changements
            st.markdown("##### 📋 Aperçu des données à importer")
            with st.expander("Contenu du fichier", expanded=True):
                st.json(data)

            # Résumé
            sections_presentes = [k for k in data if k not in ("version", "timestamp")]
            st.info(f"Sections trouvées : {', '.join(sections_presentes)}")

            # Confirmation
            st.warning("⚠️ L'import écrasera les données actuelles des sections correspondantes.")

            if st.button(
                "🔄 Importer la configuration",
                type="primary",
                key=_keys("btn_import"),
            ):
                succes, message = ProfilService.importer_configuration(profil_actif.username, data)
                if succes:
                    afficher_succes(f"✅ {message}")
                    # Invalider cache sidebar
                    st.session_state.pop("profils_disponibles", None)
                else:
                    afficher_erreur(f"❌ {message}")

        except json.JSONDecodeError:
            st.error("❌ Le fichier n'est pas un JSON valide")
        except Exception as e:
            logger.error("Erreur import: %s", e)
            afficher_erreur(f"❌ Erreur: {e}")

    # ── Section 3: Réinitialisation ──
    st.markdown("---")
    st.markdown("#### 🔄 Réinitialisation")
    st.caption("Remet une section aux valeurs par défaut")

    section_choisie = st.selectbox(
        "Section à réinitialiser",
        list(_SECTIONS_REINIT.keys()),
        format_func=lambda x: _SECTIONS_REINIT[x],
        key=_keys("section_reinit"),
    )

    st.warning(
        f"⚠️ Cette action réinitialisera **{_SECTIONS_REINIT[section_choisie]}** "
        f"pour le profil **{profil_actif.display_name}**."
    )

    col_r1, col_r2 = st.columns([3, 1])
    with col_r2:
        if st.button(
            "🗑️ Réinitialiser",
            type="primary",
            key=_keys("btn_reinit"),
        ):
            succes, message = ProfilService.reinitialiser_section(
                profil_actif.username, section_choisie
            )
            if succes:
                afficher_succes(f"✅ {message}")
            else:
                afficher_erreur(f"❌ {message}")
