"""
Base IO - Import/Export universel
Gestion automatique CSV/JSON depuis config
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.services.base import IOService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION IO
# ═══════════════════════════════════════════════════════════


@dataclass
class ConfigurationIO:
    """
    Configuration Import/Export

    Permet de mapper champs DB ↔ Export
    """

    # Mapping DB field → Export label
    field_mapping: dict[str, str]

    # Champs requis pour import
    required_fields: list[str]

    # Transformations custom
    transformers: dict[str, Callable[[Any], Any]] | None = None


# ═══════════════════════════════════════════════════════════
# SERVICE IO BASE
# ═══════════════════════════════════════════════════════════


class ServiceIOBase:
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

    def __init__(self, config: ConfigurationIO):
        self.config = config
        self.io_service = IOService()

    # ═══════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════

    def to_csv(self, items: list[dict]) -> str:
        """
        Export CSV

        Args:
            items: Liste de dicts

        Returns:
            CSV string
        """
        return self.io_service.to_csv(items=items, field_mapping=self.config.field_mapping)

    def to_json(self, items: list[dict], indent: int = 2) -> str:
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

    def from_csv(self, csv_str: str) -> tuple[list[dict], list[str]]:
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
            required_fields=self.config.required_fields,
        )

        # Appliquer transformations
        if self.config.transformers:
            items = self._apply_transformers(items)

        return items, errors

    def from_json(self, json_str: str) -> tuple[list[dict], list[str]]:
        """
        Import JSON

        Args:
            json_str: Contenu JSON

        Returns:
            (items_valides, erreurs)
        """
        items, errors = self.io_service.from_json(
            json_str=json_str, required_fields=self.config.required_fields
        )

        # Appliquer transformations
        if self.config.transformers:
            items = self._apply_transformers(items)

        return items, errors

    # ═══════════════════════════════════════════════════════
    # TRANSFORMATIONS
    # ═══════════════════════════════════════════════════════

    def _apply_transformers(self, items: list[dict]) -> list[dict]:
        """Applique transformations custom"""
        if not self.config.transformers:
            return items

        transformed = []

        for item in items:
            transformed_item = item.copy()

            for field, transformer in self.config.transformers.items():
                if field in transformed_item:
                    try:
                        transformed_item[field] = transformer(transformed_item[field])
                    except Exception as e:
                        logger.warning(f"Erreur transformation {field}: {e}")

            transformed.append(transformed_item)

        return transformed


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def creer_service_io(config: ConfigurationIO) -> ServiceIOBase:
    """Factory pour créer service I/O"""
    return ServiceIOBase(config)


# Alias pour compatibilité
IOConfig = ConfigurationIO
BaseIOService = ServiceIOBase
create_io_service = creer_service_io
