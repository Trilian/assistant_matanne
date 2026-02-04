#!/usr/bin/env python3
import json
import sys

# Essayer de lire coverage.json en premier
try:
    with open(r'd:\Projet_streamlit\assistant_matanne\coverage.json', 'r') as f:
        data = json.load(f)
    
    # Rechercher les totals
    if 'totals' in data:
        totals = data['totals']
    else:
        # Si pas de totals au niveau racine, calcul à partir de coverage_analysis.json
        with open(r'd:\Projet_streamlit\assistant_matanne\coverage_analysis.json', 'r') as f:
            analysis = json.load(f)
        
        print("=== MÉTRIQUES DE COUVERTURE (depuis coverage_analysis.json) ===")
        print(f"Pourcentage de couverture moyen (average_coverage): {analysis['average_coverage']:.2f}%")
        print(f"Nombre de fichiers total: {analysis['total_files']}")
        print(f"Nombre de fichiers testés: {analysis['tested_files']}")
        print(f"Nombre de fichiers avec couverture > 80%: {analysis['files_over_80']}")
        sys.exit(0)
    
    print("=== MÉTRIQUES DE COUVERTURE TOTALES ===")
    print(f"Pourcentage de couverture (percent_covered): {totals.get('percent_covered', 'N/A')}%")
    print(f"Nombre de lignes couvertes (covered_lines): {totals.get('covered_lines', 'N/A')}")
    print(f"Nombre total de lignes (num_statements): {totals.get('num_statements', 'N/A')}")
    
except json.JSONDecodeError as e:
    print(f"Erreur JSON: {e}")
except Exception as e:
    print(f"Erreur: {e}")
