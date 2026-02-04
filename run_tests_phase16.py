#!/usr/bin/env python3
"""Script pour executer les tests Phase 16 et generer rapport de couverture."""

import subprocess
import json
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_tests():
    """Etape 1: Executer tous les tests."""
    print("\n" + "="*70)
    print("ETAPE 1: EXECUTION DE TOUS LES TESTS")
    print("="*70)
    
    test_files = [
        "tests/services/test_services_basic.py",
        "tests/services/test_services_integration.py",
        "tests/models/test_models_basic.py",
        "tests/core/test_decorators_basic.py",
        "tests/utils/test_utils_basic.py",
        "tests/integration/test_domains_integration.py",
        "tests/integration/test_business_logic.py",
        "tests/integration/test_phase16_extended.py",
    ]
    
    start_time = time.time()
    
    cmd = ["python", "-m", "pytest"] + test_files + ["--tb=short", "-q"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\nDuree: {elapsed:.2f}s")
        print(f"Code de retour: {result.returncode}")
        
        return result.returncode == 0, elapsed
    except subprocess.TimeoutExpired:
        print("TIMEOUT apres 300 secondes")
        return False, 300
    except Exception as e:
        print(f"ERREUR: {e}")
        return False, 0

def run_coverage():
    """Etape 2: Mesurer la couverture."""
    print("\n" + "="*70)
    print("ETAPE 2: MESURE DE COUVERTURE")
    print("="*70)
    
    test_files = [
        "tests/services/test_services_basic.py",
        "tests/services/test_services_integration.py",
        "tests/models/test_models_basic.py",
        "tests/core/test_decorators_basic.py",
        "tests/utils/test_utils_basic.py",
        "tests/integration/test_domains_integration.py",
        "tests/integration/test_business_logic.py",
        "tests/integration/test_phase16_extended.py",
    ]
    
    start_time = time.time()
    
    cmd = [
        "python", "-m", "pytest"
    ] + test_files + [
        "--cov=src",
        "--cov-report=json",
        "--cov-report=term-missing",
        "-q", "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\nDuree: {elapsed:.2f}s")
        
        return elapsed
    except subprocess.TimeoutExpired:
        print("TIMEOUT apres 300 secondes")
        return 0
    except Exception as e:
        print(f"ERREUR: {e}")
        return 0

def extract_coverage():
    """Etape 3: Extraire les metriques de couverture."""
    print("\n" + "="*70)
    print("ETAPE 3: EXTRACTION METRIQUES COUVERTURE")
    print("="*70)
    
    try:
        coverage_file = Path("coverage.json")
        if not coverage_file.exists():
            print(f"Fichier coverage.json non trouve")
            return None
        
        with open(coverage_file) as f:
            data = json.load(f)
        
        total_pct = data['totals']['percent_covered']
        baseline = 9.74
        gain = total_pct - baseline
        
        print(f"\nPHASE 16 FIXED - RESULTATS")
        print(f"Couverture globale: {total_pct:.2f}%")
        print(f"Target etait: 14-16%")
        print(f"Baseline etait: {baseline}%")
        print(f"Gain: {gain:.2f}%")
        
        if total_pct >= 14:
            print(f"\nSUCCESS: Couverture >= 14% (realise: {total_pct:.2f}%)")
        elif total_pct >= 9.74:
            print(f"\nPARTIEL: Couverture > baseline mais < 14% (realise: {total_pct:.2f}%)")
        else:
            print(f"\nFAIL: Couverture < baseline (realise: {total_pct:.2f}%)")
        
        return {
            'total_pct': total_pct,
            'baseline': baseline,
            'gain': gain
        }
    except Exception as e:
        print(f"ERREUR: {e}")
        return None

def main():
    """Execute les trois etapes."""
    print("\nPHASE 16 - TEST & COUVERTURE REPORT\n")
    
    # Etape 1
    success, test_duration = run_tests()
    
    # Etape 2
    coverage_duration = run_coverage()
    
    # Etape 3
    coverage_data = extract_coverage()
    
    # Resume final
    print("\n" + "="*70)
    print("RESUME FINAL")
    print("="*70)
    print(f"Tests: {'PASSES' if success else 'ECHOUES'}")
    print(f"Duree tests: {test_duration:.2f}s")
    print(f"Duree couverture: {coverage_duration:.2f}s")
    if coverage_data:
        print(f"Couverture finale: {coverage_data['total_pct']:.2f}%")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
