#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyse précise des 260 failures par module."""

import subprocess
from collections import defaultdict
import re

print("Scanning failures...\n")

# Run pytest et collecter les failures
result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--tb=no", "-v"],
    capture_output=True,
    text=True,
    timeout=180
)

output = result.stdout + result.stderr
lines = output.split('\n')

# Parse failures par module
failures_by_module = defaultdict(list)
module_summary = defaultdict(lambda: {"failed": 0, "error": 0, "passed": 0, "skipped": 0})

for line in lines:
    if 'FAILED' in line or 'ERROR' in line or 'PASSED' in line or 'SKIPPED' in line:
        # Extraire le chemin du test
        match = re.search(r'tests[/\\]([a-zA-Z0-9_/-]+)[/\\]', line)
        if match:
            module = match.group(1)
            
            # Déterminer le status
            if 'FAILED' in line:
                module_summary[module]["failed"] += 1
                # Extraire le test name
                test_match = re.search(r'::([a-zA-Z0-9_:]+)\s', line)
                if test_match:
                    failures_by_module[module].append(test_match.group(1))
            elif 'ERROR' in line:
                module_summary[module]["error"] += 1
                test_match = re.search(r'::([a-zA-Z0-9_:]+)\s', line)
                if test_match:
                    failures_by_module[module].append(f"ERROR: {test_match.group(1)}")
            elif 'PASSED' in line:
                module_summary[module]["passed"] += 1
            elif 'SKIPPED' in line:
                module_summary[module]["skipped"] += 1

# Trier par nombre de failures
print("="*100)
print("FAILURES PAR MODULE (Trie par impact)")
print("="*100)
print(f"{'Module':<40} {'Failed':>8} {'Error':>8} {'Total Issues':>15}")
print("-"*100)

sorted_modules = sorted(
    module_summary.items(),
    key=lambda x: (x[1]['failed'] + x[1]['error']),
    reverse=True
)

total_failed = 0
total_error = 0

for module, stats in sorted_modules:
    failed = stats['failed']
    error = stats['error']
    total_issues = failed + error
    
    if total_issues > 0:
        total_failed += failed
        total_error += error
        print(f"{module:<40} {failed:>8} {error:>8} {total_issues:>15}")

print("-"*100)
print(f"{'TOTAL':<40} {total_failed:>8} {total_error:>8} {total_failed + total_error:>15}")

print("\n" + "="*100)
print("TOP 10 MODULES AVEC FAILURES")
print("="*100)

for i, (module, stats) in enumerate(sorted_modules[:10], 1):
    failed = stats['failed']
    error = stats['error']
    if failed + error > 0:
        print(f"\n{i}. {module}")
        print(f"   X {failed} failures, ! {error} errors")
        if module in failures_by_module and len(failures_by_module[module]) <= 10:
            for test in failures_by_module[module][:5]:
                print(f"      - {test}")
            if len(failures_by_module[module]) > 5:
                print(f"      ... et {len(failures_by_module[module]) - 5} autres")

print("\n" + "="*100)
print("RÉSUMÉ")
print("="*100)
print(f"Total failures: {total_failed}")
print(f"Total errors: {total_error}")
print(f"Total issues: {total_failed + total_error}")
print(f"\nModules affectés: {len([m for m, s in sorted_modules if s['failed'] + s['error'] > 0])}")
