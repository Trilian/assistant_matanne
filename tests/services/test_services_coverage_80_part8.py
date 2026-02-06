"""
Tests de couverture étendus pour src/services - Partie 8
Tests profonds: IOService, types.BaseService, helpers
Focus sur l'exécution réelle des méthodes pour la couverture
"""

import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock, Mock
import json


# ═══════════════════════════════════════════════════════════════════════════
# TESTS IO SERVICE - COUVERTURE COMPLÈTE
# ═══════════════════════════════════════════════════════════════════════════


class TestIOServiceCSV:
    """Tests complets du service IO - CSV"""

    def test_to_csv_empty_items(self):
        """Teste export CSV avec liste vide."""
        from src.services.io_service import IOService
        
        result = IOService.to_csv([], {"nom": "Nom"})
        assert result == ""

    def test_to_csv_single_item(self):
        """Teste export CSV avec un seul item."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "quantite": 10}]
        mapping = {"nom": "Nom", "quantite": "Quantité"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "Nom" in result
        assert "Quantité" in result
        assert "Test" in result
        assert "10" in result

    def test_to_csv_multiple_items(self):
        """Teste export CSV avec plusieurs items."""
        from src.services.io_service import IOService
        
        items = [
            {"nom": "Item 1", "valeur": 100},
            {"nom": "Item 2", "valeur": 200},
            {"nom": "Item 3", "valeur": 300}
        ]
        mapping = {"nom": "Nom", "valeur": "Valeur"}
        
        result = IOService.to_csv(items, mapping)
        
        lines = result.strip().split('\n')
        assert len(lines) == 4  # Header + 3 items
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result

    def test_to_csv_with_date_value(self):
        """Teste export CSV avec date."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "date": date(2026, 2, 6)}]
        mapping = {"nom": "Nom", "date": "Date"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "06/02/2026" in result

    def test_to_csv_with_datetime_value(self):
        """Teste export CSV avec datetime."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "date": datetime(2026, 2, 6, 14, 30)}]
        mapping = {"nom": "Nom", "date": "Date"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "06/02/2026 14:30" in result

    def test_to_csv_with_boolean_true(self):
        """Teste export CSV avec boolean True."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "actif": True}]
        mapping = {"nom": "Nom", "actif": "Actif"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "Oui" in result

    def test_to_csv_with_boolean_false(self):
        """Teste export CSV avec boolean False."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "actif": False}]
        mapping = {"nom": "Nom", "actif": "Actif"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "Non" in result

    def test_to_csv_with_list_value(self):
        """Teste export CSV avec liste."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "tags": ["A", "B", "C"]}]
        mapping = {"nom": "Nom", "tags": "Tags"}
        
        result = IOService.to_csv(items, mapping)
        
        assert "A, B, C" in result

    def test_to_csv_with_none_value(self):
        """Teste export CSV avec None."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "description": None}]
        mapping = {"nom": "Nom", "description": "Description"}
        
        result = IOService.to_csv(items, mapping)
        
        # None devient chaîne vide
        assert "Test" in result

    def test_from_csv_basic(self):
        """Teste import CSV basique."""
        from src.services.io_service import IOService
        
        csv_content = "Nom,Quantité\nTest,10\n"
        mapping = {"nom": "Nom", "quantite": "Quantité"}
        required = ["nom"]
        
        items, errors = IOService.from_csv(csv_content, mapping, required)
        
        assert len(items) == 1
        assert len(errors) == 0
        assert items[0]["nom"] == "Test"
        assert items[0]["quantite"] == 10

    def test_from_csv_missing_required_field(self):
        """Teste import CSV avec champ requis manquant."""
        from src.services.io_service import IOService
        
        csv_content = "Nom,Quantité\n,10\n"  # Nom vide
        mapping = {"nom": "Nom", "quantite": "Quantité"}
        required = ["nom"]
        
        items, errors = IOService.from_csv(csv_content, mapping, required)
        
        assert len(items) == 0
        assert len(errors) == 1
        assert "Champs manquants" in errors[0]

    def test_from_csv_multiple_rows(self):
        """Teste import CSV multiple lignes."""
        from src.services.io_service import IOService
        
        csv_content = "Nom,Quantité\nA,1\nB,2\nC,3\n"
        mapping = {"nom": "Nom", "quantite": "Quantité"}
        required = ["nom"]
        
        items, errors = IOService.from_csv(csv_content, mapping, required)
        
        assert len(items) == 3
        assert len(errors) == 0


class TestIOServiceJSON:
    """Tests complets du service IO - JSON"""

    def test_to_json_empty_list(self):
        """Teste export JSON liste vide."""
        from src.services.io_service import IOService
        
        result = IOService.to_json([])
        assert result == "[]"

    def test_to_json_single_item(self):
        """Teste export JSON item unique."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test", "valeur": 100}]
        result = IOService.to_json(items)
        
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["nom"] == "Test"
        assert data[0]["valeur"] == 100

    def test_to_json_custom_indent(self):
        """Teste export JSON avec indent personnalisé."""
        from src.services.io_service import IOService
        
        items = [{"nom": "Test"}]
        result = IOService.to_json(items, indent=4)
        
        assert "\n" in result  # Pretty printed

    def test_from_json_basic(self):
        """Teste import JSON basique."""
        from src.services.io_service import IOService
        
        json_content = '[{"nom": "Test", "valeur": 100}]'
        required = ["nom"]
        
        items, errors = IOService.from_json(json_content, required)
        
        assert len(items) == 1
        assert len(errors) == 0
        assert items[0]["nom"] == "Test"

    def test_from_json_invalid_json(self):
        """Teste import JSON invalide."""
        from src.services.io_service import IOService
        
        json_content = '{invalid json}'
        required = ["nom"]
        
        items, errors = IOService.from_json(json_content, required)
        
        assert len(items) == 0
        assert len(errors) == 1
        assert "JSON invalide" in errors[0]

    def test_from_json_single_object(self):
        """Teste import JSON objet unique (pas liste)."""
        from src.services.io_service import IOService
        
        json_content = '{"nom": "Test", "valeur": 100}'
        required = ["nom"]
        
        items, errors = IOService.from_json(json_content, required)
        
        assert len(items) == 1
        assert items[0]["nom"] == "Test"

    def test_from_json_missing_required(self):
        """Teste import JSON avec champ requis manquant."""
        from src.services.io_service import IOService
        
        json_content = '[{"valeur": 100}]'  # Pas de "nom"
        required = ["nom"]
        
        items, errors = IOService.from_json(json_content, required)
        
        assert len(items) == 0
        assert len(errors) == 1
        assert "Champs manquants" in errors[0]


