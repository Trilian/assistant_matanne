"""
Tests unitaires complets pour src/services/base/io_service.py
Module: IOService - Import/Export CSV, JSON.

Couverture cible: >80%
"""

import json
from datetime import date, datetime

import pytest

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def io_service():
    """Instance de IOService."""
    from src.services.core.base.io_service import IOService

    return IOService()


@pytest.fixture
def sample_items():
    """Données de test."""
    return [
        {
            "nom": "Article 1",
            "quantite": 10,
            "prix": 5.99,
            "actif": True,
            "date_creation": date(2024, 1, 15),
        },
        {
            "nom": "Article 2",
            "quantite": 20,
            "prix": 12.50,
            "actif": False,
            "date_creation": date(2024, 2, 20),
        },
    ]


@pytest.fixture
def field_mapping():
    """Mapping des champs pour export/import."""
    return {
        "nom": "Nom",
        "quantite": "Quantité",
        "prix": "Prix",
        "actif": "Actif",
        "date_creation": "Date création",
    }


# ═══════════════════════════════════════════════════════════
# TESTS TO_CSV
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceToCsv:
    """Tests pour la méthode to_csv."""

    def test_to_csv_basic(self, sample_items, field_mapping):
        """Test export CSV basique."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_csv(sample_items, field_mapping)

        assert result is not None
        assert "Nom" in result
        assert "Article 1" in result
        assert "Article 2" in result

    def test_to_csv_empty_list(self, field_mapping):
        """Test export CSV avec liste vide."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_csv([], field_mapping)

        assert result == ""

    def test_to_csv_header_row(self, sample_items, field_mapping):
        """Test que le header est présent."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_csv(sample_items, field_mapping)
        lines = result.strip().split("\n")

        # Première ligne = header
        header = lines[0]
        assert "Nom" in header
        assert "Quantité" in header
        assert "Prix" in header

    def test_to_csv_data_rows(self, sample_items, field_mapping):
        """Test que les données sont présentes."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_csv(sample_items, field_mapping)
        lines = result.strip().split("\n")

        # 1 header + 2 data rows
        assert len(lines) == 3

    def test_to_csv_boolean_format(self):
        """Test formatage des booléens."""
        from src.services.core.base.io_service import IOService

        items = [{"actif": True}, {"actif": False}]
        mapping = {"actif": "Actif"}

        result = IOService.to_csv(items, mapping)

        assert "Oui" in result
        assert "Non" in result

    def test_to_csv_date_format(self):
        """Test formatage des dates."""
        from src.services.core.base.io_service import IOService

        items = [{"date": date(2024, 3, 15)}]
        mapping = {"date": "Date"}

        result = IOService.to_csv(items, mapping)

        assert "15/03/2024" in result

    def test_to_csv_datetime_format(self):
        """Test formatage des datetime."""
        from src.services.core.base.io_service import IOService

        items = [{"created": datetime(2024, 3, 15, 14, 30)}]
        mapping = {"created": "Créé"}

        result = IOService.to_csv(items, mapping)

        assert "15/03/2024 14:30" in result

    def test_to_csv_list_format(self):
        """Test formatage des listes."""
        from src.services.core.base.io_service import IOService

        items = [{"tags": ["tag1", "tag2", "tag3"]}]
        mapping = {"tags": "Tags"}

        result = IOService.to_csv(items, mapping)

        assert "tag1, tag2, tag3" in result

    def test_to_csv_none_value(self):
        """Test formatage des valeurs None."""
        from src.services.core.base.io_service import IOService

        items = [{"valeur": None}]
        mapping = {"valeur": "Valeur"}

        result = IOService.to_csv(items, mapping)
        lines = result.strip().split("\n")

        # La valeur None devient chaîne vide
        assert len(lines) == 2


