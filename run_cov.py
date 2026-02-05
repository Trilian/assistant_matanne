"""Script pour mesurer la couverture des nouveaux tests"""
import subprocess
import sys

def run_coverage():
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/api/test_api_deep.py",
        "tests/utils/test_formatters_deep.py", 
        "tests/utils/test_helpers_deep.py",
        "tests/utils/test_image_recipe_deep.py",
        "tests/ui/test_ui_deep.py",
        "--cov=src/api",
        "--cov=src/utils", 
        "--cov=src/ui",
        "--cov-report=term",
        "-q",
        "--tb=no"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="d:/Projet_streamlit/assistant_matanne")
    
    # Afficher les dernières lignes (rapport de couverture)
    output = result.stdout + result.stderr
    lines = output.split('\n')
    
    # Trouver le début du rapport de couverture
    cov_start = None
    for i, line in enumerate(lines):
        if "TOTAL" in line or "Name" in line and "Stmts" in line:
            cov_start = max(0, i - 2)
            break
    
    if cov_start:
        print("\n".join(lines[cov_start:]))
    else:
        # Afficher les 50 dernières lignes
        print("\n".join(lines[-50:]))

if __name__ == "__main__":
    run_coverage()
