"""
Tests unitaires pour backup_utils.py.

Ces tests vérifient les fonctions pures du module backup_utils
sans nécessiter de base de données ni de dépendances externes.
"""

import pytest
from datetime import datetime, timedelta


class TestBackupId:
    """Tests pour la génération et validation d'IDs de backup."""
    
    def test_generate_backup_id_default(self):
        """Test génération ID avec date courante."""
        from src.services.backup import generate_backup_id
        
        backup_id = generate_backup_id()
        
        assert len(backup_id) == 15  # YYYYMMDD_HHMMSS
        assert "_" in backup_id
        assert backup_id.replace("_", "").isdigit()
    
    def test_generate_backup_id_specific_date(self):
        """Test génération ID avec date spécifique."""
        from src.services.backup import generate_backup_id
        
        dt = datetime(2024, 1, 15, 14, 30, 45)
        backup_id = generate_backup_id(dt)
        
        assert backup_id == "20240115_143045"
    
    def test_generate_backup_id_midnight(self):
        """Test génération ID à minuit."""
        from src.services.backup import generate_backup_id
        
        dt = datetime(2024, 12, 31, 0, 0, 0)
        backup_id = generate_backup_id(dt)
        
        assert backup_id == "20241231_000000"
    
    def test_parse_backup_id_valid(self):
        """Test parsing d'un ID valide."""
        from src.services.backup import parse_backup_id
        
        result = parse_backup_id("20240115_143045")
        
        assert result == datetime(2024, 1, 15, 14, 30, 45)
    
    def test_parse_backup_id_invalid(self):
        """Test parsing d'un ID invalide."""
        from src.services.backup import parse_backup_id
        
        assert parse_backup_id("invalid") is None
        assert parse_backup_id("20241315_143045") is None  # Mois invalide
        assert parse_backup_id("") is None
    
    def test_is_valid_backup_id(self):
        """Test validation d'ID."""
        from src.services.backup import is_valid_backup_id
        
        assert is_valid_backup_id("20240115_143045") is True
        assert is_valid_backup_id("invalid") is False
        assert is_valid_backup_id("") is False


class TestChecksum:
    """Tests pour le calcul de checksums."""
    
    def test_calculate_checksum_simple(self):
        """Test calcul MD5 simple."""
        from src.services.backup import calculate_checksum
        
        checksum = calculate_checksum('{"test": 1}')
        
        assert len(checksum) == 32  # MD5 = 32 hex chars
        assert checksum.isalnum()
    
    def test_calculate_checksum_deterministic(self):
        """Test que le checksum est déterministe."""
        from src.services.backup import calculate_checksum
        
        data = '{"key": "value", "number": 123}'
        
        assert calculate_checksum(data) == calculate_checksum(data)
    
    def test_calculate_checksum_different_data(self):
        """Test que différentes données donnent différents checksums."""
        from src.services.backup import calculate_checksum
        
        checksum1 = calculate_checksum("data1")
        checksum2 = calculate_checksum("data2")
        
        assert checksum1 != checksum2
    
    def test_verify_checksum_valid(self):
        """Test vérification checksum valide."""
        from src.services.backup import calculate_checksum, verify_checksum
        
        data = "test data"
        checksum = calculate_checksum(data)
        
        assert verify_checksum(data, checksum) is True
    
    def test_verify_checksum_invalid(self):
        """Test vérification checksum invalide."""
        from src.services.backup import verify_checksum
        
        assert verify_checksum("data", "wrong_checksum") is False


