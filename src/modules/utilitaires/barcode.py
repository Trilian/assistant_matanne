"""
Module Scanner Barcode/QR - Interface Streamlit

✅ Scanner codes-barres (vidéo temps réel, photo, manuel)
✅ Ajout rapide articles
✅ Verification stock
✅ Import/Export

Intègre les fonctionnalités avancées de détection:
- pyzbar (principal) avec fallback zxing-cpp
- Streaming webrtc temps réel
- Anti-doublon (scan_cooldown)
"""

import logging
from collections.abc import Callable
from datetime import datetime

import streamlit as st

from src.core.errors_base import ErreurNonTrouve, ErreurValidation

# Logique metier pure
from src.services.integrations import BarcodeService
from src.services.inventaire import ServiceInventaire
from src.ui import etat_vide

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# DÉTECTION CODES-BARRES (fusionné depuis camera_scanner.py)
# ═══════════════════════════════════════════════════════════


def _detect_barcode_pyzbar(frame):
    """
    Détecte les codes-barres dans une frame avec pyzbar.

    Args:
        frame: Image numpy array (BGR)

    Returns:
        Liste de codes détectés [{type, data, rect}]
    """
    try:
        import cv2
        from pyzbar import pyzbar

        # Convertir en grayscale pour meilleure détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Détecter les codes
        codes = pyzbar.decode(gray)

        results = []
        for code in codes:
            results.append(
                {
                    "type": code.type,
                    "data": code.data.decode("utf-8"),
                    "rect": code.rect,
                }
            )

        return results

    except ImportError:
        logger.warning("pyzbar non installé - détection barcode désactivée")
        return []
    except Exception as e:
        logger.error(f"Erreur détection barcode: {e}")
        return []


def _detect_barcode_zxing(frame):
    """
    Détecte les codes-barres avec zxing-cpp (fallback).

    Args:
        frame: Image numpy array

    Returns:
        Liste de codes détectés
    """
    try:
        import zxingcpp

        results = zxingcpp.read_barcodes(frame)

        return [
            {
                "type": str(r.format),
                "data": r.text,
                "rect": None,
            }
            for r in results
        ]

    except ImportError:
        return []
    except Exception as e:
        logger.error(f"Erreur zxing: {e}")
        return []


def detect_barcodes(frame):
    """
    Détecte les codes-barres dans une frame.

    Essaie pyzbar d'abord, puis zxing en fallback.

    Args:
        frame: Image numpy array

    Returns:
        Liste de codes détectés [{type, data, rect}]
    """
    # Essayer pyzbar d'abord
    results = _detect_barcode_pyzbar(frame)

    if not results:
        # Fallback sur zxing
        results = _detect_barcode_zxing(frame)

    return results


# ═══════════════════════════════════════════════════════════
# CLASSE SCANNER WEBRTC (fusionné depuis camera_scanner.py)
# ═══════════════════════════════════════════════════════════


class BarcodeScanner:
    """
    Scanner de codes-barres avec caméra streaming.

    Utilise streamlit-webrtc pour le streaming vidéo temps réel.
    """

    def __init__(self, on_scan: Callable[[str, str], None] = None):
        """
        Initialise le scanner.

        Args:
            on_scan: Callback appelé quand un code est détecté (type, data)
        """
        self.on_scan = on_scan
        self.last_scanned = None
        self.last_scan_time = None
        self.scan_cooldown = 2.0  # Secondes entre deux scans du même code

    def _should_report_scan(self, code_data: str) -> bool:
        """Vérifie si on doit reporter ce scan (évite les doublons)."""
        now = datetime.now()

        if self.last_scanned == code_data and self.last_scan_time:
            elapsed = (now - self.last_scan_time).total_seconds()
            if elapsed < self.scan_cooldown:
                return False

        self.last_scanned = code_data
        self.last_scan_time = now
        return True

    def render(self, key: str = "barcode_scanner"):
        """
        Affiche le composant scanner streaming.

        Args:
            key: Clé unique pour le composant
        """
        try:
            import av
            import numpy as np
            from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, webrtc_streamer
        except ImportError:
            st.error(
                "📦 Packages requis non installés.\n\n"
                "Exécutez: `pip install streamlit-webrtc av`"
            )
            self._afficher_fallback_input(key)
            return

        # Configuration RTC (serveurs STUN publics)
        rtc_config = RTCConfiguration(
            {
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302"]},
                    {"urls": ["stun:stun1.l.google.com:19302"]},
                ]
            }
        )

        # État du scan
        if f"{key}_detected" not in st.session_state:
            st.session_state[f"{key}_detected"] = []

        scanner_instance = self

        class BarcodeVideoProcessor(VideoProcessorBase):
            """Processeur vidéo pour détection codes-barres."""

            def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
                img = frame.to_ndarray(format="bgr24")

                # Détecter les codes
                codes = detect_barcodes(img)

                if codes:
                    for code in codes:
                        if scanner_instance._should_report_scan(code["data"]):
                            # Stocker le résultat
                            st.session_state[f"{key}_detected"].append(
                                {
                                    "type": code["type"],
                                    "data": code["data"],
                                    "time": datetime.now().isoformat(),
                                }
                            )

                            # Callback
                            if scanner_instance.on_scan:
                                scanner_instance.on_scan(code["type"], code["data"])

                        # Dessiner rectangle autour du code
                        if code.get("rect"):
                            import cv2

                            rect = code["rect"]
                            cv2.rectangle(
                                img,
                                (rect.left, rect.top),
                                (rect.left + rect.width, rect.top + rect.height),
                                (0, 255, 0),
                                3,
                            )
                            cv2.putText(
                                img,
                                code["data"][:20],
                                (rect.left, rect.top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 255, 0),
                                2,
                            )

                return av.VideoFrame.from_ndarray(img, format="bgr24")

        # Interface
        st.info("👆 Autorisez l'accès à la caméra, puis présentez le code-barres")

        # Streamer vidéo
        webrtc_streamer(
            key=key,
            video_processor_factory=BarcodeVideoProcessor,
            rtc_configuration=rtc_config,
            media_stream_constraints={
                "video": {
                    "facingMode": "environment",  # Caméra arrière sur mobile
                    "width": {"ideal": 1280},
                    "height": {"ideal": 720},
                },
                "audio": False,
            },
            async_processing=True,
        )

        # Afficher les codes détectés
        detected = st.session_state.get(f"{key}_detected", [])

        if detected:
            st.success(f"✅ {len(detected)} code(s) détecté(s)")

            # Dernier code
            last = detected[-1]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Type", last["type"])
            with col2:
                st.metric(
                    "Code", last["data"][:20] + "..." if len(last["data"]) > 20 else last["data"]
                )

            # Bouton pour effacer
            if st.button("🗑️ Effacer historique", key=f"{key}_clear"):
                st.session_state[f"{key}_detected"] = []
                st.rerun()

            # Liste des codes
            with st.expander("📋 Historique des scans"):
                for scan in reversed(detected[-10:]):
                    st.caption(f"{scan['time']}: [{scan['type']}] {scan['data']}")

    def _afficher_fallback_input(self, key: str):
        """Affiche un input texte en fallback."""
        st.warning("Caméra streaming non disponible - utilisez la saisie manuelle ou mode photo")

        code = st.text_input(
            "Entrez le code-barres:", key=f"{key}_manual", placeholder="EAN13, QR Code, etc."
        )

        if code and st.button("✅ Valider", key=f"{key}_validate"):
            if self.on_scan:
                self.on_scan("MANUAL", code)
            st.success(f"Code enregistré: {code}")


