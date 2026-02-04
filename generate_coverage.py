#!/usr/bin/env python3
"""
Script direct pour générer rapport couverture
Contourne les problèmes de terminal PowerShell
"""

import subprocess
import sys
import os

os.chdir(r"d:\Projet_streamlit\assistant_matanne")

print("🔄 Exécution de pytest avec couverture...")
print("=" * 60)

# Lancer pytest avec couverture
result = subprocess.run([
    sys.executable, "-m", "pytest", 
    "tests/", 
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "-q",
    "--tb=no",
    "-x"  # Stop au premier échec pour aller plus vite
], capture_output=False, text=True)

print("=" * 60)

# Vérifier le rapport
from pathlib import Path
html_file = Path("htmlcov/index.html")

if html_file.exists():
    print(f"\n✅ RAPPORT GÉNÉRÉ!")
    print(f"   📄 {html_file}")
    print(f"   💾 Taille: {html_file.stat().st_size / 1024:.1f} KB")
    
    # Ouvrir dans le navigateur
    import webbrowser
    url = f"file:///{html_file.resolve()}"
    print(f"\n🌐 Ouverture: {url}")
    webbrowser.open(url)
else:
    print(f"\n❌ Rapport non généré")
    print(f"   Expected: {html_file}")
    sys.exit(1)

sys.exit(result.returncode)
