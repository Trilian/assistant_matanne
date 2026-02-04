# -*- coding: utf-8 -*-
"""Extract coverage metrics from coverage.json and save to file."""
import json
import os
import subprocess
import sys

os.chdir(r"d:\Projet_streamlit\assistant_matanne")

# Exécuter les tests avec couverture
result = subprocess.run(
    ["pytest", "tests/core/", "--cov=src/core", "--cov-report=json", "-q"],
    capture_output=True,
    text=True
)

# Ouvrir fichier de sortie
with open("coverage_summary_output.txt", "w", encoding="utf-8") as out:
    out.write(f"Tests terminés: code={result.returncode}\n\n")
    
    # Lire le fichier de couverture
    try:
        with open("coverage.json") as f:
            d = json.load(f)
        
        if not d or not d.get("files"):
            out.write("coverage.json est vide ou n'a pas de fichiers\n")
            sys.exit(1)
        
        core_files = {
            k.split("\\")[-1]: v["summary"]["percent_covered"] 
            for k, v in d["files"].items() 
            if "core" in k
        }
        
        out.write("=" * 50 + "\n")
        out.write("COUVERTURE DES FICHIERS src/core/\n")
        out.write("=" * 50 + "\n\n")
        
        sorted_files = sorted(core_files.items(), key=lambda x: x[1], reverse=True)
        
        for name, cov in sorted_files:
            status = "OK" if cov >= 80 else "FAIBLE"
            out.write(f"[{status}] {name}: {cov:.1f}%\n")
        
        out.write("\n" + "=" * 50 + "\n")
        ok_count = sum(1 for _, c in core_files.items() if c >= 80)
        total_count = len(core_files)
        out.write(f"Modules >= 80%: {ok_count}/{total_count}\n")
        
    except FileNotFoundError:
        out.write("coverage.json non trouvé\n")
    except json.JSONDecodeError as e:
        out.write(f"coverage.json invalide: {e}\n")
    except Exception as e:
        out.write(f"Erreur: {e}\n")
