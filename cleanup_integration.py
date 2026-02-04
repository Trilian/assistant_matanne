#!/usr/bin/env python3
"""Renommer et nettoyer les fichiers d'intégration."""

import os
import shutil
from pathlib import Path

integration_dir = Path("tests/integration")

# Fichiers à supprimer
to_delete = [
    "test_phase16.py",
    "test_phase16_fixed.py",
    "test_phase16_v2.py",
    "test_15e_extended_coverage.py",
]

# Fichiers à renommer
to_rename = {
    "test_phase16_extended.py": "test_integration_crud_models.py",
    "test_business_logic.py": "test_integration_business_logic.py",
    "test_domains_integration.py": "test_integration_domains_workflows.py",
}

print("=" * 70)
print("NETTOYAGE ET RENOMMAGE FICHIERS INTÉGRATION")
print("=" * 70)
print()

# Supprimer les vieux fichiers
print("1. Suppression des fichiers obsolètes:")
for file in to_delete:
    filepath = integration_dir / file
    if filepath.exists():
        print(f"   ❌ Suppression: {file}")
        filepath.unlink()
    else:
        print(f"   ⊘ N'existe pas: {file}")

print()

# Renommer les fichiers
print("2. Renommage des fichiers (clair et maintenable):")
for old_name, new_name in to_rename.items():
    old_path = integration_dir / old_name
    new_path = integration_dir / new_name
    
    if old_path.exists():
        print(f"   ✅ {old_name}")
        print(f"      → {new_name}")
        old_path.rename(new_path)
    else:
        print(f"   ⊘ N'existe pas: {old_name}")

print()

# Lister les fichiers finaux
print("3. Fichiers d'intégration finaux:")
for f in sorted(integration_dir.glob("test_*.py")):
    size = f.stat().st_size
    test_count = f.read_text().count("def test_")
    print(f"   ✓ {f.name:<40} ({test_count:>3} tests, {size:>6} bytes)")

print()
print("=" * 70)
print("✅ RÉORGANISATION COMPLÈTE")
print("=" * 70)