# ═══════════════════════════════════════════════════════════
# TESTS FROM_CSV
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceFromCsv:
    """Tests pour la méthode from_csv."""

    def test_from_csv_basic(self, field_mapping):
        """Test import CSV basique."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom,Quantité,Prix,Actif,Date création\nArticle,10,5.99,Oui,15/01/2024"

        items, errors = IOService.from_csv(csv_str, field_mapping, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Article"
        assert len(errors) == 0

    def test_from_csv_multiple_rows(self, field_mapping):
        """Test import CSV avec plusieurs lignes."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom,Quantité\nArticle1,10\nArticle2,20"
        mapping = {"nom": "Nom", "quantite": "Quantité"}

        items, errors = IOService.from_csv(csv_str, mapping, required_fields=["nom"])

        assert len(items) == 2

    def test_from_csv_missing_required_field(self, field_mapping):
        """Test import avec champ obligatoire manquant."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom,Quantité\n,10"  # Nom vide
        mapping = {"nom": "Nom", "quantite": "Quantité"}

        items, errors = IOService.from_csv(csv_str, mapping, required_fields=["nom"])

        assert len(items) == 0
        assert len(errors) == 1
        assert "Ligne 2" in errors[0]

    def test_from_csv_parse_boolean_true(self):
        """Test parsing booléen Oui."""
        from src.services.core.base.io_service import IOService

        csv_str = "Actif\nOui"
        mapping = {"actif": "Actif"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["actif"] is True

    def test_from_csv_parse_boolean_false(self):
        """Test parsing booléen Non."""
        from src.services.core.base.io_service import IOService

        csv_str = "Actif\nNon"
        mapping = {"actif": "Actif"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["actif"] is False

    def test_from_csv_parse_boolean_variants(self):
        """Test parsing variantes booléennes."""
        from src.services.core.base.io_service import IOService

        csv_str = "Val\ntrue\nfalse\nyes\nno\n1\n0"
        mapping = {"val": "Val"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["val"] is True
        assert items[1]["val"] is False
        assert items[2]["val"] is True
        assert items[3]["val"] is False
        assert items[4]["val"] is True
        assert items[5]["val"] is False

    def test_from_csv_parse_integer(self):
        """Test parsing entier."""
        from src.services.core.base.io_service import IOService

        csv_str = "Quantite\n42"
        mapping = {"quantite": "Quantite"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["quantite"] == 42
        assert isinstance(items[0]["quantite"], int)

    def test_from_csv_parse_float_dot(self):
        """Test parsing float avec point."""
        from src.services.core.base.io_service import IOService

        csv_str = "Prix\n12.99"
        mapping = {"prix": "Prix"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["prix"] == 12.99
        assert isinstance(items[0]["prix"], float)

    def test_from_csv_parse_float_comma(self):
        """Test parsing float avec virgule (format FR) - via _parse_value."""
        from src.services.core.base.io_service import IOService

        # La virgule dans CSV est un délimiteur, donc on teste _parse_value directement
        result = IOService._parse_value("12,99")

        # Le parsing remplace virgule par point et convertit en float
        assert result == 12.99

    def test_from_csv_parse_date_fr(self):
        """Test parsing date format français."""
        from src.services.core.base.io_service import IOService

        csv_str = "Date\n15/03/2024"
        mapping = {"date": "Date"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["date"] == date(2024, 3, 15)

    def test_from_csv_parse_date_iso(self):
        """Test parsing date format ISO."""
        from src.services.core.base.io_service import IOService

        csv_str = "Date\n2024-03-15"
        mapping = {"date": "Date"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["date"] == date(2024, 3, 15)

    def test_from_csv_parse_date_dash(self):
        """Test parsing date format tiret."""
        from src.services.core.base.io_service import IOService

        csv_str = "Date\n15-03-2024"
        mapping = {"date": "Date"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["date"] == date(2024, 3, 15)

    def test_from_csv_parse_string(self):
        """Test parsing chaîne non convertible."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom\nBonjour le monde"
        mapping = {"nom": "Nom"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=[])

        assert items[0]["nom"] == "Bonjour le monde"
        assert isinstance(items[0]["nom"], str)

    def test_from_csv_empty_value(self):
        """Test parsing valeur vide."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom,Desc\nTest,"
        mapping = {"nom": "Nom", "desc": "Desc"}

        items, _ = IOService.from_csv(csv_str, mapping, required_fields=["nom"])

        assert items[0]["nom"] == "Test"
        assert items[0]["desc"] is None


# ═══════════════════════════════════════════════════════════
# TESTS TO_JSON
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceToJson:
    """Tests pour la méthode to_json."""

    def test_to_json_basic(self, sample_items):
        """Test export JSON basique."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_json(sample_items)

        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 2

    def test_to_json_empty_list(self):
        """Test export JSON avec liste vide."""
        from src.services.core.base.io_service import IOService

        result = IOService.to_json([])

        assert result == "[]"

    def test_to_json_indent(self):
        """Test indentation JSON."""
        from src.services.core.base.io_service import IOService

        items = [{"nom": "Test"}]

        # Indent par défaut (2)
        result_default = IOService.to_json(items)

        # Indent personnalisé
        result_custom = IOService.to_json(items, indent=4)

        # Le résultat avec indent 4 doit être différent
        assert len(result_custom) > len(result_default.replace(" ", ""))

    def test_to_json_unicode(self):
        """Test caractères unicode."""
        from src.services.core.base.io_service import IOService

        items = [{"nom": "Café crème", "desc": "Délicieux été"}]

        result = IOService.to_json(items)

        # ensure_ascii=False donc les accents sont préservés
        assert "Café" in result
        assert "Délicieux" in result

    def test_to_json_date_serialization(self):
        """Test sérialisation des dates."""
        from src.services.core.base.io_service import IOService

        items = [{"date": date(2024, 3, 15)}]

        result = IOService.to_json(items)
        parsed = json.loads(result)

        # Les dates sont sérialisées en string via default=str
        assert "2024-03-15" in parsed[0]["date"]


