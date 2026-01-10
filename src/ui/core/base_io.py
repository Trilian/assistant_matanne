"""
Base IO - Import/Export universel
Gestion automatique CSV/JSON depuis config
"""
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

from src.services.io_service import IOService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIG I/O
# ═══════════════════════════════════════════════════════════

@dataclass
class IOConfig:
    """
    Configuration Import/Export

    Permet de mapper champs DB ↔ Export
    """

    # Mapping DB field → Export label
    field_mapping: Dict[str, str]

    # Champs requis pour import
    required_fields: List[str]

    # Transformations custom
    transformers: Dict[str, callable] = None


# ═══════════════════════════════════════════════════════════
# BASE I/O SERVICE
# ═══════════════════════════════════════════════════════════

class BaseIOService:
    """
    Service I/O universel

    Génère automatiquement Import/Export depuis config

    Usage:
        config = IOConfig(
            field_mapping={
                "nom": "Nom",
                "quantite": "Quantité"
            },
            required_fields=["nom"]
        )

        io = BaseIOService(config)

        # Export
        csv = io.to_csv(items)

        # Import
        items, errors = io.from_csv(csv_content)
    """

    def __init__(self, config: IOConfig):
        self.config = config
        self.io_service = IOService()

    # ═══════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════

    def to_csv(self, items: List[Dict]) -> str:
        """
        Export CSV

        Args:
            items: Liste de dicts

        Returns:
            CSV string
        """
        return self.io_service.to_csv(
            items=items,
            field_mapping=self.config.field_mapping
        )

    def to_json(self, items: List[Dict], indent: int = 2) -> str:
        """
        Export JSON

        Args:
            items: Liste de dicts
            indent: Indentation

        Returns:
            JSON string
        """
        return self.io_service.to_json(items, indent=indent)

    # ═══════════════════════════════════════════════════════
    # IMPORT
    # ═══════════════════════════════════════════════════════

    def from_csv(self, csv_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Import CSV

        Args:
            csv_str: Contenu CSV

        Returns:
            (items_valides, erreurs)
        """
        items, errors = self.io_service.from_csv(
            csv_str=csv_str,
            field_mapping=self.config.field_mapping,
            required_fields=self.config.required_fields
        )

        # Appliquer transformations
        if self.config.transformers:
            items = self._apply_transformers(items)

        return items, errors

    def from_json(self, json_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Import JSON

        Args:
            json_str: Contenu JSON

        Returns:
            (items_valides, erreurs)
        """
        items, errors = self.io_service.from_json(
            json_str=json_str,
            required_fields=self.config.required_fields
        )

        # Appliquer transformations
        if self.config.transformers:
            items = self._apply_transformers(items)

        return items, errors

    # ═══════════════════════════════════════════════════════
    # TRANSFORMATIONS
    # ═══════════════════════════════════════════════════════

    def _apply_transformers(self, items: List[Dict]) -> List[Dict]:
        """Applique transformations custom"""
        if not self.config.transformers:
            return items

        transformed = []

        for item in items:
            transformed_item = item.copy()

            for field, transformer in self.config.transformers.items():
                if field in transformed_item:
                    try:
                        transformed_item[field] = transformer(
                            transformed_item[field]
                        )
                    except Exception as e:
                        logger.warning(
                            f"Erreur transformation {field}: {e}"
                        )

            transformed.append(transformed_item)

        return transformed


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_io_service(config: IOConfig) -> BaseIOService:
    """Factory pour créer service I/O"""
    return BaseIOService(config)