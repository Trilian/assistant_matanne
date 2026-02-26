"""
Scanner codes-barres WebRTC via webcam

Utilise streamlit-webrtc pour scanner les codes-barres
directement depuis la webcam du navigateur.

Dépendances:
    pip install streamlit-webrtc opencv-python pyzbar
"""

import logging
from dataclasses import dataclass
from typing import Callable

import streamlit as st

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ResultatScan:
    """Résultat d'un scan de code-barres."""

    code: str
    type_code: str  # EAN-13, EAN-8, QR, etc.
    timestamp: str
    confiance: float = 1.0


# ═══════════════════════════════════════════════════════════
# SCANNER WEBRTC
# ═══════════════════════════════════════════════════════════


def _get_video_processor():
    """Retourne la classe VideoProcessor pour streamlit-webrtc."""
    try:
        import cv2
        import numpy as np
        from pyzbar import pyzbar
        from streamlit_webrtc import VideoProcessorBase
    except ImportError:
        return None

    class BarcodeVideoProcessor(VideoProcessorBase):
        """Processeur vidéo pour détection de codes-barres."""

        def __init__(self):
            self.derniers_codes: list[ResultatScan] = []
            self.callback: Callable[[ResultatScan], None] | None = None

        def recv(self, frame):
            """Traite chaque frame vidéo."""
            img = frame.to_ndarray(format="bgr24")

            # Convertir en niveaux de gris pour la détection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Détecter les codes-barres
            barcodes = pyzbar.decode(gray)

            for barcode in barcodes:
                # Extraire les données
                code_data = barcode.data.decode("utf-8")
                code_type = barcode.type

                # Créer le résultat
                resultat = ResultatScan(
                    code=code_data,
                    type_code=code_type,
                    timestamp=str(np.datetime64("now")),
                )

                # Stocker le résultat
                if code_data not in [c.code for c in self.derniers_codes[-10:]]:
                    self.derniers_codes.append(resultat)

                # Dessiner le contour du code-barres
                points = barcode.polygon
                if len(points) == 4:
                    pts = np.array([(p.x, p.y) for p in points], dtype=np.int32)
                    cv2.polylines(img, [pts], True, (0, 255, 0), 3)

                    # Afficher le code
                    x, y = points[0].x, points[0].y
                    cv2.putText(
                        img, code_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                    )

            return frame.from_ndarray(img, format="bgr24")

        def get_derniers_codes(self) -> list[ResultatScan]:
            """Retourne les derniers codes scannés."""
            return self.derniers_codes[-10:]

    return BarcodeVideoProcessor


def afficher_scanner_webrtc(
    on_scan: Callable[[str, str], None] | None = None, key: str = "barcode_scanner"
):
    """
    Affiche le scanner de codes-barres WebRTC.

    Args:
        on_scan: Callback appelé quand un code est scanné (code, type)
        key: Clé unique pour le composant
    """
    st.markdown("### 📷 Scanner WebRTC")
    st.caption("Scannez un code-barres avec votre webcam")

    # Vérifier les dépendances
    try:
        import cv2
        from pyzbar import pyzbar
        from streamlit_webrtc import WebRtcMode, webrtc_streamer
    except ImportError as e:
        st.error(f"""
        ⚠️ Dépendances manquantes pour le scanner WebRTC:

        ```bash
        pip install streamlit-webrtc opencv-python-headless pyzbar
        ```

        Erreur: {e}
        """)

        # Fallback: input manuel
        _afficher_fallback_manuel(on_scan)
        return

    # Configuration RTC
    RTC_CONFIGURATION = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

    # Obtenir le processor
    VideoProcessor = _get_video_processor()
    if VideoProcessor is None:
        st.error("Impossible de charger le processeur vidéo")
        _afficher_fallback_manuel(on_scan)
        return

    # État pour stocker les codes scannés
    if f"{key}_codes" not in st.session_state:
        st.session_state[f"{key}_codes"] = []

    # Zone de streaming
    col_video, col_resultats = st.columns([2, 1])

    with col_video:
        ctx = webrtc_streamer(
            key=key,
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=VideoProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        st.caption("💡 Approchez un code-barres de la caméra")

    with col_resultats:
        st.markdown("**Codes scannés:**")

        # Récupérer les codes depuis le processor
        if ctx.video_processor:
            codes = ctx.video_processor.get_derniers_codes()
            for resultat in codes[-5:]:
                with st.container():
                    st.code(resultat.code)
                    st.caption(f"Type: {resultat.type_code}")

                    if st.button("✅ Utiliser", key=f"use_{resultat.code}_{key}"):
                        if on_scan:
                            on_scan(resultat.code, resultat.type_code)
                        st.success(f"Code {resultat.code} sélectionné!")

        # Zone de résultats persistants
        if st.session_state[f"{key}_codes"]:
            st.divider()
            st.markdown("**Historique:**")
            for code in st.session_state[f"{key}_codes"][-3:]:
                st.text(code)


def _afficher_fallback_manuel(on_scan: Callable[[str, str], None] | None = None):
    """Affiche un fallback manuel si WebRTC non disponible."""
    st.info("📝 Saisie manuelle (WebRTC non disponible)")

    code = st.text_input("Code-barres:", placeholder="3017620422003", key="barcode_manual_input")

    type_code = st.selectbox(
        "Type de code:", ["EAN-13", "EAN-8", "UPC", "QR", "CODE128"], key="barcode_type_select"
    )

    if code and st.button("✅ Valider le code", type="primary"):
        if on_scan:
            on_scan(code, type_code)
        st.success(f"Code {code} validé!")


def afficher_scanner_camera_simple(key: str = "simple_scanner"):
    """
    Version simplifiée du scanner utilisant st.camera_input().

    Plus simple que WebRTC mais moins fluide (capture photo unique).
    """
    st.markdown("### 📸 Scanner Photo")
    st.caption("Prenez une photo d'un code-barres")

    try:
        import cv2
        import numpy as np
        from pyzbar import pyzbar
    except ImportError:
        st.error("Installez: `pip install opencv-python-headless pyzbar`")
        return None

    # Capture photo
    photo = st.camera_input("📷 Photographier le code-barres", key=key)

    if photo:
        # Convertir en image OpenCV
        file_bytes = np.asarray(bytearray(photo.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Convertir en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Détecter les codes
        barcodes = pyzbar.decode(gray)

        if barcodes:
            st.success(f"✅ {len(barcodes)} code(s) détecté(s)!")

            for barcode in barcodes:
                code = barcode.data.decode("utf-8")
                type_code = barcode.type

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Code", code)
                with col2:
                    st.metric("Type", type_code)

                return ResultatScan(
                    code=code,
                    type_code=type_code,
                    timestamp=str(np.datetime64("now")),
                )
        else:
            st.warning("⚠️ Aucun code-barres détecté. Réessayez avec plus de lumière.")

    return None


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    "ResultatScan",
    "afficher_scanner_webrtc",
    "afficher_scanner_camera_simple",
]