class TestSerialization:
    """Tests pour la sérialisation et désérialisation."""
    
    def test_serialize_value_datetime(self):
        """Test sérialisation datetime."""
        from src.services.backup import serialize_value
        
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = serialize_value(dt)
        
        assert result == "2024-01-15T10:30:00"
    
    def test_serialize_value_primitives(self):
        """Test sérialisation de primitives."""
        from src.services.backup import serialize_value
        
        assert serialize_value(123) == 123
        assert serialize_value("string") == "string"
        assert serialize_value(None) is None
        assert serialize_value(True) is True
        assert serialize_value([1, 2]) == [1, 2]
    
    def test_deserialize_value_datetime(self):
        """Test désérialisation datetime."""
        from src.services.backup import deserialize_value
        
        result = deserialize_value("2024-01-15T10:30:00")
        
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
    
    def test_deserialize_value_non_datetime(self):
        """Test que les non-datetimes ne sont pas modifiées."""
        from src.services.backup import deserialize_value
        
        assert deserialize_value(123) == 123
        assert deserialize_value("simple string") == "simple string"
    
    def test_model_to_dict_simple(self):
        """Test conversion d'objet en dict."""
        from src.services.backup import model_to_dict
        
        class SimpleObject:
            def __init__(self):
                self.id = 1
                self.name = "test"
                self._private = "hidden"
        
        result = model_to_dict(SimpleObject())
        
        assert result["id"] == 1
        assert result["name"] == "test"
        assert "_private" not in result


class TestValidation:
    """Tests pour la validation de structure."""
    
    def test_validate_backup_structure_valid(self):
        """Test validation structure valide."""
        from src.services.backup import validate_backup_structure
        
        data = {"metadata": {"id": "123"}, "data": {"recettes": []}}
        is_valid, error = validate_backup_structure(data)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_backup_structure_missing_metadata(self):
        """Test validation sans metadata."""
        from src.services.backup import validate_backup_structure
        
        data = {"data": {"recettes": []}}
        is_valid, error = validate_backup_structure(data)
        
        assert is_valid is False
        assert "metadata" in error
    
    def test_validate_backup_structure_missing_data(self):
        """Test validation sans data."""
        from src.services.backup import validate_backup_structure
        
        data = {"metadata": {"id": "123"}}
        is_valid, error = validate_backup_structure(data)
        
        assert is_valid is False
        assert "data" in error
    
    def test_validate_backup_structure_not_dict(self):
        """Test validation avec non-dict."""
        from src.services.backup import validate_backup_structure
        
        is_valid, error = validate_backup_structure([1, 2, 3])
        
        assert is_valid is False
        assert "dictionnaire" in error
    
    def test_validate_backup_metadata_valid(self):
        """Test validation métadonnées valides."""
        from src.services.backup import validate_backup_metadata
        
        metadata = {"id": "20240115_143000", "created_at": "2024-01-15T14:30:00"}
        is_valid, error = validate_backup_metadata(metadata)
        
        assert is_valid is True
    
    def test_validate_backup_metadata_missing_id(self):
        """Test validation métadonnées sans ID."""
        from src.services.backup import validate_backup_metadata
        
        is_valid, error = validate_backup_metadata({"created_at": "2024-01-15"})
        
        assert is_valid is False
        assert "id" in error


class TestFileUtils:
    """Tests pour les utilitaires de fichiers."""
    
    def test_is_compressed_file_gz(self):
        """Test détection fichier gzip."""
        from src.services.backup import is_compressed_file
        
        assert is_compressed_file("backup.json.gz") is True
        assert is_compressed_file("file.gz") is True
    
    def test_is_compressed_file_json(self):
        """Test détection fichier JSON non compressé."""
        from src.services.backup import is_compressed_file
        
        assert is_compressed_file("backup.json") is False
        assert is_compressed_file("data.txt") is False
    
    def test_get_backup_filename_compressed(self):
        """Test génération nom fichier compressé."""
        from src.services.backup import get_backup_filename
        
        filename = get_backup_filename("20240115_143000", compressed=True)
        
        assert filename == "backup_20240115_143000.json.gz"
    
    def test_get_backup_filename_uncompressed(self):
        """Test génération nom fichier non compressé."""
        from src.services.backup import get_backup_filename
        
        filename = get_backup_filename("20240115_143000", compressed=False)
        
        assert filename == "backup_20240115_143000.json"
    
    def test_parse_backup_filename_compressed(self):
        """Test parsing nom fichier compressé."""
        from src.services.backup import parse_backup_filename
        
        result = parse_backup_filename("backup_20240115_143000.json.gz")
        
        assert result["id"] == "20240115_143000"
        assert result["compressed"] is True
        assert result["valid"] is True
    
    def test_parse_backup_filename_uncompressed(self):
        """Test parsing nom fichier non compressé."""
        from src.services.backup import parse_backup_filename
        
        result = parse_backup_filename("backup_20240115_143000.json")
        
        assert result["id"] == "20240115_143000"
        assert result["compressed"] is False
        assert result["valid"] is True
    
    def test_parse_backup_filename_invalid(self):
        """Test parsing nom fichier invalide."""
        from src.services.backup import parse_backup_filename
        
        result = parse_backup_filename("random_file.txt")
        
        assert result["valid"] is False
    
    def test_format_file_size_bytes(self):
        """Test formatage taille en bytes."""
        from src.services.backup import format_file_size
        
        assert format_file_size(500) == "500 B"
    
    def test_format_file_size_kb(self):
        """Test formatage taille en KB."""
        from src.services.backup import format_file_size
        
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(2048) == "2.0 KB"
    
    def test_format_file_size_mb(self):
        """Test formatage taille en MB."""
        from src.services.backup import format_file_size
        
        assert format_file_size(1024 * 1024) == "1.0 MB"
    
    def test_format_file_size_gb(self):
        """Test formatage taille en GB."""
        from src.services.backup import format_file_size
        
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