class TestIOServiceParseValue:
    """Tests du parsing de valeurs."""

    def test_parse_value_empty(self):
        """Teste parsing valeur vide."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("") is None
        assert IOService._parse_value("  ") is None

    def test_parse_value_boolean_oui(self):
        """Teste parsing 'oui'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("oui") is True
        assert IOService._parse_value("Oui") is True
        assert IOService._parse_value("OUI") is True

    def test_parse_value_boolean_yes(self):
        """Teste parsing 'yes'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("yes") is True
        assert IOService._parse_value("Yes") is True
        assert IOService._parse_value("YES") is True

    def test_parse_value_boolean_true(self):
        """Teste parsing 'true'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("true") is True
        assert IOService._parse_value("True") is True

    def test_parse_value_boolean_1(self):
        """Teste parsing '1' comme true."""
        from src.services.io_service import IOService
        
        # Note: "1" est aussi un int, donc peut retourner 1
        result = IOService._parse_value("1")
        assert result in [True, 1]

    def test_parse_value_boolean_non(self):
        """Teste parsing 'non'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("non") is False
        assert IOService._parse_value("Non") is False
        assert IOService._parse_value("NON") is False

    def test_parse_value_boolean_no(self):
        """Teste parsing 'no'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("no") is False
        assert IOService._parse_value("No") is False

    def test_parse_value_boolean_false(self):
        """Teste parsing 'false'."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("false") is False
        assert IOService._parse_value("False") is False

    def test_parse_value_boolean_0(self):
        """Teste parsing '0' comme false."""
        from src.services.io_service import IOService
        
        # Note: "0" est aussi un int, donc peut retourner 0
        result = IOService._parse_value("0")
        assert result in [False, 0]

    def test_parse_value_integer(self):
        """Teste parsing entier."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("42") == 42
        assert IOService._parse_value("123") == 123
        assert IOService._parse_value("-5") == -5

    def test_parse_value_float_dot(self):
        """Teste parsing float avec point."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("3.14") == 3.14
        assert IOService._parse_value("0.5") == 0.5

    def test_parse_value_float_comma(self):
        """Teste parsing float avec virgule (format français)."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("3,14") == 3.14

    def test_parse_value_date_dd_mm_yyyy(self):
        """Teste parsing date dd/mm/yyyy."""
        from src.services.io_service import IOService
        
        result = IOService._parse_value("06/02/2026")
        assert result == date(2026, 2, 6)

    def test_parse_value_date_yyyy_mm_dd(self):
        """Teste parsing date yyyy-mm-dd."""
        from src.services.io_service import IOService
        
        result = IOService._parse_value("2026-02-06")
        assert result == date(2026, 2, 6)

    def test_parse_value_date_dd_mm_yyyy_dash(self):
        """Teste parsing date dd-mm-yyyy."""
        from src.services.io_service import IOService
        
        result = IOService._parse_value("06-02-2026")
        assert result == date(2026, 2, 6)

    def test_parse_value_string(self):
        """Teste parsing string ordinaire."""
        from src.services.io_service import IOService
        
        assert IOService._parse_value("HelloWorld") == "HelloWorld"
        assert IOService._parse_value("Some text") == "Some text"


