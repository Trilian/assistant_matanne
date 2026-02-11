"""
Module Scanner Barcode/QR - Interface Streamlit

✅ Scanner codes-barres
✅ Ajout rapide articles
✅ Vérification stock
✅ Import/Export
"""

import streamlit as st
from datetime import datetime
from io import StringIO

from src.core.state import GestionnaireEtat, obtenir_etat
from src.services.integrations import BarcodeService
from src.services.inventaire import InventaireService
from src.core.errors_base import ErreurValidation, ErreurNonTrouve

# Logique métier pure
from src.domains.utils.logic.barcode_logic import (
    valider_code_barres,
    detecter_type_code_barres,
    extraire_infos_produit
)

# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════


def get_barcode_service() -> BarcodeService:
    """Get ou créer service barcode"""
    if "barcode_service" not in st.session_state:
        st.session_state.barcode_service = BarcodeService()
    return st.session_state.barcode_service


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée module scanner barcode"""
    
    st.markdown(
        "<h1 style='text-align: center;'>💰 Scanner Code-Barres/QR</h1>",
        unsafe_allow_html=True,
    )
    
    st.markdown("Scannez codes-barres, QR codes pour gestion rapide inventaire")
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👶 Scanner",
        "➕ Ajout rapide",
        "✅ Vérifier stock",
        "📊 Gestion",
        "💰¥ Import/Export"
    ])
    
    with tab1:
        render_scanner()
    
    with tab2:
        render_ajout_rapide()
    
    with tab3:
        render_verifier_stock()
    
    with tab4:
        render_gestion_barcodes()
    
    with tab5:
        render_import_export()


# ═══════════════════════════════════════════════════════════
# ONGLET 1: SCANNER
# ═══════════════════════════════════════════════════════════


def render_scanner():
    """Scanner codes-barres"""
    
    service = get_barcode_service()
    
    st.subheader("👶 Scanner Code")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code_input = st.text_input(
            "Scannez ou entrez le code:",
            key="scanner_input",
            placeholder="Posez le lecteur sur le code...",
            label_visibility="collapsed"
        )
    
    with col2:
        scanner_button = st.button(
            "📍Scanner",
            use_container_width=True,
            key="btn_scanner"
        )
    
    if code_input and scanner_button:
        try:
            # Valider code
            valide, type_code = service.valider_barcode(code_input)
            
            if not valide:
                st.error(f"❌ Code invalide: {type_code}")
                return
            
            # Scanner
            resultat = service.scanner_code(code_input)
            
            st.success("✅ Scan réussi!")
            
            # Afficher résultats
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Code", resultat.barcode)
                st.metric("Type", resultat.type_scan.upper())
            
            with col2:
                st.info(f"â° Scannée: {resultat.timestamp.strftime('%H:%M:%S')}")
            
            # Détails
            if resultat.type_scan == "article":
                st.subheader("[PKG] Article trouvé")
                details = resultat.details
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Article", details["nom"])
                with col2:
                    st.metric("Stock", f"{details['quantite']} {details['unite']}")
                with col3:
                    st.metric("Emplacement", details["emplacement"])
                
                # Options
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("➕ Ajouter quantité", key="btn_add_qty"):
                        st.session_state.article_id_to_add = details["id"]
                        st.session_state.article_name_to_add = details["nom"]
                        st.switch_page("pages/0_accueil.py")
                
                with col2:
                    if st.button("✏️ Éditer article", key="btn_edit_article"):
                        st.session_state.article_id_to_edit = details["id"]
                        st.switch_page("pages/0_accueil.py")
                
                with col3:
                    if st.button("🎯¸ Supprimer", key="btn_delete_article"):
                        st.warning("Action non disponible ici")
            
            else:
                st.warning("âš ï¸ Code non reconnu - doit être ajouté dans le système")
                if st.button("➕ Ajouter ce code", key="btn_add_new_barcode"):
                    st.session_state.new_barcode_to_add = code_input
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
    
    # Info
    st.info("""
    💰š **Formats supportés:**
    - EAN-13 (13 chiffres)
    - EAN-8 (8 chiffres)
    - UPC (12 chiffres)
    - QR codes
    - CODE128 & CODE39
    """)


# ═══════════════════════════════════════════════════════════
# ONGLET 2: AJOUT RAPIDE
# ═══════════════════════════════════════════════════════════


def render_ajout_rapide():
    """Ajouter rapidement un article avec code-barres"""
    
    service = get_barcode_service()
    inventaire_service = InventaireService()
    
    st.subheader("➕ Ajouter Article Rapide")
    
    st.markdown("""
    Créez un nouvel article avec code-barres en quelques secondes.
    """)
    
    # Formulaire
    with st.form("form_ajout_barcode"):
        col1, col2 = st.columns(2)
        
        with col1:
            barcode = st.text_input(
                "Code-barres *",
                placeholder="Scannez ou entrez le code"
            )
            nom = st.text_input(
                "Nom article *",
                placeholder="ex: Tomates cerises"
            )
            quantite = st.number_input(
                "Quantité",
                min_value=0.1,
                value=1.0,
                step=0.5
            )
        
        with col2:
            unite = st.selectbox(
                "Unité",
                ["unité", "kg", "g", "L", "ml", "paquet", "boîte", "litre", "portion"]
            )
            categorie = st.selectbox(
                "Catégorie",
                [
                    "Légumes", "Fruits", "Féculents", "Protéines",
                    "Laitier", "Épices & Condiments", "Conserves",
                    "Surgelés", "Autre"
                ]
            )
            emplacement = st.selectbox(
                "Emplacement",
                ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]
            )
        
        col1, col2 = st.columns(2)
        with col1:
            prix_unitaire = st.number_input(
                "Prix unitaire € (optionnel)",
                min_value=0.0,
                value=0.0,
                step=0.01
            )
        
        with col2:
            jours_peremption = st.number_input(
                "Jours avant péremption (optionnel)",
                min_value=0,
                value=0,
                step=1
            )
        
        submitted = st.form_submit_button("✅ Ajouter article", use_container_width=True)
    
    if submitted:
        if not barcode or not nom:
            st.error("❌ Veuillez remplir les champs obligatoires (*)")
            return
        
        try:
            # Ajouter article
            article = service.ajouter_article_par_barcode(
                code=barcode,
                nom=nom,
                quantite=quantite,
                unite=unite,
                categorie=categorie,
                prix_unitaire=prix_unitaire if prix_unitaire > 0 else None,
                date_peremption_jours=jours_peremption if jours_peremption > 0 else None,
                emplacement=emplacement
            )
            
            st.success(f"✅ Article créé: {nom}")
            st.balloons()
            
            # Afficher résumé
            st.info(f"""
            💰 **Article créé:**
            - Code: {barcode}
            - Nom: {nom}
            - Stock: {quantite} {unite}
            - Emplacement: {emplacement}
            - Catégorie: {categorie}
            """)
            
            st.session_state.clear()
        
        except ErreurValidation as e:
            st.error(f"❌ Validation: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3: VÉRIFIER STOCK
# ═══════════════════════════════════════════════════════════


def render_verifier_stock():
    """Vérifier stock par code-barres"""
    
    service = get_barcode_service()
    
    st.subheader("✅ Vérifier Stock par Code")
    
    st.markdown("Scannez un code pour vérifier instantanément le stock")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        code_check = st.text_input(
            "Code-barres:",
            key="check_stock_input",
            placeholder="Scannez le code..."
        )
    
    with col2:
        if st.button("📍Vérifier", key="btn_check_stock", use_container_width=True):
            check_clicked = True
        else:
            check_clicked = False
    
    if code_check and check_clicked:
        try:
            info_stock = service.verifier_stock_barcode(code_check)
            
            # Affichage
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Article", info_stock["nom"])
            
            with col2:
                stock_display = f"{info_stock['quantite']} {info_stock['unite']}"
                st.metric("Stock actuel", stock_display)
            
            with col3:
                st.metric("Minimum requis", info_stock['quantite_min'])
            
            with col4:
                etat = info_stock["etat_stock"]
                if etat == "OK":
                    st.metric("État", "✅ OK", delta="Normal")
                elif etat == "FAIBLE":
                    st.metric("État", "⚠️ FAIBLE", delta="À renouveler")
                else:
                    st.metric("État", "❌ CRITIQUE", delta="Urgent!")
            
            # Détails
            st.divider()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Emplacement", info_stock["emplacement"])
            
            with col2:
                if info_stock["prix_unitaire"]:
                    st.metric("Prix unitaire", f"€{info_stock['prix_unitaire']:.2f}")
            
            with col3:
                etat_perem = info_stock["peremption_etat"]
                emoji = "✅" if etat_perem == "OK" else "âš ï¸"
                st.metric("Péremption", f"{emoji} {etat_perem}")
            
            # Actions
            if info_stock["etat_stock"] != "OK":
                st.warning(f"[PKG] Stock faible - Considérer l'ajout de stock")
            
            if info_stock["peremption_etat"] in ["URGENT", "PÉRIMÉ"]:
                st.error(f"❌ Problème péremption - Action requise")
        
        except ErreurNonTrouve:
            st.error("❌ Code non trouvé dans la base")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 4: GESTION BARCODES
# ═══════════════════════════════════════════════════════════


def render_gestion_barcodes():
    """Gestion des codes-barres"""
    
    service = get_barcode_service()
    
    st.subheader("📊 Gestion Codes-Barres")
    
    # Lister articles avec barcode
    try:
        articles_barcode = service.lister_articles_avec_barcode()
        
        if articles_barcode:
            st.metric("Articles avec code-barres", len(articles_barcode))
            
            # Tableau
            import pandas as pd
            df = pd.DataFrame(articles_barcode)
            df_display = df.rename(columns={
                "id": "ID",
                "nom": "Article",
                "barcode": "Code-barres",
                "quantite": "Stock",
                "unite": "Unité",
                "categorie": "Catégorie"
            })
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Code-barres": st.column_config.TextColumn(width=150)
                }
            )
            
            # Édition
            st.divider()
            st.subheader("🔄 Mettre à jour code-barres")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                article_id = st.selectbox(
                    "Article",
                    options=[(a["id"], a["nom"]) for a in articles_barcode],
                    format_func=lambda x: x[1],
                    key="sel_article_barcode"
                )
            
            with col2:
                nouveau_code = st.text_input(
                    "Nouveau code-barres",
                    key="new_barcode_input"
                )
            
            with col3:
                if st.button("✅ Mettre à jour", key="btn_update_barcode"):
                    if nouveau_code and article_id:
                        try:
                            service.mettre_a_jour_barcode(
                                article_id[0],
                                nouveau_code
                            )
                            st.success("✅ Code-barres mis à jour")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")
        
        else:
            st.info("ℹ️ Aucun article avec code-barres pour le moment")
    
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 5: IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════


def render_import_export():
    """Import/Export codes-barres"""
    
    service = get_barcode_service()
    
    st.subheader("📅Ÿ“¤ Import/Export")
    
    col1, col2 = st.columns(2)
    
    # EXPORT
    with col1:
        st.subheader("💡 Exporter")
        
        if st.button("â¬‡ï¸ Télécharger CSV", key="btn_export_barcode"):
            try:
                csv_data = service.exporter_barcodes()
                st.download_button(
                    label="💰¥ Télécharger codes-barres.csv",
                    data=csv_data,
                    file_name=f"codes_barres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_barcode_csv"
                )
                st.success("✅ CSV généré")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    # IMPORT
    with col2:
        st.subheader("💰¥ Importer")
        
        uploaded_file = st.file_uploader(
            "Choisir fichier CSV",
            type="csv",
            key="upload_barcode_csv"
        )
        
        if uploaded_file:
            csv_content = uploaded_file.read().decode('utf-8')
            
            if st.button("✅ Importer", key="btn_import_barcode"):
                try:
                    resultats = service.importer_barcodes(csv_content)
                    
                    st.success(f"✅ {resultats['success']} articles importés")
                    
                    if resultats['errors']:
                        st.warning(f"âš ï¸ {len(resultats['errors'])} erreurs")
                        for err in resultats['errors'][:5]:
                            st.text(f"- {err['barcode']}: {err['erreur']}")
                except Exception as e:
                    st.error(f"❌ Erreur import: {str(e)}")


# ═══════════════════════════════════════════════════════════
# PAGE ENTRY
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    app()
