"""
Composant de scan code-barres par caméra.

Utilise streamlit-webrtc pour le streaming vidéo
et pyzbar/opencv pour la détection des codes-barres.
"""

import logging
from datetime import datetime
from typing import Callable

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# DÉTECTION AVEC PYZBAR (si disponible)
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
        from pyzbar import pyzbar
        import cv2
        
        # Convertir en grayscale pour meilleure détection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détecter les codes
        codes = pyzbar.decode(gray)
        
        results = []
        for code in codes:
            results.append({
                "type": code.type,
                "data": code.data.decode("utf-8"),
                "rect": code.rect,
            })
        
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
        Liste de codes détectés
    """
    # Essayer pyzbar d'abord
    results = _detect_barcode_pyzbar(frame)
    
    if not results:
        # Fallback sur zxing
        results = _detect_barcode_zxing(frame)
    
    return results


# ═══════════════════════════════════════════════════════════
# COMPOSANT STREAMLIT-WEBRTC
# ═══════════════════════════════════════════════════════════


class BarcodeScanner:
    """
    Scanner de codes-barres avec caméra.
    
    Utilise streamlit-webrtc pour le streaming vidéo.
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
        Affiche le composant scanner.
        
        Args:
            key: Clé unique pour le composant
        """
        try:
            from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
            import av
            import numpy as np
        except ImportError:
            st.error(
                "📦 Packages requis non installés.\n\n"
                "Exécutez: `pip install streamlit-webrtc opencv-python pyzbar`"
            )
            self._render_fallback_input(key)
            return
        
        # Configuration RTC (serveurs STUN publics)
        rtc_config = RTCConfiguration({
            "iceServers": [
                {"urls": ["stun:stun.l.google.com:19302"]},
                {"urls": ["stun:stun1.l.google.com:19302"]},
            ]
        })
        
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
                            st.session_state[f"{key}_detected"].append({
                                "type": code["type"],
                                "data": code["data"],
                                "time": datetime.now().isoformat(),
                            })
                            
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
                                3
                            )
                            cv2.putText(
                                img,
                                code["data"][:20],
                                (rect.left, rect.top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 255, 0),
                                2
                            )
                
                return av.VideoFrame.from_ndarray(img, format="bgr24")
        
        # Interface
        st.markdown("### 📷 Scanner par caméra")
        st.info("👆 Autorisez l'accès à la caméra, puis présentez le code-barres")
        
        # Streamer vidéo
        ctx = webrtc_streamer(
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
                st.metric("Code", last["data"][:20] + "..." if len(last["data"]) > 20 else last["data"])
            
            # Bouton pour effacer
            if st.button("🗑️ Effacer historique", key=f"{key}_clear"):
                st.session_state[f"{key}_detected"] = []
                st.rerun()
            
            # Liste des codes
            with st.expander("📋 Historique des scans"):
                for i, scan in enumerate(reversed(detected[-10:])):
                    st.caption(f"{scan['time']}: [{scan['type']}] {scan['data']}")
    
    def _render_fallback_input(self, key: str):
        """Affiche un input texte en fallback."""
        st.markdown("### 📝 Saisie manuelle")
        st.warning("Caméra non disponible - utilisez la saisie manuelle")
        
        code = st.text_input(
            "Entrez le code-barres:",
            key=f"{key}_manual",
            placeholder="EAN13, QR Code, etc."
        )
        
        if code and st.button("✅ Valider", key=f"{key}_validate"):
            if self.on_scan:
                self.on_scan("MANUAL", code)
            st.success(f"Code enregistré: {code}")


# ═══════════════════════════════════════════════════════════
# COMPOSANT SIMPLIFIÉ (sans webrtc)
# ═══════════════════════════════════════════════════════════


def render_camera_scanner_simple(
    on_scan: Callable[[str], None] = None,
    key: str = "simple_scanner"
):
    """
    Scanner simplifié utilisant st.camera_input.
    
    Plus compatible mais moins fluide que webrtc.
    
    Args:
        on_scan: Callback quand code détecté
        key: Clé unique
    """
    st.markdown("### 📷 Scanner (mode photo)")
    st.info("Prenez une photo du code-barres")
    
    # Capture photo
    camera_photo = st.camera_input(
        "Prendre une photo",
        key=f"{key}_camera",
        label_visibility="collapsed"
    )
    
    if camera_photo:
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            # Convertir en numpy array
            image = Image.open(camera_photo)
            frame = np.array(image)
            
            # Convertir RGB -> BGR pour OpenCV
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Détecter
            codes = detect_barcodes(frame)
            
            if codes:
                st.success(f"✅ {len(codes)} code(s) détecté(s)!")
                
                for code in codes:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Type", code["type"])
                    with col2:
                        st.metric("Code", code["data"])
                    
                    if on_scan:
                        on_scan(code["data"])
            else:
                st.warning("⚠️ Aucun code détecté. Essayez avec plus de lumière ou de plus près.")
        
        except ImportError as e:
            st.error(f"Package manquant: {e}")
        except Exception as e:
            st.error(f"Erreur de traitement: {e}")


# ═══════════════════════════════════════════════════════════
# HELPER POUR INTÉGRATION
# ═══════════════════════════════════════════════════════════


def render_barcode_scanner_widget(
    mode: str = "auto",
    on_scan: Callable[[str], None] = None,
    key: str = "barcode_widget"
):
    """
    Widget de scanner code-barres adaptif.
    
    Choisit automatiquement le meilleur mode selon les packages disponibles.
    
    Args:
        mode: 'auto', 'webrtc', 'camera', 'manual'
        on_scan: Callback quand code détecté
        key: Clé unique
    """
    # Détecter les packages disponibles
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
    
    # Sélection du mode
    if mode == "auto":
        if has_webrtc and has_cv2 and has_pyzbar:
            mode = "webrtc"
        elif has_cv2 and has_pyzbar:
            mode = "camera"
        else:
            mode = "manual"
    
    # Onglets pour choisir le mode
    available_modes = []
    if has_webrtc and has_cv2:
        available_modes.append("📹 Vidéo")
    if has_cv2:
        available_modes.append("📷 Photo")
    available_modes.append("⌨️ Manuel")
    
    if len(available_modes) > 1:
        selected_tab = st.radio(
            "Mode de scan:",
            available_modes,
            horizontal=True,
            key=f"{key}_mode"
        )
    else:
        selected_tab = available_modes[0]
    
    # Afficher le mode sélectionné
    if selected_tab == "📹 Vidéo":
        scanner = BarcodeScanner(
            on_scan=lambda t, d: on_scan(d) if on_scan else None
        )
        scanner.render(key=f"{key}_webrtc")
    
    elif selected_tab == "📷 Photo":
        render_camera_scanner_simple(
            on_scan=on_scan,
            key=f"{key}_photo"
        )
    
    else:
        # Mode manuel
        st.markdown("### ⌨️ Saisie manuelle")
        code = st.text_input(
            "Code-barres:",
            key=f"{key}_manual_input",
            placeholder="Entrez ou scannez avec un lecteur externe"
        )
        
        if code:
            if st.button("✅ Valider", key=f"{key}_manual_btn"):
                if on_scan:
                    on_scan(code)
                st.success(f"Code: {code}")


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    "BarcodeScanner",
    "detect_barcodes",
    "render_camera_scanner_simple",
    "render_barcode_scanner_widget",
]
