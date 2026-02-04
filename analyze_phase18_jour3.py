"""
Script d'analyse automatique pour fixer les patterns d'erreurs Jour 3.
Identifie les patterns et applique des fixes massives.
"""

import subprocess
import re
from collections import defaultdict

def analyze_test_failures():
    """Analyse les tests échoués et categorise les erreurs."""
    
    # Exécuter les tests
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/api/", "-q", "--tb=line"],
        capture_output=True,
        text=True,
        cwd="d:\\Projet_streamlit\\assistant_matanne"
    )
    
    output = result.stdout + result.stderr
    
    # Extraire les patterns d'erreur
    error_patterns = defaultdict(list)
    
    for line in output.split('\n'):
        if 'assert' in line and '==' in line:
            # Pattern: assert 500 == 200
            match = re.search(r'assert (\d+) == (\d+)', line)
            if match:
                actual, expected = match.groups()
                error_patterns[f"Status {actual} != {expected}"].append(line)
            
            # Pattern: assert X in [...]
            match = re.search(r'assert (\d+) in \[(.*?)\]', line)
            if match:
                status, allowed = match.groups()
                error_patterns[f"Status {status} not in allowed"].append(line)
    
    print("=" * 60)
    print("PATTERN D'ERREURS DÉTECTÉES:")
    print("=" * 60)
    for pattern, occurrences in sorted(error_patterns.items(), key=lambda x: -len(x[1])):
        print(f"{pattern}: {len(occurrences)} occurrences")
    
    return error_patterns

def get_test_stats():
    """Récupère les statistiques des tests."""
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/api/", "tests/services/test_services_basic.py", 
         "tests/edge_cases/", "tests/benchmarks/", "-q", "--tb=no"],
        capture_output=True,
        text=True,
        cwd="d:\\Projet_streamlit\\assistant_matanne"
    )
    
    output = result.stdout + result.stderr
    
    # Extraire le résumé final
    match = re.search(r'(\d+) failed.*?(\d+) passed', output)
    if match:
        failed, passed = match.groups()
        return {"failed": int(failed), "passed": int(passed)}
    
    return {}

if __name__ == "__main__":
    print("\n📊 PHASE 18 JOUR 3 - ANALYSE AUTOMATIQUE\n")
    
    stats = get_test_stats()
    if stats:
        total = stats['failed'] + stats['passed']
        pass_rate = (stats['passed'] / total * 100) if total > 0 else 0
        print(f"Résultat actuel: {stats['passed']}/{total} ({pass_rate:.1f}%)")
        print(f"Tests échoués: {stats['failed']}\n")
    
    analyze_test_failures()
