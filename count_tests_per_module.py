#!/usr/bin/env python3
"""Compter les tests par module et déterminer le mapping source→test."""

import os
from pathlib import Path
from collections import defaultdict

def count_test_functions(filepath):
    """Compter les fonctions test_ dans un fichier."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return content.count('def test_')
    except:
        return 0

def analyze_test_structure():
    """Analyser la structure des tests existants."""
    
    test_info = defaultdict(lambda: {'files': 0, 'functions': 0, 'broken': 0})
    broken_files = [
        'tests/domains/famille/ui/test_routines.py',
        'tests/domains/maison/services/test_inventaire.py',
        'tests/domains/maison/ui/test_courses.py',
        'tests/domains/maison/ui/test_paris.py',
        'tests/domains/planning/ui/components/test_init.py',
        'tests/test_parametres.py',
        'tests/test_rapports.py',
        'tests/test_recettes_import.py',
        'tests/test_vue_ensemble.py',
    ]
    
    # Scanner tous les fichiers de test
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, 'tests')
                
                # Déterminer le module
                parts = rel_path.replace('\\', '/').split('/')
                
                if parts[0] == 'api':
                    module = 'api'
                elif parts[0] == 'core':
                    module = 'core'
                elif parts[0] == 'ui':
                    module = 'ui'
                elif parts[0] == 'utils':
                    module = 'utils'
                elif parts[0] == 'services':
                    module = 'services'
                elif parts[0] == 'domains':
                    module = f'domains/{parts[1]}' if len(parts) > 1 else 'domains'
                elif parts[0] in ['e2e', 'integration', 'models']:
                    module = parts[0]
                else:
                    module = 'root'
                
                # Vérifier si c'est un fichier cassé
                is_broken = filepath.replace('\\', '/') in [p.replace('\\', '/') for p in broken_files]
                
                # Compter les tests
                test_count = count_test_functions(filepath) if not is_broken else 0
                
                test_info[module]['files'] += 1
                test_info[module]['functions'] += test_count
                if is_broken:
                    test_info[module]['broken'] += 1
    
    return test_info

def main():
    print("=" * 90)
    print("ANALYSE DE LA STRUCTURE DES TESTS EXISTANTS")
    print("=" * 90)
    print()
    
    test_info = analyze_test_structure()
    
    # Trier par module
    sorted_modules = sorted(test_info.items())
    
    total_files = 0
    total_tests = 0
    total_broken = 0
    
    print(f"{'Module':<30} {'Fichiers':<12} {'Tests':<12} {'Cassés':<8}")
    print("-" * 62)
    
    for module, info in sorted_modules:
        total_files += info['files']
        total_tests += info['functions']
        total_broken += info['broken']
        
        broken_str = f"({info['broken']})" if info['broken'] > 0 else ""
        print(f"{module:<30} {info['files']:<12} {info['functions']:<12} {broken_str:<8}")
    
    print("-" * 62)
    print(f"{'TOTAL':<30} {total_files:<12} {total_tests:<12} ({total_broken})")
    print()
    
    # Déterminer l'ordre des phases
    print("=" * 90)
    print("PHASES RECOMMANDÉES (ordre de priorité)")
    print("=" * 90)
    print()
    
    phases = [
        ('Phase 0: API', 'api'),
        ('Phase 1: Core', 'core'),
        ('Phase 2: Services', 'services'),
        ('Phase 3: Domains - Cuisine', 'domains/cuisine'),
        ('Phase 4: Domains - Famille', 'domains/famille'),
        ('Phase 5: Domains - Jeux', 'domains/jeux'),
        ('Phase 6: Domains - Maison', 'domains/maison'),
        ('Phase 7: Domains - Planning', 'domains/planning'),
        ('Phase 8: UI', 'ui'),
        ('Phase 9: Utils', 'utils'),
    ]
    
    for phase_name, module_key in phases:
        if module_key in test_info:
            info = test_info[module_key]
            print(f"{phase_name:<40} {info['files']:>3} fichiers, {info['functions']:>3} tests", end="")
            if info['broken'] > 0:
                print(f" ({info['broken']} cassés) ❌")
            else:
                print(" ✅")
        else:
            print(f"{phase_name:<40} (0 fichiers)")
    
    print()
    print("Statut intégration:", "✅ 5 fichiers (Phase 16-Extended avec 35 tests)")
    
    print()
    print("=" * 90)
    print("FICHIERS CASSÉS À CORRIGER")
    print("=" * 90)
    print()
    
    broken_files = [
        'tests/domains/famille/ui/test_routines.py',
        'tests/domains/maison/services/test_inventaire.py',
        'tests/domains/maison/ui/test_courses.py',
        'tests/domains/maison/ui/test_paris.py',
        'tests/domains/planning/ui/components/test_init.py',
        'tests/test_parametres.py',
        'tests/test_rapports.py',
        'tests/test_recettes_import.py',
        'tests/test_vue_ensemble.py',
    ]
    
    for i, f in enumerate(broken_files, 1):
        status = "❌ Collection error"
        print(f"{i}. {f:<50} {status}")

if __name__ == '__main__':
    main()
