"""Tests pour backup/utils.py - Fonctions utilitaires pures."""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.services.core.backup import (
    calculate_backup_stats,
    calculate_checksum,
    compare_backup_stats,
    deserialize_value,
    filter_and_order_tables,
    format_file_size,
    generate_backup_id,
    get_backup_filename,
    get_backups_to_rotate,
    get_restore_order,
    is_compressed_file,
    is_valid_backup_id,
    model_to_dict,
    parse_backup_filename,
    parse_backup_id,
    serialize_value,
    should_run_backup,
    validate_backup_metadata,
    validate_backup_structure,
    verify_checksum,
)

# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION ET VALIDATION D'IDENTIFIANTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenerateBackupId:
    """Tests pour generate_backup_id."""

    def test_specific_datetime(self):
        """Test avec datetime spécifique."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = generate_backup_id(dt)
        assert result == "20240115_143000"

    def test_midnight(self):
        """Test à minuit."""
        dt = datetime(2024, 6, 1, 0, 0, 0)
        result = generate_backup_id(dt)
        assert result == "20240601_000000"

    def test_end_of_day(self):
        """Test en fin de journée."""
        dt = datetime(2024, 12, 31, 23, 59, 59)
        result = generate_backup_id(dt)
        assert result == "20241231_235959"

    def test_default_is_now(self):
        """Test que la valeur par défaut est datetime.now()."""
        before = datetime.now()
        result = generate_backup_id()
        after = datetime.now()

        # Le résultat doit être entre before et after
        parsed = parse_backup_id(result)
        assert before.replace(microsecond=0) <= parsed <= after.replace(microsecond=0)

    def test_format_is_correct(self):
        """Test le format YYYYMMDD_HHMMSS."""
        dt = datetime(2024, 3, 5, 8, 9, 7)
        result = generate_backup_id(dt)

        assert len(result) == 15
        assert result[8] == "_"
        assert result[:4] == "2024"


@pytest.mark.unit
class TestParseBackupId:
    """Tests pour parse_backup_id."""

    def test_valid_id(self):
        """Test avec ID valide."""
        result = parse_backup_id("20240115_143000")

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
        assert result.second == 0

    def test_invalid_format(self):
        """Test avec format invalide."""
        assert parse_backup_id("invalid") is None
        assert parse_backup_id("2024-01-15") is None
        assert parse_backup_id("20240115143000") is None  # Sans underscore

    def test_none_input(self):
        """Test avec None."""
        assert parse_backup_id(None) is None

    def test_empty_string(self):
        """Test avec chaîne vide."""
        assert parse_backup_id("") is None

    def test_partial_date(self):
        """Test avec date partielle."""
        assert parse_backup_id("20240115") is None
        assert parse_backup_id("20240115_") is None

    def test_invalid_date_values(self):
        """Test avec valeurs de date invalides."""
        # Mois 13 n'existe pas
        assert parse_backup_id("20241315_120000") is None
        # Jour 32 n'existe pas
        assert parse_backup_id("20240132_120000") is None

    def test_roundtrip(self):
        """Test aller-retour generate -> parse."""
        orig_dt = datetime(2024, 6, 15, 10, 30, 45)
        backup_id = generate_backup_id(orig_dt)
        parsed_dt = parse_backup_id(backup_id)

        assert parsed_dt == orig_dt


@pytest.mark.unit
class TestIsValidBackupId:
    """Tests pour is_valid_backup_id."""

    def test_valid_ids(self):
        """Test avec IDs valides."""
        assert is_valid_backup_id("20240115_143000") is True
        assert is_valid_backup_id("20001231_235959") is True
        assert is_valid_backup_id("19990101_000000") is True

    def test_invalid_ids(self):
        """Test avec IDs invalides."""
        assert is_valid_backup_id("") is False
        assert is_valid_backup_id("invalid") is False
        assert is_valid_backup_id("2024-01-15_14:30:00") is False
        assert is_valid_backup_id("backup_20240115") is False


# ═══════════════════════════════════════════════════════════
# TESTS CHECKSUMS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculateChecksum:
    """Tests pour calculate_checksum."""

    def test_basic_string(self):
        """Test avec chaîne simple."""
        result = calculate_checksum("hello world")

        assert len(result) == 32  # MD5 hex = 32 chars
        assert all(c in "0123456789abcdef" for c in result)

    def test_json_string(self):
        """Test avec JSON."""
        result = calculate_checksum('{"test": 1}')

        assert len(result) == 32
        # Le résultat doit être déterministe
        assert calculate_checksum('{"test": 1}') == result

    def test_empty_string(self):
        """Test avec chaîne vide."""
        result = calculate_checksum("")

        assert len(result) == 32
        # MD5 de chaîne vide connu
        assert result == "d41d8cd98f00b204e9800998ecf8427e"

    def test_deterministic(self):
        """Test que le résultat est déterministe."""
        data = "test data for checksum"

        result1 = calculate_checksum(data)
        result2 = calculate_checksum(data)
        result3 = calculate_checksum(data)

        assert result1 == result2 == result3

    def test_different_inputs_different_outputs(self):
        """Test que des entrées différentes donnent des sorties différentes."""
        result1 = calculate_checksum("data1")
        result2 = calculate_checksum("data2")

        assert result1 != result2

    def test_unicode_support(self):
        """Test avec caractères Unicode."""
        result = calculate_checksum("æ—¥æœ¬èªžãƒ†ã‚¹ãƒˆ ðŸŽ‰")
        assert len(result) == 32


@pytest.mark.unit
class TestVerifyChecksum:
    """Tests pour verify_checksum."""

    def test_valid_checksum(self):
        """Test avec checksum valide."""
        data = "test data"
        checksum = calculate_checksum(data)

        assert verify_checksum(data, checksum) is True

    def test_invalid_checksum(self):
        """Test avec checksum invalide."""
        data = "test data"
        wrong_checksum = "00000000000000000000000000000000"

        assert verify_checksum(data, wrong_checksum) is False

    def test_modified_data(self):
        """Test avec données modifiées."""
        original = "original data"
        checksum = calculate_checksum(original)

        modified = "modified data"
        assert verify_checksum(modified, checksum) is False

    def test_empty_data(self):
        """Test avec données vides."""
        checksum = calculate_checksum("")
        assert verify_checksum("", checksum) is True


# ═══════════════════════════════════════════════════════════
# TESTS SÉRIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSerializeValue:
    """Tests pour serialize_value."""

    def test_none(self):
        """Test avec None."""
        assert serialize_value(None) is None

    def test_primitives(self):
        """Test avec types primitifs."""
        assert serialize_value(42) == 42
        assert serialize_value(3.14) == 3.14
        assert serialize_value("hello") == "hello"
        assert serialize_value(True) is True
        assert serialize_value(False) is False

    def test_datetime(self):
        """Test avec datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = serialize_value(dt)

        assert result == "2024-01-15T10:30:00"

    def test_datetime_with_microseconds(self):
        """Test datetime avec microsecondes."""
        dt = datetime(2024, 1, 15, 10, 30, 0, 123456)
        result = serialize_value(dt)

        assert "2024-01-15T10:30:00" in result

    def test_date(self):
        """Test avec date (pas datetime)."""
        from datetime import date

        d = date(2024, 1, 15)
        result = serialize_value(d)

        assert result == "2024-01-15"

    def test_lists(self):
        """Test avec listes."""
        assert serialize_value([1, 2, 3]) == [1, 2, 3]
        assert serialize_value([]) == []

    def test_dicts(self):
        """Test avec dictionnaires."""
        d = {"a": 1, "b": 2}
        assert serialize_value(d) == d