# ═══════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════


def get_barcode_service() -> BarcodeService:
    """Get ou creer service barcode"""
    if "barcode_service" not in st.session_state:
        st.session_state.barcode_service = BarcodeService()
    return st.session_state.barcode_service


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entree module scanner barcode"""

    st.markdown(
        "<h1 style='text-align: center;'>💰 Scanner Code-Barres/QR</h1>",
        unsafe_allow_html=True,
    )

    st.markdown("Scannez codes-barres, QR codes pour gestion rapide inventaire")
    st.markdown("---")

    # Onglets
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📷 Scanner", "➕ Ajout rapide", "✅ Vérifier stock", "📊 Gestion", "📥 Import/Export"]
    )

    with tab1:
        afficher_scanner()

    with tab2:
        afficher_ajout_rapide()

    with tab3:
        afficher_verifier_stock()

    with tab4:
        afficher_gestion_barcodes()

    with tab5:
        afficher_import_export()


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
        st.session_state["last_webrtc_scan"] = {
            "type": code_type,
            "data": code_data,
            "time": datetime.now(),
        }

    scanner = BarcodeScanner(on_scan=on_scan_callback)
    scanner.render(key="webrtc_scanner")

    # Traiter le dernier code scanné
    if "last_webrtc_scan" in st.session_state:
        last_scan = st.session_state["last_webrtc_scan"]
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
            st.session_state.nouveau_barcode = code_input

    except Exception as e:
        st.error(f"❌ Erreur: {e}")


def afficher_scanner():
    """Scanner codes-barres avec 3 modes: vidéo streaming, photo, manuel."""

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
                        st.session_state.article_id_to_add = details["id"]
                        st.session_state.article_name_to_add = details["nom"]
                        st.switch_page("pages/0_accueil.py")

                with col2:
                    if st.button("✏️ Éditer article", key="btn_edit_article"):
                        st.session_state.article_id_to_edit = details["id"]
                        st.switch_page("pages/0_accueil.py")

                with col3:
                    if st.button("🗑️ Supprimer", key="btn_delete_article"):
                        st.warning("Action non disponible ici")

            else:
                st.warning("âš ï¸ Code non reconnu - doit être ajoute dans le système")
                if st.button("➕ Ajouter ce code", key="btn_add_new_barcode"):
                    st.session_state.new_barcode_to_add = code_input
                    st.rerun()

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


# ═══════════════════════════════════════════════════════════
# ONGLET 2: AJOUT RAPIDE
# ═══════════════════════════════════════════════════════════


def afficher_ajout_rapide():
    """Ajouter rapidement un article avec code-barres"""

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

            st.session_state.clear()

        except ErreurValidation as e:
            st.error(f"❌ Validation: {str(e)}")
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 3: VÉRIFIER STOCK
# ═══════════════════════════════════════════════════════════


def afficher_verifier_stock():
    """Vérifier stock par code-barres"""

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
                emoji = "✅" if etat_perem == "OK" else "âš ï¸"
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


def afficher_gestion_barcodes():
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
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

        else:
            etat_vide("Aucun article avec code-barres", "📦")

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# ONGLET 5: IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════


def afficher_import_export():
    """Import/Export codes-barres"""

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


# ═══════════════════════════════════════════════════════════
# PAGE ENTRY
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    app()
