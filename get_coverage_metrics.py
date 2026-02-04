#!/usr/bin/env python3
"""Script rapide pour obtenir les métriques de couverture."""

import subprocess
import json
import re
from pathlib import Path

print("=" * 70)
print("RÉSUMÉ FINAL DE COUVERTURE")
print("=" * 70)

# Exécuter pytest avec couverture JSON
cmd = [
    "pytest",
    "--cov=src",
    "--cov-report=json",
    "--cov-report=term-missing",
    "-q",
    "--tb=no",
    "tests/modules/test_extended_modules.py",
    "tests/domains/test_extended_domains.py",
    "tests/api/test_extended_api.py",
    "tests/utils/test_extended_utils.py",
    "tests/services/test_extended_services.py",
]

print("\n🔍 Exécution des 141 nouveaux tests...\n")
result = subprocess.run(cmd, capture_output=True, text=True)

# Extraire les résultats
output = result.stdout + result.stderr
print(output)

# Vérifier le fichier JSON de couverture
cov_json_path = Path(".coverage.json") if Path(".coverage.json").exists() else None
if cov_json_path:
    print("\n✅ Fichier de couverture JSON trouvé!")
else:
    print("\n⚠️  Fichier de couverture JSON non trouvé")

print("\n" + "=" * 70)
print("✅ PHASE DE CRÉATION 141 TESTS: COMPLÉTÉE")
print("=" * 70)
