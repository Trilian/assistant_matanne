#!/usr/bin/env python3
"""Clean up and rename integration tests."""
from pathlib import Path
import shutil

print("PHASE 17: CLEANUP DES TESTS INTEGRATION")
print("="*60)

# Files to delete (old phase 16 variants)
to_delete = [
    "tests/integration/test_phase16.py",
    "tests/integration/test_phase16_fixed.py",
    "tests/integration/test_phase16_v2.py",
    "tests/integration/test_15e_extended_coverage.py",
]

print("\n1. Suppression des fichiers obsolètes:")
for file in to_delete:
    path = Path(file)
    if path.exists():
        path.unlink()
        print(f"   ✓ Supprimé: {file}")
    else:
        print(f"   ⊘ Non trouvé: {file}")

# Files to rename
to_rename = {
    "tests/integration/test_phase16_extended.py": "tests/integration/test_integration_crud_models.py",
    "tests/integration/test_business_logic.py": "tests/integration/test_integration_business_logic.py",
    "tests/integration/test_domains_integration.py": "tests/integration/test_integration_domains_workflows.py",
}

print("\n2. Renommage des fichiers d'intégration:")
for old, new in to_rename.items():
    old_path = Path(old)
    new_path = Path(new)
    if old_path.exists():
        shutil.move(str(old_path), str(new_path))
        print(f"   ✓ Renommé: {old} → {new}")
    else:
        print(f"   ⊘ Non trouvé: {old}")

print("\n3. État final des tests d'intégration:")
integration_dir = Path("tests/integration")
if integration_dir.exists():
    files = sorted(integration_dir.glob("*.py"))
    for f in files:
        size = f.stat().st_size
        print(f"   • {f.name} ({size} bytes)")

print("\n" + "="*60)
print("✓ CLEANUP COMPLET")
