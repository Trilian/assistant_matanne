"""
Utilitaires de sérialisation et validation pour les backups.

Contient les fonctions de :
- Conversion de modèles SQLAlchemy en dictionnaires sérialisables
- Sérialisation et désérialisation de valeurs (datetime, etc.)
- Validation de la structure et des métadonnées des backups
- Détection de fichiers compressés
"""

from datetime import datetime
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════
# CONVERSION ET SÉRIALISATION
# ═══════════════════════════════════════════════════════════


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
    if hasattr(obj, "__table__"):
        for column in obj.__table__.columns:
            value = getattr(obj, column.name, None)
            result[column.name] = serialize_value(value)
    # Sinon, utiliser __dict__
    elif hasattr(obj, "__dict__"):
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
                result[key] = serialize_value(value)

    return result


def serialize_value(value: Any) -> Any:
    """
    Sérialise une valeur pour JSON.

    Args:
        value: Valeur à sérialiser

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
    if hasattr(value, "isoformat"):  # date
        return value.isoformat()
    if hasattr(value, "__str__") and not isinstance(value, str | int | float | bool | list | dict):
        return str(value)
    return value


def deserialize_value(value: Any, key: str = "") -> Any:
    """
    Désérialise une valeur JSON (notamment les dates ISO).

    Args:
        value: Valeur à désérialiser
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
    if "T" in value and len(value) >= 19:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass

    return value


# ═══════════════════════════════════════════════════════════
# VALIDATION DE STRUCTURE
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# DÉTECTION DE FICHIERS COMPRESSÉS
# ═══════════════════════════════════════════════════════════


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
    return path.suffix == ".gz" or ".gz" in path.name


__all__ = [
    "model_to_dict",
    "serialize_value",
    "deserialize_value",
    "validate_backup_structure",
    "validate_backup_metadata",
    "is_compressed_file",
]
