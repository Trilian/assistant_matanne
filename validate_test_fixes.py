"""
Script pour valider les corrections des tests et générer un rapport de couverture.
"""
import subprocess
import sys
import os
from pathlib import Path

# Change to project directory
os.chdir(Path(__file__).parent)


def run_tests(test_path: str = "tests/", extra_args: list = None) -> tuple:
    """Run pytest and return results."""
    cmd = [
        sys.executable, "-m", "pytest", 
        test_path,
        "-v", "--tb=short",
        "-q",
        "--no-header",
    ]
    if extra_args:
        cmd.extend(extra_args)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.returncode, result.stdout, result.stderr


def count_test_results(output: str) -> dict:
    """Parse pytest output to count results."""
    counts = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
    
    # Look for summary line like "809 passed, 35 skipped, 3 failed"
    for line in output.split('\n'):
        if 'passed' in line or 'failed' in line or 'skipped' in line:
            import re
            for key in counts:
                match = re.search(rf'(\d+) {key}', line)
                if match:
                    counts[key] = int(match.group(1))
            if any(counts.values()):
                break
    
    return counts


def main():
    print("=" * 60)
    print("VALIDATION DES CORRECTIONS DE TESTS")
    print("=" * 60)
    
    # 1. Test core
    print("\n[1/4] Tests Core...")
    code, stdout, stderr = run_tests("tests/core/")
    core_counts = count_test_results(stdout + stderr)
    print(f"  Core: {core_counts}")
    
    # 2. Test services
    print("\n[2/4] Tests Services...")
    code, stdout, stderr = run_tests("tests/services/")
    services_counts = count_test_results(stdout + stderr)
    print(f"  Services: {services_counts}")
    
    # 3. Test UI
    print("\n[3/4] Tests UI...")
    code, stdout, stderr = run_tests("tests/ui/")
    ui_counts = count_test_results(stdout + stderr)
    print(f"  UI: {ui_counts}")
    
    # 4. All tests
    print("\n[4/4] Tous les tests...")
    code, stdout, stderr = run_tests("tests/", ["--cov=src", "--cov-report=term-missing:skip-covered", "-q"])
    all_counts = count_test_results(stdout + stderr)
    print(f"  Total: {all_counts}")
    
    # Extract coverage from output
    coverage_line = None
    for line in (stdout + stderr).split('\n'):
        if 'TOTAL' in line and '%' in line:
            coverage_line = line
            break
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Core:     {core_counts['passed']} passed, {core_counts['skipped']} skipped, {core_counts['failed']} failed")
    print(f"Services: {services_counts['passed']} passed, {services_counts['skipped']} skipped, {services_counts['failed']} failed")
    print(f"UI:       {ui_counts['passed']} passed, {ui_counts['skipped']} skipped, {ui_counts['failed']} failed")
    print(f"Total:    {all_counts['passed']} passed, {all_counts['skipped']} skipped, {all_counts['failed']} failed")
    
    if coverage_line:
        print(f"\nCouverture: {coverage_line}")
    
    # Save detailed output to file
    with open("test_validation_results.txt", "w") as f:
        f.write("=" * 60 + "\n")
        f.write("RESULTATS DE VALIDATION DES TESTS\n")
        f.write("=" * 60 + "\n\n")
        f.write(stdout)
        f.write("\n\n=== STDERR ===\n")
        f.write(stderr)
    
    print("\nRésultats détaillés sauvegardés dans: test_validation_results.txt")
    
    total_failed = all_counts['failed']
    if total_failed == 0:
        print("\n✅ SUCCESS: Aucun test échoué!")
        return 0
    else:
        print(f"\n⚠️ {total_failed} tests échouent encore")
        return 1


if __name__ == "__main__":
    sys.exit(main())
