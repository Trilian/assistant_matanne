#!/usr/bin/env python3
"""Script de migration des imports src.core shims → packages canoniques.

Migre:
- src.core.database → src.core.db
- src.core.cache_multi → src.core.caching
- src.core.performance → src.core.monitoring

Usage: python scripts/migrate_core_imports.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Patterns de remplacement
REPLACEMENTS = [
    # database.py → db/
    (r"from src\.core\.database import", "from src.core.db import"),
    # cache_multi.py → caching/
    (r"from src\.core\.cache_multi import", "from src.core.caching import"),
    # performance.py → monitoring/
    (r"from src\.core\.performance import", "from src.core.monitoring import"),
]

# Fichiers à exclure (les shims eux-mêmes)
EXCLUDE_FILES = {
    "src/core/database.py",
    "src/core/cache_multi.py",
    "src/core/performance.py",
}

# Dossiers à exclure
EXCLUDE_DIRS = {".venv", "__pycache__", ".git", "htmlcov", "backups"}


def should_process(filepath: Path) -> bool:
    """Vérifie si le fichier doit être traité."""
    rel = filepath.relative_to(ROOT).as_posix()

    # Exclure les shims eux-mêmes
    if rel in EXCLUDE_FILES:
        return False

    # Exclure certains dossiers
    for part in filepath.parts:
        if part in EXCLUDE_DIRS:
            return False

    return True


def migrate_file(filepath: Path) -> bool:
    """Migre les imports d'un fichier. Retourne True si modifié."""
    if not should_process(filepath):
        return False

    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return False

    original = content

    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        rel = filepath.relative_to(ROOT).as_posix()
        print(f"✓ {rel}")
        return True

    return False


def main():
    """Point d'entrée principal."""
    print("Migration des imports src.core shims → packages canoniques\n")
    print("=" * 60)

    modified = 0

    # Parcourir tous les fichiers Python
    for pattern in ["src/**/*.py", "tests/**/*.py", "scripts/**/*.py"]:
        for filepath in ROOT.glob(pattern):
            if filepath.suffix == ".py" and migrate_file(filepath):
                modified += 1

    print("=" * 60)
    print(f"\n✅ {modified} fichiers modifiés")

    if modified > 0:
        print("\nProchaines étapes:")
        print('1. Vérifier les imports: python -c "from src.core import *"')
        print("2. Lancer les tests: pytest tests/ -v")
        print("3. Supprimer les shims si tout est OK")


if __name__ == "__main__":
    main()
