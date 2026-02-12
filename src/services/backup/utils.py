"""
Fonctions utilitaires pures pour le service de backup.

Ces fonctions peuvent être testées sans base de données ni dépendances externes.
Elles représentent la logique métier pure extraite de backup.py.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÉNÉRATION ET VALIDATION D'IDENTIFIANTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def generate_backup_id(dt: datetime | None = None) -> str:
    """
    Génère un ID unique pour le backup basé sur un timestamp.
    
    Args:
        dt: Date/heure Ã  utiliser (par défaut: maintenant)
        
    Returns:
        ID au format YYYYMMDD_HHMMSS
        
    Examples:
        >>> generate_backup_id(datetime(2024, 1, 15, 14, 30, 0))
        '20240115_143000'
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y%m%d_%H%M%S")


def parse_backup_id(backup_id: str) -> datetime | None:
    """
    Parse un ID de backup pour récupérer la date.
    
    Args:
        backup_id: ID au format YYYYMMDD_HHMMSS
        
    Returns:
        datetime ou None si format invalide
        
    Examples:
        >>> parse_backup_id('20240115_143000')
        datetime(2024, 1, 15, 14, 30, 0)
    """
    try:
        return datetime.strptime(backup_id, "%Y%m%d_%H%M%S")
    except (ValueError, TypeError):
        return None


def is_valid_backup_id(backup_id: str) -> bool:
    """
    Vérifie si un ID de backup est valide.
    
    Args:
        backup_id: ID Ã  vérifier
        
    Returns:
        True si le format est valide
        
    Examples:
        >>> is_valid_backup_id('20240115_143000')
        True
        >>> is_valid_backup_id('invalid')
        False
    """
    return parse_backup_id(backup_id) is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL ET VALIDATION DE CHECKSUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculate_checksum(data: str) -> str:
    """
    Calcule le checksum MD5 des données.
    
    Args:
        data: Chaîne de caractères Ã  hasher
        
    Returns:
        Hash MD5 hexadécimal (32 caractères)
        
    Examples:
        >>> calculate_checksum('{"test": 1}')
        'e1568c571e684e0fb1724da85d215dc0'
    """
    return hashlib.md5(data.encode()).hexdigest()


def verify_checksum(data: str, expected_checksum: str) -> bool:
    """
    Vérifie que le checksum des données correspond Ã  l'attendu.
    
    Args:
        data: Données Ã  vérifier
        expected_checksum: Checksum attendu
        
    Returns:
        True si les checksums correspondent
    """
    return calculate_checksum(data) == expected_checksum


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONVERSION ET SÉRIALISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def model_to_dict(obj: Any) -> dict:
    """
    Convertit un objet SQLAlchemy-like en dictionnaire sérialisable.
    
    Gère automatiquement:
    - datetime -> ISO string
    - date -> ISO string
    - Les colonnes définies dans __table__.columns
    
    Args:
        obj: Objet avec attribut __table__.columns
        
    Returns:
        Dictionnaire avec les valeurs sérialisables
        
    Examples:
        >>> class FakeModel:
        ...     def __init__(self):
        ...         self.id = 1
        ...         self.created_at = datetime(2024, 1, 15)
        >>> # model_to_dict(fake_model)
    """
    result = {}
    
    # Si l'objet a __table__ (modèle SQLAlchemy)
    if hasattr(obj, '__table__'):
        for column in obj.__table__.columns:
            value = getattr(obj, column.name, None)
            result[column.name] = serialize_value(value)
    # Sinon, utiliser __dict__
    elif hasattr(obj, '__dict__'):
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
                result[key] = serialize_value(value)
    
    return result