# ═══════════════════════════════════════════════════════════
# TESTS FROM_JSON
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceFromJson:
    """Tests pour la méthode from_json."""

    def test_from_json_basic(self):
        """Test import JSON basique."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": "Article", "quantite": 10}]'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Article"
        assert len(errors) == 0

    def test_from_json_single_object(self):
        """Test import JSON avec objet unique (pas array)."""
        from src.services.core.base.io_service import IOService

        json_str = '{"nom": "Article unique"}'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Article unique"

    def test_from_json_multiple_items(self):
        """Test import JSON avec plusieurs items."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": "A1"}, {"nom": "A2"}, {"nom": "A3"}]'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 3

    def test_from_json_missing_required_field(self):
        """Test import avec champ obligatoire manquant."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"quantite": 10}]'  # Pas de 'nom'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 0
        assert len(errors) == 1
        assert "Item 1" in errors[0]

    def test_from_json_empty_required_field(self):
        """Test import avec champ obligatoire vide."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": ""}]'  # Nom vide

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 0
        assert len(errors) == 1

    def test_from_json_invalid_json(self):
        """Test import avec JSON invalide."""
        from src.services.core.base.io_service import IOService

        json_str = "{invalid json}"

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 0
        assert len(errors) == 1
        assert "JSON invalide" in errors[0]

    def test_from_json_no_required_fields(self):
        """Test import sans champs obligatoires."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"foo": "bar"}]'

        items, errors = IOService.from_json(json_str, required_fields=[])

        assert len(items) == 1
        assert len(errors) == 0

    def test_from_json_partial_valid(self):
        """Test import avec certains items invalides."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": "Valid"}, {"desc": "No name"}]'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 1
        assert len(errors) == 1


