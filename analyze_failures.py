#!/usr/bin/env python3
"""Analyse les résultats des tests par module."""

import subprocess
import re
from collections import defaultdict
from pathlib import Path

# Run pytest and capture output
result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--tb=no", "-v"],
    capture_output=True,
    text=True,
    cwd="."
)

output = result.stdout + result.stderr

# Parse results
lines = output.split('\n')
summary_line = [l for l in lines if 'passed' in l and ('failed' in l or 'error' in l or 'skipped' in l)]

print("="*80)
print("RÉSUMÉ GLOBAL")
print("="*80)
for line in summary_line[-3:]:
    print(line)

# Analyze by module
module_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "error": 0, "skipped": 0})

for line in lines:
    if 'PASSED' in line or 'FAILED' in line or 'ERROR' in line or 'SKIPPED' in line:
        # Extract module path
        match = re.search(r'tests[/\\]([^/\\]+)', line)
        if match:
            module = match.group(1)
            if 'PASSED' in line:
                module_stats[module]["passed"] += 1
            elif 'FAILED' in line:
                module_stats[module]["failed"] += 1
            elif 'ERROR' in line:
                module_stats[module]["error"] += 1
            elif 'SKIPPED' in line:
                module_stats[module]["skipped"] += 1

print("\n" + "="*80)
print("RÉSULTATS PAR MODULE")
print("="*80)
print(f"{'Module':<30} {'Passed':>8} {'Failed':>8} {'Error':>8} {'Skipped':>8} {'Pass %':>8}")
print("-"*80)

for module in sorted(module_stats.keys()):
    stats = module_stats[module]
    total = sum(stats.values())
    pass_rate = (stats["passed"] / total * 100) if total > 0 else 0
    print(f"{module:<30} {stats['passed']:>8} {stats['failed']:>8} {stats['error']:>8} {stats['skipped']:>8} {pass_rate:>7.1f}%")

print("\n" + "="*80)
print("MODULES CRITIQUES (Lowest Pass Rate)")
print("="*80)

# Sort by pass rate
sorted_modules = sorted(
    module_stats.items(),
    key=lambda x: (x[1]['passed'] / (sum(x[1].values()) or 1)) if sum(x[1].values()) > 0 else 0
)

for module, stats in sorted_modules[:10]:
    total = sum(stats.values())
    if total > 0:
        pass_rate = stats["passed"] / total * 100
        print(f"{module:<30} {stats['failed']:>3} failures, {stats['error']:>3} errors - Pass rate: {pass_rate:>5.1f}%")
