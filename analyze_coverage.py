#!/usr/bin/env python
"""Analyser la couverture théorique du système de test."""

import json
import re
from pathlib import Path
from collections import defaultdict


def count_tests_in_file(filepath):
    """Compter les tests dans un fichier."""
    try:
        content = filepath.read_text(encoding='utf-8')
        # Compter les fonctions de test
        test_functions = len(re.findall(r'def test_\w+\(', content))
        # Compter les méthodes de test
        test_methods = len(re.findall(r'def test_\w+\(self', content))
        return test_functions + test_methods
    except Exception as e:
        print(f"  Erreur lecture {filepath.name}: {e}")
        return 0


def analyze_test_coverage():
    """Analyser la couverture globale."""
    
    workspace = Path(__file__).parent
    tests_dir = workspace / "tests"
    
    results = {
        "core": [],
        "api": [],
        "ui": [],
        "utils": [],
        "services": [],
        "modules": [],
        "e2e": [],
    }
    
    total_tests = 0
    total_lines = 0
    
    # Parcourir tous les répertoires de tests
    for layer in results.keys():
        layer_dir = tests_dir / layer
        if layer_dir.exists():
            print(f"\n📦 Layer: {layer.upper()}")
            print("-" * 60)
            
            for test_file in sorted(layer_dir.glob("test_*.py")):
                test_count = count_tests_in_file(test_file)
                lines = len(test_file.read_text().splitlines())
                
                if test_count > 0:
                    results[layer].append({
                        "file": test_file.name,
                        "tests": test_count,
                        "lines": lines
                    })
                    total_tests += test_count
                    total_lines += lines
                    
                    status = "✅" if test_count > 0 else "⚠️"
                    print(f"  {status} {test_file.name:<40} {test_count:>4} tests | {lines:>5} lignes")
    
    # Résumé par layer
    print("\n" + "=" * 80)
    print("RÉSUMÉ PAR LAYER")
    print("=" * 80)
    
    layer_stats = {}
    for layer, files in results.items():
        if files:
            layer_tests = sum(f["tests"] for f in files)
            layer_lines = sum(f["lines"] for f in files)
            layer_stats[layer] = {
                "files": len(files),
                "tests": layer_tests,
                "lines": layer_lines,
            }
            print(f"  {layer.upper():<15} {len(files):>2} fichiers | {layer_tests:>5} tests | {layer_lines:>6} lignes")
    
    # Total
    print("\n" + "=" * 80)
    total_files = sum(len(f) for f in results.values())
    print(f"{'TOTAL':<15} {total_files:>2} fichiers | {total_tests:>5} tests | {total_lines:>6} lignes")
    print("=" * 80)
    
    # Analyser la couverture théorique
    print("\n📊 ANALYSE COUVERTURE THÉORIQUE")
    print("-" * 80)
    
    src_dir = workspace / "src"
    src_stats = analyze_src_coverage(src_dir)
    
    # Combiner et afficher
    for layer, src_lines in src_stats.items():
        test_count = sum(f["tests"] for f in results.get(layer, []))
        ratio = (test_count / src_lines * 100) if src_lines > 0 else 0
        
        print(f"\n  {layer.upper()}:")
        print(f"    Source:  {src_lines:>6} lignes")
        print(f"    Tests:   {test_count:>6} tests")
        print(f"    Ratio:   {ratio:>6.1f}% (target: 65%+)")
    
    # Rapport JSON
    report = {
        "summary": {
            "total_test_files": total_files,
            "total_tests": total_tests,
            "total_test_lines": total_lines,
            "average_tests_per_file": total_tests / total_files if total_files > 0 else 0,
        },
        "by_layer": layer_stats,
        "files": results,
    }
    
    # Sauvegarder le rapport
    report_file = workspace / "test_coverage_analysis.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Rapport sauvegardé: {report_file}")
    
    return report


def analyze_src_coverage(src_dir):
    """Analyser les lignes de code source."""
    
    stats = defaultdict(int)
    
    for py_file in src_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        relative = py_file.relative_to(src_dir)
        layer = relative.parts[0]
        
        try:
            lines = len(py_file.read_text().splitlines())
            # Compter seulement le code métier (pas les imports/docstrings)
            content = py_file.read_text()
            code_lines = len([l for l in content.splitlines() 
                             if l.strip() and not l.strip().startswith('#')])
            stats[layer] += code_lines
        except Exception:
            pass
    
    return dict(stats)


if __name__ == "__main__":
    print("🔍 ANALYSE COUVERTURE DE TEST")
    print("=" * 80)
    
    report = analyze_test_coverage()
    
    print("\n✅ Analyse complétée!")
    print(f"\nRatio moyen: {report['summary']['average_tests_per_file']:.1f} tests par fichier")
