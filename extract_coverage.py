#!/usr/bin/env python
"""Extraire les données de couverture du rapport HTML."""

import re
from pathlib import Path
from html.parser import HTMLParser

class CoverageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_summary = False
        self.coverage_data = {}
        
    def handle_data(self, data):
        if "%" in data and any(char.isdigit() for char in data):
            # Peut être une ligne de couverture
            parts = data.strip().split()
            if len(parts) >= 2:
                try:
                    percent = float(parts[-1].rstrip('%'))
                    # On a trouvé un pourcentage
                    print(f"Couverture trouvée: {data.strip()}")
                except:
                    pass

# Lire le rapport HTML
html_file = Path("htmlcov/index.html")
if html_file.exists():
    content = html_file.read_text(encoding='utf-8', errors='ignore')
    
    # Chercher la ligne de résumé
    match = re.search(r'<td class="summary">(\d+)%</td>', content)
    if match:
        percent = match.group(1)
        print(f"\n✅ Couverture Globale: {percent}%")
    
    # Chercher les lignes couvertes/manquantes
    for line in content.split('\n'):
        if '<td class="summary">' in line:
            print(f"Données trouvées: {line.strip()}")
            
    print("\n📊 Rapport HTML généré: htmlcov/index.html")
    print("Ouvrez dans un navigateur pour voir le détail complet!")
else:
    print("Rapport HTML non trouvé")
