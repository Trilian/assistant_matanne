#!/usr/bin/env python3
"""
Script de lancement des tests Planning Module

Facilite l'exécution des tests avec différentes options

Usage:
    python run_tests_planning.py              # Tous les tests
    python run_tests_planning.py --unit       # Unitaires seulement
    python run_tests_planning.py --integration # Intégration seulement
    python run_tests_planning.py --coverage   # Avec rapport couverture
    python run_tests_planning.py --watch      # Mode watch (auto-reload)
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Exécuter commande et afficher résultats"""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Lancer tests Planning Module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python run_tests_planning.py                    # Tous les tests
  python run_tests_planning.py --unit             # Tests unitaires
  python run_tests_planning.py --integration      # Tests intégration
  python run_tests_planning.py --coverage         # Avec couverture
  python run_tests_planning.py --watch            # Mode watch
  python run_tests_planning.py --specific test_planning_unified.py  # Fichier spécifique
        """,
    )

    parser.add_argument(
        "--unit",
        action="store_true",
        help="Exécuter seulement tests unitaires",
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Exécuter seulement tests intégration",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Générer rapport couverture HTML",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Mode watch (réexécute à chaque sauvegarde)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mode verbose (affiche print statements)",
    )
    parser.add_argument(
        "--specific",
        type=str,
        help="Exécuter fichier test spécifique",
    )
    parser.add_argument(
        "--class",
        type=str,
        dest="test_class",
        help="Exécuter classe de tests spécifique",
    )
    parser.add_argument(
        "--method",
        type=str,
        help="Exécuter méthode de test spécifique",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Mode rapide (stop au 1er erreur)",
    )

    args = parser.parse_args()

    # Construire commande de base
    cmd = ["pytest"]

    # Déterminer fichiers à tester
    test_files = [
        "tests/test_planning_unified.py",
        "tests/test_planning_schemas.py",
        "tests/test_planning_components.py",
        "tests/integration/test_planning_full.py",
    ]

    if args.specific:
        test_files = [f"tests/{args.specific}"]
    elif args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])

    cmd.extend(test_files)

    # Ajouter options
    if args.verbose:
        cmd.extend(["-v", "-s", "--capture=no"])
    else:
        cmd.append("-v")

    if args.coverage:
        cmd.extend([
            "--cov=src/services/planning_unified",
            "--cov-report=html",
            "--cov-report=term-missing",
        ])

    if args.fast:
        cmd.append("-x")  # Stop au 1er erreur

    if args.test_class:
        cmd.append(f"::{args.test_class}")

    if args.method:
        cmd.append(f"::{args.method}")

    # Mode watch
    if args.watch:
        try:
            import pytest_watch  # noqa
            cmd_watch = ["ptw"] + cmd[1:]  # ptw remplace pytest
            return run_command(cmd_watch, "Mode Watch Activé")
        except ImportError:
            print("❌ pytest-watch non installé")
            print("Installation: pip install pytest-watch")
            return 1

    # Exécuter
    description = "Tests Planning Module"
    if args.specific:
        description += f" - {args.specific}"
    if args.unit:
        description += " (Unitaires)"
    if args.integration:
        description += " (Intégration)"
    if args.coverage:
        description += " (+ Couverture)"

    return_code = run_command(cmd, description)

    # Afficher résumé
    if return_code == 0:
        print(f"\n{'='*70}")
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print(f"{'='*70}\n")

        if args.coverage:
            print("📊 Rapport couverture généré: htmlcov/index.html\n")
    else:
        print(f"\n{'='*70}")
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"{'='*70}\n")

    return return_code


if __name__ == "__main__":
    sys.exit(main())
