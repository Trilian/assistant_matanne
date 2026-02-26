"""
WebRTC Barcode Scanner — Innovation v11: Scan codes-barres via webcam.

Composant Streamlit utilisant WebRTC + QuaggaJS/ZXing pour scanner
les codes-barres directement depuis la webcam du navigateur.

Fonctionnalités:
- Scan EAN-13, EAN-8, UPC, Code128, QR codes
- Détection automatique en temps réel
- Callback avec info produit (OpenFoodFacts)
- Mode continu ou single-scan
- Support mobile (caméra arrière)

Usage:
    from src.ui.components.barcode_scanner import (
        scanner_codes_barres,
        BarcodeScanner,
        obtenir_info_produit,
    )

    # Scanner simple
    code = scanner_codes_barres(key="scan_courses")
    if code:
        st.write(f"Code scanné: {code}")
        info = obtenir_info_produit(code)
        st.write(info)

    # Scanner avec callback
    def on_scan(code, info):
        ajouter_a_liste(info["nom"], 1)

    BarcodeScanner(key="scan_ajout").on_detect(on_scan).render()
"""

from __future__ import annotations

import logging
from typing import Any, Callable

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

__all__ = [
    "scanner_codes_barres",
    "BarcodeScanner",
    "obtenir_info_produit",
]


# ═══════════════════════════════════════════════════════════
# COMPOSANT HTML/JS — QuaggaJS Barcode Scanner
# ═══════════════════════════════════════════════════════════

_SCANNER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/@nicka80/quagga2@1.8.4/dist/quagga.min.js"></script>
    <style>
        #scanner-container-{key} {{
            position: relative;
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
        }}
        #scanner-video-{key} {{
            width: 100%;
            border-radius: 12px;
            background: #1a202c;
        }}
        #scanner-overlay-{key} {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80%;
            height: 40%;
            border: 3px solid rgba(102, 126, 234, 0.8);
            border-radius: 8px;
            pointer-events: none;
        }}
        #scanner-result-{key} {{
            text-align: center;
            padding: 12px;
            margin-top: 8px;
            border-radius: 8px;
            background: rgba(102, 126, 234, 0.1);
        }}
        .scanner-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin: 8px;
            transition: transform 0.2s;
        }}
        .scanner-btn:hover {{ transform: scale(1.05); }}
        .scanner-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .scanner-status {{
            text-align: center;
            color: #a0aec0;
            font-size: 14px;
            margin: 8px 0;
        }}
        .detected {{
            animation: pulse 0.5s ease-in-out;
            border-color: #48bb78 !important;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: translate(-50%, -50%) scale(1); }}
            50% {{ transform: translate(-50%, -50%) scale(1.05); }}
        }}
    </style>
