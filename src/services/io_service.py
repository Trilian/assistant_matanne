"""
Service I/O Universel - Import/Export CSV/JSON
Remplace inventaire_io_service.py + recette_io_service.py + base_io_service.py
"""
import csv
import json
import io
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)


class IOService:
    """Service Import/Export universel"""

    @staticmethod
    def to_csv(items: List[Dict], field_mapping: Dict[str, str]) -> str:
        """
        Exporte en CSV

        Args:
            items: Liste de dicts
            field_mapping: {"db_field": "export_label"}

        Returns:
            String CSV
        """
        if not items:
            return ""

        output = io.StringIO()
        fieldnames = list(field_mapping.values())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in items:
            row = {}
            for db_field, export_label in field_mapping.items():
                value = item.get(db_field)
                row[export_label] = IOService._format_value(value)
            writer.writerow(row)

        logger.info(f"CSV export: {len(items)} items")
        return output.getvalue()

    @staticmethod
    def from_csv(csv_str: str, field_mapping: Dict[str, str],
                 required_fields: List[str]) -> tuple[List[Dict], List[str]]:
        """
        Importe depuis CSV

        Args:
            csv_str: Contenu CSV
            field_mapping: {"db_field": "export_label"}
            required_fields: Champs obligatoires

        Returns:
            (items_validés, erreurs)
        """
        reader = csv.DictReader(io.StringIO(csv_str))
        items = []
        errors = []

        inverse_mapping = {v: k for k, v in field_mapping.items()}

        for row_num, row in enumerate(reader, start=2):
            try:
                item_dict = {}
                for export_label, value in row.items():
                    if export_label in inverse_mapping:
                        db_field = inverse_mapping[export_label]
                        item_dict[db_field] = IOService._parse_value(value)

                missing = [f for f in required_fields if not item_dict.get(f)]
                if missing:
                    errors.append(f"Ligne {row_num}: Champs manquants: {missing}")
                    continue

                items.append(item_dict)
            except Exception as e:
                errors.append(f"Ligne {row_num}: {str(e)}")

        logger.info(f"CSV import: {len(items)} items, {len(errors)} errors")
        return items, errors

    @staticmethod
    def to_json(items: List[Dict], indent: int = 2) -> str:
        """Exporte en JSON"""
        if not items:
            return "[]"
        logger.info(f"JSON export: {len(items)} items")
        return json.dumps(items, indent=indent, ensure_ascii=False, default=str)

    @staticmethod
    def from_json(json_str: str, required_fields: List[str]) -> tuple[List[Dict], List[str]]:
        """Importe depuis JSON"""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return [], [f"JSON invalide: {str(e)}"]

        if not isinstance(data, list):
            data = [data]

        items = []
        errors = []

        for idx, item_dict in enumerate(data, start=1):
            try:
                missing = [f for f in required_fields if f not in item_dict or not item_dict[f]]
                if missing:
                    errors.append(f"Item {idx}: Champs manquants: {missing}")
                    continue
                items.append(item_dict)
            except Exception as e:
                errors.append(f"Item {idx}: {str(e)}")

        logger.info(f"JSON import: {len(items)} items, {len(errors)} errors")
        return items, errors

    @staticmethod
    def _format_value(value: Any) -> str:
        """Formate valeur pour export"""
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            if isinstance(value, datetime):
                return value.strftime("%d/%m/%Y %H:%M")
            return value.strftime("%d/%m/%Y")
        if isinstance(value, bool):
            return "Oui" if value else "Non"
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        return str(value)

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse valeur depuis import"""
        if not value or value.strip() == "":
            return None

        value = value.strip()

        # Boolean
        if value.lower() in ["oui", "yes", "true", "1"]:
            return True
        if value.lower() in ["non", "no", "false", "0"]:
            return False

        # Number
        try:
            if "." in value or "," in value:
                return float(value.replace(",", "."))
            return int(value)
        except ValueError:
            pass

        # Date
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

        return value


# ════════════════════════════════════════════════════════════
# TEMPLATES PRÉDÉFINIS
# ════════════════════════════════════════════════════════════

# Recettes
RECETTE_FIELD_MAPPING = {
    "nom": "Nom",
    "description": "Description",
    "temps_preparation": "Temps préparation (min)",
    "temps_cuisson": "Temps cuisson (min)",
    "portions": "Portions",
    "difficulte": "Difficulté"
}

# Inventaire
INVENTAIRE_FIELD_MAPPING = {
    "nom": "Nom",
    "categorie": "Catégorie",
    "quantite": "Quantité",
    "unite": "Unité",
    "seuil": "Seuil",
    "emplacement": "Emplacement",
    "date_peremption": "Péremption"
}

# Courses
COURSES_FIELD_MAPPING = {
    "nom": "Nom",
    "quantite": "Quantité",
    "unite": "Unité",
    "priorite": "Priorité",
    "magasin": "Magasin"
}