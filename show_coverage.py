import json

# Lire coverage.json pour les métriques totales
try:
    with open('coverage.json', 'r') as f:
        coverage_data = json.load(f)
    
    # Vérifier s'il y a une section totals
    if 'totals' in coverage_data:
        totals = coverage_data['totals']
        print("MÉTRIQUES TOTALES DE COUVERTURE:")
        print(f"1. Pourcentage de couverture: {totals['percent_covered']:.2f}%")
        print(f"2. Nombre de lignes couvertes: {totals['covered_lines']}")
        print(f"3. Nombre total de lignes: {totals['num_statements']}")
    else:
        # Rechercher les données au niveau fichier
        total_covered = 0
        total_statements = 0
        
        for filepath, filedata in coverage_data.get('files', {}).items():
            summary = filedata.get('summary', {})
            total_covered += summary.get('covered_lines', 0)
            total_statements += summary.get('num_statements', 0)
        
        percent = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        print("MÉTRIQUES TOTALES DE COUVERTURE (calculées):")
        print(f"1. Pourcentage de couverture: {percent:.2f}%")
        print(f"2. Nombre de lignes couvertes: {total_covered}")
        print(f"3. Nombre total de lignes: {total_statements}")
        
except Exception as e:
    print(f"Erreur: {e}")
    # Fallback sur coverage_analysis.json
    try:
        with open('coverage_analysis.json', 'r') as f:
            analysis = json.load(f)
        
        print("MÉTRIQUES DEPUIS ANALYSE DE COUVERTURE:")
        print(f"1. Pourcentage de couverture moyen: {analysis['average_coverage']:.2f}%")
        print(f"2. Nombre de fichiers testés: {analysis['tested_files']}")
        print(f"3. Nombre total de fichiers: {analysis['total_files']}")
    except Exception as e2:
        print(f"Erreur fallback: {e2}")