class TestRestoreOrder:
    """Tests pour l'ordre de restauration."""
    
    def test_get_restore_order_returns_list(self):
        """Test que l'ordre retourne une liste."""
        from src.services.backup import get_restore_order
        
        order = get_restore_order()
        
        assert isinstance(order, list)
        assert len(order) > 0
    
    def test_get_restore_order_ingredients_first(self):
        """Test que ingredients est en premier."""
        from src.services.backup import get_restore_order
        
        order = get_restore_order()
        
        assert order[0] == "ingredients"
    
    def test_get_restore_order_recettes_before_repas(self):
        """Test que recettes vient avant repas."""
        from src.services.backup import get_restore_order
        
        order = get_restore_order()
        
        recettes_idx = order.index("recettes")
        repas_idx = order.index("repas")
        
        assert recettes_idx < repas_idx
    
    def test_filter_and_order_tables(self):
        """Test filtrage et tri des tables."""
        from src.services.backup import filter_and_order_tables
        
        tables = ["repas", "ingredients", "recettes"]
        result = filter_and_order_tables(tables)
        
        assert result[0] == "ingredients"
        assert result[1] == "recettes"
        assert result[2] == "repas"
    
    def test_filter_and_order_tables_unknown(self):
        """Test filtrage avec tables inconnues."""
        from src.services.backup import filter_and_order_tables
        
        tables = ["unknown_table", "ingredients"]
        result = filter_and_order_tables(tables)
        
        assert result == ["ingredients"]


class TestBackupStats:
    """Tests pour les statistiques de backup."""
    
    def test_calculate_backup_stats(self):
        """Test calcul des stats."""
        from src.services.backup import calculate_backup_stats
        
        data = {
            "data": {
                "recettes": [1, 2, 3],
                "ingredients": [1, 2],
            }
        }
        
        stats = calculate_backup_stats(data)
        
        assert stats["tables_count"] == 2
        assert stats["total_records"] == 5
        assert stats["records_per_table"]["recettes"] == 3
        assert stats["records_per_table"]["ingredients"] == 2
    
    def test_calculate_backup_stats_empty(self):
        """Test calcul stats backup vide."""
        from src.services.backup import calculate_backup_stats
        
        stats = calculate_backup_stats({"data": {}})
        
        assert stats["tables_count"] == 0
        assert stats["total_records"] == 0
    
    def test_compare_backup_stats_identical(self):
        """Test comparaison stats identiques."""
        from src.services.backup import compare_backup_stats
        
        stats = {"tables_count": 5, "total_records": 100, "records_per_table": {"a": 50, "b": 50}}
        
        diff = compare_backup_stats(stats, stats)
        
        assert diff["tables_diff"] == 0
        assert diff["records_diff"] == 0
        assert diff["tables_missing"] == []
        assert diff["tables_extra"] == []
    
    def test_compare_backup_stats_different(self):
        """Test comparaison stats différentes."""
        from src.services.backup import compare_backup_stats
        
        original = {"tables_count": 5, "total_records": 100, "records_per_table": {"a": 50, "b": 50}}
        restored = {"tables_count": 4, "total_records": 80, "records_per_table": {"a": 50, "c": 30}}
        
        diff = compare_backup_stats(original, restored)
        
        assert diff["tables_diff"] == 1
        assert diff["records_diff"] == 20
        assert "b" in diff["tables_missing"]
        assert "c" in diff["tables_extra"]


