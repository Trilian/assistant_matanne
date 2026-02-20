"""
Module Scan Factures - Interface Streamlit

Scan et extraction OCR de factures d'énergie (EDF, Engie, Veolia).
Utilise Mistral Vision pour l'extraction automatique de données.
"""

import base64
import logging
from datetime import date

import streamlit as st

from src.core.session_keys import SK
from src.ui import etat_vide

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

FOURNISSEURS_ICON = {
    "edf": "⚡",
    "engie": "🔥",
    "totalenergies": "⚡",
    "veolia": "💧",
    "eau de paris": "💧",
    "suez": "💧",
}

TYPE_ENERGIE_LABEL = {
    "electricite": "⚡ Électricité",
    "gaz": "🔥 Gaz",
    "eau": "💧 Eau",
    "autre": "📄 Autre",
}


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def _afficher_confiance(confiance: float):
    """Affiche un indicateur de confiance visuel."""
    pourcent = int(confiance * 100)
    if pourcent >= 80:
        couleur = "🟢"
        label = "Haute"
    elif pourcent >= 50:
        couleur = "🟡"
        label = "Moyenne"
    else:
        couleur = "🔴"
        label = "Faible"

    st.caption(f"{couleur} Confiance: {pourcent}% ({label})")


def _afficher_resultat(donnees):
    """Affiche les données extraites d'une facture."""
    if donnees is None:
        st.error("Aucune donnée extraite")
        return

    # En-tête fournisseur
    fournisseur = donnees.fournisseur or "Inconnu"
    icon = FOURNISSEURS_ICON.get(fournisseur.lower(), "📄")
    type_label = TYPE_ENERGIE_LABEL.get(donnees.type_energie, "📄 Autre")

    st.markdown(f"### {icon} {fournisseur}")
    st.caption(type_label)

    # Métriques principales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Montant TTC", f"{donnees.montant_ttc:.2f} €")
    with col2:
        if donnees.consommation:
            st.metric(
                "📊 Consommation",
                f"{donnees.consommation:.0f} {donnees.unite_consommation}",
            )
        else:
            st.metric("📊 Consommation", "—")
    with col3:
        if donnees.prix_kwh:
            st.metric("💶 Prix unitaire", f"{donnees.prix_kwh:.4f} €")
        elif donnees.abonnement:
            st.metric("📋 Abonnement", f"{donnees.abonnement:.2f} €")
        else:
            st.metric("📋 Abonnement", "—")

    # Période et références
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**📅 Période**")
        if donnees.date_debut and donnees.date_fin:
            st.write(f"{donnees.date_debut} → {donnees.date_fin}")
        elif donnees.mois_facturation and donnees.annee_facturation:
            st.write(f"{donnees.mois_facturation:02d}/{donnees.annee_facturation}")
        else:
            st.write("Non disponible")

    with col_b:
        st.markdown("**📋 Références**")
        if donnees.numero_facture:
            st.write(f"Facture: {donnees.numero_facture}")
        if donnees.numero_client:
            st.write(f"Client: {donnees.numero_client}")
        if not donnees.numero_facture and not donnees.numero_client:
            st.write("Non disponible")

    # Confiance
    _afficher_confiance(donnees.confiance)

    # Erreurs éventuelles
    if donnees.erreurs:
        with st.expander("⚠️ Avertissements", expanded=False):
            for err in donnees.erreurs:
                st.warning(err)


