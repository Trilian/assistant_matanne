"""
Base IO Service - Import/Export Universel
Génère automatiquement Import/Export depuis config
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
    """Configuration Import/Export"""
    field_mapping: Dict[str, str]  # {db_field: export_label}
    required_fields: List[str]


# ═══════════════════════════════════════════════════════════
# BASE I/O SERVICE
# ═══════════════════════════════════════════════════════════

class BaseIOService:
    """
    Service I/O universel

    Génère automatiquement Import/Export depuis config
    """

    def __init__(self, config: IOConfig):
        self.config = config
        self.io_service = IOService()

    # ═══════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════

    def to_csv(self, items: List[Dict]) -> str:
        """Export CSV"""
        return self.io_service.to_csv(
            items=items,
            field_mapping=self.config.field_mapping
        )

    def to_json(self, items: List[Dict], indent: int = 2) -> str:
        """Export JSON"""
        return self.io_service.to_json(items, indent=indent)

    # ═══════════════════════════════════════════════════════
    # IMPORT
    # ═══════════════════════════════════════════════════════

    def from_csv(self, csv_str: str) -> Tuple[List[Dict], List[str]]:
        """Import CSV"""
        return self.io_service.from_csv(
            csv_str=csv_str,
            field_mapping=self.config.field_mapping,
            required_fields=self.config.required_fields
        )

    def from_json(self, json_str: str) -> Tuple[List[Dict], List[str]]:
        """Import JSON"""
        return self.io_service.from_json(
            json_str=json_str,
            required_fields=self.config.required_fields
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_io_service(config: IOConfig) -> BaseIOService:
    """Factory pour créer service I/O"""
    return BaseIOService(config)