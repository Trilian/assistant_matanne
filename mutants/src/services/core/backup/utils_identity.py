"""
Utilitaires d'identification et de nommage pour les backups.

Contient les fonctions de :
- Génération et parsing d'identifiants de backup
- Calcul et vérification de checksums (MD5)
- Génération et parsing de noms de fichiers
- Formatage de tailles de fichiers
"""

import hashlib
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# GÉNÉRATION ET VALIDATION D'IDENTIFIANTS
# ═══════════════════════════════════════════════════════════


def generate_backup_id(dt: datetime | None = None) -> str:
    """
    Génère un ID unique pour le backup basé sur un timestamp.

    Args:
        dt: Date/heure à utiliser (par défaut: maintenant)

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
        backup_id: ID à vérifier

    Returns:
        True si le format est valide

    Examples:
        >>> is_valid_backup_id('20240115_143000')
        True
        >>> is_valid_backup_id('invalid')
        False
    """
    return parse_backup_id(backup_id) is not None


# ═══════════════════════════════════════════════════════════
# CALCUL ET VALIDATION DE CHECKSUMS
# ═══════════════════════════════════════════════════════════


def calculate_checksum(data: str) -> str:
    """
    Calcule le checksum MD5 des données.

    Args:
        data: Chaîne de caractères à hasher

    Returns:
        Hash MD5 hexadécimal (32 caractères)

    Examples:
        >>> calculate_checksum('{"test": 1}')
        'e1568c571e684e0fb1724da85d215dc0'
    """
    return hashlib.md5(data.encode()).hexdigest()


def verify_checksum(data: str, expected_checksum: str) -> bool:
    """
    Vérifie que le checksum des données correspond à l'attendu.

    Args:
        data: Données à vérifier
        expected_checksum: Checksum attendu

    Returns:
        True si les checksums correspondent
    """
    return calculate_checksum(data) == expected_checksum


# ═══════════════════════════════════════════════════════════
# GESTION DES NOMS DE FICHIERS
# ═══════════════════════════════════════════════════════════


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


__all__ = [
    "generate_backup_id",
    "parse_backup_id",
    "is_valid_backup_id",
    "calculate_checksum",
    "verify_checksum",
    "get_backup_filename",
    "parse_backup_filename",
    "format_file_size",
]
