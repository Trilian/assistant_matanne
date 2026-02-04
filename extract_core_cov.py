# -*- coding: utf-8 -*-
"""Extract coverage metrics from coverage.json."""
import json
import os
import subprocess

os.chdir(r"d:\Projet_streamlit\assistant_matanne")

# Exécuter les tests avec couverture
print("Exécution des tests avec couverture...")
result = subprocess.run(
    ["pytest", "tests/core/", "--cov=src/core", "--cov-report=json", "-q"],
    capture_output=True,
    text=True
)
print(f"Tests terminés: code={result.returncode}")

# Lire le fichier de couverture
try:
    with open("coverage.json") as f:
        d = json.load(f)
    
    core_files = {k.split("\\")[-1]: v["summary"]["percent_covered"] for k, v in d["files"].items() if "core" in k}
    
    print("\n" + "=" * 50)
    print("COUVERTURE DES FICHIERS src/core/")
    print("=" * 50 + "\n")
    
    sorted_files = sorted(core_files.items(), key=lambda x: x[1], reverse=True)
    
    for name, cov in sorted_files:
        status = "✓" if cov >= 80 else "✗"
        print(f"{status} {name}: {cov:.1f}%")
    
    print("\n" + "=" * 50)
    ok_count = sum(1 for _, c in core_files.items() if c >= 80)
    total_count = len(core_files)
    print(f"Modules >= 80%: {ok_count}/{total_count}")
    
except FileNotFoundError:
    print("coverage.json non trouvé")
except json.JSONDecodeError:
    print("coverage.json vide ou invalide")