class TestIOServiceFieldMappings:
    """Tests des mappings de champs prédéfinis."""

    def test_recette_field_mapping_exists(self):
        """Teste que le mapping recettes existe."""
        from src.services.io_service import RECETTE_FIELD_MAPPING
        
        assert "nom" in RECETTE_FIELD_MAPPING
        assert "description" in RECETTE_FIELD_MAPPING
        assert "temps_preparation" in RECETTE_FIELD_MAPPING
        assert "temps_cuisson" in RECETTE_FIELD_MAPPING
        assert "portions" in RECETTE_FIELD_MAPPING
        assert "difficulte" in RECETTE_FIELD_MAPPING

    def test_inventaire_field_mapping_exists(self):
        """Teste que le mapping inventaire existe."""
        from src.services.io_service import INVENTAIRE_FIELD_MAPPING
        
        assert "nom" in INVENTAIRE_FIELD_MAPPING
        assert "categorie" in INVENTAIRE_FIELD_MAPPING
        assert "quantite" in INVENTAIRE_FIELD_MAPPING
        assert "unite" in INVENTAIRE_FIELD_MAPPING
        assert "seuil" in INVENTAIRE_FIELD_MAPPING
        assert "emplacement" in INVENTAIRE_FIELD_MAPPING
        assert "date_peremption" in INVENTAIRE_FIELD_MAPPING

    def test_courses_field_mapping_exists(self):
        """Teste que le mapping courses existe."""
        from src.services.io_service import COURSES_FIELD_MAPPING
        
        assert "nom" in COURSES_FIELD_MAPPING
        assert "quantite" in COURSES_FIELD_MAPPING
        assert "unite" in COURSES_FIELD_MAPPING
        assert "priorite" in COURSES_FIELD_MAPPING
        assert "magasin" in COURSES_FIELD_MAPPING


