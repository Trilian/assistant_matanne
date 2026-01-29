#!/usr/bin/env python
"""Script simplifié pour lancer les tests et générer le rapport de couverture."""

import subprocess
import sys
from pathlib import Path

def main():
    """Lancer les tests avec couverture."""
    
    work_dir = Path(__file__).parent
    
    # Définir les chemins
    tests_dir = work_dir / "tests"
    src_dir = work_dir / "src"
    
    # Commande pytest
    cmd = [
        sys.executable, "-m", "pytest",
        str(tests_dir / "core"),
        "--ignore=" + str(tests_dir / "core" / "test_offline.py"),
        "--ignore=" + str(tests_dir / "core" / "test_sql_optimizer.py"),
        "--cov=" + str(src_dir / "core"),
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov_core",
        "-v",
        "--tb=short",
    ]
    
    print(f"Lancement des tests depuis: {work_dir}")
    print(f"Commande: {' '.join(cmd)}")
    print("-" * 80)
    
    # Exécuter
    result = subprocess.run(cmd, cwd=work_dir)
    
    print("-" * 80)
    print(f"Tests termines avec code: {result.returncode}")
    print(f"Rapport HTML: htmlcov_core/index.html")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
