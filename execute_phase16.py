#!/usr/bin/env python3
"""
Script pour exécuter Phase 16 et générer un rapport de couverture détaillé.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

def run_command(cmd, description):
    """Exécute une commande et retourne le résultat."""
    print(f"\n{'='*60}")
    print(f"Exécution: {description}")
    print(f"Commande: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode

def extract_test_results(returncode):
    """Extrait les résultats des tests."""
    # Pour une approche plus robuste, on pourrait parser la sortie pytest
    # Ici, on utilise le returncode comme indicateur
    return returncode

def read_coverage_json(coverage_file="coverage.json"):
    """Lit le fichier coverage.json et extrait les données."""
    if not os.path.exists(coverage_file):
        print(f"⚠️  {coverage_file} non trouvé")
        return None
    
    try:
        with open(coverage_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {coverage_file}: {e}")
        return None

def categorize_files(files_data):
    """
    Catégorise les fichiers par module.
    Retourne un dictionnaire {module: {fichiers et couverture}}
    """
    categories = defaultdict(lambda: {
        'files': [],
        'total_coverage': 0,
        'file_count': 0
    })
    
    for filepath, file_info in files_data.items():
        if not filepath.startswith('src/'):
            continue
        
        # Déterminer la catégorie
        if 'core/' in filepath:
            category = 'core'
        elif 'api/' in filepath:
            category = 'api'
        elif 'app.py' in filepath:
            category = 'app.py'
        elif 'utils/' in filepath:
            category = 'utils'
        elif 'domains/' in filepath:
            category = 'domains'
        elif 'ui/' in filepath:
            category = 'ui'
        elif 'services/' in filepath:
            category = 'services'
        else:
            category = 'other'
        
        # Extraire la couverture
        coverage_percent = 0
        if 'summary' in file_info:
            summary = file_info['summary']
            if 'percent_covered' in summary:
                coverage_percent = summary['percent_covered']
        
        categories[category]['files'].append({
            'path': filepath,
            'coverage': coverage_percent
        })
        categories[category]['file_count'] += 1
        categories[category]['total_coverage'] += coverage_percent
    
    # Calculer la moyenne pour chaque catégorie
    for category in categories:
        if categories[category]['file_count'] > 0:
            categories[category]['total_coverage'] = (
                categories[category]['total_coverage'] / 
                categories[category]['file_count']
            )
    
    return categories

def generate_report(phase16_returncode, coverage_data):
    """Génère le rapport final."""
    report = []
    report.append("="*70)
    report.append("PHASE 16 - RAPPORT D'EXÉCUTION")
    report.append("="*70)
    
    # Résultats des tests Phase 16
    report.append("\n📋 RÉSULTATS DES TESTS PHASE 16:")
    report.append("-" * 70)
    if phase16_returncode == 0:
        report.append("✅ Phase 16 tests: PASSED (returncode: 0)")
    else:
        report.append(f"❌ Phase 16 tests: FAILED (returncode: {phase16_returncode})")
    
    # Couverture combinée
    report.append("\n📊 COUVERTURE COMBINÉE:")
    report.append("-" * 70)
    
    if coverage_data and 'totals' in coverage_data:
        total_percent = coverage_data['totals'].get('percent_covered', 0)
        report.append(f"Couverture totale: {total_percent:.2f}%")
    else:
        total_percent = 0
        report.append("⚠️  Données de couverture non disponibles")
    
    # Décomposition par module
    report.append("\n📈 DÉCOMPOSITION PAR MODULE:")
    report.append("-" * 70)
    
    if coverage_data and 'files' in coverage_data:
        categories = categorize_files(coverage_data['files'])
        
        # Ordre d'affichage préféré
        module_order = ['core', 'app.py', 'ui', 'services', 'domains', 'api', 'utils', 'other']
        
        for module in module_order:
            if module in categories:
                cat_data = categories[module]
                avg_coverage = cat_data['total_coverage']
                file_count = cat_data['file_count']
                
                status = "✅" if avg_coverage >= 80 else "⚠️ " if avg_coverage >= 70 else "❌"
                report.append(f"\n{status} {module.upper()}: {avg_coverage:.2f}% ({file_count} fichiers)")
                
                # Top 3 fichiers pour chaque catégorie
                sorted_files = sorted(
                    cat_data['files'], 
                    key=lambda x: x['coverage'], 
                    reverse=True
                )
                for i, file_info in enumerate(sorted_files[:3], 1):
                    report.append(f"   {i}. {file_info['path']}: {file_info['coverage']:.2f}%")
    
    report.append("\n" + "="*70)
    report.append("FIN DU RAPPORT")
    report.append("="*70)
    
    return "\n".join(report)

def main():
    """Fonction principale."""
    print("\n🚀 DÉMARRAGE DE L'EXÉCUTION PHASE 16\n")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('pyproject.toml'):
        print("❌ Erreur: Execute ce script depuis la racine du projet")
        sys.exit(1)
    
    # 1. Exécuter Phase 16
    print("\n[1/3] Exécution des tests Phase 16...")
    phase16_cmd = [
        "pytest",
        "tests/integration/test_phase_16_expanded.py",
        "-v",
        "--tb=short"
    ]
    phase16_returncode = run_command(phase16_cmd, "Tests Phase 16")
    
    # 2. Exécuter tests combinés avec couverture
    print("\n[2/3] Exécution des tests combinés avec couverture...")
    coverage_cmd = [
        "pytest",
        "tests/services/test_services_basic.py",
        "tests/ui/",
        "tests/modules/",
        "-v",
        "--cov=src",
        "--cov-report=json",
        "--tb=short"
    ]
    coverage_returncode = run_command(coverage_cmd, "Tests combinés avec couverture")
    
    # 3. Lire coverage.json et extraire les données
    print("\n[3/3] Traitement des données de couverture...")
    coverage_data = read_coverage_json("coverage.json")
    
    # 4. Générer le rapport
    report = generate_report(phase16_returncode, coverage_data)
    
    # 5. Sauvegarder dans phase16_results.txt
    output_file = "phase16_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Rapport sauvegardé dans: {output_file}")
    print("\n" + report)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
