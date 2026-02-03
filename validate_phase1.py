#!/usr/bin/env python3
"""
Script de validation PHASE 1
Exécute tous les tests PHASE 1 et génère un rapport
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime


def run_tests_phase1():
    """Exécute tous les tests PHASE 1"""
    
    test_files = [
        "tests/utils/test_image_generator.py",
        "tests/utils/test_helpers_general.py",
        "tests/domains/maison/ui/test_depenses.py",
        "tests/domains/planning/ui/components/test_components_init.py",
        "tests/domains/famille/ui/test_jules_planning.py",
        "tests/domains/cuisine/ui/test_planificateur_repas.py",
        "tests/domains/jeux/test_setup.py",
        "tests/domains/jeux/test_integration.py",
    ]
    
    print("="*80)
    print("VALIDATION PHASE 1: Exécution des 8 fichiers de test")
    print("="*80 + "\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "PHASE_1",
        "files": test_files,
        "tests": {}
    }
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_file in test_files:
        print(f"📝 Exécution: {test_file}")
        
        # Exécuter le test
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parser les résultats
            stdout = result.stdout
            if "passed" in stdout:
                # Compter les tests
                import re
                match = re.search(r'(\d+) passed', stdout)
                if match:
                    count = int(match.group(1))
                    passed += count
                    print(f"  ✅ PASSED: {count} tests")
            
            if "failed" in stdout:
                match = re.search(r'(\d+) failed', stdout)
                if match:
                    count = int(match.group(1))
                    failed += count
                    print(f"  ❌ FAILED: {count} tests")
            
            if "skipped" in stdout:
                match = re.search(r'(\d+) skipped', stdout)
                if match:
                    count = int(match.group(1))
                    skipped += count
                    print(f"  ⏭️  SKIPPED: {count} tests")
            
            # Enregistrer le résultat
            results["tests"][test_file] = {
                "status": "passed" if result.returncode == 0 else "failed",
                "return_code": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  TIMEOUT after 30s")
            results["tests"][test_file] = {"status": "timeout"}
        except Exception as e:
            print(f"  ⚠️  ERROR: {e}")
            results["tests"][test_file] = {"status": "error", "message": str(e)}
        
        print()
    
    # Résumé
    print("="*80)
    print("RÉSUMÉ PHASE 1")
    print("="*80)
    print(f"✅ PASSED:  {passed} tests")
    print(f"❌ FAILED:  {failed} tests")
    print(f"⏭️  SKIPPED: {skipped} tests")
    print(f"📊 TOTAL:   {passed + failed + skipped} tests")
    print("="*80 + "\n")
    
    # Sauvegarder le rapport
    report_file = Path("PHASE_1_TEST_RESULTS.json")
    results["summary"] = {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "total": passed + failed + skipped
    }
    
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Rapport sauvegardé: {report_file}")
    
    return passed, failed, skipped


def run_coverage_phase1():
    """Exécute le rapport de couverture PHASE 1"""
    
    print("\n" + "="*80)
    print("RAPPORT DE COUVERTURE PHASE 1")
    print("="*80 + "\n")
    
    try:
        result = subprocess.run(
            [
                "python", "-m", "pytest",
                "tests/utils/test_image_generator.py",
                "tests/utils/test_helpers_general.py",
                "tests/domains/maison/ui/test_depenses.py",
                "tests/domains/planning/ui/components/test_components_init.py",
                "tests/domains/famille/ui/test_jules_planning.py",
                "tests/domains/cuisine/ui/test_planificateur_repas.py",
                "tests/domains/jeux/test_setup.py",
                "tests/domains/jeux/test_integration.py",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html",
                "-q"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Afficher les résultats
        print(result.stdout)
        
        if "TOTAL" in result.stdout:
            print("\n✅ Rapport HTML généré: htmlcov/index.html")
        
    except Exception as e:
        print(f"⚠️  Erreur lors de la génération du rapport: {e}")


def main():
    """Main function"""
    
    print("\n🚀 PHASE 1: VALIDATION COMPLÈTE\n")
    
    # Exécuter les tests
    passed, failed, skipped = run_tests_phase1()
    
    # Exécuter la couverture
    run_coverage_phase1()
    
    # Résumé final
    print("\n" + "="*80)
    print("RÉSUMÉ FINAL")
    print("="*80)
    
    if failed == 0:
        print("✅ TOUS LES TESTS PHASE 1 PASSENT!")
    else:
        print(f"⚠️  {failed} test(s) en échec à corriger")
    
    print(f"📊 {passed} tests passés, {skipped} skipped")
    print("\n📍 Prochaines étapes:")
    print("  1. Voir htmlcov/index.html pour la couverture")
    print("  2. Améliorer les templates avec de vraies logiques")
    print("  3. Valider >32% couverture")
    print("  4. Passer à PHASE 2")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
