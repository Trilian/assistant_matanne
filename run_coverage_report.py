#!/usr/bin/env python3
"""
Générer un rapport de couverture et des statistiques de tests.
"""
import json
import subprocess
import sys
from pathlib import Path

workspace = Path("d:\\Projet_streamlit\\assistant_matanne")

print("Exécution de pytest avec rapport de couverture...")
print("Cela peut prendre quelques minutes...\n")

# Lancer pytest
result = subprocess.run(
    [
        "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=json",
        "--co-report=term-missing",
        "-q",
        "--tb=no"
    ],
    cwd=workspace,
    capture_output=True,
    text=True,
    timeout=600
)

# Afficher le résumé
output_lines = result.stdout.split('\n')
for line in output_lines[-30:]:
    if line.strip():
        print(line)

# Charger et afficher la couverture
coverage_file = workspace / ".coverage.json"
if coverage_file.exists():
    print("\n" + "="*100)
    print("RÉSUMÉ DE LA COUVERTURE")
    print("="*100)
    
    with open(coverage_file) as f:
        coverage = json.load(f)
    
    # Couverture globale
    summary = coverage.get('totals', {})
    covered = summary.get('covered_lines', 0)
    total = summary.get('num_statements', 0)
    pct = (covered / total * 100) if total > 0 else 0
    
    print(f"Couverture globale: {pct:.2f}% ({covered}/{total} lignes)")
    
    # Top 10 fichiers non couverts
    print("\nFichiers moins couverts:")
    files_coverage = []
    for file_path, data in coverage.get('files', {}).items():
        file_summary = data.get('summary', {})
        file_covered = file_summary.get('covered_lines', 0)
        file_total = file_summary.get('num_statements', 0)
        if file_total > 0:
            pct = (file_covered / file_total) * 100
            files_coverage.append((file_path, pct, file_covered, file_total))
    
    files_coverage.sort(key=lambda x: x[1])
    
    for file_path, pct, covered, total in files_coverage[:15]:
        clean_path = file_path.replace("\\", "/").split("src/")[-1]
        status = "✗" if pct < 50 else "⚠️" if pct < 80 else "✓"
        print(f"  {status} {clean_path:<60} {pct:>6.2f}%")

print(f"\nRapport JSON sauvegardé: .coverage.json")
