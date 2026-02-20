"""Package PWA - Progressive Web App pour l'Assistant Matanne."""

from .config import PWA_CONFIG, generate_icon_svg, generate_manifest
from .generation import (
    afficher_install_prompt,
    generate_pwa_files,
    inject_pwa_meta,
    is_pwa_installed,
)
from .offline import generate_offline_page
from .service_worker import generate_service_worker

__all__ = [
    "PWA_CONFIG",
    "generate_manifest",
    "generate_service_worker",
    "generate_offline_page",
    "generate_pwa_files",
    "is_pwa_installed",
    "generate_icon_svg",
    "inject_pwa_meta",
    "afficher_install_prompt",
]
