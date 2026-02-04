#!/usr/bin/env python3
"""
Analyse complète de la couverture de tests et identification des gaps.
"""
import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

def get_python_files(directory: str) -> List[str]:
    """Récupère tous les fichiers Python d'un répertoire."""
    files = []
    for root, dirs, filenames in os.walk(directory):
        # Ignorer __pycache__ et .pytest_cache
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', '__pycache__']]
        for filename in filenames:
            if filename.endswith('.py') and not filename.startswith('__'):
                rel_path = os.path.relpath(os.path.join(root, filename), directory)
                files.append(rel_path)
    return sorted(files)

def analyze_structure() -> Dict:
    """Analyse la structure src/ vs tests/."""
    workspace = "d:\\Projet_streamlit\\assistant_matanne"
    src_dir = os.path.join(workspace, "src")
    tests_dir = os.path.join(workspace, "tests")
    
    src_files = get_python_files(src_dir)
    test_files = get_python_files(tests_dir)
    
    # Analyse par dossier
    src_by_folder = defaultdict(list)
    test_by_folder = defaultdict(list)
    
    for f in src_files:
        folder = f.split('\\')[0] if '\\' in f else 'root'
        src_by_folder[folder].append(f)
    
    for f in test_files:
        folder = f.split('\\')[0] if '\\' in f else 'root'
        test_by_folder[folder].append(f)
    
    # Trouver les fichiers manquants
    missing_tests = {}
    for folder, files in src_by_folder.items():
        if folder not in test_by_folder:
            missing_tests[folder] = files
        else:
            test_files_set = {os.path.basename(f).replace('.py', '') 
                             for f in test_by_folder[folder]}
            missing = []
            for f in files:
                test_name = 'test_' + os.path.basename(f).replace('.py', '')
                if test_name not in test_files_set and os.path.basename(f) != '__init__.py':
                    missing.append(f)
            if missing:
                missing_tests[folder] = missing
    
    return {
        'src_files': src_files,
        'test_files': test_files,
        'src_by_folder': dict(src_by_folder),
        'test_by_folder': dict(test_by_folder),
        'missing_tests': missing_tests
    }

def run_coverage_analysis() -> Dict:
    """Lance pytest avec couverture et collecte les résultats."""
    workspace = "d:\\Projet_streamlit\\assistant_matanne"
    
    # Lancer pytest avec couverture
    cmd = [
        "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=json",
        "--cov-report=term-missing",
        "--tb=short",
        "-v"
    ]
    
    print("Lancement de pytest avec couverture...")
    result = subprocess.run(
        cmd,
        cwd=workspace,
        capture_output=True,
        text=True
    )
    
    # Charger le rapport JSON
    coverage_file = os.path.join(workspace, ".coverage.json")
    coverage_data = {}
    
    if os.path.exists(coverage_file):
        try:
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
        except:
            pass
    
    return {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode,
        'coverage_data': coverage_data
    }

def calculate_coverage_per_module(coverage_data: Dict) -> Dict:
    """Calcule la couverture par module."""
    modules = defaultdict(lambda: {'lines': 0, 'covered': 0, 'percentage': 0})
    
    if 'files' in coverage_data:
        for file_path, data in coverage_data['files'].items():
            # Extraire le module racine
            parts = file_path.replace('\\', '/').split('/src/')[1].split('/')
            module = parts[0] if parts else 'unknown'
            
            summary = data.get('summary', {})
            lines = summary.get('num_statements', 0)
            covered = summary.get('covered_lines', 0)
            
            modules[module]['lines'] += lines
            modules[module]['covered'] += covered
    
    # Calculer les pourcentages
    for module, data in modules.items():
        if data['lines'] > 0:
            data['percentage'] = round((data['covered'] / data['lines']) * 100, 2)
    
    return dict(modules)

def analyze_test_results(output: str) -> Dict:
    """Parse le résultat des tests pour extraire pass rate."""
    lines = output.split('\n')
    summary = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0}
    
    for line in lines:
        if 'passed' in line and ('failed' in line or 'error' in line or 'skipped' in line):
            # Ligne de résumé final
            import re
            passed = re.findall(r'(\d+) passed', line)
            failed = re.findall(r'(\d+) failed', line)
            errors = re.findall(r'(\d+) error', line)
            skipped = re.findall(r'(\d+) skipped', line)
            
            if passed:
                summary['passed'] = int(passed[0])
            if failed:
                summary['failed'] = int(failed[0])
            if errors:
                summary['errors'] = int(errors[0])
            if skipped:
                summary['skipped'] = int(skipped[0])
            
            summary['total'] = summary['passed'] + summary['failed'] + summary['errors']
    
    if summary['total'] > 0:
        summary['pass_rate'] = round((summary['passed'] / summary['total']) * 100, 2)
    else:
        summary['pass_rate'] = 0
    
    return summary

