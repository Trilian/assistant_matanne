#!/usr/bin/env python3
"""
Script pour analyser l'état actuel des tests et couverture après les ajouts.
"""
import subprocess
import json
import os
from pathlib import Path
from collections import defaultdict

workspace = Path("d:\\Projet_streamlit\\assistant_matanne")

print("="*100)
print("ANALYSE POST-CRÉATION DE TESTS")
print("="*100)

# Compter les fichiers de tests
tests_dir = workspace / "tests"
test_files = list(tests_dir.rglob("test_*.py"))

print(f"\n✓ Total fichiers de tests: {len(test_files)}")

# Compter par dossier
tests_by_folder = defaultdict(list)
for f in test_files:
    rel_path = f.relative_to(tests_dir)
    folder = str(rel_path.parent)
    if folder == '.':
        folder = 'root'
    tests_by_folder[folder].append(f)

print("\nRépartition par dossier:")
for folder in sorted(tests_by_folder.keys()):
    count = len(tests_by_folder[folder])
    print(f"  {folder}: {count} fichiers")

# Lancer pytest pour obtenir les nombres
print("\n" + "-"*100)
print("Exécution des tests...")
print("-"*100 + "\n")

result = subprocess.run(
    ["pytest", "tests/", "-q", "--tb=no", "--co"],
    cwd=workspace,
    capture_output=True,
    text=True,
    timeout=30
)

# Compter les tests collectés
output = result.stdout
lines = output.split('\n')

test_count = 0
for line in lines:
    if 'test session starts' in line or 'error' in line.lower():
        continue
    if 'test' in line.lower() and '::test_' in line:
        test_count += 1

# Chercher la ligne de résumé
for line in lines[-20:]:
    if 'selected' in line or 'error' in line:
        print(line)

# Créer un rapport structuré
report = {
    "timestamp": Path.cwd().stat(),
    "test_files_count": len(test_files),
    "tests_by_folder": {k: len(v) for k, v in tests_by_folder.items()},
    "newly_created": {
        "core/test_models_batch_cooking.py": "Tests pour BatchCooking model",
        "core/test_ai_modules.py": "Tests pour AI client/parser/rate_limit",
        "core/test_models_comprehensive.py": "Tests pour Articles, Famille, Recettes, Planning",
        "services/test_additional_services.py": "Tests pour Weather, Push, Garmin, Calendar, Realtime",
        "ui/test_components_additional.py": "Tests pour UI components",
        "utils/test_utilities_comprehensive.py": "Tests pour formatters/validators/helpers",
        "domains/test_logic_comprehensive.py": "Tests pour logiques domaines",
    }
}

# Sauvegarder le rapport
report_file = workspace / "TESTS_STATUS_POST_CREATION.json"
with open(report_file, "w") as f:
    json.dump(report, f, indent=2)

print(f"\n✓ Rapport sauvegardé: {report_file.relative_to(workspace)}")
print(f"✓ Fichiers de tests créés: {len(report['newly_created'])}")

# Afficher un résumé
print("\n" + "="*100)
print("RÉSUMÉ DES CRÉATIONS")
print("="*100 + "\n")

for file, desc in report["newly_created"].items():
    print(f"✓ {file}")
    print(f"  └─ {desc}\n")

print("\n" + "="*100)
print("PROCHAINES ÉTAPES")
print("="*100)
print("""
1. Exécuter les tests complets: pytest tests/ --cov=src
2. Analyser les résultats de couverture
3. Corriger les tests échoués
4. Itérer jusqu'à atteindre:
   - 80% de couverture globale
   - 95% de pass rate
""")
