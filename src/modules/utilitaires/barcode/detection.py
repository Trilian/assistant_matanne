"""
Détection codes-barres - pyzbar, zxing-cpp, BarcodeScanner streaming.

Fonctions de détection:
- pyzbar (principal) avec fallback zxing-cpp
- Streaming webrtc temps réel
- Anti-doublon (scan_cooldown)
"""

import logging
from collections.abc import Callable
from datetime import datetime

import streamlit as st

from src.core.state import rerun
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("barcode")

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
                "📦 Packages requis non installés.\n\nExécutez: `pip install streamlit-webrtc av`"
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
        if _keys("detected", key) not in st.session_state:
            st.session_state[_keys("detected", key)] = []

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
                            st.session_state[_keys("detected", key)].append(
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
        detected = st.session_state.get(_keys("detected", key), [])

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
                st.session_state[_keys("detected", key)] = []
                rerun()

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