def generate_report(structure: Dict, coverage_result: Dict):
    """Génère un rapport complet."""
    print("\n" + "="*80)
    print("ANALYSE DE COUVERTURE DE TESTS - RAPPORT COMPLET")
    print("="*80)
    
    # Section 1: Structure
    print("\n1. STRUCTURE SRC/ vs TESTS/")
    print("-" * 80)
    
    src_folders = set(structure['src_by_folder'].keys())
    test_folders = set(structure['test_by_folder'].keys())
    
    print(f"Dossiers en src/: {sorted(src_folders)}")
    print(f"Dossiers en tests/: {sorted(test_folders)}")
    
    missing_folders = src_folders - test_folders
    if missing_folders:
        print(f"\n⚠️  Dossiers sans tests: {missing_folders}")
    
    extra_folders = test_folders - src_folders
    if extra_folders:
        print(f"✓ Dossiers de tests supplémentaires: {extra_folders}")
    
    # Section 2: Fichiers manquants
    print("\n2. FICHIERS MANQUANTS")
    print("-" * 80)
    
    if structure['missing_tests']:
        total_missing = sum(len(v) for v in structure['missing_tests'].values())
        print(f"Total: {total_missing} fichiers sans tests correspondants\n")
        
        for folder, files in sorted(structure['missing_tests'].items()):
            print(f"  {folder}/ ({len(files)} fichiers):")
            for f in sorted(files)[:5]:  # Afficher max 5
                print(f"    - {f}")
            if len(files) > 5:
                print(f"    ... et {len(files) - 5} autres")
    else:
        print("✓ Tous les fichiers ont des tests correspondants")
    
    # Section 3: Résultats des tests
    print("\n3. RÉSULTATS DES TESTS")
    print("-" * 80)
    
    if coverage_result['returncode'] == 0:
        print("✓ Tous les tests sont passés")
    else:
        print(f"⚠️  Certains tests ont échoué (code retour: {coverage_result['returncode']})")
    
    # Parser les résultats
    test_summary = analyze_test_results(coverage_result['stdout'])
    if test_summary['total'] > 0:
        print(f"\nRésultats:")
        print(f"  Passés: {test_summary['passed']}/{test_summary['total']}")
        print(f"  Échoués: {test_summary['failed']}")
        print(f"  Erreurs: {test_summary['errors']}")
        print(f"  Ignorés: {test_summary['skipped']}")
        print(f"  Pass rate: {test_summary['pass_rate']}%")
    
    # Section 4: Couverture par module
    print("\n4. COUVERTURE PAR MODULE")
    print("-" * 80)
    
    modules = calculate_coverage_per_module(coverage_result['coverage_data'])
    
    if modules:
        print(f"{'Module':<20} {'Couverture':<20} {'Lignes':<15}")
        print("-" * 55)
        
        sorted_modules = sorted(modules.items(), key=lambda x: x[1]['percentage'], reverse=True)
        for module, data in sorted_modules:
            status = "✓" if data['percentage'] >= 80 else "⚠️"
            print(f"{module:<20} {data['percentage']:>6.2f}% {status:<3} {data['covered']}/{data['lines']} lignes")
        
        # Statistiques globales
        total_lines = sum(m['lines'] for m in modules.values())
        total_covered = sum(m['covered'] for m in modules.values())
        global_coverage = (total_covered / total_lines * 100) if total_lines > 0 else 0
        
        print("-" * 55)
        print(f"{'GLOBAL':<20} {global_coverage:>6.2f}%")
    
    # Section 5: Recommandations
    print("\n5. RECOMMANDATIONS")
    print("-" * 80)
    
    recommendations = []
    
    # Modules sous 80%
    for module, data in sorted(modules.items(), key=lambda x: x[1]['percentage']):
        if data['percentage'] < 80:
            gap = 80 - data['percentage']
            recommendations.append(
                f"  - {module}: {gap:.2f}% de couverture manquante ({int(gap/100*data['lines'])} lignes)"
            )
    
    # Fichiers manquants
    if structure['missing_tests']:
        recommendations.append(f"  - Créer {sum(len(v) for v in structure['missing_tests'].values())} fichiers de tests")
    
    if recommendations:
        for rec in sorted(recommendations):
            print(rec)
    else:
        print("✓ La couverture est bonne, continuez comme ça!")
    
    return test_summary, modules

if __name__ == "__main__":
    print("Analyse en cours...")
    
    # Étape 1: Analyser la structure
    structure = analyze_structure()
    
    # Étape 2: Lancer l'analyse de couverture
    coverage_result = run_coverage_analysis()
    
    # Étape 3: Générer le rapport
    test_summary, modules = generate_report(structure, coverage_result)
    
    # Sauvegarder le rapport détaillé
    report = {
        'structure': {
            'src_files_count': len(structure['src_files']),
            'test_files_count': len(structure['test_files']),
            'missing_test_count': sum(len(v) for v in structure['missing_tests'].values()),
        },
        'test_results': test_summary,
        'coverage_by_module': modules,
        'missing_tests': structure['missing_tests']
    }
    
    with open(os.path.join("d:\\Projet_streamlit\\assistant_matanne", "ANALYSIS_TEST_COVERAGE.json"), 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Rapport détaillé sauvegardé dans ANALYSIS_TEST_COVERAGE.json")