# ═══════════════════════════════════════════════════════════════════════════
# TESTS TYPES.BASESERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestTypesBaseServiceInit:
    """Tests d'initialisation de types.BaseService."""

    def test_init_with_model(self):
        """Teste l'initialisation avec un modèle."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        
        assert service.model == Recette
        assert service.model_name == "Recette"
        assert service.cache_ttl == 60  # Default

    def test_init_with_custom_ttl(self):
        """Teste l'initialisation avec TTL personnalisé."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette, cache_ttl=1800)
        
        assert service.cache_ttl == 1800


class TestTypesBaseServiceMethods:
    """Tests des méthodes de types.BaseService."""

    def test_has_create_method(self):
        """Teste que create existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'create')
        assert callable(service.create)

    def test_has_get_by_id_method(self):
        """Teste que get_by_id existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'get_by_id')
        assert callable(service.get_by_id)

    def test_has_get_all_method(self):
        """Teste que get_all existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'get_all')
        assert callable(service.get_all)

    def test_has_update_method(self):
        """Teste que update existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'update')
        assert callable(service.update)

    def test_has_delete_method(self):
        """Teste que delete existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'delete')
        assert callable(service.delete)

    def test_has_count_method(self):
        """Teste que count existe."""
        from src.services.types import BaseService
        from src.core.models import Recette
        
        service = BaseService(Recette)
        assert hasattr(service, 'count')
        assert callable(service.count)


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PWA SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestPWAServiceImport:
    """Tests d'import du PWA Service."""

    def test_import_pwa_module(self):
        """Teste l'import du module pwa."""
        from src.services import pwa
        assert pwa is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS PUSH SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestNotificationsPushImport:
    """Tests d'import du service notifications push."""

    def test_import_notifications_push_module(self):
        """Teste l'import du module."""
        from src.services import notifications_push
        assert notifications_push is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS REALTIME SYNC SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestRealtimeSyncImport:
    """Tests d'import du service realtime sync."""

    def test_import_realtime_sync_module(self):
        """Teste l'import du module."""
        from src.services import realtime_sync
        assert realtime_sync is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS OPENFOODFACTS SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestOpenFoodFactsImport:
    """Tests d'import du service OpenFoodFacts."""

    def test_import_openfoodfacts_module(self):
        """Teste l'import du module."""
        from src.services import openfoodfacts
        assert openfoodfacts is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS ACTION HISTORY SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestActionHistoryImport:
    """Tests d'import du service action history."""

    def test_import_action_history_module(self):
        """Teste l'import du module."""
        from src.services import action_history
        assert action_history is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS COURSES INTELLIGENTES SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestCoursesIntelligentesImport:
    """Tests d'import du service courses intelligentes."""

    def test_import_courses_intelligentes_module(self):
        """Teste l'import du module."""
        from src.services import courses_intelligentes
        assert courses_intelligentes is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PLANNING UNIFIED SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestPlanningUnifiedImport:
    """Tests d'import du service planning unified."""

    def test_import_planning_unified_module(self):
        """Teste l'import du module."""
        from src.services import planning_unified
        assert planning_unified is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS RECIPE IMPORT SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestRecipeImportImport:
    """Tests d'import du service recipe import."""

    def test_import_recipe_import_module(self):
        """Teste l'import du module."""
        from src.services import recipe_import
        assert recipe_import is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS PDF EXPORT SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestPDFExportImport:
    """Tests d'import du service pdf export."""

    def test_import_pdf_export_module(self):
        """Teste l'import du module."""
        from src.services import pdf_export
        assert pdf_export is not None


# ═══════════════════════════════════════════════════════════════════════════
# TESTS FACTURE OCR SERVICE
# ═══════════════════════════════════════════════════════════════════════════


class TestFactureOCRImport:
    """Tests d'import du service facture OCR."""

    def test_import_facture_ocr_module(self):
        """Teste l'import du module."""
        from src.services import facture_ocr
        assert facture_ocr is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
