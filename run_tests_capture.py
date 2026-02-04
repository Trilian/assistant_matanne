"""Script pour capturer les résultats des tests."""
import subprocess
import sys
import os

def run_tests(test_path):
    """Exécute les tests et capture la sortie."""
    os.chdir(r'd:\Projet_streamlit\assistant_matanne')
    
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', test_path, '-v', '--tb=short', '-x'],
        capture_output=True,
        text=True
    )
    
    output_file = 'test_output.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== STDOUT ===\n")
        f.write(result.stdout if result.stdout else "(empty)")
        f.write("\n=== STDERR ===\n")
        f.write(result.stderr if result.stderr else "(empty)")
        f.write(f"\n=== RETURN CODE: {result.returncode} ===\n")
    
    print(f"Résultats écrits dans {output_file}")
    print(f"Return code: {result.returncode}")
    print(f"Stdout length: {len(result.stdout) if result.stdout else 0}")
    print(f"Stderr length: {len(result.stderr) if result.stderr else 0}")
    return result.returncode

if __name__ == '__main__':
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'tests/services/test_phase1_courses.py'
    run_tests(test_path)
