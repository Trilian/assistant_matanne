#!/usr/bin/env python3
"""
RUN_UI_UTILS_TESTS.py - Launcher pour tous les tests UI et Utils

Usage:
    python RUN_UI_UTILS_TESTS.py all          # Tous les tests
    python RUN_UI_UTILS_TESTS.py ui           # UI seulement
    python RUN_UI_UTILS_TESTS.py utils        # Utils seulement
    python RUN_UI_UTILS_TESTS.py coverage     # Avec couverture
    python RUN_UI_UTILS_TESTS.py week1        # UI Week 1 seulement
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Exécuter une commande shell."""
    print(f"\n{'='*70}")
    print(f"📋 Exécution: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
    return result.returncode


def main():
    """Main entry point."""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    # ═══════════════════════════════════════════════════════════
    # UI TESTS
    # ═══════════════════════════════════════════════════════════
    
    if command == "ui_week1":
        cmd = ["pytest", "tests/ui/test_week1.py", "-v"]
        return run_command(cmd)
    
    elif command == "ui_week2":
        cmd = ["pytest", "tests/ui/test_week2.py", "-v"]
        return run_command(cmd)
    
    elif command == "ui_week3_4":
        cmd = ["pytest", "tests/ui/test_week3_4.py", "-v"]
        return run_command(cmd)
    
    elif command == "ui":
        cmd = ["pytest", "tests/ui/", "-v", "--tb=short"]
        return run_command(cmd)
    
    # ═══════════════════════════════════════════════════════════
    # UTILS TESTS
    # ═══════════════════════════════════════════════════════════
    
    elif command == "utils_week1_2":
        cmd = ["pytest", "tests/utils/test_week1_2.py", "-v"]
        return run_command(cmd)
    
    elif command == "utils_week3_4":
        cmd = ["pytest", "tests/utils/test_week3_4.py", "-v"]
        return run_command(cmd)
    
    elif command == "utils":
        cmd = ["pytest", "tests/utils/", "-v", "--tb=short"]
        return run_command(cmd)
    
    # ═══════════════════════════════════════════════════════════
    # COMBINED
    # ═══════════════════════════════════════════════════════════
    
    elif command == "all" or command == "both":
        cmd = ["pytest", "tests/ui/", "tests/utils/", "-v", "--tb=short"]
        return run_command(cmd)
    
    elif command == "coverage":
        cmd = [
            "pytest", 
            "tests/ui/", 
            "tests/utils/",
            "--cov=src/ui",
            "--cov=src/utils",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ]
        return run_command(cmd)
    
    # ═══════════════════════════════════════════════════════════
    # MARKERS
    # ═══════════════════════════════════════════════════════════
    
    elif command == "unit":
        cmd = ["pytest", "tests/ui/", "tests/utils/", "-m", "unit", "-v"]
        return run_command(cmd)
    
    elif command == "integration":
        cmd = ["pytest", "tests/ui/", "tests/utils/", "-m", "integration", "-v"]
        return run_command(cmd)
    
    elif command == "performance":
        cmd = ["pytest", "tests/utils/", "-m", "performance", "-v"]
        return run_command(cmd)
    
    # ═══════════════════════════════════════════════════════════
    # HELP
    # ═══════════════════════════════════════════════════════════
    
    elif command in ["help", "-h", "--help", "?"]:
        print_help()
        return 0
    
    elif command == "status":
        print_status()
        return 0
    
    else:
        print(f"❌ Commande inconnue: {command}")
        print_help()
        return 1


def print_help():
    """Afficher l'aide."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           UI & UTILS TESTS LAUNCHER                               ║
║           307 tests combinés                                      ║
╚════════════════════════════════════════════════════════════════════╝

📋 COMMANDES DISPONIBLES:

  UI TESTS:
    python RUN_UI_UTILS_TESTS.py ui              # Tous les tests UI (169 tests)
    python RUN_UI_UTILS_TESTS.py ui_week1        # Week 1 (51 tests)
    python RUN_UI_UTILS_TESTS.py ui_week2        # Week 2 (48 tests)
    python RUN_UI_UTILS_TESTS.py ui_week3_4      # Week 3-4 (70 tests)

  UTILS TESTS:
    python RUN_UI_UTILS_TESTS.py utils           # Tous les tests Utils (138 tests)
    python RUN_UI_UTILS_TESTS.py utils_week1_2   # Week 1-2 (80 tests)
    python RUN_UI_UTILS_TESTS.py utils_week3_4   # Week 3-4 (58 tests)

  COMBINED:
    python RUN_UI_UTILS_TESTS.py all             # UI + Utils (307 tests)
    python RUN_UI_UTILS_TESTS.py both            # Alias pour 'all'
    python RUN_UI_UTILS_TESTS.py coverage        # Avec rapport de couverture

  PAR MARQUEUR:
    python RUN_UI_UTILS_TESTS.py unit            # Tests unitaires seulement
    python RUN_UI_UTILS_TESTS.py integration     # Tests d'intégration seulement
    python RUN_UI_UTILS_TESTS.py performance     # Tests de performance

  AUTRES:
    python RUN_UI_UTILS_TESTS.py status          # Afficher le statut
    python RUN_UI_UTILS_TESTS.py help            # Cette aide

📊 STATISTIQUES:

  UI Tests:          169 tests
    ├─ Week 1:       51 tests (Atoms, Forms, Data Display, BaseForm)
    ├─ Week 2:       48 tests (Layouts, DataGrid, Navigation, Charts)
    └─ Week 3-4:     70 tests (Feedback, Modals, Responsive, Integration)

  Utils Tests:       138 tests
    ├─ Week 1-2:     80 tests (Formatters, Validators)
    └─ Week 3-4:     58 tests (Conversions, Text, Media, Integration)

  TOTAL:             307 tests ✅

💾 FICHIERS DE TEST:
    tests/ui/test_week1.py           - 51 tests
    tests/ui/test_week2.py           - 48 tests
    tests/ui/test_week3_4.py         - 70 tests
    tests/utils/test_week1_2.py      - 80 tests
    tests/utils/test_week3_4.py      - 58 tests

📚 DOCUMENTATION:
    UI_UTILS_TESTS_4WEEKS_COMPLETE.md - Breakdown complet par semaine
    UI_UTILS_TESTS_IMPLEMENTATION_SUMMARY.md - Résumé d'implémentation

⚙️ OPTIONS PYTEST SUPPLÉMENTAIRES:
    -v              Verbose (afficher chaque test)
    -x              Arrêter au premier échec
    -k "pattern"    Filtrer par pattern
    --tb=short      Traceback court
    --pdb           Debugger au premier échec
    -n auto         Exécution parallèle (nécessite pytest-xdist)

📝 EXEMPLES COMPLETS:
    pytest tests/ui/ tests/utils/ -v -x
    pytest tests/ui/ -k "form" -v
    pytest tests/utils/ --tb=short -x
    pytest tests/ -m unit --cov=src --cov-report=html
    """)