@pytest.mark.unit
class TestDeserializeValue:
    """Tests pour deserialize_value."""

    def test_non_string_passthrough(self):
        """Test que les non-strings passent directement."""
        assert deserialize_value(42) == 42
        assert deserialize_value(None) is None
        assert deserialize_value([1, 2, 3]) == [1, 2, 3]

    def test_iso_datetime(self):
        """Test parsing datetime ISO."""
        result = deserialize_value("2024-01-15T10:30:00")

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.minute == 30

    def test_iso_datetime_with_z(self):
        """Test datetime avec Z (UTC)."""
        result = deserialize_value("2024-01-15T10:30:00Z")

        assert isinstance(result, datetime)

    def test_regular_string(self):
        """Test que les strings normales restent strings."""
        assert deserialize_value("hello") == "hello"
        assert deserialize_value("not a date") == "not a date"

    def test_short_string_with_t(self):
        """Test string courte avec T (pas une date)."""
        result = deserialize_value("short T")
        assert result == "short T"


@pytest.mark.unit
class TestModelToDict:
    """Tests pour model_to_dict."""

    def test_simple_object_with_dict(self):
        """Test avec objet ayant __dict__."""

        class SimpleObj:
            def __init__(self):
                self.name = "test"
                self.value = 42
                self._private = "hidden"

        obj = SimpleObj()
        result = model_to_dict(obj)

        assert result["name"] == "test"
        assert result["value"] == 42
        assert "_private" not in result  # Les attributs privés sont exclus

    def test_object_with_datetime(self):
        """Test avec objet contenant datetime."""

        class WithDate:
            def __init__(self):
                self.created = datetime(2024, 1, 15, 10, 30, 0)
                self.name = "test"

        obj = WithDate()
        result = model_to_dict(obj)

        assert result["name"] == "test"
        assert result["created"] == "2024-01-15T10:30:00"

    def test_empty_object(self):
        """Test avec objet vide."""

        class Empty:
            pass

        obj = Empty()
        result = model_to_dict(obj)

        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION DE STRUCTURE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValidateBackupStructure:
    """Tests pour validate_backup_structure."""

    def test_valid_structure(self):
        """Test avec structure valide."""
        data = {
            "metadata": {"id": "test", "created_at": "2024-01-15"},
            "data": {"recettes": [], "ingredients": []},
        }

        is_valid, error = validate_backup_structure(data)

        assert is_valid is True
        assert error == ""

    def test_missing_metadata(self):
        """Test avec metadata manquante."""
        data = {"data": {}}

        is_valid, error = validate_backup_structure(data)

        assert is_valid is False
        assert "metadata" in error.lower()

    def test_missing_data(self):
        """Test avec data manquante."""
        data = {"metadata": {}}

        is_valid, error = validate_backup_structure(data)

        assert is_valid is False
        assert "data" in error.lower()

    def test_not_a_dict(self):
        """Test avec non-dictionnaire."""
        is_valid, error = validate_backup_structure("not a dict")

        assert is_valid is False
        assert "dictionnaire" in error.lower()

    def test_metadata_not_dict(self):
        """Test avec metadata non-dict."""
        data = {
            "metadata": "not a dict",
            "data": {},
        }

        is_valid, error = validate_backup_structure(data)

        assert is_valid is False
        assert "metadata" in error.lower()

    def test_data_not_dict(self):
        """Test avec data non-dict."""
        data = {
            "metadata": {},
            "data": "not a dict",
        }

        is_valid, error = validate_backup_structure(data)

        assert is_valid is False
        assert "data" in error.lower()

    def test_empty_dicts_valid(self):
        """Test avec dictionnaires vides."""
        data = {"metadata": {}, "data": {}}

        is_valid, error = validate_backup_structure(data)

        assert is_valid is True


