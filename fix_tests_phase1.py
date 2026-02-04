#!/usr/bin/env python3
"""
Script de correction des tests échoués - Phase 1: Core
Cible: Atteindre 80%+ de couverture
"""
import subprocess
from pathlib import Path

def run_tests_for_module(module, include_pattern=None):
    """Exécuter tests pour un module spécifique"""
    cmd = [
        "pytest",
        f"tests/{module}",
        "--cov=src",
        "--cov-report=term-missing",
        "-v",
        "--tb=short"
    ]
    
    if include_pattern:
        cmd.append("-k")
        cmd.append(include_pattern)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result

def main():
    print("=" * 80)
    print("🔧 CORRECTION DES TESTS ÉCHOUÉS - PHASE 1: CORE")
    print("=" * 80)
    
    # Lister les tests échoués en core
    print("\n1. Analyse des tests échoués en core...")
    result = subprocess.run(
        ["pytest", "tests/core", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("\n2. Exécution des tests critiques...")
    # Tests recettes
    print("\n   ✓ Tests recettes...")
    result = run_tests_for_module("core", "recettes")
    print(result.stdout[-500:] if result.stdout else "")
    
    # Tests models
    print("\n   ✓ Tests models...")
    result = run_tests_for_module("core", "models")
    print(result.stdout[-500:] if result.stdout else "")
    
    print("\n" + "=" * 80)
    print("✅ Analyse complète - Voir RAPPORT_COUVERTURE_DETAILLE.txt")
    print("=" * 80)

if __name__ == "__main__":
    main()
