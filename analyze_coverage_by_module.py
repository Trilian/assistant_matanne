#!/usr/bin/env python3
"""Analyser la couverture par module et compter les tests."""

import json
import os
import subprocess
from pathlib import Path
from collections import defaultdict

def get_coverage_by_module():
    """Extraire la couverture par module depuis coverage.json"""
    with open('coverage.json', 'r') as f:
        data = json.load(f)
    
    modules = defaultdict(lambda: {'covered': 0, 'total': 0})
    
    for filepath, info in data['files'].items():
        # Extraire le module (src/core -> core, src/domains/cuisine -> cuisine, etc.)
        if not filepath.startswith('src/'):
            continue
        
        parts = filepath.replace('\\', '/').split('/')
        if len(parts) < 3:
            continue
        
        # Déterminer le module principal
        if parts[1] == 'core':
            module = 'core'
        elif parts[1] == 'api':
            module = 'api'
        elif parts[1] == 'ui':
            module = 'ui'
        elif parts[1] == 'utils':
            module = 'utils'
        elif parts[1] == 'services':
            module = 'services'
        elif parts[1] == 'domains':
            if len(parts) >= 3:
                module = f'domains/{parts[2]}'
            else:
                module = 'domains'
        else:
            module = parts[1]
        
        summary = info['summary']
        modules[module]['covered'] += int(summary['covered_lines'])
        modules[module]['total'] += int(summary['num_statements'])
    
    return modules

def count_tests_per_module():
    """Compter les tests dans tests/ par module."""
    test_counts = defaultdict(int)
    
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Mapper le dossier test au module source
                rel_path = os.path.relpath(filepath, 'tests')
                parts = rel_path.split(os.sep)
                
                if parts[0] in ['api', 'core', 'ui', 'utils', 'services']:
                    module = parts[0]
                elif parts[0] == 'domains':
                    if len(parts) >= 2:
                        module = f'domains/{parts[1]}'
                    else:
                        module = 'domains'
                elif parts[0] in ['e2e', 'integration', 'models']:
                    module = 'integration'
                else:
                    module = 'other'
                
                # Compter les tests dans le fichier
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Compter les fonctions test_
                    count = content.count('def test_')
                    test_counts[module] += count
    
    return test_counts

def run_module_tests(module_path):
    """Exécuter les tests d'un module et compter les résultats."""
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', module_path, '-q', '--tb=no'],
            capture_output=True,
            text=True,
            timeout=60
        )
        # Parser la sortie pour extraire le nombre de tests
        for line in result.stdout.split('\n'):
            if 'passed' in line or 'failed' in line:
                return line.strip()
    except:
        pass
    return "N/A"

def main():
    print("=" * 80)
    print("ANALYSE DE COUVERTURE PAR MODULE")
    print("=" * 80)
    print()
    
    modules_coverage = get_coverage_by_module()
    modules_tests = count_tests_per_module()
    
    # Trier par couverture
    sorted_modules = sorted(
        modules_coverage.items(),
        key=lambda x: (x[1]['covered'] / x[1]['total'] * 100) if x[1]['total'] > 0 else 0,
        reverse=True
    )
    
    print(f"{'Module':<30} {'Coverage':<12} {'Lines':<20} {'Tests':<8}")
    print("-" * 70)
    
    total_covered = 0
    total_lines = 0
    
    for module, stats in sorted_modules:
        if stats['total'] == 0:
            continue
        
        pct = (stats['covered'] / stats['total'] * 100) if stats['total'] > 0 else 0
        lines_info = f"{stats['covered']}/{stats['total']}"
        test_count = modules_tests.get(module, 0)
        
        coverage_status = "✅" if pct >= 50 else "⚠️ " if pct >= 20 else "❌"
        
        print(f"{module:<30} {pct:>6.2f}% {coverage_status:<5} {lines_info:<20} {test_count:<8}")
        
        total_covered += stats['covered']
        total_lines += stats['total']
    
    print("-" * 70)
    if total_lines > 0:
        total_pct = (total_covered / total_lines * 100)
        print(f"{'TOTAL':<30} {total_pct:>6.2f}%       {total_covered}/{total_lines}")
    
    print()
    print("=" * 80)
    print("SYNTHÈSE PAR PHASE")
    print("=" * 80)
    
    phases = {
        'Phase API': ['api'],
        'Phase Core': ['core'],
        'Phase Domains Cuisine': ['domains/cuisine'],
        'Phase Domains Famille': ['domains/famille'],
        'Phase Domains Jeux': ['domains/jeux'],
        'Phase Domains Maison': ['domains/maison'],
        'Phase Domains Planning': ['domains/planning'],
        'Phase UI': ['ui'],
        'Phase Utils': ['utils'],
        'Phase Services': ['services'],
    }
    
    for phase_name, phase_modules in phases.items():
        phase_covered = 0
        phase_total = 0
        phase_tests = 0
        
        for module in phase_modules:
            if module in modules_coverage:
                stats = modules_coverage[module]
                phase_covered += stats['covered']
                phase_total += stats['total']
                phase_tests += modules_tests.get(module, 0)
        
        if phase_total > 0:
            pct = (phase_covered / phase_total * 100)
            status = "✅" if pct >= 50 else "⚠️ " if pct >= 20 else "❌"
            print(f"{phase_name:<30} {pct:>6.2f}% {status:<5} {phase_covered}/{phase_total:<10} Tests: {phase_tests}")

if __name__ == '__main__':
    main()
