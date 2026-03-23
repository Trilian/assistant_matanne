"""
Génération PWA - Orchestration de la génération des fichiers PWA.

Ce module contient:
- generate_pwa_files(): Orchestrateur de génération de tous les fichiers PWA
- is_pwa_installed(): Vérification d'installation PWA (stub côté client)
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


def is_pwa_installed() -> bool:
    """
    Vérifie si l'app est installée en PWA.

    Note: Ne fonctionne que côté client via JavaScript.
    """
    return False


# ═══════════════════════════════════════════════════════════
# STUBS DEPRECATED (rétrocompatibilité)
# ═══════════════════════════════════════════════════════════


def inject_pwa_meta() -> None:
    """DEPRECATED — plus nécessaire avec Next.js."""
    pass


def afficher_install_prompt() -> None:
    """DEPRECATED — plus nécessaire avec Next.js."""
    pass
