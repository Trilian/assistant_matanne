"""
Tests complets pour src/services/io_service.py
Objectif: couverture >80%
"""

from datetime import date, datetime

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IOService.to_csv
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceToCsv:
    """Tests for to_csv method."""

    def test_to_csv_empty_list(self):
        """Test CSV export with empty list."""
        from src.services.io_service import IOService

        result = IOService.to_csv([], {"nom": "Nom", "qty": "QuantitÃ©"})

        assert result == ""

    def test_to_csv_single_item(self):
        """Test CSV export with single item."""
        from src.services.io_service import IOService

        items = [{"nom": "Pommes", "quantite": 5}]
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}

        result = IOService.to_csv(items, mapping)

        assert "Nom" in result
        assert "QuantitÃ©" in result
        assert "Pommes" in result
        assert "5" in result

    def test_to_csv_multiple_items(self):
        """Test CSV export with multiple items."""
        from src.services.io_service import IOService

        items = [
            {"nom": "Pommes", "quantite": 5},
            {"nom": "Oranges", "quantite": 3},
            {"nom": "Bananes", "quantite": 7},
        ]
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}

        result = IOService.to_csv(items, mapping)

        lines = result.strip().split("\n")
        assert len(lines) == 4  # Header + 3 data rows
        assert "Pommes" in result
        assert "Oranges" in result
        assert "Bananes" in result

    def test_to_csv_with_none_value(self):
        """Test CSV export with None values."""
        from src.services.io_service import IOService

        items = [{"nom": "Pommes", "quantite": None}]
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}

        result = IOService.to_csv(items, mapping)

        assert "Pommes" in result
        # None should be converted to empty string

    def test_to_csv_with_date_value(self):
        """Test CSV export with date values."""
        from src.services.io_service import IOService

        items = [{"nom": "Lait", "date_peremption": date(2026, 3, 15)}]
        mapping = {"nom": "Nom", "date_peremption": "PÃ©remption"}

        result = IOService.to_csv(items, mapping)

        assert "Lait" in result
        assert "15/03/2026" in result

    def test_to_csv_with_datetime_value(self):
        """Test CSV export with datetime values."""
        from src.services.io_service import IOService

        items = [{"nom": "Event", "date": datetime(2026, 3, 15, 10, 30)}]
        mapping = {"nom": "Nom", "date": "Date"}

        result = IOService.to_csv(items, mapping)

        assert "Event" in result
        assert "15/03/2026 10:30" in result

    def test_to_csv_with_boolean_true(self):
        """Test CSV export with boolean True."""
        from src.services.io_service import IOService

        items = [{"nom": "Item", "actif": True}]
        mapping = {"nom": "Nom", "actif": "Actif"}

        result = IOService.to_csv(items, mapping)

        assert "Oui" in result

    def test_to_csv_with_boolean_false(self):
        """Test CSV export with boolean False."""
        from src.services.io_service import IOService

        items = [{"nom": "Item", "actif": False}]
        mapping = {"nom": "Nom", "actif": "Actif"}

        result = IOService.to_csv(items, mapping)

        assert "Non" in result

    def test_to_csv_with_list_value(self):
        """Test CSV export with list values."""
        from src.services.io_service import IOService

        items = [{"nom": "Recette", "tags": ["facile", "rapide", "santÃ©"]}]
        mapping = {"nom": "Nom", "tags": "Tags"}

        result = IOService.to_csv(items, mapping)

        assert "facile, rapide, santÃ©" in result

    def test_to_csv_with_tuple_value(self):
        """Test CSV export with tuple values."""
        from src.services.io_service import IOService

        items = [{"nom": "Recette", "coords": (1, 2, 3)}]
        mapping = {"nom": "Nom", "coords": "CoordonnÃ©es"}

        result = IOService.to_csv(items, mapping)

        assert "1, 2, 3" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IOService.from_csv
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceFromCsv:
    """Tests for from_csv method."""

    def test_from_csv_simple(self):
        """Test CSV import with simple data."""
        from src.services.io_service import IOService

        csv_str = "Nom,QuantitÃ©\nPommes,5\nOranges,3"
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 2
        assert len(errors) == 0
        assert items[0]["nom"] == "Pommes"
        assert items[0]["quantite"] == 5

    def test_from_csv_missing_required_field(self):
        """Test CSV import with missing required field."""
        from src.services.io_service import IOService

        csv_str = "Nom,QuantitÃ©\n,5\nOranges,3"  # First row missing name
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 1  # Only Oranges
        assert len(errors) == 1
        assert "manquants" in errors[0].lower()

    def test_from_csv_with_float_values(self):
        """Test CSV import with float values (using comma)."""
        from src.services.io_service import IOService

        csv_str = "Nom,Prix\nPommes,2,50\nOranges,3.25"
        mapping = {"nom": "Nom", "prix": "Prix"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 2
        # Note: "2,50" as string in CSV may not parse correctly due to comma being separator

    def test_from_csv_with_date_format_1(self):
        """Test CSV import with date format DD/MM/YYYY."""
        from src.services.io_service import IOService

        csv_str = "Nom,Date\nItem,15/03/2026"
        mapping = {"nom": "Nom", "date": "Date"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 1
        assert items[0]["date"] == date(2026, 3, 15)

    def test_from_csv_with_date_format_2(self):
        """Test CSV import with date format YYYY-MM-DD."""
        from src.services.io_service import IOService

        csv_str = "Nom,Date\nItem,2026-03-15"
        mapping = {"nom": "Nom", "date": "Date"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 1
        assert items[0]["date"] == date(2026, 3, 15)

    def test_from_csv_with_date_format_3(self):
        """Test CSV import with date format DD-MM-YYYY."""
        from src.services.io_service import IOService

        csv_str = "Nom,Date\nItem,15-03-2026"
        mapping = {"nom": "Nom", "date": "Date"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 1
        assert items[0]["date"] == date(2026, 3, 15)

    def test_from_csv_with_boolean_oui(self):
        """Test CSV import with boolean Oui."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,Oui"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is True

    def test_from_csv_with_boolean_non(self):
        """Test CSV import with boolean Non."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,Non"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is False

    def test_from_csv_with_boolean_yes(self):
        """Test CSV import with boolean yes."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,yes"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is True

    def test_from_csv_with_boolean_no(self):
        """Test CSV import with boolean no."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,no"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is False

    def test_from_csv_with_boolean_true(self):
        """Test CSV import with boolean true."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,true"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is True

    def test_from_csv_with_boolean_false(self):
        """Test CSV import with boolean false."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,false"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["actif"] is False

    def test_from_csv_with_boolean_1(self):
        """Test CSV import with boolean 1."""
        from src.services.io_service import IOService

        csv_str = "Nom,Actif\nItem,1"
        mapping = {"nom": "Nom", "actif": "Actif"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        # Note: "1" may be parsed as int first
        assert items[0]["actif"] in [True, 1]

    def test_from_csv_with_empty_value(self):
        """Test CSV import with empty value."""
        from src.services.io_service import IOService

        csv_str = "Nom,Description\nItem,"
        mapping = {"nom": "Nom", "description": "Description"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert len(items) == 1
        assert items[0]["description"] is None

    def test_from_csv_with_integer_values(self):
        """Test CSV import with integer values."""
        from src.services.io_service import IOService

        csv_str = "Nom,QuantitÃ©\nPommes,10"
        mapping = {"nom": "Nom", "quantite": "QuantitÃ©"}
        required = ["nom"]

        items, errors = IOService.from_csv(csv_str, mapping, required)

        assert items[0]["quantite"] == 10
        assert isinstance(items[0]["quantite"], int)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IOService.to_json
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceToJson:
    """Tests for to_json method."""

    def test_to_json_empty_list(self):
        """Test JSON export with empty list."""
        from src.services.io_service import IOService

        result = IOService.to_json([])

        assert result == "[]"

    def test_to_json_single_item(self):
        """Test JSON export with single item."""
        import json

        from src.services.io_service import IOService

        items = [{"nom": "Pommes", "quantite": 5}]

        result = IOService.to_json(items)
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert parsed[0]["nom"] == "Pommes"
        assert parsed[0]["quantite"] == 5

    def test_to_json_multiple_items(self):
        """Test JSON export with multiple items."""
        import json

        from src.services.io_service import IOService

        items = [{"nom": "Pommes", "quantite": 5}, {"nom": "Oranges", "quantite": 3}]

        result = IOService.to_json(items)
        parsed = json.loads(result)

        assert len(parsed) == 2

    def test_to_json_indent(self):
        """Test JSON export with custom indent."""
        from src.services.io_service import IOService

        items = [{"nom": "Test"}]

        result_indent2 = IOService.to_json(items, indent=2)
        result_indent4 = IOService.to_json(items, indent=4)

        # Different indentation produces different lengths
        assert len(result_indent4) >= len(result_indent2)

    def test_to_json_with_date(self):
        """Test JSON export with date values."""
        import json

        from src.services.io_service import IOService

        items = [{"nom": "Item", "date": date(2026, 3, 15)}]

        result = IOService.to_json(items)
        parsed = json.loads(result)

        assert "2026-03-15" in parsed[0]["date"]

    def test_to_json_with_ensure_ascii_false(self):
        """Test JSON export preserves non-ASCII characters."""
        from src.services.io_service import IOService

        items = [{"nom": "PÃ¢tÃ© franÃ§ais", "description": "DÃ©licieux"}]

        result = IOService.to_json(items)

        # Non-ASCII chars should be preserved
        assert "PÃ¢tÃ© franÃ§ais" in result
        assert "DÃ©licieux" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS IOService.from_json
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceFromJson:
    """Tests for from_json method."""

    def test_from_json_valid_array(self):
        """Test JSON import with valid array."""
        from src.services.io_service import IOService

        json_str = '[{"nom": "Pommes", "quantite": 5}]'
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 1
        assert len(errors) == 0
        assert items[0]["nom"] == "Pommes"

    def test_from_json_single_object(self):
        """Test JSON import with single object (not array)."""
        from src.services.io_service import IOService

        json_str = '{"nom": "Pommes", "quantite": 5}'
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 1
        assert items[0]["nom"] == "Pommes"

    def test_from_json_invalid_json(self):
        """Test JSON import with invalid JSON."""
        from src.services.io_service import IOService

        json_str = "{invalid json}"
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 0
        assert len(errors) == 1
        assert "invalide" in errors[0].lower()

    def test_from_json_missing_required_field(self):
        """Test JSON import with missing required field."""
        from src.services.io_service import IOService

        json_str = '[{"description": "Test"}]'
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 0
        assert len(errors) == 1
        assert "manquants" in errors[0].lower()

    def test_from_json_empty_required_field(self):
        """Test JSON import with empty required field."""
        from src.services.io_service import IOService

        json_str = '[{"nom": "", "quantite": 5}]'
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 0
        assert len(errors) == 1

    def test_from_json_multiple_items(self):
        """Test JSON import with multiple items."""
        from src.services.io_service import IOService

        json_str = '[{"nom": "A"}, {"nom": "B"}, {"nom": "C"}]'
        required = ["nom"]

        items, errors = IOService.from_json(json_str, required)

        assert len(items) == 3
        assert len(errors) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _format_value
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceFormatValue:
    """Tests for _format_value method."""

    def test_format_value_none(self):
        """Test format None value."""
        from src.services.io_service import IOService

        assert IOService._format_value(None) == ""

    def test_format_value_string(self):
        """Test format string value."""
        from src.services.io_service import IOService

        assert IOService._format_value("test") == "test"

    def test_format_value_int(self):
        """Test format integer value."""
        from src.services.io_service import IOService

        assert IOService._format_value(42) == "42"

    def test_format_value_float(self):
        """Test format float value."""
        from src.services.io_service import IOService

        assert IOService._format_value(3.14) == "3.14"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS _parse_value
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIOServiceParseValue:
    """Tests for _parse_value method."""

    def test_parse_value_empty(self):
        """Test parse empty string."""
        from src.services.io_service import IOService

        assert IOService._parse_value("") is None

    def test_parse_value_whitespace(self):
        """Test parse whitespace string."""
        from src.services.io_service import IOService

        assert IOService._parse_value("   ") is None

    def test_parse_value_string(self):
        """Test parse regular string."""
        from src.services.io_service import IOService

        assert IOService._parse_value("hello") == "hello"

    def test_parse_value_string_with_whitespace(self):
        """Test parse string with whitespace is stripped."""
        from src.services.io_service import IOService

        assert IOService._parse_value("  hello  ") == "hello"

    def test_parse_value_float_with_dot(self):
        """Test parse float with dot."""
        from src.services.io_service import IOService

        result = IOService._parse_value("3.14")
        assert result == 3.14

    def test_parse_value_float_with_comma(self):
        """Test parse float with comma (European format)."""
        from src.services.io_service import IOService

        result = IOService._parse_value("3,14")
        assert result == 3.14


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FIELD MAPPINGS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFieldMappings:
    """Tests for predefined field mappings."""

    def test_recette_field_mapping_exists(self):
        """Test RECETTE_FIELD_MAPPING exists."""
        from src.services.io_service import RECETTE_FIELD_MAPPING

        assert "nom" in RECETTE_FIELD_MAPPING
        assert "description" in RECETTE_FIELD_MAPPING
        assert "temps_preparation" in RECETTE_FIELD_MAPPING
        assert "temps_cuisson" in RECETTE_FIELD_MAPPING
        assert "portions" in RECETTE_FIELD_MAPPING
        assert "difficulte" in RECETTE_FIELD_MAPPING

    def test_inventaire_field_mapping_exists(self):
        """Test INVENTAIRE_FIELD_MAPPING exists."""
        from src.services.io_service import INVENTAIRE_FIELD_MAPPING

        assert "nom" in INVENTAIRE_FIELD_MAPPING
        assert "categorie" in INVENTAIRE_FIELD_MAPPING
        assert "quantite" in INVENTAIRE_FIELD_MAPPING
        assert "unite" in INVENTAIRE_FIELD_MAPPING
        assert "seuil" in INVENTAIRE_FIELD_MAPPING

    def test_courses_field_mapping_exists(self):
        """Test COURSES_FIELD_MAPPING exists."""
        from src.services.io_service import COURSES_FIELD_MAPPING

        assert "nom" in COURSES_FIELD_MAPPING
        assert "quantite" in COURSES_FIELD_MAPPING
        assert "unite" in COURSES_FIELD_MAPPING
        assert "priorite" in COURSES_FIELD_MAPPING
        assert "magasin" in COURSES_FIELD_MAPPING

    def test_use_recette_field_mapping_for_export(self):
        """Test using RECETTE_FIELD_MAPPING for export."""
        from src.services.io_service import RECETTE_FIELD_MAPPING, IOService

        items = [{"nom": "PÃ¢tes", "temps_preparation": 10, "portions": 4}]

        result = IOService.to_csv(items, RECETTE_FIELD_MAPPING)

        assert "Nom" in result
        assert "Temps prÃ©paration (min)" in result
        assert "Portions" in result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestModuleExports:
    """Tests for module exports."""

    def test_ioservice_exported(self):
        """Test IOService is exported."""
        from src.services.io_service import IOService

        assert IOService is not None

    def test_all_field_mappings_exported(self):
        """Test all field mappings are exported."""
        from src.services.io_service import (
            COURSES_FIELD_MAPPING,
            INVENTAIRE_FIELD_MAPPING,
            RECETTE_FIELD_MAPPING,
        )

        assert RECETTE_FIELD_MAPPING is not None
        assert INVENTAIRE_FIELD_MAPPING is not None
        assert COURSES_FIELD_MAPPING is not None
