# Script pour vérifier la couverture des modules prioritaires
import subprocess
import sys

def run_coverage():
    """Exécuter les tests et afficher la couverture."""
    print("=" * 60)
    print("Exécution des tests avec mesure de couverture...")
    print("=" * 60)
    
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/core/",
            "--cov=src/core",
            "--cov-report=term",
            "-q",
            "--tb=no"
        ],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    # Afficher les résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DE COUVERTURE:")
    print("=" * 60)
    
    # Filtrer les lignes de couverture
    for line in result.stdout.split("\n"):
        if any(k in line.lower() for k in ["decorators", "validation", "errors", "cache", "lazy_loader", "state", "total", "stmts", "cover"]):
            print(line)
    
    print("\n" + "=" * 60)
    print("TOUTE LA SORTIE:")
    print("=" * 60)
    print(result.stdout)
    
    if result.stderr:
        print("\n" + "=" * 60)
        print("ERREURS:")
        print("=" * 60)
        print(result.stderr[-1000:])

if __name__ == "__main__":
    run_coverage()