def serialize_value(value: Any) -> Any:
    """
    Sérialise une valeur pour JSON.
    
    Args:
        value: Valeur Ã  sérialiser
        
    Returns:
        Valeur sérialisable en JSON
        
    Examples:
        >>> serialize_value(datetime(2024, 1, 15, 10, 30))
        '2024-01-15T10:30:00'
        >>> serialize_value(123)
        123
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if hasattr(value, 'isoformat'):  # date
        return value.isoformat()
    if hasattr(value, '__str__') and not isinstance(value, (str, int, float, bool, list, dict)):
        return str(value)
    return value


def deserialize_value(value: Any, key: str = "") -> Any:
    """
    Désérialise une valeur JSON (notamment les dates ISO).
    
    Args:
        value: Valeur Ã  désérialiser
        key: Nom de la clé (pour contexte)
        
    Returns:
        Valeur désérialisée (datetime si applicable)
        
    Examples:
        >>> deserialize_value('2024-01-15T10:30:00')
        datetime(2024, 1, 15, 10, 30)
    """
    if not isinstance(value, str):
        return value
    
    # Tenter de parser comme datetime ISO
    if 'T' in value and len(value) >= 19:
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            pass
    
    return value


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION DE STRUCTURE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def validate_backup_structure(data: dict) -> tuple[bool, str]:
    """
    Valide la structure d'un fichier de backup.
    
    Args:
        data: Données du backup parsées depuis JSON
        
    Returns:
        Tuple (is_valid, error_message)
        
    Examples:
        >>> validate_backup_structure({'metadata': {}, 'data': {}})
        (True, '')
        >>> validate_backup_structure({'invalid': 'structure'})
        (False, 'Structure invalide: clé "metadata" manquante')
    """
    if not isinstance(data, dict):
        return False, "Le backup doit être un dictionnaire JSON"
    
    if "metadata" not in data:
        return False, 'Structure invalide: clé "metadata" manquante'
    
    if "data" not in data:
        return False, 'Structure invalide: clé "data" manquante'
    
    if not isinstance(data["metadata"], dict):
        return False, 'Le champ "metadata" doit être un dictionnaire'
    
    if not isinstance(data["data"], dict):
        return False, 'Le champ "data" doit être un dictionnaire'
    
    return True, ""


def validate_backup_metadata(metadata: dict) -> tuple[bool, str]:
    """
    Valide les métadonnées d'un backup.
    
    Args:
        metadata: Dictionnaire de métadonnées
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not metadata.get("id"):
        return False, 'Métadonnée "id" manquante'
    
    if not metadata.get("created_at"):
        return False, 'Métadonnée "created_at" manquante'
    
    return True, ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GESTION DES FICHIERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def is_compressed_file(file_path: str | Path) -> bool:
    """
    Vérifie si un fichier est compressé (gzip).
    
    Args:
        file_path: Chemin du fichier
        
    Returns:
        True si le fichier est compressé
        
    Examples:
        >>> is_compressed_file('backup.json.gz')
        True
        >>> is_compressed_file('backup.json')
        False
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    return path.suffix == '.gz' or '.gz' in path.name


def get_backup_filename(backup_id: str, compressed: bool = True) -> str:
    """
    Génère le nom de fichier pour un backup.
    
    Args:
        backup_id: ID du backup
        compressed: Si le fichier est compressé
        
    Returns:
        Nom de fichier complet
        
    Examples:
        >>> get_backup_filename('20240115_143000')
        'backup_20240115_143000.json.gz'
        >>> get_backup_filename('20240115_143000', compressed=False)
        'backup_20240115_143000.json'
    """
    extension = ".json.gz" if compressed else ".json"
    return f"backup_{backup_id}{extension}"


def parse_backup_filename(filename: str) -> dict:
    """
    Parse un nom de fichier de backup pour en extraire les informations.
    
    Args:
        filename: Nom du fichier (backup_YYYYMMDD_HHMMSS.json.gz)
        
    Returns:
        Dict avec id, compressed, valid
        
    Examples:
        >>> parse_backup_filename('backup_20240115_143000.json.gz')
        {'id': '20240115_143000', 'compressed': True, 'valid': True}
    """
    result = {"id": "", "compressed": False, "valid": False}
    
    if not filename.startswith("backup_"):
        return result
    
    # Enlever le préfixe
    rest = filename[7:]  # Après "backup_"
    
    # Déterminer la compression
    if rest.endswith(".json.gz"):
        result["compressed"] = True
        backup_id = rest[:-8]  # Enlever ".json.gz"
    elif rest.endswith(".json"):
        result["compressed"] = False
        backup_id = rest[:-5]  # Enlever ".json"
    else:
        return result
    
    # Valider l'ID
    if is_valid_backup_id(backup_id):
        result["id"] = backup_id
        result["valid"] = True
    
    return result


def format_file_size(size_bytes: int) -> str:
    """
    Formate une taille en bytes de façon humainement lisible.
    
    Args:
        size_bytes: Taille en bytes
        
    Returns:
        Taille formatée (ex: "1.5 KB", "2.3 MB")
        
    Examples:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
        >>> format_file_size(500)
        '500 B'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ORDRE DE RESTAURATION (RESPECTE LES FK)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def get_restore_order() -> list[str]:
    """
    Retourne l'ordre de restauration des tables (respecte les FK).
    
    Les tables sans dépendances sont en premier, celles avec FK en dernier.
    
    Returns:
        Liste ordonnée des noms de tables
        
    Examples:
        >>> order = get_restore_order()
        >>> order[0]
        'ingredients'
        >>> 'recette_ingredients' in order
        True
    """
    return [
        "ingredients",
        "recettes",
        "recette_ingredients",
        "etapes_recette",
        "versions_recette",
        "articles_inventaire",
        "plannings",
        "repas",
        "articles_courses",
        "child_profiles",
        "milestones",
        "wellbeing_entries",
        "family_activities",
        "family_budgets",
        "health_routines",
        "health_objectives",
        "health_entries",
        "projects",
        "project_tasks",
        "routines",
        "routine_tasks",
        "garden_items",
        "garden_logs",
        "calendar_events",
    ]