@pytest.mark.unit
class TestValidateBackupMetadata:
    """Tests pour validate_backup_metadata."""

    def test_valid_metadata(self):
        """Test avec métadonnées valides."""
        metadata = {
            "id": "20240115_143000",
            "created_at": "2024-01-15T14:30:00",
        }

        is_valid, error = validate_backup_metadata(metadata)

        assert is_valid is True
        assert error == ""

    def test_missing_id(self):
        """Test avec id manquant."""
        metadata = {"created_at": "2024-01-15"}

        is_valid, error = validate_backup_metadata(metadata)

        assert is_valid is False
        assert "id" in error.lower()

    def test_missing_created_at(self):
        """Test avec created_at manquant."""
        metadata = {"id": "test"}

        is_valid, error = validate_backup_metadata(metadata)

        assert is_valid is False
        assert "created_at" in error.lower()

    def test_empty_id(self):
        """Test avec id vide."""
        metadata = {"id": "", "created_at": "2024-01-15"}

        is_valid, error = validate_backup_metadata(metadata)

        assert is_valid is False


# ═══════════════════════════════════════════════════════════
# TESTS GESTION DES FICHIERS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIsCompressedFile:
    """Tests pour is_compressed_file."""

    def test_gz_extension(self):
        """Test avec extension .gz."""
        assert is_compressed_file("backup.json.gz") is True
        assert is_compressed_file("/path/to/backup.json.gz") is True

    def test_json_extension(self):
        """Test avec extension .json."""
        assert is_compressed_file("backup.json") is False
        assert is_compressed_file("/path/to/backup.json") is False

    def test_path_object(self):
        """Test avec objet Path."""
        assert is_compressed_file(Path("backup.json.gz")) is True
        assert is_compressed_file(Path("backup.json")) is False

    def test_no_extension(self):
        """Test sans extension."""
        assert is_compressed_file("backup") is False


