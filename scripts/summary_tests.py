#!/usr/bin/env python3
"""
Script pour afficher un rÃ©sumÃ© des tests crÃ©Ã©s pour src/core
"""
import subprocess
import re

result = subprocess.run(
    ["python", "-m", "pytest", "tests/core/", "--cov=src/core", "--cov-report=term", "--tb=no", "-q"],
    capture_output=True,
    text=True,
    cwd="."
)

output = result.stdout + result.stderr

print("=" * 80)
print("RÃ‰SUMÃ‰ COUVERTURE SRC/CORE - PHASE 1")
print("=" * 80)

# Extraire le rÃ©sumÃ©
lines = output.split('\n')

# Chercher les stats
for i, line in enumerate(lines):
    if 'passed' in line or 'failed' in line:
        print(line)
    if 'Name' in line and 'Stmts' in line:
        # Afficher les 20 lignes suivantes (couverture dÃ©taillÃ©e)
        for j in range(i, min(i+60, len(lines))):
            if 'src\\core' in lines[j]:
                print(lines[j])

# Chercher le TOTAL
for i, line in enumerate(lines):
    if 'TOTAL' in line:
        print("\n" + "=" * 80)
        print(line)
        for j in range(i+1, min(i+3, len(lines))):
            if lines[j].strip():
                print(lines[j])
        print("=" * 80)
