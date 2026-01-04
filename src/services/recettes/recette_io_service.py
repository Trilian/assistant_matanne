"""
Service Import/Export Recettes

Gère l'import et l'export des recettes en CSV/JSON.
"""
import logging
from typing import List, Dict, Tuple

from src.services.io_service import IOService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

RECETTE_FIELD_MAPPING = {
    "nom": "Nom",
    "description": "Description",
    "temps_preparation": "Temps préparation (min)",
    "temps_cuisson": "Temps cuisson (min)",
    "portions": "Portions",
    "difficulte": "Difficulté",
    "type_repas": "Type repas",
    "saison": "Saison",
}

RECETTE_REQUIRED_FIELDS = ["nom", "temps_preparation", "temps_cuisson", "portions"]


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

class RecetteExporter:
    """Exporteur de recettes."""

    @staticmethod
    def to_csv(recettes: List[Dict]) -> str:
        """
        Exporte recettes en CSV.

        Args:
            recettes: Liste de recettes

        Returns:
            String CSV
        """
        return IOService.to_csv(recettes, RECETTE_FIELD_MAPPING)

    @staticmethod
    def to_json(recettes: List[Dict], indent: int = 2) -> str:
        """
        Exporte recettes en JSON.

        Args:
            recettes: Liste de recettes
            indent: Indentation JSON

        Returns:
            String JSON
        """
        return IOService.to_json(recettes, indent=indent)


# ═══════════════════════════════════════════════════════════
# IMPORT
# ═══════════════════════════════════════════════════════════

class RecetteImporter:
    """Importeur de recettes."""

    @staticmethod
    def from_csv(csv_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe recettes depuis CSV.

        Args:
            csv_str: Contenu CSV

        Returns:
            (recettes_validées, erreurs)
        """
        return IOService.from_csv(
            csv_str,
            RECETTE_FIELD_MAPPING,
            RECETTE_REQUIRED_FIELDS
        )

    @staticmethod
    def from_json(json_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe recettes depuis JSON.

        Args:
            json_str: Contenu JSON

        Returns:
            (recettes_validées, erreurs)
        """
        return IOService.from_json(json_str, RECETTE_REQUIRED_FIELDS)