"""
Onglets opérations barcode - ajout rapide, vérification stock, gestion, import/export.
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.exceptions import ErreurNonTrouve, ErreurValidation
from src.core.state import rerun
from src.ui import etat_vide
from src.ui.fragments import ui_fragment

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ONGLET 2: AJOUT RAPIDE
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_ajout_rapide():
    """Ajouter rapidement un article avec code-barres"""

    from src.modules.utilitaires.barcode import (
        get_barcode_service,
        st,  # noqa: F811 — resolve via package for @patch
    )

    service = get_barcode_service()

    st.subheader("➕ Ajouter Article Rapide")

    st.markdown("""
    Creez un nouvel article avec code-barres en quelques secondes.
    """)

    # Formulaire
    with st.form("form_ajout_barcode"):
        col1, col2 = st.columns(2)

        with col1:
            barcode = st.text_input("Code-barres *", placeholder="Scannez ou entrez le code")
            nom = st.text_input("Nom article *", placeholder="ex: Tomates cerises")
            quantite = st.number_input("Quantite", min_value=0.1, value=1.0, step=0.5)

        with col2:
            unite = st.selectbox(
                "Unite", ["unite", "kg", "g", "L", "ml", "paquet", "boîte", "litre", "portion"]
            )
            categorie = st.selectbox(
                "Categorie",
                [
                    "Legumes",
                    "Fruits",
                    "Feculents",
                    "Proteines",
                    "Laitier",
                    "Épices & Condiments",
                    "Conserves",
                    "Surgeles",
                    "Autre",
                ],
            )
            emplacement = st.selectbox(
                "Emplacement", ["Frigo", "Congelateur", "Placard", "Cave", "Garde-manger"]
            )

        col1, col2 = st.columns(2)
        with col1:
            prix_unitaire = st.number_input(
                "Prix unitaire € (optionnel)", min_value=0.0, value=0.0, step=0.01
            )

        with col2:
            jours_peremption = st.number_input(
                "Jours avant peremption (optionnel)", min_value=0, value=0, step=1
            )

        submitted = st.form_submit_button("✅ Ajouter article", use_container_width=True)

    if submitted:
        if not barcode or not nom:
            st.error("❌ Veuillez remplir les champs obligatoires (*)")
            return

        try:
            # Ajouter article
            service.ajouter_article_par_barcode(
                code=barcode,
                nom=nom,
                quantite=quantite,
                unite=unite,
                categorie=categorie,
                prix_unitaire=prix_unitaire if prix_unitaire > 0 else None,
                date_peremption_jours=jours_peremption if jours_peremption > 0 else None,
                emplacement=emplacement,
            )

            st.success(f"✅ Article cree: {nom}")
            st.balloons()

            # Afficher resume
            st.info(f"""
            💰 **Article cree:**
            - Code: {barcode}
            - Nom: {nom}
            - Stock: {quantite} {unite}
            - Emplacement: {emplacement}
            - Categorie: {categorie}
            """)

            # Reset barcode-specific keys only (not global state)
            for key in list(st.session_state.keys()):
                if key.startswith(("barcode_", "last_webrtc")):
                    del st.session_state[key]

        except ErreurValidation as e:
            st.error(f"❌ Validation: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3: VÉRIFIER STOCK
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_verifier_stock():
    """Vérifier stock par code-barres"""

    from src.modules.utilitaires.barcode import (
        get_barcode_service,
        st,  # noqa: F811 — resolve via package for @patch
    )

    service = get_barcode_service()

    st.subheader("✅ Vérifier Stock par Code")

    st.markdown("Scannez un code pour vérifier instantanément le stock")

    col1, col2 = st.columns([3, 1])

    with col1:
        code_check = st.text_input(
            "Code-barres:", key="check_stock_input", placeholder="Scannez le code..."
        )

    with col2:
        if st.button("📍Verifier", key="btn_check_stock", use_container_width=True):
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
                st.metric("Minimum requis", info_stock["quantite_min"])

            with col4:
                etat = info_stock["etat_stock"]
                if etat == "OK":
                    st.metric("État", "✅ OK", delta="Normal")
                elif etat == "FAIBLE":
                    st.metric("État", "⚠️ FAIBLE", delta="À renouveler")
                else:
                    st.metric("État", "❌ CRITIQUE", delta="Urgent!")

            # Details
            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Emplacement", info_stock["emplacement"])

            with col2:
                if info_stock["prix_unitaire"]:
                    st.metric("Prix unitaire", f"€{info_stock['prix_unitaire']:.2f}")

            with col3:
                etat_perem = info_stock["peremption_etat"]
                emoji = "✅" if etat_perem == "OK" else "⚠️"
                st.metric("Peremption", f"{emoji} {etat_perem}")

            # Actions
            if info_stock["etat_stock"] != "OK":
                st.warning("📦 Stock faible - Considérer l'ajout de stock")

            if info_stock["peremption_etat"] in ["URGENT", "PÉRIMÉ"]:
                st.error("❌ Problème peremption - Action requise")

        except ErreurNonTrouve:
            st.error("❌ Code non trouve dans la base")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 4: GESTION BARCODES
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_gestion_barcodes():
    """Gestion des codes-barres"""

    from src.modules.utilitaires.barcode import (
        get_barcode_service,
        st,  # noqa: F811 — resolve via package for @patch
    )

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
            df_display = df.rename(
                columns={
                    "id": "ID",
                    "nom": "Article",
                    "barcode": "Code-barres",
                    "quantite": "Stock",
                    "unite": "Unite",
                    "categorie": "Categorie",
                }
            )

            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={"Code-barres": st.column_config.TextColumn(width=150)},
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
                    key="sel_article_barcode",
                )

            with col2:
                nouveau_code = st.text_input("Nouveau code-barres", key="new_barcode_input")

            with col3:
                if st.button("✅ Mettre à jour", key="btn_update_barcode"):
                    if nouveau_code and article_id:
                        try:
                            service.mettre_a_jour_barcode(article_id[0], nouveau_code)
                            st.success("✅ Code-barres mis à jour")
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

        else:
            etat_vide("Aucun article avec code-barres", "📦")

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 5: IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_import_export():
    """Import/Export codes-barres"""

    from src.modules.utilitaires.barcode import (
        get_barcode_service,
        st,  # noqa: F811 — resolve via package for @patch
    )

    service = get_barcode_service()

    st.subheader("📥 Import/Export")

    col1, col2 = st.columns(2)

    # EXPORT
    with col1:
        st.markdown("#### 📤 Exporter")

        try:
            csv_data = service.exporter_barcodes()
            st.download_button(
                label="⬇️ Télécharger CSV",
                data=csv_data,
                file_name=f"codes_barres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_barcode_csv",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ Erreur export: {str(e)}")

    # IMPORT
    with col2:
        st.markdown("#### 📥 Importer")

        uploaded_file = st.file_uploader(
            "Choisir fichier CSV", type="csv", key="upload_barcode_csv"
        )

        if uploaded_file:
            csv_content = uploaded_file.read().decode("utf-8")

            if st.button("✅ Importer", key="btn_import_barcode", use_container_width=True):
                try:
                    resultats = service.importer_barcodes(csv_content)

                    st.success(f"✅ {resultats['success']} articles importés")

                    if resultats["errors"]:
                        st.warning(f"⚠️ {len(resultats['errors'])} erreurs")
                        for err in resultats["errors"][:5]:
                            st.text(f"- {err['barcode']}: {err['erreur']}")
                except Exception as e:
                    st.error(f"❌ Erreur import: {str(e)}")
