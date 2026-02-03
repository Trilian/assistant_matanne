#!/usr/bin/env python
"""Script pour exécuter pytest avec couverture et sauvegarder les résultats."""
import subprocess
import sys
import os
import json

os.chdir(r"d:/Projet_streamlit/assistant_matanne")

print("Running pytest with coverage...")

# Run pytest with JSON coverage output
result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', 
     '--cov=src', 
     '--cov-report=json:coverage.json',
     '--cov-report=term-missing',
     '-v', '--tb=short'],
    capture_output=True,
    text=True,
    timeout=600
)

# Save full output
output = result.stdout + "\n" + result.stderr
with open('coverage_output.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Output saved to coverage_output.txt ({len(output)} chars)")
print(f"Return code: {result.returncode}")

# Read and display coverage summary
try:
    with open('coverage.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    totals = data.get('totals', {})
    print(f"\nCoverage: {totals.get('percent_covered', 0):.1f}%")
    print(f"Lines: {totals.get('covered_lines', 0)}/{totals.get('num_statements', 0)}")
except Exception as e:
    print(f"Error reading coverage.json: {e}")
