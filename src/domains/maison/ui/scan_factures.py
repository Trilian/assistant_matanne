"""
Module Scan Factures - Interface pour scanner et extraire les données de factures.

Fonctionnalités:
- Upload photo de facture
- Extraction OCR via Mistral Vision
- Prévisualisation des données extraites
- Enregistrement dans les dépenses maison
"""

import streamlit as st
import base64
from datetime import date
from typing import Any

from src.services.facture_ocr import get_facture_ocr_service, DonneesFacture, ResultatOCR
from src.services.budget import get_budget_service, FactureMaison, CategorieDepense
from src.core.database import obtenir_contexte_db
from src.core.models import HouseExpense


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

FOURNISSEURS_CONNUS = {
    "EDF": {"type": "electricite", "emoji": "⚡"},
    "ENGIE": {"type": "gaz", "emoji": "🔥"},
    "TOTALENERGIES": {"type": "electricite", "emoji": "⚡"},
    "VEOLIA": {"type": "eau", "emoji": "💧"},
    "EAU DE PARIS": {"type": "eau", "emoji": "💧"},
    "SUEZ": {"type": "eau", "emoji": "💧"},
}

TYPE_ENERGIE_LABELS = {
    "electricite": "⚡ Électricité",
    "gaz": "🔥 Gaz",
    "eau": "💧 Eau",
}

MOIS_FR = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def image_to_base64(uploaded_file: Any) -> str:
    """Convertit un fichier uploadé en base64."""
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode("utf-8")


def sauvegarder_facture(donnees: DonneesFacture) -> bool:
    """Sauvegarde la facture en base de données."""
    try:
        # Mapper le type vers CategorieDepense
        type_mapping = {
            "electricite": "electricite",
            "gaz": "gaz",
            "eau": "eau",
        }
        categorie = type_mapping.get(donnees.type_energie, "autre")
        
        # Créer via service budget
        service = get_budget_service()
        facture = FactureMaison(
            categorie=CategorieDepense(categorie),
            montant=donnees.montant_ttc,
            consommation=donnees.consommation,
            unite_consommation=donnees.unite_consommation,
            mois=donnees.mois_facturation or date.today().month,
            annee=donnees.annee_facturation or date.today().year,
            date_facture=donnees.date_fin,
            fournisseur=donnees.fournisseur,
            numero_facture=donnees.numero_facture,
            note=f"Importé par OCR - Confiance: {donnees.confiance:.0%}",
        )
        service.ajouter_facture_maison(facture)
        
        # Aussi dans HouseExpense pour compatibilité
        with obtenir_contexte_db() as db:
            expense = HouseExpense(
                categorie=categorie,
                montant=donnees.montant_ttc,
                consommation=donnees.consommation,
                mois=donnees.mois_facturation or date.today().month,
                annee=donnees.annee_facturation or date.today().year,
                fournisseur=donnees.fournisseur,
                notes=f"Importé OCR ({donnees.confiance:.0%})",
            )
            db.add(expense)
            db.commit()
        
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_upload():
    """Interface d'upload de facture."""
    st.subheader("📸 Scanner une facture")
    
    st.info("""
    **Fournisseurs supportés:** EDF, Engie, TotalEnergies, Veolia, Eau de Paris
    
    **Conseils pour une bonne extraction:**
    - Photo nette et bien cadrée
    - Toute la facture visible
    - Bonne luminosité
    """)
    
    uploaded_file = st.file_uploader(
        "Choisir une photo de facture",
        type=["jpg", "jpeg", "png", "webp"],
        help="Formats acceptés: JPG, PNG, WebP"
    )
    
    if uploaded_file:
        # Afficher preview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Facture uploadée", use_container_width=True)
        
        with col2:
            st.markdown("**Informations fichier:**")
            st.caption(f"📄 {uploaded_file.name}")
            st.caption(f"📏 {uploaded_file.size / 1024:.1f} Ko")
            
            if st.button("🔍 Analyser la facture", type="primary", use_container_width=True):
                with st.spinner("Extraction en cours... (peut prendre 10-20s)"):
                    # Convertir en base64
                    image_b64 = image_to_base64(uploaded_file)
                    
                    # Appeler OCR
                    service = get_facture_ocr_service()
                    resultat = service.extraire_donnees_facture_sync(image_b64)
                    
                    # Stocker le résultat en session
                    st.session_state["ocr_resultat"] = resultat
                    st.rerun()
    
    return uploaded_file


