#!/usr/bin/env python3
"""Delete duplicate test files to fix collection errors."""
from pathlib import Path

# Files to keep (new fixed versions)
keep_files = {
    "tests/domains/famille/ui/test_routines.py",
    "tests/domains/maison/services/test_inventaire.py",
    "tests/domains/maison/ui/test_courses.py",
    "tests/domains/maison/ui/test_paris.py",
    "tests/domains/planning/ui/components/test_init.py",
    "tests/test_parametres.py",
    "tests/test_rapports.py",
    "tests/test_recettes_import.py",
    "tests/test_vue_ensemble.py",
}

# Files to delete (duplicates/old versions)
delete_files = [
    "tests/domains/famille/services/test_routines.py",  # Duplicate of test_routines.py
    "tests/domains/cuisine/ui/test_inventaire.py",  # Duplicate of test_inventaire.py
    "tests/domains/cuisine/ui/test_courses.py",  # Duplicate of test_courses.py
    "tests/domains/jeux/ui/test_paris.py",  # Duplicate of test_paris.py
]

for file in delete_files:
    path = Path(file)
    if path.exists():
        path.unlink()
        print(f"✓ Deleted: {file}")
    else:
        print(f"⊘ Not found: {file}")

print("\nFiles kept (new fixed versions):")
for file in sorted(keep_files):
    if Path(file).exists():
        print(f"✓ Kept: {file}")
    else:
        print(f"✗ MISSING: {file}")
