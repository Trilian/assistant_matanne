#!/usr/bin/env python3
"""
Script pour gÃ©rer les tests et la couverture du projet Assistant Matanne.

Utilisation:
    python test_manager.py              # ExÃ©cuter tous les tests
    python test_manager.py coverage     # ExÃ©cuter avec rapport de couverture
    python test_manager.py core         # Tests du noyau seulement
    python test_manager.py services     # Tests des services seulement
    python test_manager.py ui           # Tests UI seulement
    python test_manager.py integration  # Tests d'intÃ©gration seulement
    python test_manager.py report       # GÃ©nÃ©rer un rapport HTML
    python test_manager.py quick        # Tests rapides (skip lents)
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """ExÃ©cuter une commande et afficher le rÃ©sultat."""
    if description:
        print(f"\n{'='*70}")
        print(f"ðŸ“Œ {description}")
        print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nâ¸ï¸  Tests interrompus par l'utilisateur")
        return False
    except Exception as e:
        print(f"\nâŒ Erreur: {e}")
        return False


def run_all_tests():
    """ExÃ©cuter tous les tests."""
    cmd = "python -m pytest tests/ -v --tb=short"
    return run_command(cmd, "ExÃ©cution de TOUS les tests")


def run_coverage():
    """ExÃ©cuter les tests avec rapport de couverture."""
    cmd = (
        "python -m pytest tests/ "
        "--cov=src "
        "--cov-report=term-missing "
        "--cov-report=html "
        "--cov-report=xml "
        "-v"
    )
    success = run_command(cmd, "Tests avec RAPPORT DE COUVERTURE")
    
    if success:
        print("\nâœ… Rapport de couverture gÃ©nÃ©rÃ©")
        print("ðŸ“Š Rapport HTML: htmlcov/index.html")
        print("ðŸ“Š Rapport XML: coverage.xml")
    
    return success


def run_core_tests():
    """Tests du noyau."""
    cmd = "python -m pytest tests/core/ -v --tb=short"
    return run_command(cmd, "Tests du NOYAU (core)")


def run_services_tests():
    """Tests des services."""
    cmd = "python -m pytest tests/services/ -v --tb=short"
    return run_command(cmd, "Tests des SERVICES")


def run_ui_tests():
    """Tests UI."""
    cmd = "python -m pytest tests/ui/ -v --tb=short"
    return run_command(cmd, "Tests UI")


def run_integration_tests():
    """Tests d'intÃ©gration."""
    cmd = "python -m pytest tests/integration/ -v --tb=short"
    return run_command(cmd, "Tests d'INTÃ‰GRATION")


def run_utils_tests():
    """Tests utils."""
    cmd = "python -m pytest tests/utils/ -v --tb=short"
    return run_command(cmd, "Tests UTILS")


def run_quick_tests():
    """Tests rapides (skip lents)."""
    cmd = 'python -m pytest tests/ -v --tb=short -m "not slow"'
    return run_command(cmd, "Tests RAPIDES (skip lents)")


def run_specific_test(pattern):
    """ExÃ©cuter un test spÃ©cifique par pattern."""
    cmd = f'python -m pytest tests/ -k "{pattern}" -v'
    return run_command(cmd, f"Tests correspondant Ã : {pattern}")


def generate_report():
    """GÃ©nÃ©rer un rapport complet de couverture."""
    print("\n" + "="*70)
    print("ðŸ“Š GÃ‰NÃ‰RATION DU RAPPORT COMPLET DE COUVERTURE")
    print("="*70 + "\n")
    
    cmd = (
        "python -m pytest tests/ "
        "--cov=src "
        "--cov-report=term-missing:skip-covered "
        "--cov-report=html "
        "--cov-report=json "
        "-v --tb=line"
    )
    
    success = run_command(cmd)
    
    if success:
        print("\n" + "="*70)
        print("âœ… RAPPORTS GÃ‰NÃ‰RÃ‰S")
        print("="*70)
        print("ðŸ“Š Rapport HTML: htmlcov/index.html")
        print("ðŸ“Š Rapport JSON: coverage.json")
        print("ðŸ“Š Rapport Terminal: Voir au-dessus")
        
        # Afficher un rÃ©sumÃ©
        print("\n" + "="*70)
        print("ðŸ” RÃ‰SUMÃ‰")
        print("="*70)
        print("""
Pour visualiser le rapport de couverture:
  Windows: start htmlcov/index.html
  Mac:     open htmlcov/index.html
  Linux:   xdg-open htmlcov/index.html

Principaux fichiers Ã  amÃ©liorer:
  1. VÃ©rifier les fichiers avec couverture < 50%
  2. PrioritÃ©: src/modules/maison/
  3. PrioritÃ©: src/services/weather.py
  4. PrioritÃ©: src/services/budget.py
        """)
    
    return success


def show_stats():
    """Afficher les statistiques des tests."""
    print("\n" + "="*70)
    print("ðŸ“Š STATISTIQUES DES TESTS")
    print("="*70 + "\n")
    
    # Compter les fichiers de test
    test_dir = Path("tests")
    
    stats = {
        "core": len(list(test_dir.glob("core/test_*.py"))),
        "services": len(list(test_dir.glob("services/test_*.py"))),
        "ui": len(list(test_dir.glob("ui/test_*.py"))),
        "integration": len(list(test_dir.glob("integration/test_*.py"))),
        "utils": len(list(test_dir.glob("utils/test_*.py"))),
        "logic": len(list(test_dir.glob("logic/test_*.py"))),
        "e2e": len(list(test_dir.glob("e2e/test_*.py"))),
    }
    
    total = sum(stats.values())
    
    print(f"ðŸ“ Fichiers de test par catÃ©gorie:")
    for category, count in stats.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {category:15} {count:3} fichiers ({percentage:5.1f}%)")
    
    print(f"\nðŸ“Š Total: {total} fichiers de test")
    print(f"\nâœ… Tous les tests sont organisÃ©s et prÃªts Ã  s'exÃ©cuter!")


def main():
    """Point d'entrÃ©e principal."""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de tests pour Assistant Matanne"
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=[
            "all", "coverage", "core", "services", "ui", 
            "integration", "utils", "quick", "report", "stats"
        ],
        help="Commande Ã  exÃ©cuter"
    )
    
    parser.add_argument(
        "-k", "--pattern",
        help="Pattern pour filtrer les tests (ex: 'test_recettes')"
    )
    
    args = parser.parse_args()
    
    commands = {
        "all": run_all_tests,
        "coverage": run_coverage,
        "core": run_core_tests,
        "services": run_services_tests,
        "ui": run_ui_tests,
        "integration": run_integration_tests,
        "utils": run_utils_tests,
        "quick": run_quick_tests,
        "report": generate_report,
        "stats": show_stats,
    }
    
    # ExÃ©cuter la commande
    if args.pattern and args.command in ["all", "coverage"]:
        success = run_specific_test(args.pattern)
    else:
        command_func = commands.get(args.command)
        if command_func:
            success = command_func()
        else:
            print(f"âŒ Commande inconnue: {args.command}")
            parser.print_help()
            return 1
    
    # Retourner le code de sortie
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
