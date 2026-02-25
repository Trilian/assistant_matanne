"""
Scanner tab UI - modes caméra, streaming vidéo et saisie manuelle.
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.integrations import BarcodeService
from src.ui.fragments import ui_fragment

from .detection import BarcodeScanner, detect_barcodes

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# ONGLET 1: SCANNER
# ═══════════════════════════════════════════════════════════


def _afficher_scanner_camera(service: BarcodeService):
    """Scanner via caméra (st.camera_input) - Mode photo."""
    import cv2
    import numpy as np
    from PIL import Image

    st.info("📱 **Prenez une photo du code-barres** - Fonctionne sur téléphone!")

    # Capture photo via caméra native
    camera_photo = st.camera_input(
        "Prendre une photo",
        key="barcode_camera",
        label_visibility="collapsed",
    )

    if camera_photo:
        with st.spinner("Analyse de l'image..."):
            try:
                # Convertir en numpy array
                image = Image.open(camera_photo)
                frame = np.array(image)

                # Convertir RGB -> BGR pour OpenCV
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Détecter les codes-barres (utilise detect_barcodes unifié)
                codes = detect_barcodes(frame)

                if codes:
                    st.success(f"✅ {len(codes)} code(s) détecté(s)!")

                    for code in codes:
                        code_data = code["data"]
                        code_type = code["type"]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Type", code_type)
                        with col2:
                            st.metric("Code", code_data)

                        # Traiter le code détecté
                        st.divider()
                        _process_scanned_code(service, code_data)
                else:
                    st.warning(
                        "⚠️ Aucun code détecté.\n\n"
                        "**Conseils:**\n"
                        "- Rapprochez-vous du code-barres\n"
                        "- Assurez-vous d'avoir assez de lumière\n"
                        "- Évitez les reflets"
                    )

            except Exception as e:
                st.error(f"❌ Erreur: {e}")


def _afficher_scanner_webrtc(service: BarcodeService):
    """Scanner via streaming vidéo webrtc - Mode temps réel."""

    def on_scan_callback(code_type: str, code_data: str):
        """Callback quand un code est détecté en streaming."""
        st.session_state[SK.LAST_WEBRTC_SCAN] = {
            "type": code_type,
            "data": code_data,
            "time": datetime.now(),
        }

    scanner = BarcodeScanner(on_scan=on_scan_callback)
    scanner.render(key="webrtc_scanner")

    # Traiter le dernier code scanné
    if SK.LAST_WEBRTC_SCAN in st.session_state:
        last_scan = st.session_state[SK.LAST_WEBRTC_SCAN]
        st.divider()
        st.subheader("🔄 Dernier code détecté")
        _process_scanned_code(service, last_scan["data"])


def _process_scanned_code(service: BarcodeService, code_input: str):
    """Traite un code scanné (partagé entre caméra et manuel)."""
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
        if resultat.type_scan == "article":
            st.subheader("📦 Article trouvé")
            details = resultat.details

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Article", details["nom"])
            with col2:
                st.metric("Stock", f"{details['quantite']} {details['unite']}")
            with col3:
                st.metric("Emplacement", details["emplacement"])

        elif resultat.type_scan == "nouveau":
            st.info("🆕 Code inconnu - Ajoutez-le comme nouvel article!")

    except Exception as e:
        st.error(f"❌ Erreur: {e}")


@ui_fragment
def afficher_scanner():
    """Scanner codes-barres avec 3 modes: vidéo streaming, photo, manuel."""

    from src.modules.utilitaires.barcode import (
        get_barcode_service,
        st,  # noqa: F811 — resolve via package for @patch
    )

    service = get_barcode_service()

    st.subheader("📷 Scanner Code")

    # Vérifier les packages disponibles
    has_webrtc = False
    has_cv2 = False
    has_pyzbar = False

    try:
        import streamlit_webrtc

        has_webrtc = True
    except ImportError:
        pass

    try:
        import cv2

        has_cv2 = True
    except ImportError:
        pass

    try:
        from pyzbar import pyzbar

        has_pyzbar = True
    except ImportError:
        pass

    # Construire les modes disponibles
    modes_disponibles = []
    if has_webrtc and has_cv2 and has_pyzbar:
        modes_disponibles.append("📹 Vidéo (temps réel)")
    if has_cv2 and has_pyzbar:
        modes_disponibles.append("📷 Photo")
    modes_disponibles.append("⌨️ Manuel")
    modes_disponibles.append("🎮 Démo (codes test)")

    mode = st.radio(
        "Mode de saisie",
        modes_disponibles,
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "📹 Vidéo (temps réel)":
        _afficher_scanner_webrtc(service)

    elif mode == "📷 Photo":
        _afficher_scanner_camera(service)
    elif mode == "🎮 Démo (codes test)":
        st.info("💡 **Mode Démo** - Sélectionnez un code-barres de test")
        demo_codes = {
            "Lait demi-écrémé 1L": "3017620422003",
            "Pâtes Panzani 500g": "3038350012005",
            "Eau Evian 1.5L": "3068320114484",
            "Nutella 400g": "3017620425035",
            "Café Carte Noire 250g": "3104060013510",
            "Code invalide (test)": "1234567890",
        }
        selected_demo = st.selectbox("Produit test", list(demo_codes.keys()))
        code_input = demo_codes[selected_demo]
        st.code(f"Code: {code_input}")
        scanner_button = st.button(
            "📍 Scanner ce code", use_container_width=True, key="btn_demo_scan"
        )
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            code_input = st.text_input(
                "Scannez ou entrez le code:",
                key="scanner_input",
                placeholder="Entrez le code-barres (ex: 3017620422003)...",
                label_visibility="collapsed",
            )
        with col2:
            scanner_button = st.button("📍 Scanner", use_container_width=True, key="btn_scanner")

    if code_input and scanner_button:
        try:
            # Valider code
            valide, type_code = service.valider_barcode(code_input)

            if not valide:
                st.error(f"❌ Code invalide: {type_code}")
                return

            # Scanner
            resultat = service.scanner_code(code_input)

            st.success("✅ Scan reussi!")

            # Afficher resultats
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Code", resultat.barcode)
                st.metric("Type", resultat.type_scan.upper())

            with col2:
                st.info(f"⏰ Scannee: {resultat.timestamp.strftime('%H:%M:%S')}")

            # Details
            if resultat.type_scan == "article":
                st.subheader("📦 Article trouvé")
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
                    if st.button("➕ Ajouter quantite", key="btn_add_qty"):
                        st.switch_page("pages/0_accueil.py")

                with col2:
                    if st.button("✏️ Éditer article", key="btn_edit_article"):
                        st.switch_page("pages/0_accueil.py")

                with col3:
                    if st.button("🗑️ Supprimer", key="btn_delete_article"):
                        st.warning("Action non disponible ici")

            else:
                st.warning("⚠️ Code non reconnu - doit être ajoute dans le système")
                if st.button("➕ Ajouter ce code", key="btn_add_new_barcode"):
                    rerun()

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # Info
    st.info("""
    📝 **Formats supportés:**
    - EAN-13 (13 chiffres)
    - EAN-8 (8 chiffres)
    - UPC (12 chiffres)
    - QR codes
    - CODE128 & CODE39
    """)
