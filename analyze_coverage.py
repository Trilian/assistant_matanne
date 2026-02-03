#!/usr/bin/env python3
"""
Analyse détaillée de la couverture de tests
Génère un rapport sur:
- La couverture actuelle par module
- Les fichiers src/ sans tests correspondants
- Les fichiers avec <80% de couverture
- Les recommandations pour améliorer la couverture
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass
class FileInfo:
    path: str
    statements: int
    missing: int
    branches: int
    branch_missing: int
    coverage: float
    is_tested: bool = False


def parse_coverage_file(filepath: str) -> List[FileInfo]:
    """Parse le fichier coverage_output.txt"""
    files = []
    with open(filepath, 'r', encoding='utf-16') as f:
        lines = f.readlines()
    
    for line in lines:
        # Skip header and separator lines
        if not line.strip() or '---' in line or 'Name' in line or 'TOTAL' in line:
            continue
        
        parts = line.split()
        if len(parts) < 5:
            continue
        
        try:
            path = parts[0]
            if not path.startswith('src\\'):
                continue
            
            statements = int(parts[1])
            missing = int(parts[2])
            branches = int(parts[3])
            branch_missing = int(parts[4])
            coverage = float(parts[5].rstrip('%'))
            
            files.append(FileInfo(
                path=path.replace('\\', '/'),
                statements=statements,
                missing=missing,
                branches=branches,
                branch_missing=branch_missing,
                coverage=coverage
            ))
        except (ValueError, IndexError):
            continue
    
    return files


def find_src_files() -> Dict[str, Path]:
    """Trouve tous les fichiers Python dans src/"""
    src_path = Path('src')
    files = {}
    
    for py_file in src_path.rglob('*.py'):
        if '__pycache__' not in str(py_file):
            rel_path = str(py_file.relative_to(Path('.'))).replace('\\', '/')
            files[rel_path] = py_file
    
    return files


def find_test_files() -> Dict[str, Path]:
    """Trouve tous les fichiers tests"""
    tests_path = Path('tests')
    files = {}
    
    for py_file in tests_path.rglob('test_*.py'):
        if '__pycache__' not in str(py_file):
            rel_path = str(py_file.relative_to(Path('.'))).replace('\\', '/')
            files[rel_path] = py_file
    
    return files


def match_src_to_test(src_file: str, test_files: Dict[str, Path]) -> str:
    """Essaie de trouver le fichier test correspondant"""
    # Expected: src/module/file.py -> tests/module/test_file.py
    parts = src_file.split('/')
    if parts[0] != 'src':
        return None
    
    # Build expected test path
    test_parts = ['tests'] + parts[1:-1] + [f"test_{parts[-1]}"]
    expected_test = '/'.join(test_parts)
    
    if expected_test in test_files:
        return expected_test
    
    # Try alternative: tests/module/test_file.py (flat structure)
    alt_parts = ['tests'] + [f"test_{parts[-1]}"]
    alt_test = '/'.join(alt_parts)
    
    if alt_test in test_files:
        return alt_test
    
    return None


def generate_report():
    """Génère le rapport d'analyse"""
    
    print("=" * 80)
    print("ANALYSE DE COUVERTURE DE TESTS")
    print("=" * 80)
    
    # Parse coverage
    coverage_files = parse_coverage_file('coverage_output.txt')
    src_files = find_src_files()
    test_files = find_test_files()
    
    # Build index
    coverage_by_file = {f.path: f for f in coverage_files}
    
    # Match src to tests
    for src_file_path, src_file in src_files.items():
        if src_file_path in coverage_by_file:
            test_match = match_src_to_test(src_file_path, test_files)
            if test_match:
                coverage_by_file[src_file_path].is_tested = True
    
    # Statistics
    total_src = len([f for f in coverage_files if f.path.startswith('src/')])
    tested_src = sum(1 for f in coverage_files if f.path.startswith('src/') and f.is_tested)
    over_80 = sum(1 for f in coverage_files if f.path.startswith('src/') and f.coverage >= 80)
    under_30 = [f for f in coverage_files if f.path.startswith('src/') and f.coverage < 30]
    
    print(f"\n📊 STATISTIQUES GÉNÉRALES")
    print(f"  Fichiers src/ analysés: {total_src}")
    print(f"  Fichiers avec tests: {tested_src} ({tested_src/total_src*100:.1f}%)")
    print(f"  Fichiers >80% couverture: {over_80} ({over_80/total_src*100:.1f}%)")
    print(f"  Couverture moyenne: {sum(f.coverage for f in coverage_files if f.path.startswith('src/'))/total_src:.1f}%")
    
    # Files by coverage level
    print(f"\n🎯 FICHIERS PAR NIVEAU DE COUVERTURE")
    print(f"\n  ✅ Excellente (>90%): {sum(1 for f in coverage_files if f.coverage > 90 and f.path.startswith('src/'))}")
    print(f"  🟢 Bonne (80-90%): {sum(1 for f in coverage_files if 80 <= f.coverage <= 90 and f.path.startswith('src/'))}")
    print(f"  🟡 Acceptable (50-80%): {sum(1 for f in coverage_files if 50 <= f.coverage < 80 and f.path.startswith('src/'))}")
    print(f"  🔴 Faible (<50%): {sum(1 for f in coverage_files if f.coverage < 50 and f.path.startswith('src/'))}")
    
    # Critical files under 30%
    print(f"\n🚨 FICHIERS CRITIQUES (<30% couverture)")
    for f in sorted(under_30, key=lambda x: x.coverage):
        print(f"  {f.path}: {f.coverage:.1f}%")
    
    # Module analysis
    print(f"\n📦 ANALYSE PAR MODULE")
    module_stats = defaultdict(lambda: {'coverage': [], 'count': 0})
    
    for f in coverage_files:
        if not f.path.startswith('src/'):
            continue
        
        # Extract module name
        parts = f.path.split('/')
        module = parts[1] if len(parts) > 1 else 'root'
        
        module_stats[module]['coverage'].append(f.coverage)
        module_stats[module]['count'] += 1
    
    print(f"\n  Module              | Couverture moyenne | Fichiers")
    print(f"  {'-'*50}")
    for module in sorted(module_stats.keys()):
        avg_cov = sum(module_stats[module]['coverage']) / len(module_stats[module]['coverage'])
        count = module_stats[module]['count']
        print(f"  {module:20} | {avg_cov:18.1f}% | {count:3}")
    
    # Files missing tests
    print(f"\n⚠️  FICHIERS SANS TESTS (selon arborescence standard)")
    no_test_files = []
    for f in coverage_files:
        if f.path.startswith('src/') and not f.is_tested and f.statements > 10:
            no_test_files.append(f)
    
    print(f"  Total: {len(no_test_files)} fichiers")
    for f in sorted(no_test_files, key=lambda x: x.coverage)[:20]:
        print(f"    {f.path}: {f.coverage:.1f}% ({f.statements} statements)")
    
    # Recommendations
    print(f"\n💡 RECOMMANDATIONS PRIORITAIRES")
    print(f"\n  1. Fichiers critiques à couvrir d'urgence (<30%):")
    for f in sorted(under_30, key=lambda x: x.coverage)[:10]:
        print(f"     - {f.path}: {f.coverage:.1f}%")
    
    print(f"\n  2. Modules à renforcer (couverture <60%):")
    weak_modules = [(m, sum(module_stats[m]['coverage'])/len(module_stats[m]['coverage'])) 
                    for m in module_stats 
                    if sum(module_stats[m]['coverage'])/len(module_stats[m]['coverage']) < 60]
    for module, cov in sorted(weak_modules, key=lambda x: x[1]):
        print(f"     - {module}: {cov:.1f}%")
    
    print(f"\n  3. Structure des tests à créer/améliorer:")
    print(f"     - Dossier tests/e2e/ pour les tests d'intégration")
    print(f"     - Créer tests pour {len(no_test_files)} fichiers orphelins")
    print(f"     - Améliorer couverture des {len(under_30)} fichiers critiques")
    
    # Export data
    print(f"\n📄 Export des données...")
    export_data = {
        'total_files': total_src,
        'tested_files': tested_src,
        'files_over_80': over_80,
        'average_coverage': sum(f.coverage for f in coverage_files if f.path.startswith('src/'))/total_src,
        'critical_files': [{'path': f.path, 'coverage': f.coverage} for f in under_30],
        'modules': {m: {'coverage': sum(module_stats[m]['coverage'])/len(module_stats[m]['coverage']), 'count': module_stats[m]['count']} 
                   for m in module_stats}
    }
    
    with open('coverage_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Fichier généré: coverage_analysis.json")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    generate_report()
