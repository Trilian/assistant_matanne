"""Script pour exécuter les tests et sauvegarder les résultats."""
import subprocess
import sys
import os

# Change to workspace directory
os.chdir(r'd:\Projet_streamlit\assistant_matanne')

# Run the test
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 
     'tests/services/test_critical_services.py::TestRecetteServiceCoverage::test_create_recipe_basic',
     '-v', '--tb=short'],
    capture_output=True,
    text=True
)

# Write results to file
with open('pytest_output.txt', 'w', encoding='utf-8') as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(empty)")
    f.write("\n\n=== STDERR ===\n")
    f.write(result.stderr or "(empty)")
    f.write(f"\n\n=== RETURN CODE: {result.returncode} ===\n")

# Print confirmation  
print(f"Done! stdout={len(result.stdout or '')} chars, stderr={len(result.stderr or '')} chars, rc={result.returncode}")
