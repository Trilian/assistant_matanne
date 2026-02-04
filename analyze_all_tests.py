#!/usr/bin/env python3
"""Analyser TOUS les tests existants"""
import subprocess
import os
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("📊 ANALYSE COMPLÈTE DES TESTS EXISTANTS")
print("=" * 80)

# 1. Compter fichiers
test_files = list(Path("tests").rglob("test_*.py"))
print(f"\n📁 Fichiers de tests: {len(test_files)}")

# 2. Collecter avec pytest
print("\n🔄 Collection des tests...")
result = subprocess.run(
    ["python", "-m", "pytest", "--collect-only", "-q", "tests/"],
    capture_output=True,
    text=True,
    timeout=120
)

output = result.stdout + result.stderr
lines = output.split('\n')

# Chercher le nombre total
total_tests = 0
for line in lines[-20:]:
    if 'test' in line.lower() and ('collected' in line.lower() or 'deselected' in line.lower()):
        print(f"  {line.strip()}")
        if 'collected' in line.lower():
            try:
                num = int(line.split()[0])
                total_tests = num
                print(f"\n✅ Total tests collectés: {total_tests}")
            except:
                pass

# 3. Analyser par répertoire
print("\n📂 TESTS PAR RÉPERTOIRE:")
print("-" * 80)

dirs_stats = defaultdict(int)
for test_file in test_files:
    rel_path = str(test_file.relative_to("tests"))
    top_dir = rel_path.split(os.sep)[0]
    
    # Compter tests dans ce fichier (approximation: grep def test_)
    with open(test_file) as f:
        content = f.read()
        count = content.count("def test_")
    
    dirs_stats[top_dir] += count

total_from_files = sum(dirs_stats.values())

for directory in sorted(dirs_stats.keys()):
    count = dirs_stats[directory]
    print(f"  {directory:<25} {count:>4} tests")

print("-" * 80)
print(f"  {'TOTAL (estimation)':<25} {total_from_files:>4} tests")

print("\n" + "=" * 80)
print(f"📊 RÉSUMÉ:")
print(f"  • Fichiers de tests:     {len(test_files)}")
print(f"  • Tests (pytest collect): {total_tests}")
print(f"  • Tests (par fichiers):   {total_from_files} (estimation)")
print("=" * 80)
