#!/usr/bin/env python3
"""Script pour ouvrir le rapport HTML de couverture une fois généré."""

import os
import time
import webbrowser
from pathlib import Path

html_file = Path(r"d:\Projet_streamlit\assistant_matanne\htmlcov\index.html")

print("⏳ Attente de la génération du rapport HTML...")
print(f"   Chemin attendu: {html_file}")

# Attendre que le fichier existe (max 5 min)
for i in range(300):  # 5 minutes
    if html_file.exists():
        print(f"\n✅ Rapport généré! ({html_file.stat().st_size} bytes)")
        time.sleep(1)  # Attendre que pytest finisse d'écrire
        
        # Ouvrir dans le navigateur
        url = f"file:///{html_file}"
        print(f"🌐 Ouverture dans le navigateur: {url}")
        webbrowser.open(url)
        print("✅ Rapport ouvert!")
        break
    
    if (i+1) % 10 == 0:
        print(f"   {i+1}s écoulées...")
    time.sleep(1)
else:
    print("\n❌ Rapport non généré après 5 minutes")
