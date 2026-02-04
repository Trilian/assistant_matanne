#!/usr/bin/env python3
"""Analyse détaillée des fichiers de test par module"""

import os
import re
from collections import defaultdict
from pathlib import Path

def count_tests_in_file(filepath):
    """Compte les tests dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Compte les fonctions test_
            count = len(re.findall(r'def test_\w+', content))
            # Compte les classes Test
            classes = len(re.findall(r'class Test\w+', content))
            # Compte les parametrize
            params = len(re.findall(r'@pytest\.mark\.parametrize', content))
            return count, classes, params
    except:
        return 0, 0, 0

def analyze_tests_directory():
    """Analyse complète du répertoire des tests"""
    tests_root = Path("tests")
    module_stats = defaultdict(lambda: {"files": 0, "functions": 0, "classes": 0, "parametrize": 0, "size": 0})
    
    for test_file in sorted(tests_root.rglob("test_*.py")):
        # Déterminer le module (premier répertoire)
        try:
            rel_path = test_file.relative_to(tests_root)
            parts = rel_path.parts
            if len(parts) > 1:
                module = parts[0]
            else:
                module = "root"
        except:
            module = "unknown"
        
        count, classes, params = count_tests_in_file(test_file)
        size = test_file.stat().st_size
        
        module_stats[module]["files"] += 1
        module_stats[module]["functions"] += count
        module_stats[module]["classes"] += classes
        module_stats[module]["parametrize"] += params
        module_stats[module]["size"] += size
    
    return module_stats

def main():
    stats = analyze_tests_directory()
    
    # Afficher tableau
    print("\n" + "="*100)
    print("ANALYSE COMPLÈTE DES TESTS PAR MODULE".center(100))
    print("="*100 + "\n")
    
    print(f"{'Module':<20} {'Fichiers':<12} {'Fonctions':<12} {'Classes':<12} {'Parametrize':<15} {'Taille (KB)':<15}")
    print("-"*100)
    
    total_files = 0
    total_functions = 0
    total_classes = 0
    total_params = 0
    total_size = 0
    
    for module in sorted(stats.keys(), key=lambda m: stats[m]["functions"], reverse=True):
        s = stats[module]
        total_files += s["files"]
        total_functions += s["functions"]
        total_classes += s["classes"]
        total_params += s["parametrize"]
        total_size += s["size"]
        
        size_kb = s["size"] / 1024
        print(f"{module:<20} {s['files']:<12} {s['functions']:<12} {s['classes']:<12} {s['parametrize']:<15} {size_kb:<15.1f}")
    
    print("-"*100)
    print(f"{'TOTAL':<20} {total_files:<12} {total_functions:<12} {total_classes:<12} {total_params:<15} {total_size/1024:<15.1f}")
    print("="*100)
    
    # Analyse de couverture attendue
    print("\n📊 ANALYSE DE COUVERTURE ATTENDUE:\n")
    
    for module in sorted(stats.keys(), key=lambda m: stats[m]["functions"], reverse=True):
        s = stats[module]
        pct = (s["functions"] / total_functions * 100) if total_functions > 0 else 0
        print(f"  {module:20} {s['functions']:5} tests  ({pct:5.1f}% du total)")
    
    print(f"\n💡 NOTES:")
    print(f"  - Total réel: {total_functions} tests")
    print(f"  - Fichiers: {total_files}")
    print(f"  - Classes de test: {total_classes}")
    print(f"  - Tests parametrisés: {total_params} (@pytest.mark.parametrize)")
    print(f"  - Taille totale: {total_size/1024:.1f} KB\n")

if __name__ == "__main__":
    main()
