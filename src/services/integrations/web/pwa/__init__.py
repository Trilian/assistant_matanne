"""Package PWA - Progressive Web App pour l'Assistant Matanne."""

from .config import PWA_CONFIG, generate_icon_svg, generate_manifest
from .generation import (
    afficher_install_prompt,
    generate_pwa_files,
    inject_pwa_meta,
    is_pwa_installed,
)
from .offline import OFFLINE_HTML, generate_offline_page
from .service_worker import SERVICE_WORKER_JS, generate_service_worker

__all__ = [
    "PWA_CONFIG",
    "generate_manifest",
    "generate_service_worker",
    "SERVICE_WORKER_JS",
    "generate_offline_page",
    "OFFLINE_HTML",
    "generate_pwa_files",
    "is_pwa_installed",
    "generate_icon_svg",
    "inject_pwa_meta",
    "afficher_install_prompt",
]
