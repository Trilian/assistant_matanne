"""
Génération et injection PWA - Orchestration et intégration Streamlit.

Ce module contient:
- generate_pwa_files(): Orchestrateur de génération de tous les fichiers PWA
- is_pwa_installed(): Vérification d'installation PWA
- inject_pwa_meta(): Injection des meta tags PWA dans Streamlit
- afficher_install_prompt(): Affichage du bouton d'installation PWA
"""

import logging
from pathlib import Path

from .config import generate_icon_svg, generate_manifest
from .offline import generate_offline_page
from .service_worker import generate_service_worker

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE GÉNÉRATION
# ═══════════════════════════════════════════════════════════


def generate_pwa_files(output_path: str | Path = "static") -> dict[str, Path]:
    """
    Génère tous les fichiers PWA.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Dictionnaire des fichiers créés
    """
    output_path = Path(output_path)

    files = {
        "manifest": generate_manifest(output_path),
        "service_worker": generate_service_worker(output_path),
        "offline": generate_offline_page(output_path),
    }

    # Créer le dossier des icônes
    icons_path = output_path / "icons"
    icons_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"✅ Tous les fichiers PWA générés dans: {output_path}")
    return files


# ═══════════════════════════════════════════════════════════
# INJECTION DANS STREAMLIT
# ═══════════════════════════════════════════════════════════


def is_pwa_installed() -> bool:
    """
    Vérifie si l'app est installée en PWA.

    Note: Ne fonctionne que côté client via JavaScript.
    """
    # Cette vérification doit être faite côté client
    return False


# ═══════════════════════════════════════════════════════════
# RE-EXPORTS UI (rétrocompatibilité)
# ═══════════════════════════════════════════════════════════


def inject_pwa_meta() -> None:
    """Injecte les meta tags PWA (délègue à src.ui.views.pwa)."""
    from src.ui.views.pwa import injecter_meta_pwa

    injecter_meta_pwa()


def afficher_install_prompt() -> None:
    """Affiche le bouton d'installation PWA."""
    import streamlit.components.v1 as components

    install_html = """
    <div id="pwa-install-container" style="text-align: center; padding: 10px;">
        <button id="pwa-install-btn" onclick="installPWA()"
                style="background: linear-gradient(135deg, #667eea, #764ba2);
                       color: white; border: none; padding: 12px 24px;
                       border-radius: 8px; cursor: pointer; font-size: 16px;">
            📱 Installer l'application
        </button>
    </div>
    <script>
        let deferredPrompt;
        const installBtn = document.getElementById('pwa-install-btn');

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
        });

        async function installPWA() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('Install outcome:', outcome);
                deferredPrompt = null;
            }
        }
    </script>
    """
    components.html(install_html, height=80)