@pytest.mark.unit
class TestGetBackupFilename:
    """Tests pour get_backup_filename."""

    def test_compressed(self):
        """Test avec compression."""
        result = get_backup_filename("20240115_143000", compressed=True)
        assert result == "backup_20240115_143000.json.gz"

    def test_not_compressed(self):
        """Test sans compression."""
        result = get_backup_filename("20240115_143000", compressed=False)
        assert result == "backup_20240115_143000.json"

    def test_default_is_compressed(self):
        """Test que la valeur par défaut est compressé."""
        result = get_backup_filename("test_id")
        assert result.endswith(".json.gz")


@pytest.mark.unit
class TestParseBackupFilename:
    """Tests pour parse_backup_filename."""

    def test_compressed_file(self):
        """Test avec fichier compressé."""
        result = parse_backup_filename("backup_20240115_143000.json.gz")

        assert result["id"] == "20240115_143000"
        assert result["compressed"] is True
        assert result["valid"] is True

    def test_uncompressed_file(self):
        """Test avec fichier non compressé."""
        result = parse_backup_filename("backup_20240115_143000.json")

        assert result["id"] == "20240115_143000"
        assert result["compressed"] is False
        assert result["valid"] is True

    def test_invalid_prefix(self):
        """Test avec préfixe invalide."""
        result = parse_backup_filename("notbackup_20240115_143000.json")

        assert result["valid"] is False
        assert result["id"] == ""

    def test_invalid_id_format(self):
        """Test avec format d'ID invalide."""
        result = parse_backup_filename("backup_invalid.json")

        assert result["valid"] is False

    def test_unknown_extension(self):
        """Test avec extension inconnue."""
        result = parse_backup_filename("backup_20240115_143000.txt")

        assert result["valid"] is False


@pytest.mark.unit
class TestFormatFileSize:
    """Tests pour format_file_size."""

    def test_bytes(self):
        """Test avec bytes."""
        assert format_file_size(500) == "500 B"
        assert format_file_size(0) == "0 B"
        assert format_file_size(1023) == "1023 B"

    def test_kilobytes(self):
        """Test avec kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(10240) == "10.0 KB"

    def test_megabytes(self):
        """Test avec megabytes."""
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1572864) == "1.5 MB"

    def test_gigabytes(self):
        """Test avec gigabytes."""
        assert format_file_size(1073741824) == "1.0 GB"
        assert format_file_size(2147483648) == "2.0 GB"


# ═══════════════════════════════════════════════════════════
# TESTS ORDRE DE RESTAURATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetRestoreOrder:
    """Tests pour get_restore_order."""

    def test_returns_list(self):
        """Test que le retour est une liste."""
        result = get_restore_order()
        assert isinstance(result, list)

    def test_ingredients_first(self):
        """Test que ingredients est en premier."""
        result = get_restore_order()
        assert result[0] == "ingredients"

    def test_contains_main_tables(self):
        """Test que les tables principales sont présentes."""
        result = get_restore_order()

        assert "ingredients" in result
        assert "recettes" in result
        assert "plannings" in result
        assert "repas" in result

    def test_fk_order(self):
        """Test que l'ordre respecte les FK."""
        result = get_restore_order()

        # ingredients doit venir avant recette_ingredients
        assert result.index("ingredients") < result.index("recette_ingredients")
        # recettes doit venir avant recette_ingredients
        assert result.index("recettes") < result.index("recette_ingredients")