</head>
<body>
    <div id="scanner-container-{key}">
        <div id="scanner-viewport-{key}">
            <video id="scanner-video-{key}" autoplay muted playsinline></video>
            <div id="scanner-overlay-{key}"></div>
        </div>
        <div class="scanner-status" id="scanner-status-{key}">
            Cliquez sur "Démarrer" pour scanner un code-barres
        </div>
        <div style="text-align: center;">
            <button class="scanner-btn" id="start-btn-{key}" onclick="startScanner_{key}()">
                📷 Démarrer
            </button>
            <button class="scanner-btn" id="stop-btn-{key}" onclick="stopScanner_{key}()" disabled>
                ⏹️ Arrêter
            </button>
        </div>
        <div id="scanner-result-{key}" style="display: none;"></div>
        <input type="hidden" id="scanner-output-{key}" value="">
    </div>

    <script>
    (function() {{
        let isScanning_{key} = false;
        let lastCode_{key} = '';
        let detectionCount_{key} = 0;
        const DETECTION_THRESHOLD = 3; // Confirmations requises

        window.startScanner_{key} = async function() {{
            const video = document.getElementById('scanner-video-{key}');
            const status = document.getElementById('scanner-status-{key}');
            const startBtn = document.getElementById('start-btn-{key}');
            const stopBtn = document.getElementById('stop-btn-{key}');

            try {{
                // Demander accès caméra (préférer arrière sur mobile)
                const stream = await navigator.mediaDevices.getUserMedia({{
                    video: {{
                        facingMode: {{ ideal: '{camera_facing}' }},
                        width: {{ ideal: 1280 }},
                        height: {{ ideal: 720 }}
                    }}
                }});

                video.srcObject = stream;
                await video.play();

                isScanning_{key} = true;
                startBtn.disabled = true;
                stopBtn.disabled = false;
                status.textContent = '🔍 Recherche de code-barres...';

                // Initialiser QuaggaJS
                Quagga.init({{
                    inputStream: {{
                        name: "Live",
                        type: "LiveStream",
                        target: document.getElementById('scanner-viewport-{key}'),
                        constraints: {{
                            facingMode: '{camera_facing}'
                        }}
                    }},
                    decoder: {{
                        readers: [
                            'ean_reader',
                            'ean_8_reader',
                            'upc_reader',
                            'upc_e_reader',
                            'code_128_reader',
                            'code_39_reader'
                        ]
                    }},
                    locate: true,
                    frequency: 10
                }}, function(err) {{
                    if (err) {{
                        console.error('QuaggaJS init error:', err);
                        // Fallback: utiliser video stream direct
                        startBrowserDetection_{key}(video);
                        return;
                    }}
                    Quagga.start();
                }});

                Quagga.onDetected(function(result) {{
                    const code = result.codeResult.code;
                    handleDetection_{key}(code);
                }});

            }} catch (err) {{
                console.error('Camera access error:', err);
                status.textContent = '❌ Accès caméra refusé: ' + err.message;
            }}
        }};

        window.stopScanner_{key} = function() {{
            isScanning_{key} = false;

            // Arrêter QuaggaJS
            try {{ Quagga.stop(); }} catch(e) {{}}

            // Arrêter le stream vidéo
            const video = document.getElementById('scanner-video-{key}');
            if (video.srcObject) {{
                video.srcObject.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }}

            document.getElementById('start-btn-{key}').disabled = false;
            document.getElementById('stop-btn-{key}').disabled = true;
            document.getElementById('scanner-status-{key}').textContent = 'Scanner arrêté';
        }};

        function handleDetection_{key}(code) {{
            if (!code || code.length < 8) return;

            // Confirmation multi-lecture pour éviter les faux positifs
            if (code === lastCode_{key}) {{
                detectionCount_{key}++;
            }} else {{
                lastCode_{key} = code;
                detectionCount_{key} = 1;
            }}

            if (detectionCount_{key} >= DETECTION_THRESHOLD) {{
                // Code confirmé!
                onCodeDetected_{key}(code);
                detectionCount_{key} = 0;
                lastCode_{key} = '';
            }}
        }}

        function onCodeDetected_{key}(code) {{
            // Feedback visuel
            const overlay = document.getElementById('scanner-overlay-{key}');
            overlay.classList.add('detected');
            setTimeout(() => overlay.classList.remove('detected'), 500);

            // Son de confirmation (optionnel)
            try {{
                const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2telegoAHIj');
                audio.volume = 0.3;
                audio.play().catch(() => {{}});
            }} catch(e) {{}}

            // Mettre à jour le résultat
            const resultDiv = document.getElementById('scanner-result-{key}');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<strong>✅ Code détecté:</strong> ' + code;

            const status = document.getElementById('scanner-status-{key}');
            status.textContent = '✅ Code scanné: ' + code;

            // Stocker le résultat
            document.getElementById('scanner-output-{key}').value = code;

            // Envoyer à Streamlit
            if (window.parent) {{
                window.parent.postMessage({{
                    type: 'BARCODE_DETECTED',
                    key: '{key}',
                    code: code,
                    format: 'EAN'
                }}, '*');
            }}

            // Mode single: arrêter après détection
            if ({single_scan}) {{
                stopScanner_{key}();
            }}
        }}

        // Fallback pour navigateurs sans QuaggaJS
        function startBrowserDetection_{key}(video) {{
            // Utiliser BarcodeDetector API si disponible (Chrome)
            if ('BarcodeDetector' in window) {{
                const detector = new BarcodeDetector({{
                    formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e', 'code_128', 'qr_code']
                }});

                const detect = async () => {{
                    if (!isScanning_{key}) return;

                    try {{
                        const barcodes = await detector.detect(video);
                        if (barcodes.length > 0) {{
                            handleDetection_{key}(barcodes[0].rawValue);
                        }}
                    }} catch(e) {{}}

                    requestAnimationFrame(detect);
                }};
                detect();
            }} else {{
                document.getElementById('scanner-status-{key}').textContent =
                    '⚠️ BarcodeDetector non supporté. Utilisez Chrome/Edge.';
            }}
        }}
    }})();
    </script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
# BARCODE SCANNER CLASS
# ═══════════════════════════════════════════════════════════