def filter_and_order_tables(tables: list[str]) -> list[str]:
    """
    Filtre et ordonne une liste de tables selon l'ordre de restauration.
    
    Args:
        tables: Liste de noms de tables
        
    Returns:
        Liste ordonnée des tables présentes
        
    Examples:
        >>> filter_and_order_tables(['repas', 'ingredients', 'recettes'])
        ['ingredients', 'recettes', 'repas']
    """
    order = get_restore_order()
    return [t for t in order if t in tables]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES DE BACKUP
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def calculate_backup_stats(backup_data: dict) -> dict:
    """
    Calcule les statistiques d'un backup.
    
    Args:
        backup_data: Données complètes du backup
        
    Returns:
        Dict avec tables_count, total_records, par table
        
    Examples:
        >>> data = {'data': {'recettes': [1,2,3], 'ingredients': [1,2]}}
        >>> stats = calculate_backup_stats(data)
        >>> stats['total_records']
        5
    """
    data_section = backup_data.get("data", {})
    
    stats = {
        "tables_count": len(data_section),
        "total_records": 0,
        "records_per_table": {},
    }
    
    for table_name, records in data_section.items():
        count = len(records) if isinstance(records, list) else 0
        stats["records_per_table"][table_name] = count
        stats["total_records"] += count
    
    return stats


def compare_backup_stats(original: dict, restored: dict) -> dict:
    """
    Compare les statistiques entre original et restauré.
    
    Args:
        original: Stats du backup original
        restored: Stats après restauration
        
    Returns:
        Dict avec les différences
    """
    diff = {
        "tables_diff": original.get("tables_count", 0) - restored.get("tables_count", 0),
        "records_diff": original.get("total_records", 0) - restored.get("total_records", 0),
        "tables_missing": [],
        "tables_extra": [],
    }
    
    orig_tables = set(original.get("records_per_table", {}).keys())
    rest_tables = set(restored.get("records_per_table", {}).keys())
    
    diff["tables_missing"] = list(orig_tables - rest_tables)
    diff["tables_extra"] = list(rest_tables - orig_tables)
    
    return diff


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROTATION DE BACKUPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def get_backups_to_rotate(
    backup_files: list[tuple[str, float]],  # (filename, mtime)
    max_backups: int
) -> list[str]:
    """
    Détermine quels backups doivent être supprimés lors de la rotation.
    
    Args:
        backup_files: Liste de tuples (filename, modification_time)
        max_backups: Nombre maximum de backups Ã  conserver
        
    Returns:
        Liste des fichiers Ã  supprimer (les plus anciens)
        
    Examples:
        >>> files = [('a.json', 100), ('b.json', 200), ('c.json', 300)]
        >>> get_backups_to_rotate(files, max_backups=2)
        ['a.json']
    """
    if len(backup_files) <= max_backups:
        return []
    
    # Trier par date (plus récent en premier)
    sorted_files = sorted(backup_files, key=lambda x: x[1], reverse=True)
    
    # Retourner les plus anciens Ã  supprimer
    return [f[0] for f in sorted_files[max_backups:]]


def should_run_backup(
    last_backup_time: datetime | None,
    interval_hours: int,
    current_time: datetime | None = None
) -> bool:
    """
    Vérifie s'il faut exécuter un backup automatique.
    
    Args:
        last_backup_time: Date du dernier backup
        interval_hours: Intervalle en heures entre backups
        current_time: Heure actuelle (défaut: maintenant)
        
    Returns:
        True si un backup doit être exécuté
        
    Examples:
        >>> from datetime import datetime, timedelta
        >>> last = datetime.now() - timedelta(hours=25)
        >>> should_run_backup(last, interval_hours=24)
        True
    """
    if current_time is None:
        current_time = datetime.now()
    
    if last_backup_time is None:
        return True
    
    elapsed = current_time - last_backup_time
    return elapsed.total_seconds() >= interval_hours * 3600


__all__ = [
    # Identifiants
    "generate_backup_id",
    "parse_backup_id",
    "is_valid_backup_id",
    # Checksums
    "calculate_checksum",
    "verify_checksum",
    # Sérialisation
    "model_to_dict",
    "serialize_value",
    "deserialize_value",
    # Validation
    "validate_backup_structure",
    "validate_backup_metadata",
    # Fichiers
    "is_compressed_file",
    "get_backup_filename",
    "parse_backup_filename",
    "format_file_size",
    # Ordre de restauration
    "get_restore_order",
    "filter_and_order_tables",
    # Statistiques
    "calculate_backup_stats",
    "compare_backup_stats",
    # Rotation
    "get_backups_to_rotate",
    "should_run_backup",
]