# ═══════════════════════════════════════════════════════════
# TESTS FORMAT VALUE (HELPER)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceFormatValue:
    """Tests pour la méthode _format_value."""

    def test_format_none(self):
        """Test formatage None."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(None)

        assert result == ""

    def test_format_date(self):
        """Test formatage date."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(date(2024, 3, 15))

        assert result == "15/03/2024"

    def test_format_datetime(self):
        """Test formatage datetime."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(datetime(2024, 3, 15, 14, 30))

        assert result == "15/03/2024 14:30"

    def test_format_bool_true(self):
        """Test formatage booléen True."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(True)

        assert result == "Oui"

    def test_format_bool_false(self):
        """Test formatage booléen False."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(False)

        assert result == "Non"

    def test_format_list(self):
        """Test formatage liste."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(["a", "b", "c"])

        assert result == "a, b, c"

    def test_format_tuple(self):
        """Test formatage tuple."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(("x", "y"))

        assert result == "x, y"

    def test_format_string(self):
        """Test formatage chaîne."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value("Hello")

        assert result == "Hello"

    def test_format_number(self):
        """Test formatage nombre."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(42)

        assert result == "42"

    def test_format_float(self):
        """Test formatage float."""
        from src.services.core.base.io_service import IOService

        result = IOService._format_value(3.14)

        assert result == "3.14"


# ═══════════════════════════════════════════════════════════
# TESTS PARSE VALUE (HELPER)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceParseValue:
    """Tests pour la méthode _parse_value."""

    def test_parse_empty(self):
        """Test parsing chaîne vide."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("")

        assert result is None

    def test_parse_whitespace(self):
        """Test parsing espaces."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("   ")

        assert result is None

    def test_parse_boolean_oui(self):
        """Test parsing 'Oui'."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("Oui")

        assert result is True

    def test_parse_boolean_yes(self):
        """Test parsing 'yes'."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("yes")

        assert result is True

    def test_parse_boolean_non(self):
        """Test parsing 'Non'."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("Non")

        assert result is False

    def test_parse_boolean_no(self):
        """Test parsing 'no'."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("no")

        assert result is False

    def test_parse_integer(self):
        """Test parsing entier."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("42")

        assert result == 42
        assert isinstance(result, int)

    def test_parse_float_dot(self):
        """Test parsing float avec point."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("3.14")

        assert result == 3.14
        assert isinstance(result, float)

    def test_parse_float_comma(self):
        """Test parsing float avec virgule."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("3,14")

        assert result == 3.14

    def test_parse_date_fr(self):
        """Test parsing date française."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("15/03/2024")

        assert result == date(2024, 3, 15)

    def test_parse_date_iso(self):
        """Test parsing date ISO."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("2024-03-15")

        assert result == date(2024, 3, 15)

    def test_parse_date_dash(self):
        """Test parsing date tiret."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("15-03-2024")

        assert result == date(2024, 3, 15)

    def test_parse_text(self):
        """Test parsing texte simple."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("Hello World")

        assert result == "Hello World"

    def test_parse_strips_whitespace(self):
        """Test que les espaces sont retirés."""
        from src.services.core.base.io_service import IOService

        result = IOService._parse_value("  test  ")

        assert result == "test"