class BarcodeScanner:
    """Scanner de codes-barres WebRTC avancé.

    Usage:
        scanner = BarcodeScanner(key="mon_scanner")
        scanner.on_detect(callback_function)
        scanner.render()
    """

    def __init__(
        self,
        key: str = "barcode_scanner",
        *,
        single_scan: bool = True,
        camera_facing: str = "environment",  # environment (arrière) ou user (avant)
        height: int = 450,
        auto_lookup: bool = True,
    ):
        """
        Args:
            key: Clé unique du composant
            single_scan: Arrêter après une détection
            camera_facing: Caméra à utiliser (environment/user)
            height: Hauteur du composant
            auto_lookup: Rechercher auto les infos produit
        """
        self.key = key
        self.single_scan = single_scan
        self.camera_facing = camera_facing
        self.height = height
        self.auto_lookup = auto_lookup
        self._callbacks: list[Callable[[str, dict], None]] = []

    def on_detect(self, callback: Callable[[str, dict[str, Any]], None]) -> BarcodeScanner:
        """Ajoute un callback appelé lors de la détection.

        Args:
            callback: Fonction(code: str, info: dict)

        Returns:
            self pour chaînage
        """
        self._callbacks.append(callback)
        return self

    def render(self) -> str | None:
        """Affiche le scanner et retourne le code détecté.

        Returns:
            Code-barres détecté ou None
        """
        # Session state pour stocker le résultat
        state_key = f"barcode_{self.key}"
        if state_key not in st.session_state:
            st.session_state[state_key] = None

        # Input caché pour recevoir le code
        code_input = st.text_input(
            f"barcode_input_{self.key}",
            key=f"barcode_input_{self.key}",
            label_visibility="collapsed",
        )

        # Render HTML component
        html = _SCANNER_HTML.format(
            key=self.key,
            single_scan="true" if self.single_scan else "false",
            camera_facing=self.camera_facing,
        )
        components.html(html, height=self.height)

        # Traiter le code si détecté
        if code_input and code_input != st.session_state.get(f"{state_key}_last"):
            st.session_state[f"{state_key}_last"] = code_input
            st.session_state[state_key] = code_input

            # Lookup info produit
            info = {}
            if self.auto_lookup:
                info = obtenir_info_produit(code_input) or {}

            # Appeler les callbacks
            for callback in self._callbacks:
                try:
                    callback(code_input, info)
                except Exception as e:
                    logger.error(f"Callback error: {e}")

            # Afficher les infos
            if info:
                st.success(f"✅ **{info.get('nom', 'Produit inconnu')}**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Marque", info.get("marque", "N/A"))
                with col2:
                    st.metric("Nutri-Score", info.get("nutriscore", "N/A"))

            return code_input

        return st.session_state.get(state_key)


# ═══════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════


def scanner_codes_barres(
    *,
    key: str = "barcode",
    single_scan: bool = True,
    camera: str = "environment",
    height: int = 450,
) -> str | None:
    """Scanner de codes-barres simplifié.

    Args:
        key: Clé unique
        single_scan: Arrêter après détection
        camera: Caméra (environment=arrière, user=avant)
        height: Hauteur du widget

    Returns:
        Code-barres détecté ou None
    """
    scanner = BarcodeScanner(
        key=key,
        single_scan=single_scan,
        camera_facing=camera,
        height=height,
    )
    return scanner.render()


def obtenir_info_produit(code: str) -> dict[str, Any] | None:
    """Récupère les informations d'un produit via OpenFoodFacts.

    Args:
        code: Code-barres EAN/UPC

    Returns:
        Dict avec nom, marque, nutriscore, etc. ou None
    """
    if not code or len(code) < 8:
        return None

    try:
        import httpx

        url = f"https://world.openfoodfacts.org/api/v2/product/{code}.json"
        response = httpx.get(url, timeout=10, follow_redirects=True)

        if response.status_code != 200:
            return None

        data = response.json()
        product = data.get("product", {})

        if not product:
            return None

        return {
            "code": code,
            "nom": product.get("product_name_fr") or product.get("product_name", "Inconnu"),
            "marque": product.get("brands", "N/A"),
            "quantite": product.get("quantity", ""),
            "nutriscore": product.get("nutriscore_grade", "").upper() or "N/A",
            "nova": product.get("nova_group", ""),
            "ecoscore": product.get("ecoscore_grade", "").upper() or "N/A",
            "categories": product.get("categories", ""),
            "image_url": product.get("image_url", ""),
            "ingredients": product.get("ingredients_text_fr", ""),
            "allergenes": product.get("allergens_tags", []),
            "energie_kcal": product.get("nutriments", {}).get("energy-kcal_100g", 0),
        }

    except Exception as e:
        logger.error(f"OpenFoodFacts lookup error: {e}")
        return None


@st.fragment
def widget_scan_rapide(
    *,
    key: str = "scan_rapide",
    on_produit: Callable[[dict[str, Any]], None] | None = None,
) -> None:
    """Widget compact de scan rapide pour ajout à liste.

    Args:
        key: Clé unique
        on_produit: Callback quand produit détecté
    """
    st.markdown("### 📷 Scan rapide")

    code = scanner_codes_barres(key=key, single_scan=True, height=350)

    if code:
        info = obtenir_info_produit(code)

        if info:
            st.success(f"✅ {info['nom']}")

            col1, col2, col3 = st.columns(3)
            col1.metric("Marque", info.get("marque", "N/A"))
            col2.metric("Nutri-Score", info.get("nutriscore", "N/A"))
            col3.metric("Calories", f"{info.get('energie_kcal', 0)} kcal")

            if st.button("➕ Ajouter à la liste", key=f"{key}_add"):
                if on_produit:
                    on_produit(info)
                st.success("Ajouté!")
                # Reset
                del st.session_state[f"barcode_{key}"]
                st.rerun()
        else:
            st.warning(f"Produit non trouvé: {code}")
            st.text_input("Nom du produit", key=f"{key}_manual_name")
            if st.button("Ajouter manuellement", key=f"{key}_manual_add"):
                nom = st.session_state.get(f"{key}_manual_name", code)
                if on_produit:
                    on_produit({"code": code, "nom": nom})