def render_resultat(resultat: ResultatOCR):
    """Affiche le résultat de l'extraction."""
    if not resultat.succes:
        st.error(f"❌ {resultat.message}")
        return
    
    donnees = resultat.donnees
    if not donnees:
        st.warning("Aucune donnée extraite")
        return
    
    st.subheader("✅ Données extraites")
    
    # Score de confiance
    confiance_color = "🟢" if donnees.confiance > 0.7 else "🟡" if donnees.confiance > 0.4 else "🔴"
    st.markdown(f"**Confiance:** {confiance_color} {donnees.confiance:.0%}")
    
    if donnees.erreurs:
        for err in donnees.erreurs:
            st.warning(f"⚠️ {err}")
    
    # Données principales
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        type_label = TYPE_ENERGIE_LABELS.get(donnees.type_energie, donnees.type_energie)
        st.markdown(f"**Fournisseur:** {donnees.fournisseur}")
        st.markdown(f"**Type:** {type_label}")
        st.markdown(f"**N° Facture:** {donnees.numero_facture or 'N/A'}")
        st.markdown(f"**N° Client:** {donnees.numero_client or 'N/A'}")
    
    with col2:
        st.metric("💰 Montant TTC", f"{donnees.montant_ttc:.2f}€")
        if donnees.consommation:
            st.metric(
                f"📊 Consommation",
                f"{donnees.consommation:.0f} {donnees.unite_consommation}"
            )
    
    # Période
    if donnees.mois_facturation and donnees.annee_facturation:
        st.markdown(f"**Période:** {MOIS_FR[donnees.mois_facturation]} {donnees.annee_facturation}")
    
    if donnees.date_debut and donnees.date_fin:
        st.caption(f"Du {donnees.date_debut.strftime('%d/%m/%Y')} au {donnees.date_fin.strftime('%d/%m/%Y')}")
    
    # Détails tarif
    if donnees.prix_kwh or donnees.abonnement:
        st.divider()
        st.markdown("**Détails tarif:**")
        if donnees.prix_kwh:
            st.caption(f"Prix unitaire: {donnees.prix_kwh:.4f}€/{donnees.unite_consommation}")
        if donnees.abonnement:
            st.caption(f"Abonnement: {donnees.abonnement:.2f}€")


def render_formulaire_correction(donnees: DonneesFacture) -> DonneesFacture:
    """Formulaire pour corriger les données extraites."""
    st.subheader("✏️ Vérifier et corriger")
    
    with st.form("correction_facture"):
        col1, col2 = st.columns(2)
        
        with col1:
            fournisseur = st.text_input("Fournisseur", value=donnees.fournisseur)
            
            type_options = ["electricite", "gaz", "eau"]
            type_index = type_options.index(donnees.type_energie) if donnees.type_energie in type_options else 0
            type_energie = st.selectbox(
                "Type d'énergie",
                options=type_options,
                format_func=lambda x: TYPE_ENERGIE_LABELS.get(x, x) or x,
                index=type_index
            )
            
            montant_ttc = st.number_input(
                "Montant TTC (€)",
                value=donnees.montant_ttc,
                min_value=0.0,
                step=0.01
            )
        
        with col2:
            consommation = st.number_input(
                f"Consommation ({donnees.unite_consommation or 'kWh'})",
                value=donnees.consommation or 0.0,
                min_value=0.0
            )
            
            mois = st.selectbox(
                "Mois",
                options=list(range(1, 13)),
                format_func=lambda x: MOIS_FR[x],
                index=(donnees.mois_facturation or date.today().month) - 1
            )
            
            annee = st.number_input(
                "Année",
                value=donnees.annee_facturation or date.today().year,
                min_value=2020,
                max_value=2030
            )
        
        numero_facture = st.text_input("N° Facture", value=donnees.numero_facture)
        
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            submitted = st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
        
        with col_cancel:
            cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
        
        if submitted:
            # Créer les données corrigées
            donnees_corrigees = DonneesFacture(
                fournisseur=fournisseur,
                type_energie=type_energie,
                montant_ttc=montant_ttc,
                consommation=consommation if consommation > 0 else None,
                unite_consommation=donnees.unite_consommation or ("kWh" if type_energie == "electricite" else "m³"),
                mois_facturation=mois,
                annee_facturation=annee,
                numero_facture=numero_facture,
                confiance=1.0,  # Validé manuellement
            )
            
            if sauvegarder_facture(donnees_corrigees):
                st.success("✅ Facture enregistrée avec succès!")
                # Reset session
                if "ocr_resultat" in st.session_state:
                    del st.session_state["ocr_resultat"]
                st.rerun()
        
        if cancelled:
            if "ocr_resultat" in st.session_state:
                del st.session_state["ocr_resultat"]
            st.rerun()
    
    return donnees


def render_historique():
    """Affiche l'historique des factures scannées."""
    st.subheader("📋 Dernières factures importées")
    
    try:
        with obtenir_contexte_db() as db:
            factures = db.query(HouseExpense).filter(
                HouseExpense.notes.like("%OCR%")
            ).order_by(HouseExpense.id.desc()).limit(5).all()
            
            if not factures:
                st.caption("Aucune facture importée par OCR")
                return
            
            for f in factures:
                emoji = {"electricite": "⚡", "gaz": "🔥", "eau": "💧"}.get(f.categorie, "📄")
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{emoji} {f.fournisseur or f.categorie}**")
                        st.caption(f"{MOIS_FR[f.mois]} {f.annee}")
                    with col2:
                        st.metric("Montant", f"{f.montant:.2f}€")
                    with col3:
                        if f.consommation:
                            unite = "kWh" if f.categorie == "electricite" else "m³"
                            st.metric("Conso", f"{f.consommation:.0f} {unite}")
    except Exception as e:
        st.error(f"Erreur: {e}")
    except Exception as e:
        st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module scan factures."""
    st.title("📸 Scan Factures")
    st.caption("Extraction automatique des données de factures énergie")
    
    # Tabs
    tabs = st.tabs(["📤 Scanner", "📋 Historique"])
    
    with tabs[0]:
        # Vérifier si on a un résultat en session
        resultat = st.session_state.get("ocr_resultat")
        
        if resultat and resultat.succes and resultat.donnees:
            # Afficher résultat et formulaire correction
            render_resultat(resultat)
            st.divider()
            render_formulaire_correction(resultat.donnees)
        else:
            # Interface upload
            render_upload()
            
            if resultat and not resultat.succes:
                st.error(f"❌ {resultat.message}")
    
    with tabs[1]:
        render_historique()


if __name__ == "__main__":
    app()