@pytest.mark.unit
class TestFilterAndOrderTables:
    """Tests pour filter_and_order_tables."""

    def test_reorders_tables(self):
        """Test réordonnancement des tables."""
        tables = ["repas", "ingredients", "recettes"]
        result = filter_and_order_tables(tables)

        # Doit être dans l'ordre défini
        assert result == ["ingredients", "recettes", "repas"]

    def test_filters_unknown_tables(self):
        """Test filtrage des tables inconnues."""
        tables = ["ingredients", "unknown_table", "recettes"]
        result = filter_and_order_tables(tables)

        assert "unknown_table" not in result
        assert result == ["ingredients", "recettes"]

    def test_empty_list(self):
        """Test avec liste vide."""
        result = filter_and_order_tables([])
        assert result == []

    def test_all_unknown(self):
        """Test avec toutes tables inconnues."""
        result = filter_and_order_tables(["fake1", "fake2"])
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalculateBackupStats:
    """Tests pour calculate_backup_stats."""

    def test_basic_stats(self):
        """Test statistiques basiques."""
        data = {
            "data": {
                "recettes": [1, 2, 3],
                "ingredients": [1, 2],
            }
        }

        result = calculate_backup_stats(data)

        assert result["tables_count"] == 2
        assert result["total_records"] == 5
        assert result["records_per_table"]["recettes"] == 3
        assert result["records_per_table"]["ingredients"] == 2

    def test_empty_data(self):
        """Test avec données vides."""
        data = {"data": {}}

        result = calculate_backup_stats(data)

        assert result["tables_count"] == 0
        assert result["total_records"] == 0

    def test_missing_data_key(self):
        """Test avec clé data manquante."""
        data = {}

        result = calculate_backup_stats(data)

        assert result["tables_count"] == 0
        assert result["total_records"] == 0

    def test_empty_tables(self):
        """Test avec tables vides."""
        data = {
            "data": {
                "recettes": [],
                "ingredients": [],
            }
        }

        result = calculate_backup_stats(data)

        assert result["tables_count"] == 2
        assert result["total_records"] == 0


@pytest.mark.unit
class TestCompareBackupStats:
    """Tests pour compare_backup_stats."""

    def test_identical_stats(self):
        """Test avec stats identiques."""
        stats = {
            "tables_count": 5,
            "total_records": 100,
            "records_per_table": {"a": 50, "b": 50},
        }

        result = compare_backup_stats(stats, stats)

        assert result["tables_diff"] == 0
        assert result["records_diff"] == 0
        assert result["tables_missing"] == []
        assert result["tables_extra"] == []

    def test_missing_tables(self):
        """Test avec tables manquantes."""
        original = {
            "tables_count": 3,
            "total_records": 100,
            "records_per_table": {"a": 30, "b": 30, "c": 40},
        }
        restored = {
            "tables_count": 2,
            "total_records": 60,
            "records_per_table": {"a": 30, "b": 30},
        }

        result = compare_backup_stats(original, restored)

        assert result["tables_diff"] == 1
        assert result["records_diff"] == 40
        assert "c" in result["tables_missing"]

    def test_extra_tables(self):
        """Test avec tables supplémentaires."""
        original = {
            "records_per_table": {"a": 10},
        }
        restored = {
            "records_per_table": {"a": 10, "b": 20},
        }

        result = compare_backup_stats(original, restored)

        assert "b" in result["tables_extra"]


