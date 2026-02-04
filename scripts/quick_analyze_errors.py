#!/usr/bin/env python3
"""
Analyseur rapide des erreurs de test Phase 18
Parser le fichier phase_18_test_results_raw.txt
"""

import re
from pathlib import Path
from collections import defaultdict


def analyze_pytest_output():
    """Analyser la sortie brute des tests."""
    
    results_file = Path("phase_18_test_results_raw.txt")
    if not results_file.exists():
        print("[!] Fichier phase_18_test_results_raw.txt non trouvé")
        return
    
    content = results_file.read_text(encoding='utf-8', errors='ignore')
    
    # Compter les résultats
    passed = len(re.findall(r'\.', content))  # Chaque point c'est un pass
    failed = len(re.findall(r'F', content))    # Chaque F c'est un fail
    errors = len(re.findall(r'E', content))    # Chaque E c'est une erreur
    skipped = len(re.findall(r's', content))   # Chaque s c'est un skip
    
    print("[*] ANALYSE RAPIDE DES RÉSULTATS DE TEST")
    print("=" * 80)
    print(f"Tests PASSÉS   : {passed}")
    print(f"Tests ÉCHOUÉS  : {failed}")
    print(f"Tests ERREUR   : {errors}")
    print(f"Tests SKIPPÉS  : {skipped}")
    print(f"TOTAL          : {passed + failed + errors + skipped}")
    print("=" * 80)
    
    # Calculer le taux de passage
    total = passed + failed + errors
    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"[+] Taux de passage: {pass_rate:.1f}%")
    
    # Analyser par fichier
    print("\n[*] FICHIERS AVEC LE PLUS DE PROBLÈMES:")
    print("-" * 80)
    
    # Chercher les lignes avec des F et E
    file_patterns = defaultdict(lambda: {"failed": 0, "errors": 0})
    
    lines = content.split('\n')
    for line in lines:
        # Match pattern: tests/path/file.py FFFFFFF...
        match = re.search(r'tests[\\\/][\w\/_\.]+\.py\s+([FEs\.]+)', line)
        if match:
            file_path = re.search(r'(tests[\\\/][\w\/_\.]+\.py)', line).group(1)
            status_str = match.group(1)
            
            file_patterns[file_path]["failed"] += status_str.count('F')
            file_patterns[file_path]["errors"] += status_str.count('E')
    
    # Trier par nombre total de problèmes
    sorted_files = sorted(
        file_patterns.items(),
        key=lambda x: x[1]["failed"] + x[1]["errors"],
        reverse=True
    )
    
    for file_path, counts in sorted_files[:15]:  # Top 15
        total_issues = counts["failed"] + counts["errors"]
        if total_issues > 0:
            print(f"  {file_path:60s} : {counts['failed']:2d}F + {counts['errors']:2d}E")
    
    print("\n[+] RECOMMANDATIONS:")
    print("    1. Corriger les endpoints 404 en premier (pattern API)")
    print("    2. Implémenter les factories de service (corriger les TypeError)")
    print("    3. Utiliser mocks standardisés pour Streamlit/IA")
    print("    4. Valider progressivement")
    
    # Chercher le résumé final
    print("\n[*] RÉSUMÉ FINAL DU TEST:")
    for line in reversed(lines[-20:]):
        if "passed" in line or "failed" in line or "error" in line:
            print(f"    {line.strip()}")


if __name__ == "__main__":
    analyze_pytest_output()
