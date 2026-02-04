# -*- coding: utf-8 -*-
"""Script pour afficher la couverture des fichiers core."""
import subprocess
import json
import os

os.chdir(r"d:\Projet_streamlit\assistant_matanne")

# Exécuter les tests avec couverture
result = subprocess.run(
    ["pytest", "tests/core/", "--cov=src/core", "--cov-report=json", "-q"],
    capture_output=True,
    text=True
)

print("=" * 60)
print(f"Tests terminés avec code: {result.returncode}")
print("=" * 60)

# Lire le fichier de couverture
if os.path.exists("coverage.json"):
    with open("coverage.json") as f:
        d = json.load(f)
    
    core_files = {k: v['summary']['percent_covered'] for k, v in d['files'].items() if 'core' in k}
    
    print("\nCouverture des fichiers src/core/:")
    print("-" * 40)
    for name, cov in sorted(core_files.items(), key=lambda x: x[1], reverse=True):
        short = name.replace('src\\core\\', '').replace('src/core/', '')
        status = "✓" if cov >= 80 else "✗"
        print(f"{status} {short}: {cov:.1f}%")
    
    total = d.get('totals', {}).get('percent_covered', 0)
    print("-" * 40)
    print(f"TOTAL: {total:.1f}%")
else:
    print("Fichier coverage.json non trouvé")
    print("STDOUT:", result.stdout[-500:])
    print("STDERR:", result.stderr[-500:])