def print_status():
    """Afficher le statut des tests."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           STATUS - UI & UTILS TESTS                               ║
╚════════════════════════════════════════════════════════════════════╝

✅ INFRASTRUCTURE CRÉÉE:
   ├─ Fixtures Streamlit (session_state, UI components)
   ├─ Database fixtures (temp_db, mock_session)
   ├─ Sample data (recipes, ingredients, forms)
   ├─ Builders (FormBuilder, DataGridBuilder)
   ├─ Assertion helpers
   └─ Parametrization fixtures

✅ TESTS UI (169):
   ├─ Week 1: Atoms, Forms, Data Display (51)
   ├─ Week 2: Layouts, DataGrid, Navigation, Charts (48)
   └─ Week 3-4: Feedback, Modals, Responsive, Integration (70)

✅ TESTS UTILS (138):
   ├─ Week 1-2: Formatters, Validators (80)
   └─ Week 3-4: Conversions, Text, Media, Integration (58)

📊 COUVERTURE ATTENDUE:
   └─ src/ui:    >85%
   └─ src/utils: >90%

🚀 PRÊT POUR:
   ├─ Exécution locale
   ├─ CI/CD integration
   ├─ Rapports de couverture
   └─ Développement itératif

📈 PROGRESSION GLOBALE:
   ├─ src/core:  684 tests  ✅
   ├─ src/api:   270 tests  ✅
   ├─ src/ui:    169 tests  ✅
   └─ src/utils: 138 tests  ✅
   
   TOTAL: 1,261 tests ✅

Pour plus de détails, consultez:
- UI_UTILS_TESTS_4WEEKS_COMPLETE.md
- UI_UTILS_TESTS_IMPLEMENTATION_SUMMARY.md
    """)


if __name__ == "__main__":
    sys.exit(main() or 0)
