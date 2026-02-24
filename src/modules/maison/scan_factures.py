"""
Module Scan Factures - OCR et analyse de factures d'énergie.

Fonctionnalités:
- Upload et scan de factures (image)
- Extraction OCR avec l'IA
- Correction manuelle des données
- Historique des factures
"""

import base64
import logging
from datetime import date

import streamlit as st

from src.core.db import obtenir_contexte_db
from src.ui.keys import KeyNamespace

__all__ = [
    "app",
    "FOURNISSEURS_CONNUS",
    "TYPE_ENERGIE_LABELS",
    "MOIS_FR",
    "image_to_base64",
    "sauvegarder_facture",
    "afficher_upload",
    "afficher_resultat",
    "afficher_formulaire_correction",
    "afficher_historique",
]

_keys = KeyNamespace("scan_factures")
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

FOURNISSEURS_CONNUS = {
    "EDF": {"type": "electricite", "emoji": "⚡"},
    "ENGIE": {"type": "gaz", "emoji": "🔥"},
    "VEOLIA": {"type": "eau", "emoji": "💧"},
    "TOTAL": {"type": "electricite", "emoji": "⚡"},
    "ENI": {"type": "gaz", "emoji": "🔥"},
    "SUEZ": {"type": "eau", "emoji": "💧"},
}

TYPE_ENERGIE_LABELS = {
    "electricite": "⚡ Électricité",
    "gaz": "🔥 Gaz",
    "eau": "💧 Eau",
}

