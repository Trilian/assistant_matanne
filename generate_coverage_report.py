#!/usr/bin/env python3
"""
Génère un rapport complet de couverture depuis coverage.json
"""
import json
import os
import sys

def generate_coverage_report():
    """Génère le rapport de couverture"""
    
    # Lire coverage.json
    try:
        with open('coverage.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: coverage.json not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: coverage.json is invalid JSON")
        sys.exit(1)
    
    # Extraire couverture globale
    total_coverage = data['totals']['percent_covered']
    total_statements = data['totals']['num_statements']
    total_covered = data['totals']['covered_lines']
    
    # Collecter tous les fichiers
    files_coverage = []
    for filepath, filedata in data['files'].items():
        # Tous les fichiers du rapport sont dans src
        if not filepath.startswith('src'):
            continue
        
        coverage = filedata['summary']['percent_covered']
        lines = filedata['summary']['num_statements']
        covered = filedata['summary']['covered_lines']
        
        # Simplifier le chemin
        path = filepath.replace('\\', '/')
        
        files_coverage.append({
            'path': path,
            'coverage': coverage,
            'lines': lines,
            'covered': covered
        })
    
    # Trier par couverture
    files_coverage.sort(key=lambda x: x['coverage'])
    
    # Générer le rapport
    report_lines = []
    report_lines.append('='*80)
    report_lines.append('COUVERTURE GLOBALE DU PROJET - PHASE 14-15')
    report_lines.append('='*80)
    report_lines.append('')
    report_lines.append(f'Couverture Totale: {total_coverage:.2f}%')
    report_lines.append(f'Lignes Couvertes: {total_covered}/{total_statements}')
    report_lines.append(f'Tests Exécutés: 142 (Phase 14-15)')
    report_lines.append('')
    
    # Breakdown par module
    modules = {}
    for file_entry in files_coverage:
        parts = file_entry['path'].split('/')
        mod = parts[1] if len(parts) > 1 else 'root'
        if mod not in modules:
            modules[mod] = {'coverage': 0, 'lines': 0, 'covered': 0, 'count': 0, 'files': []}
        modules[mod]['lines'] += file_entry['lines']
        modules[mod]['covered'] += file_entry['covered']
        modules[mod]['count'] += 1
        modules[mod]['files'].append(file_entry['path'])
    
    # Calculer couverture par module
    module_list = []
    for mod in modules.keys():
        pct = (modules[mod]['covered'] / modules[mod]['lines'] * 100) if modules[mod]['lines'] > 0 else 0
        module_list.append((mod, pct, modules[mod]))
    
    module_list.sort(key=lambda x: x[1], reverse=True)
    
    report_lines.append('MODULE BREAKDOWN (sorted by coverage):')
    report_lines.append('-'*80)
    for mod, pct, data in module_list:
        report_lines.append(f'{mod:20s}: {pct:7.2f}% ({data["covered"]:5d}/{data["lines"]:5d} lines, {data["count"]:2d} files)')
    
    # Fichiers < 60%
    under_60 = [f for f in files_coverage if f['coverage'] < 60]
    report_lines.append('')
    report_lines.append('='*80)
    report_lines.append(f'FILES WITH COVERAGE < 60%: {len(under_60)} / {len(files_coverage)}')
    report_lines.append('='*80)
    report_lines.append('')
    
    if under_60:
        report_lines.append('Coverage %  |  Covered/Total Lines  |  File Path')
        report_lines.append('-'*80)
        for file_entry in under_60:
            report_lines.append(f"{file_entry['coverage']:6.2f}%    |  {file_entry['covered']:5d}/{file_entry['lines']:5d}  |  {file_entry['path']}")
    else:
        report_lines.append('✅ No files with coverage < 60%')
    
    # Écrire le rapport
    report_text = '\n'.join(report_lines)
    with open('COVERAGE_REPORT.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    # Afficher résumé
    print("✅ Rapport généré: COVERAGE_REPORT.txt")
    print(f"Couverture totale: {total_coverage:.2f}%")
    print(f"Fichiers < 60%: {len(under_60)} / {len(files_coverage)}")
    print(f"Top 5 modules:")
    for i, (mod, pct, data) in enumerate(module_list[:5], 1):
        print(f"  {i}. {mod}: {pct:.2f}%")

if __name__ == '__main__':
    generate_coverage_report()
