"""
Script pour identifier et marquer les tests qui échouent.

Ce script identifie les tests qui:
1. Utilisent get_xxx_service() sans session DB de test
2. Utilisent des services singletons qui se connectent à Supabase
"""
import os
import re
from pathlib import Path

WORKSPACE = Path(r"d:\Projet_streamlit\assistant_matanne")

# Services qui sont des singletons utilisant la DB de production
PROBLEMATIC_SERVICES = [
    "get_planning_service",
    "get_recette_service", 
    "get_courses_service",
    "get_inventaire_service",
    "get_budget_service",
]

# Patterns qui indiquent un test nécessitant la DB de production
PATTERNS = [
    r"get_planning_service\(\)",
    r"get_recette_service\(\)",
    r"get_courses_service\(\)",
    r"get_inventaire_service\(\)",
    r"get_budget_service\(\)",
    r"PlanningService\(db\)",  # Wrong usage
    r"RecetteService\(db\)",   # Wrong usage
    r"service\.generer",
    r"service\.creer_planning",
]

def find_problematic_tests():
    """Trouve les tests qui utilisent des services problématiques."""
    test_files = list((WORKSPACE / "tests" / "services").glob("test_*.py"))
    
    problems = []
    
    for test_file in test_files:
        content = test_file.read_text(encoding='utf-8')
        
        for pattern in PATTERNS:
            if re.search(pattern, content):
                problems.append({
                    'file': str(test_file.relative_to(WORKSPACE)),
                    'pattern': pattern
                })
                break
    
    return problems

def count_tests_by_status():
    """Compte les tests par statut dans le résumé existant."""
    results_file = WORKSPACE / "test_results.txt"
    
    if not results_file.exists():
        return None
    
    content = results_file.read_text(encoding='utf-8')
    
    # Count PASSED, FAILED, etc
    passed = content.count(" PASSED")
    failed = content.count(" FAILED")
    skipped = content.count(" SKIPPED")
    xfailed = content.count(" XFAIL")
    xpassed = content.count(" XPASS")
    
    return {
        'passed': passed,
        'failed': failed, 
        'skipped': skipped,
        'xfailed': xfailed,
        'xpassed': xpassed
    }

if __name__ == '__main__':
    print("=== Analyse des tests problématiques ===\n")
    
    problems = find_problematic_tests()
    print(f"Fichiers de test avec patterns problématiques: {len(problems)}")
    for p in problems:
        print(f"  - {p['file']} ({p['pattern']})")
    
    print("\n=== Statistiques actuelles ===\n")
    
    stats = count_tests_by_status()
    if stats:
        total = sum(stats.values())
        print(f"Total tests: {total}")
        for status, count in stats.items():
            print(f"  {status}: {count}")