# ═══════════════════════════════════════════════════════════
# TESTS TEMPLATES PRÉDÉFINIS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceTemplates:
    """Tests pour les templates prédéfinis."""

    def test_recette_field_mapping_exists(self):
        """Vérifie que le mapping recettes existe."""
        from src.services.core.base.io_service import RECETTE_FIELD_MAPPING

        assert "nom" in RECETTE_FIELD_MAPPING
        assert "description" in RECETTE_FIELD_MAPPING
        assert "temps_preparation" in RECETTE_FIELD_MAPPING

    def test_inventaire_field_mapping_exists(self):
        """Vérifie que le mapping inventaire existe."""
        from src.services.core.base.io_service import INVENTAIRE_FIELD_MAPPING

        assert "nom" in INVENTAIRE_FIELD_MAPPING
        assert "categorie" in INVENTAIRE_FIELD_MAPPING
        assert "quantite" in INVENTAIRE_FIELD_MAPPING

    def test_courses_field_mapping_exists(self):
        """Vérifie que le mapping courses existe."""
        from src.services.core.base.io_service import COURSES_FIELD_MAPPING

        assert "nom" in COURSES_FIELD_MAPPING
        assert "quantite" in COURSES_FIELD_MAPPING


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceEdgeCases:
    """Tests pour les cas limites."""

    def test_csv_roundtrip(self):
        """Test export puis import CSV."""
        from src.services.core.base.io_service import IOService

        original = [{"nom": "Test", "actif": True}]
        mapping = {"nom": "Nom", "actif": "Actif"}

        csv = IOService.to_csv(original, mapping)
        items, errors = IOService.from_csv(csv, mapping, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Test"
        assert items[0]["actif"] is True

    def test_json_roundtrip(self):
        """Test export puis import JSON."""
        from src.services.core.base.io_service import IOService

        original = [{"nom": "Test", "quantite": 42}]

        json_str = IOService.to_json(original)
        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Test"
        assert items[0]["quantite"] == 42

    def test_csv_special_characters(self):
        """Test CSV avec caractères spéciaux."""
        from src.services.core.base.io_service import IOService

        items = [{"nom": 'Test "avec" guillemets, et virgules'}]
        mapping = {"nom": "Nom"}

        csv = IOService.to_csv(items, mapping)

        # Le CSV doit gérer les guillemets et virgules
        assert "Test" in csv

    def test_from_csv_unmapped_column(self):
        """Test import CSV avec colonne non mappée."""
        from src.services.core.base.io_service import IOService

        csv_str = "Nom,ExtraCol\nTest,Ignored"
        mapping = {"nom": "Nom"}

        items, errors = IOService.from_csv(csv_str, mapping, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["nom"] == "Test"
        # ExtraCol n'est pas dans le mapping, donc ignorée

    def test_json_nested_not_parsed(self):
        """Test que les objets imbriqués sont préservés."""
        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": "Test", "details": {"foo": "bar"}}]'

        items, errors = IOService.from_json(json_str, required_fields=["nom"])

        assert len(items) == 1
        assert items[0]["details"] == {"foo": "bar"}


# ═══════════════════════════════════════════════════════════
# TESTS LOGGING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIOServiceLogging:
    """Tests pour la journalisation."""

    def test_to_csv_logs(self, caplog, sample_items, field_mapping):
        """Vérifie que to_csv log le nombre d'items."""
        import logging

        from src.services.core.base.io_service import IOService

        with caplog.at_level(logging.INFO):
            IOService.to_csv(sample_items, field_mapping)

        assert "CSV export: 2 items" in caplog.text

    def test_from_csv_logs(self, caplog, field_mapping):
        """Vérifie que from_csv log le nombre d'items."""
        import logging

        from src.services.core.base.io_service import IOService

        csv_str = "Nom,Quantité\nA,1\nB,2"
        mapping = {"nom": "Nom", "quantite": "Quantité"}

        with caplog.at_level(logging.INFO):
            IOService.from_csv(csv_str, mapping, required_fields=["nom"])

        assert "CSV import: 2 items" in caplog.text

    def test_to_json_logs(self, caplog, sample_items):
        """Vérifie que to_json log le nombre d'items."""
        import logging

        from src.services.core.base.io_service import IOService

        with caplog.at_level(logging.INFO):
            IOService.to_json(sample_items)

        assert "JSON export: 2 items" in caplog.text

    def test_from_json_logs(self, caplog):
        """Vérifie que from_json log le nombre d'items."""
        import logging

        from src.services.core.base.io_service import IOService

        json_str = '[{"nom": "A"}, {"nom": "B"}]'

        with caplog.at_level(logging.INFO):
            IOService.from_json(json_str, required_fields=["nom"])

        assert "JSON import: 2 items" in caplog.text
