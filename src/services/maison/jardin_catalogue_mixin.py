"""
Mixin Catalogue Jardin - Chargement et gestion du catalogue de plantes.

Fonctionnalités:
- Chargement du catalogue depuis fichier JSON
- Catalogue par défaut minimal
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JardinCatalogueMixin:
    """Mixin pour le chargement et la gestion du catalogue de plantes."""

    _catalogue_cache: dict | None = None

    # ─────────────────────────────────────────────────────────
    # CATALOGUE PLANTES
    # ─────────────────────────────────────────────────────────

    def charger_catalogue_plantes(self) -> dict:
        """Charge le catalogue des plantes depuis le fichier JSON."""
        if self._catalogue_cache is not None:
            return self._catalogue_cache

        try:
            catalogue_path = (
                Path(__file__).parent.parent.parent.parent / "data" / "catalogue_jardin.json"
            )
            if catalogue_path.exists():
                with open(catalogue_path, encoding="utf-8") as f:
                    self._catalogue_cache = json.load(f)
                    return self._catalogue_cache
        except Exception as e:
            logger.error(f"Erreur chargement catalogue: {e}")

        # Catalogue minimal par défaut
        self._catalogue_cache = self._catalogue_defaut()
        return self._catalogue_cache

    def _catalogue_defaut(self) -> dict:
        """Retourne le catalogue par défaut."""
        return {
            "plantes": {
                "tomate": {
                    "nom": "Tomate",
                    "emoji": "🍅",
                    "categorie": "légume-fruit",
                    "semis_interieur": [2, 3],
                    "plantation_exterieur": [5, 6],
                    "recolte": [7, 8, 9],
                    "rendement_kg_m2": 4,
                    "besoin_eau": "moyen",
                    "exposition": "soleil",
                },
                "courgette": {
                    "nom": "Courgette",
                    "emoji": "🥒",
                    "categorie": "légume-fruit",
                    "semis_interieur": [3, 4],
                    "plantation_exterieur": [5, 6],
                    "recolte": [6, 7, 8, 9],
                    "rendement_kg_m2": 5,
                    "besoin_eau": "élevé",
                },
                "carotte": {
                    "nom": "Carotte",
                    "emoji": "🥕",
                    "categorie": "légume-racine",
                    "semis_direct": [3, 4, 5, 6],
                    "recolte": [6, 7, 8, 9, 10],
                    "rendement_kg_m2": 3,
                    "besoin_eau": "faible",
                },
                "salade": {
                    "nom": "Salade",
                    "emoji": "🥬",
                    "categorie": "légume-feuille",
                    "semis_direct": [3, 4, 5, 6, 7, 8],
                    "recolte": [4, 5, 6, 7, 8, 9, 10],
                    "rendement_kg_m2": 2,
                    "besoin_eau": "moyen",
                },
                "basilic": {
                    "nom": "Basilic",
                    "emoji": "🌿",
                    "categorie": "aromatique",
                    "semis_interieur": [3, 4],
                    "plantation_exterieur": [5, 6],
                    "recolte": [6, 7, 8, 9],
                    "rendement_kg_m2": 0.5,
                    "besoin_eau": "moyen",
                },
            },
            "objectifs_autonomie": {
                "legumes_fruits_kg": 150,
                "legumes_feuilles_kg": 50,
                "legumes_racines_kg": 60,
                "aromatiques_kg": 5,
            },
        }