def _afficher_historique():
    """Affiche l'historique des factures scannées."""
    historique = st.session_state.get(SK.HISTORIQUE_FACTURES, [])

    if not historique:
        etat_vide("Aucune facture scannée", "📄", "Utilisez l'onglet Scanner pour commencer")
        return

    for i, facture in enumerate(reversed(historique)):
        donnees = facture.get("donnees")
        date_scan = facture.get("date_scan", "")

        if donnees:
            icon = FOURNISSEURS_ICON.get(donnees.fournisseur.lower(), "📄")
            with st.expander(
                f"{icon} {donnees.fournisseur} - {donnees.montant_ttc:.2f}€ ({date_scan})"
            ):
                _afficher_resultat(donnees)
        else:
            st.warning(f"Scan échoué ({date_scan})")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée module scan factures."""
    st.title("🧾 Scan de Factures")
    st.caption("Extraction automatique des données de factures énergie par IA")

    # Initialiser l'état
    if SK.HISTORIQUE_FACTURES not in st.session_state:
        st.session_state[SK.HISTORIQUE_FACTURES] = []

    # Onglets
    onglet_scan, onglet_historique = st.tabs(["📷 Scanner", "📋 Historique"])

    # ─── Onglet Scanner ───
    with onglet_scan:
        st.markdown("### 📤 Charger une facture")
        st.markdown(
            "Prenez en photo votre facture **EDF**, **Engie**, **Veolia** ou autre "
            "et l'IA extraira automatiquement les données."
        )

        fichier = st.file_uploader(
            "Charger une image de facture",
            type=["png", "jpg", "jpeg", "webp"],
            help="Formats acceptés: PNG, JPG, JPEG, WebP",
        )

        if fichier is not None:
            # Afficher l'image
            col_img, col_action = st.columns([2, 1])
            with col_img:
                st.image(fichier, caption="Facture chargée", use_container_width=True)

            with col_action:
                st.markdown("**Informations fichier**")
                st.caption(f"📁 {fichier.name}")
                st.caption(f"📐 {fichier.size / 1024:.1f} Ko")

                if st.button("🔍 Extraire les données", type="primary", use_container_width=True):
                    with st.spinner("🤖 Analyse IA en cours..."):
                        try:
                            # Encoder en base64
                            image_bytes = fichier.getvalue()
                            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

                            # Appeler le service OCR
                            from src.services.integrations.facture import (
                                get_facture_ocr_service,
                            )

                            service = get_facture_ocr_service()
                            resultat = service.extraire_donnees_facture_sync(image_b64)

                            if resultat.succes and resultat.donnees:
                                st.success("✅ Extraction réussie !")

                                # Sauvegarder dans l'historique
                                st.session_state[SK.HISTORIQUE_FACTURES].append(
                                    {
                                        "donnees": resultat.donnees,
                                        "date_scan": date.today().isoformat(),
                                        "fichier": fichier.name,
                                    }
                                )

                                # Afficher le résultat
                                st.markdown("---")
                                _afficher_resultat(resultat.donnees)

                                # Bouton pour sauvegarder dans les charges
                                st.markdown("---")
                                if st.button(
                                    "💾 Ajouter aux charges",
                                    help="Enregistrer cette facture dans le suivi des charges",
                                ):
                                    st.info(
                                        "💡 Intégration avec le module Charges à venir. "
                                        "Les données sont sauvegardées dans l'historique."
                                    )
                            else:
                                st.error(f"❌ Échec: {resultat.message}")
                                if resultat.texte_brut:
                                    with st.expander("📝 Réponse brute IA"):
                                        st.code(resultat.texte_brut)

                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                            logger.error(f"Erreur scan facture: {e}")

        else:
            # Guide d'utilisation
            st.markdown("---")
            st.markdown("#### 💡 Conseils pour un bon scan")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    """
                    **✅ À faire:**
                    - Photo bien éclairée
                    - Facture à plat, entière
                    - Texte lisible et net
                    """
                )
            with col2:
                st.markdown(
                    """
                    **❌ À éviter:**
                    - Photo floue ou sombre
                    - Facture pliée ou coupée
                    - Reflets sur le papier
                    """
                )

            st.info(
                "🏷️ **Fournisseurs supportés:** EDF, Engie, TotalEnergies, Veolia, "
                "Eau de Paris, Suez et la plupart des fournisseurs français."
            )

    # ─── Onglet Historique ───
    with onglet_historique:
        st.markdown("### 📋 Historique des scans")
        historique = st.session_state.get(SK.HISTORIQUE_FACTURES, [])

        if historique:
            st.caption(f"{len(historique)} facture(s) scannée(s)")

            if st.button("🗑️ Effacer l'historique"):
                st.session_state[SK.HISTORIQUE_FACTURES] = []
                st.rerun()

        _afficher_historique()