class TestRotation:
    """Tests pour la rotation des backups."""
    
    def test_get_backups_to_rotate_under_limit(self):
        """Test rotation sous la limite."""
        from src.services.backup import get_backups_to_rotate
        
        files = [("a.json", 100), ("b.json", 200)]
        
        to_delete = get_backups_to_rotate(files, max_backups=5)
        
        assert to_delete == []
    
    def test_get_backups_to_rotate_over_limit(self):
        """Test rotation au-dessus de la limite."""
        from src.services.backup import get_backups_to_rotate
        
        files = [
            ("a.json", 100),  # Le plus ancien
            ("b.json", 200),
            ("c.json", 300),  # Le plus récent
        ]
        
        to_delete = get_backups_to_rotate(files, max_backups=2)
        
        assert to_delete == ["a.json"]
    
    def test_should_run_backup_first_time(self):
        """Test backup première fois."""
        from src.services.backup import should_run_backup
        
        assert should_run_backup(None, interval_hours=24) is True
    
    def test_should_run_backup_interval_passed(self):
        """Test backup après intervalle écoulé."""
        from src.services.backup import should_run_backup
        
        last = datetime.now() - timedelta(hours=25)
        
        assert should_run_backup(last, interval_hours=24) is True
    
    def test_should_run_backup_interval_not_passed(self):
        """Test backup avant intervalle."""
        from src.services.backup import should_run_backup
        
        last = datetime.now() - timedelta(hours=12)
        
        assert should_run_backup(last, interval_hours=24) is False


class TestEdgeCases:
    """Tests pour les cas limites."""
    
    def test_empty_data_serialization(self):
        """Test sérialisation données vides."""
        from src.services.backup import serialize_value
        
        assert serialize_value({}) == {}
        assert serialize_value([]) == []
    
    def test_unicode_checksum(self):
        """Test checksum avec caractères unicode."""
        from src.services.backup import calculate_checksum
        
        checksum = calculate_checksum('{"nom": "Bœuf bourguignon", "émoji": "🍖"}')
        
        assert len(checksum) == 32
    
    def test_deserialize_value_with_z_timezone(self):
        """Test désérialisation avec timezone Z."""
        from src.services.backup import deserialize_value
        
        result = deserialize_value("2024-01-15T10:30:00Z")
        
        assert isinstance(result, datetime)
    
    def test_format_file_size_zero(self):
        """Test formatage taille zéro."""
        from src.services.backup import format_file_size
        
        assert format_file_size(0) == "0 B"
    
    def test_validate_backup_structure_nested_invalid(self):
        """Test validation avec data non-dict."""
        from src.services.backup import validate_backup_structure
        
        data = {"metadata": {}, "data": "not a dict"}
        is_valid, error = validate_backup_structure(data)
        
        assert is_valid is False
        assert "dictionnaire" in error


# Tests de performance
class TestPerformance:
    """Tests de performance."""
    
    def test_checksum_performance(self):
        """Test performance du calcul de checksum."""
        from src.services.backup import calculate_checksum
        import time
        
        # Générer une grande chaîne
        data = "x" * 100000
        
        start = time.time()
        for _ in range(100):
            calculate_checksum(data)
        elapsed = time.time() - start
        
        # Doit être rapide (< 1 seconde pour 100 itérations)
        assert elapsed < 1.0
    
    def test_filter_and_order_performance(self):
        """Test performance du filtrage."""
        from src.services.backup import filter_and_order_tables
        import time
        
        tables = ["repas", "ingredients", "recettes"] * 100
        
        start = time.time()
        for _ in range(1000):
            filter_and_order_tables(tables)
        elapsed = time.time() - start
        
        assert elapsed < 1.0
