#!/usr/bin/env python3
"""
Script pour gerer les tests et la couverture du projet Assistant Matanne.

Utilisation:
    python test_manager.py              # Executer tous les tests
    python test_manager.py coverage     # Executer avec rapport de couverture
    python test_manager.py core         # Tests du noyau seulement
    python test_manager.py services     # Tests des services seulement
    python test_manager.py api          # Tests API seulement
    python test_manager.py quick        # Tests rapides (skip lents)
    python test_manager.py report       # Generer un rapport HTML
    python test_manager.py stats        # Statistiques des tests
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Executer une commande et afficher le resultat."""
    if description:
        print(f"\n{'=' * 70}")
        print(f"  {description}")
        print(f"{'=' * 70}\n")

    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTests interrompus par l'utilisateur")
        return False
    except Exception as e:
        print(f"\nErreur: {e}")
        return False


def run_all_tests():
    """Executer tous les tests."""
    return run_command("python -m pytest tests/ -v --tb=short", "Execution de TOUS les tests")


def run_coverage():
    """Executer les tests avec rapport de couverture."""
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
        print("\nRapport HTML: htmlcov/index.html")
        print("Rapport XML: coverage.xml")
    return success


def run_core_tests():
    """Tests du noyau."""
    return run_command("python -m pytest tests/core/ -v --tb=short", "Tests du NOYAU (core)")


def run_services_tests():
    """Tests des services."""
    return run_command(
        "python -m pytest tests/services/ -v --tb=short", "Tests des SERVICES"
    )


def run_api_tests():
    """Tests de l'API."""
    return run_command("python -m pytest tests/api/ -v --tb=short", "Tests de l'API")


def run_benchmarks():
    """Benchmarks de performance."""
    return run_command(
        "python -m pytest tests/benchmarks/ -v --tb=short", "BENCHMARKS"
    )


def run_quick_tests():
    """Tests rapides (skip lents)."""
    return run_command(
        'python -m pytest tests/ -v --tb=short -m "not slow"',
        "Tests RAPIDES (skip lents)",
    )


def run_specific_test(pattern):
    """Executer un test specifique par pattern."""
    return run_command(
        f'python -m pytest tests/ -k "{pattern}" -v',
        f"Tests correspondant a: {pattern}",
    )


def generate_report():
    """Generer un rapport complet de couverture."""
    cmd = (
        "python -m pytest tests/ "
        "--cov=src "
        "--cov-report=term-missing:skip-covered "
        "--cov-report=html "
        "--cov-report=json "
        "-v --tb=line"
    )
    success = run_command(cmd, "GENERATION DU RAPPORT COMPLET DE COUVERTURE")
    if success:
        print("\nRapport HTML: htmlcov/index.html")
        print("Rapport JSON: coverage.json")
    return success


def show_stats():
    """Afficher les statistiques des tests."""
    print("\n" + "=" * 70)
    print("STATISTIQUES DES TESTS")
    print("=" * 70 + "\n")

    test_dir = Path("tests")

    categories = {
        "core": list(test_dir.glob("core/**/test_*.py")),
        "services": list(test_dir.glob("services/**/test_*.py")),
        "api": list(test_dir.glob("api/**/test_*.py")),
        "benchmarks": list(test_dir.glob("benchmarks/**/test_*.py")),
    }

    total = sum(len(files) for files in categories.values())

    print("Fichiers de test par categorie:")
    for category, files in categories.items():
        count = len(files)
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {category:15} {count:3} fichiers ({percentage:5.1f}%)")

    print(f"\nTotal: {total} fichiers de test")

    test_count = 0
    for files in categories.values():
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                test_count += content.count("\ndef test_") + content.count("\n    def test_")
            except Exception:
                pass
    print(f"Fonctions de test: ~{test_count}")


def main():
    """Point d'entree principal."""
    parser = argparse.ArgumentParser(
        description="Gestionnaire de tests pour Assistant Matanne"
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="all",
        choices=[
            "all",
            "coverage",
            "core",
            "services",
            "api",
            "benchmarks",
            "quick",
            "report",
            "stats",
        ],
        help="Commande a executer",
    )

    parser.add_argument("-k", "--pattern", help="Pattern pour filtrer les tests")

    args = parser.parse_args()

    commands = {
        "all": run_all_tests,
        "coverage": run_coverage,
        "core": run_core_tests,
        "services": run_services_tests,
        "api": run_api_tests,
        "benchmarks": run_benchmarks,
        "quick": run_quick_tests,
        "report": generate_report,
        "stats": show_stats,
    }

    if args.pattern and args.command in ["all", "coverage"]:
        success = run_specific_test(args.pattern)
    else:
        command_func = commands.get(args.command)
        if command_func:
            success = command_func()
        else:
            print(f"Commande inconnue: {args.command}")
            parser.print_help()
            return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