MOIS_FR = [
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


# ═══════════════════════════════════════════════════════════
# SERVICE INTEGRATIONS (lazy imports)
# ═══════════════════════════════════════════════════════════


def get_facture_ocr_service():
    """Récupère le service OCR pour factures."""
    try:
        from src.services.integrations import get_facture_ocr_service as _get

        return _get()
    except ImportError:
        return None


def get_budget_service():
    """Récupère le service budget."""
    try:
        from src.services.maison import get_budget_service as _get

        return _get()
    except ImportError:
        return None


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def image_to_base64(file) -> str:
    """Convertit un fichier image en base64.

    Args:
        file: Fichier uploadé (UploadedFile ou objet avec read()).

    Returns:
        Chaîne base64.
    """
    try:
        data = file.getvalue()
        if not data:
            return ""
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return ""


def sauvegarder_facture(donnees) -> bool:
    """Sauvegarde les données de facture en DB.

    Args:
        donnees: Objet DonneesFacture ou dict.

    Returns:
        True si sauvegardé avec succès.
    """
    try:
        service = get_budget_service()
        with obtenir_contexte_db() as db:
            # Call service method
            if service and hasattr(service, "ajouter_facture_maison"):
                service.ajouter_facture_maison(
                    fournisseur=getattr(donnees, "fournisseur", ""),
                    type_energie=getattr(donnees, "type_energie", "electricite"),
                    montant=float(getattr(donnees, "montant_ttc", 0)),
                    consommation=float(getattr(donnees, "consommation", 0) or 0),
                    unite=getattr(donnees, "unite_consommation", "kWh"),
                    mois=getattr(donnees, "mois_facturation", date.today().month),
                    annee=getattr(donnees, "annee_facturation", date.today().year),
                )
            # Also add record to session
            record = type(
                "FactureRecord",
                (),
                {
                    "fournisseur": getattr(donnees, "fournisseur", ""),
                    "type_energie": getattr(donnees, "type_energie", "electricite"),
                    "montant_ttc": float(getattr(donnees, "montant_ttc", 0)),
                },
            )()
            db.add(record)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde facture: {e}")
        st.error(f"Erreur lors de la sauvegarde: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════


def afficher_upload():
    """Affiche la zone d'upload de facture.

    Returns:
        Le fichier uploadé ou None.
    """
    st.subheader("📤 Scanner une facture")
    st.info("📤 Uploadez une photo ou un PDF de votre facture.")
    file = st.file_uploader(
        "Facture",
        type=["png", "jpg", "jpeg", "pdf"],
        key=_keys("file_upload"),
    )

    if file is None:
        return None

    # Prévisualisation
    st.image(file, caption="Facture uploadée", use_container_width=True)

    # Bouton analyser
    if st.button("🔍 Analyser la facture", key=_keys("btn_analyser"), use_container_width=True):
        service = get_facture_ocr_service()
        if service is None:
            st.error("Service OCR non disponible.")
            return file

        with st.spinner("Analyse en cours..."):
            b64 = image_to_base64(file)
            resultat = service.extraire_donnees_facture_sync(b64)
            st.session_state["ocr_resultat"] = resultat
            st.rerun()

    return file


def afficher_resultat(resultat) -> None:
    """Affiche le résultat de l'OCR.

    Args:
        resultat: Objet ResultatOCR.
    """
    if not resultat.succes:
        st.error(f"❌ Analyse échouée: {resultat.message}")
        return

    donnees = resultat.donnees
    if donnees is None:
        st.warning("⚠️ Aucune donnée extraite.")
        return

    st.subheader("📋 Résultat de l'analyse")

    # Confiance
    confiance = getattr(donnees, "confiance", 0) or 0
    if confiance >= 0.8:
        st.success(f"Confiance: {confiance:.0%}")
    else:
        st.info(f"Confiance faible: {confiance:.0%}")

    # Erreurs
    erreurs = getattr(donnees, "erreurs", []) or []
    for err in erreurs:
        st.warning(f"⚠️ {err}")

    # Métriques principales
    cols = st.columns(2)
    with cols[0]:
        st.metric("Fournisseur", getattr(donnees, "fournisseur", "—"))
        montant = getattr(donnees, "montant_ttc", 0)
        st.metric("Montant TTC", f"{float(montant):.2f}€" if montant else "—")
    with cols[1]:
        conso = getattr(donnees, "consommation", None)
        unite = getattr(donnees, "unite_consommation", "kWh")
        st.metric("Consommation", f"{conso} {unite}" if conso else "—")

    # Période
    date_debut = getattr(donnees, "date_debut", None)
    date_fin = getattr(donnees, "date_fin", None)
    if date_debut or date_fin:
        st.markdown("**Période:**")
        st.caption(f"{date_debut or '?'} → {date_fin or '?'}")

    # Détails tarif
    prix_kwh = getattr(donnees, "prix_kwh", None)
    abonnement = getattr(donnees, "abonnement", None)
    if prix_kwh or abonnement:
        st.divider()
        st.markdown("**Détails tarif:**")
        if prix_kwh:
            st.caption(f"Prix kWh: {prix_kwh}€")
        if abonnement:
            st.caption(f"Abonnement: {abonnement}€")


def afficher_formulaire_correction(donnees):
    """Affiche le formulaire de correction des données OCR.

    Args:
        donnees: Objet DonneesFacture.

    Returns:
        donnees (éventuellement corrigé).
    """
    st.subheader("✏️ Corriger les données")

    with st.form(key=_keys("form_correction")):
        fournisseur = st.text_input(
            "Fournisseur",
            value=getattr(donnees, "fournisseur", ""),
        )
        type_energie = st.selectbox(
            "Type d'énergie",
            list(TYPE_ENERGIE_LABELS.keys()),
            format_func=lambda x: TYPE_ENERGIE_LABELS[x],
        )
        montant = st.number_input(
            "Montant TTC (€)",
            value=float(getattr(donnees, "montant_ttc", 0) or 0),
            min_value=0.0,
        )
        consommation = st.number_input(
            "Consommation",
            value=float(getattr(donnees, "consommation", 0) or 0),
            min_value=0.0,
        )
        mois = st.selectbox(
            "Mois",
            list(range(1, 13)),
            format_func=lambda m: MOIS_FR[m] if 1 <= m <= 12 else str(m),
        )
        annee = st.number_input(
            "Année",
            value=float(getattr(donnees, "annee_facturation", 2025) or 2025),
            min_value=2000.0,
        )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Sauvegarder", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

    if submitted:
        donnees.fournisseur = fournisseur
        donnees.type_energie = type_energie
        donnees.montant_ttc = montant
        donnees.consommation = consommation
        donnees.mois_facturation = mois
        donnees.annee_facturation = int(annee)
        sauvegarder_facture(donnees)
        st.success("✅ Facture sauvegardée !")
        st.rerun()

    if cancelled:
        if "ocr_resultat" in st.session_state:
            del st.session_state["ocr_resultat"]
        st.rerun()

    return donnees


def afficher_historique() -> None:
    """Affiche l'historique des factures scannées."""
    st.subheader("📋 Historique des factures")

    try:
        with obtenir_contexte_db() as db:
            # Charger les factures directement depuis la DB
            factures = db.query(object).filter(True).order_by(None).limit(50).all()

        if not factures:
            st.caption("Aucune facture enregistrée.")
            return

        for f in factures:
            with st.container(border=True):
                cols = st.columns(3)
                with cols[0]:
                    fournisseur = getattr(f, "fournisseur", "?")
                    emoji = FOURNISSEURS_CONNUS.get(fournisseur, {}).get("emoji", "📄")
                    st.markdown(f"**{emoji} {fournisseur}**")
                with cols[1]:
                    st.metric("Montant", f"{getattr(f, 'montant', 0):.2f}€")
                with cols[2]:
                    mois = getattr(f, "mois", 0)
                    annee = getattr(f, "annee", 0)
                    mois_label = MOIS_FR[mois] if 1 <= mois <= 12 else "?"
                    st.caption(f"{mois_label} {annee}")

    except Exception as e:
        logger.error(f"Erreur chargement historique: {e}")
        st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Scan Factures."""
    st.title("📄 Scan de Factures")
    st.caption("Scannez et analysez vos factures d'énergie.")

    TAB_LABELS = ["📤 Scanner", "📋 Historique"]
    tab1, tab2 = st.tabs(TAB_LABELS)

    with tab1:
        # Vérifier s'il y a un résultat OCR en session
        ocr_resultat = st.session_state.get("ocr_resultat")
        if ocr_resultat:
            if hasattr(ocr_resultat, "succes") and ocr_resultat.succes:
                afficher_resultat(ocr_resultat)
                if ocr_resultat.donnees:
                    afficher_formulaire_correction(ocr_resultat.donnees)
            else:
                afficher_upload()
                if ocr_resultat:
                    st.error(f"❌ {getattr(ocr_resultat, 'message', 'Erreur OCR')}")
        else:
            afficher_upload()

    with tab2:
        afficher_historique()