# ═══════════════════════════════════════════════════════════
# TESTS ROTATION DE BACKUPS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetBackupsToRotate:
    """Tests pour get_backups_to_rotate."""

    def test_under_limit(self):
        """Test avec moins de backups que la limite."""
        files = [
            ("a.json", 100),
            ("b.json", 200),
        ]

        result = get_backups_to_rotate(files, max_backups=5)

        assert result == []

    def test_at_limit(self):
        """Test exactement à la limite."""
        files = [
            ("a.json", 100),
            ("b.json", 200),
            ("c.json", 300),
        ]

        result = get_backups_to_rotate(files, max_backups=3)

        assert result == []

    def test_over_limit(self):
        """Test au-delà de la limite."""
        files = [
            ("a.json", 100),  # Plus ancien
            ("b.json", 200),
            ("c.json", 300),  # Plus récent
        ]

        result = get_backups_to_rotate(files, max_backups=2)

        assert len(result) == 1
        assert "a.json" in result  # Le plus ancien doit être supprimé

    def test_multiple_to_rotate(self):
        """Test avec plusieurs à supprimer."""
        files = [
            ("a.json", 100),
            ("b.json", 200),
            ("c.json", 300),
            ("d.json", 400),
            ("e.json", 500),
        ]

        result = get_backups_to_rotate(files, max_backups=2)

        assert len(result) == 3
        assert "a.json" in result
        assert "b.json" in result
        assert "c.json" in result

    def test_empty_list(self):
        """Test avec liste vide."""
        result = get_backups_to_rotate([], max_backups=3)
        assert result == []


@pytest.mark.unit
class TestShouldRunBackup:
    """Tests pour should_run_backup."""

    def test_no_previous_backup(self):
        """Test sans backup précédent."""
        result = should_run_backup(None, interval_hours=24)
        assert result is True

    def test_backup_overdue(self):
        """Test avec backup en retard."""
        last = datetime.now() - timedelta(hours=25)
        result = should_run_backup(last, interval_hours=24)
        assert result is True

    def test_backup_recent(self):
        """Test avec backup récent."""
        last = datetime.now() - timedelta(hours=1)
        result = should_run_backup(last, interval_hours=24)
        assert result is False

    def test_exactly_at_interval(self):
        """Test exactement à l'intervalle."""
        now = datetime(2024, 1, 15, 12, 0, 0)
        last = datetime(2024, 1, 14, 12, 0, 0)  # Exactement 24h avant

        result = should_run_backup(last, interval_hours=24, current_time=now)

        assert result is True

    def test_just_before_interval(self):
        """Test juste avant l'intervalle."""
        now = datetime(2024, 1, 15, 11, 59, 59)
        last = datetime(2024, 1, 14, 12, 0, 0)  # Presque 24h

        result = should_run_backup(last, interval_hours=24, current_time=now)

        assert result is False

    def test_short_interval(self):
        """Test avec intervalle court."""
        last = datetime.now() - timedelta(hours=2)
        result = should_run_backup(last, interval_hours=1)
        assert result is True

    def test_zero_interval(self):
        """Test avec intervalle zéro."""
        last = datetime.now()
        result = should_run_backup(last, interval_hours=0)
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Tests des cas limites."""

    def test_generate_backup_id_leap_year(self):
        """Test generate_backup_id avec année bissextile."""
        dt = datetime(2024, 2, 29, 12, 0, 0)
        result = generate_backup_id(dt)
        assert result == "20240229_120000"

    def test_checksum_large_data(self):
        """Test checksum avec grandes données."""
        large_data = "x" * 1_000_000  # 1MB
        result = calculate_checksum(large_data)
        assert len(result) == 32

    def test_format_file_size_zero(self):
        """Test format_file_size avec zéro."""
        assert format_file_size(0) == "0 B"

    def test_format_file_size_exact_boundaries(self):
        """Test format_file_size aux limites exactes."""
        assert format_file_size(1023) == "1023 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024 - 1) == "1024.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"

    def test_filter_and_order_duplicates(self):
        """Test filter_and_order_tables avec doublons."""
        tables = ["recettes", "ingredients", "recettes", "ingredients"]
        result = filter_and_order_tables(tables)

        # Ne doit pas avoir de doublons
        assert result == ["ingredients", "recettes"]

    def test_compare_backup_stats_empty(self):
        """Test compare_backup_stats avec stats vides."""
        empty = {}
        result = compare_backup_stats(empty, empty)

        assert result["tables_diff"] == 0
        assert result["records_diff"] == 0
