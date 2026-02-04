#!/usr/bin/env python3
"""Script pour lire et afficher les métriques de couverture"""

import json
import os

coverage_file = r'd:\Projet_streamlit\assistant_matanne\coverage.json'

if os.path.exists(coverage_file):
    try:
        with open(coverage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        totals = data.get('totals', {})
        
        percent_covered = totals.get('percent_covered', 'N/A')
        covered_lines = totals.get('covered_lines', 'N/A')
        num_statements = totals.get('num_statements', 'N/A')
        
        print('=== MÉTRIQUES DE COUVERTURE TOTALES ===')
        print(f'Pourcentage de couverture (percent_covered): {percent_covered}%')
        print(f'Nombre de lignes couvertes (covered_lines): {covered_lines}')
        print(f'Nombre total de lignes (num_statements): {num_statements}')
    except json.JSONDecodeError:
        print("Erreur: Le fichier JSON n'est pas valide")
else:
    print(f"Erreur: Le fichier {coverage_file} n'existe pas")
