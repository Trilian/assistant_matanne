"""
Configuration PWA - Constantes et génération du manifest/icônes.

Ce module contient:
- PWA_CONFIG: Configuration complète du manifest PWA
- generate_manifest(): Génération du fichier manifest.json
- generate_icon_svg(): Génération d'icônes SVG par défaut
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION PWA
# ═══════════════════════════════════════════════════════════


PWA_CONFIG = {
    "name": "Assistant Matanne",
    "short_name": "Matanne",
    "description": "Hub de gestion familiale - Recettes, Courses, Planning",
    "start_url": "/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#ffffff",
    "theme_color": "#667eea",
    "scope": "/",
    "lang": "fr-FR",
    "categories": ["lifestyle", "productivity", "food"],
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable any",
        },
    ],
    "shortcuts": [
        {
            "name": "Recettes",
            "short_name": "Recettes",
            "description": "Accéder aux recettes",
            "url": "/?module=cuisine.recettes",
            "icons": [{"src": "/static/icons/recipe-96x96.png", "sizes": "96x96"}],
        },
        {
            "name": "Liste de courses",
            "short_name": "Courses",
            "description": "Voir la liste de courses",
            "url": "/?module=cuisine.courses",
            "icons": [{"src": "/static/icons/cart-96x96.png", "sizes": "96x96"}],
        },
        {
            "name": "Planning",
            "short_name": "Planning",
            "description": "Voir le planning des repas",
            "url": "/?module=planning",
            "icons": [{"src": "/static/icons/calendar-96x96.png", "sizes": "96x96"}],
        },
    ],
    "screenshots": [
        {
            "src": "/static/screenshots/home.png",
            "sizes": "1280x720",
            "type": "image/png",
            "form_factor": "wide",
            "label": "Tableau de bord",
        },
        {
            "src": "/static/screenshots/mobile.png",
            "sizes": "750x1334",
            "type": "image/png",
            "form_factor": "narrow",
            "label": "Vue mobile",
        },
    ],
    "related_applications": [],
    "prefer_related_applications": False,
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE GÉNÉRATION
# ═══════════════════════════════════════════════════════════


def generate_manifest(output_path: str | Path) -> Path:
    """
    Génère le fichier manifest.json.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Chemin du fichier créé
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest_path = output_path / "manifest.json"
    manifest_path.write_text(json.dumps(PWA_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"✅ Manifest généré: {manifest_path}")
    return manifest_path


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION D'ICÔNES
# ═══════════════════════════════════════════════════════════


def generate_icon_svg(size: int = 512) -> str:
    """
    Génère un SVG d'icône par défaut.

    Args:
        size: Taille de l'icône

    Returns:
        Code SVG
    """
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="{size}" height="{size}" rx="{size // 8}" fill="url(#grad)"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
              font-size="{size // 2}" font-family="Arial" fill="white">🏠</text>
    </svg>
    """
