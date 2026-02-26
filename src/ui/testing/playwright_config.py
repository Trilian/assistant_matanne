"""
Configuration des tests visuels Playwright pour Streamlit.

Ce module configure Playwright pour effectuer des tests de régression
visuelle sur l'application Streamlit.

Usage:
    # Lancer les tests visuels
    pytest tests/visual/ --headed

    # Mettre à jour les snapshots
    pytest tests/visual/ --update-snapshots
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class PlaywrightConfig:
    """Configuration pour les tests Playwright."""

    # URL de l'application Streamlit
    base_url: str = "http://localhost:8501"

    # Timeout pour le chargement des pages (ms)
    timeout: int = 30000

    # Viewport par défaut
    viewport_width: int = 1280
    viewport_height: int = 720

    # Dossier des screenshots de référence
    snapshot_dir: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "snapshots" / "visual"
    )

    # Dossier des screenshots d'erreur
    output_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "test-results")

    # Seuil de différence acceptable (0-1)
    threshold: float = 0.1

    # Navigateurs à tester
    browsers: tuple[str, ...] = ("chromium",)

    # Appareils à simuler
    devices: tuple[str, ...] = ("Desktop Chrome", "iPhone 12", "iPad Pro")

    # Attente avant screenshot (ms)
    screenshot_delay: int = 500

    @property
    def update_snapshots(self) -> bool:
        """True si on doit mettre à jour les snapshots."""
        return os.environ.get("UPDATE_SNAPSHOTS") == "1"


# Configuration globale
config = PlaywrightConfig()


# ═══════════════════════════════════════════════════════════
# HELPERS POUR LES TESTS
# ═══════════════════════════════════════════════════════════


def get_pages_to_test() -> list[dict[str, str]]:
    """Retourne la liste des pages à tester.

    Returns:
        Liste de dict avec url_path et name.
    """
    return [
        {"path": "/", "name": "accueil"},
        {"path": "/design_system", "name": "design_system"},
        {"path": "/planning_calendrier", "name": "calendrier"},
        {"path": "/cuisine_recettes", "name": "recettes"},
        {"path": "/famille_hub", "name": "famille_hub"},
        {"path": "/parametres", "name": "parametres"},
    ]


def get_components_to_test() -> list[dict[str, str]]:
    """Retourne la liste des composants à tester isolément.

    Returns:
        Liste de dict avec component et variants.
    """
    return [
        {"component": "badge", "variants": ["success", "warning", "danger", "info"]},
        {"component": "boite_info", "variants": ["info", "success", "warning", "error"]},
        {"component": "metric_card", "variants": ["default", "highlight"]},
        {"component": "button", "variants": ["primary", "secondary", "danger"]},
    ]


__all__ = [
    "PlaywrightConfig",
    "config",
    "get_pages_to_test",
    "get_components_to_test",
]
