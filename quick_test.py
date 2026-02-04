"""Run tests and save results to file."""
import subprocess
import sys
import os

os.chdir(r"D:\Projet_streamlit\assistant_matanne")

# Write directly to file
with open("quick_test_result.txt", "w") as f:
    # Run a quick test to check syntax
    result = subprocess.run(
        [sys.executable, "-c", "print('Python works'); import pytest; print(f'pytest version: {pytest.__version__}')"],
        capture_output=True, text=True
    )
    f.write("=== Python Check ===\n")
    f.write(result.stdout + "\n")
    f.write(result.stderr + "\n")
    
    # Collect tests
    f.write("\n=== Collecting Tests ===\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/core/", "--collect-only", "-q"],
        capture_output=True, text=True, timeout=120
    )
    lines = (result.stdout + result.stderr).split('\n')
    f.write(f"Lines collected: {len(lines)}\n")
    # Just count tests
    test_count = sum(1 for line in lines if '::test_' in line or '::Test' in line)
    f.write(f"Test count in core: ~{test_count}\n")
    
    # Run quick subset of tests
    f.write("\n=== Running Core Tests (first 10 failures) ===\n")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/core/", "-x", "-v", "--tb=line", "-q", "--maxfail=10"],
        capture_output=True, text=True, timeout=300
    )
    f.write(result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout)
    f.write("\n--- STDERR ---\n")
    f.write(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

print("Results written to quick_test_result.txt")
