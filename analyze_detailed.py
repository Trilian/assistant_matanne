#!/usr/bin/env python3
"""Analyse détaillée des tests - génère rapport par module."""

import subprocess
import json
from collections import defaultdict
from pathlib import Path

# Run pytest avec report détaillé
print("Collecte des tests...\n")

result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--tb=no", "-v", "--no-header"],
    capture_output=True,
    text=True
)

output = result.stdout

# Parse results
lines = output.split('\n')
module_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "error": 0, "skipped": 0, "tests": []})

for line in lines:
    if 'tests' in line and ('PASSED' in line or 'FAILED' in line or 'ERROR' in line or 'SKIPPED' in line):
        # Extract file path (tests/xxx/yyy.py::Test)
        parts = line.split('::')
        if len(parts) >= 2:
            test_path = parts[0].strip()
            test_name = parts[1].split()[0] if len(parts[1]) > 0 else ""
            
            # Get folder depth
            path_parts = test_path.replace('\\', '/').split('/')
            if len(path_parts) >= 2:
                folder = path_parts[1] if len(path_parts) > 1 else "root"
                
                # Determine status
                status = "unknown"
                if "PASSED" in line:
                    status = "passed"
                    module_stats[folder]["passed"] += 1
                elif "FAILED" in line:
                    status = "failed"
                    module_stats[folder]["failed"] += 1
                elif "ERROR" in line:
                    status = "error"
                    module_stats[folder]["error"] += 1
                elif "SKIPPED" in line:
                    status = "skipped"
                    module_stats[folder]["skipped"] += 1
                
                module_stats[folder]["tests"].append({
                    "name": f"{test_name}",
                    "status": status,
                    "file": test_path
                })

# Get global stats
total_passed = sum(s["passed"] for s in module_stats.values())
total_failed = sum(s["failed"] for s in module_stats.values())
total_error = sum(s["error"] for s in module_stats.values())
total_skipped = sum(s["skipped"] for s in module_stats.values())
total = total_passed + total_failed + total_error + total_skipped

print("="*100)
print("RÉSUMÉ GLOBAL")
print("="*100)
print(f"✓ Passed:  {total_passed:>5}")
print(f"✗ Failed:  {total_failed:>5}")
print(f"⚠ Error:   {total_error:>5}")
print(f"⊘ Skipped: {total_skipped:>5}")
print(f"─────────────────")
print(f"  Total:   {total:>5}")
print(f"  Pass Rate: {(total_passed/(total_passed+total_failed+total_error)*100):.1f}%")

print("\n" + "="*100)
print("RÉSULTATS PAR MODULE")
print("="*100)
print(f"{'Module':<30} {'Passed':>8} {'Failed':>8} {'Error':>8} {'Skipped':>8} {'Pass %':>10}")
print("-"*100)

# Sort by pass rate (lowest first - most urgent)
sorted_modules = sorted(
    module_stats.items(),
    key=lambda x: (x[1]['passed'] / (x[1]['passed'] + x[1]['failed'] + x[1]['error']) 
                   if (x[1]['passed'] + x[1]['failed'] + x[1]['error']) > 0 else 0)
)

module_priority = []
for module, stats in sorted_modules:
    total_tests = sum(stats.values())
    if total_tests > 0:
        pass_rate = (stats["passed"] / (stats["passed"] + stats["failed"] + stats["error"]) * 100) \
                    if (stats["passed"] + stats["failed"] + stats["error"]) > 0 else 0
        
        priority_score = (stats["failed"] + stats["error"]) * 100 - pass_rate * 10
        module_priority.append((module, stats, pass_rate, priority_score))
        
        print(f"{module:<30} {stats['passed']:>8} {stats['failed']:>8} {stats['error']:>8} {stats['skipped']:>8} {pass_rate:>9.1f}%")

print("\n" + "="*100)
print("MODULES CRITIQUES (À traiter en priorité)")
print("="*100)
print(f"{'Module':<30} {'Failures':>10} {'Pass Rate':>12} {'Priority':>12}")
print("-"*100)

for module, stats, pass_rate, priority in sorted(module_priority, key=lambda x: -x[3])[:15]:
    failures = stats['failed'] + stats['error']
    if failures > 0 or pass_rate < 80:
        print(f"{module:<30} {failures:>10} {pass_rate:>11.1f}% {priority:>11.0f}")

print("\n" + "="*100)
print("STATISTIQUES DÉTAILLÉES")
print("="*100)

# Modules that need most work (high failure count OR low pass rate)
print("\n🔴 MODULES CRITIQUES - Taux de pass < 50%:")
for module, stats, pass_rate, priority in module_priority:
    if pass_rate < 50 and (stats['failed'] + stats['error']) > 0:
        print(f"  - {module}: {stats['failed']} failures, {stats['error']} errors ({pass_rate:.0f}% pass rate)")

print("\n🟠 MODULES IMPORTANTS - Taux de pass 50-80%:")
for module, stats, pass_rate, priority in module_priority:
    if 50 <= pass_rate < 80 and (stats['failed'] + stats['error']) > 0:
        print(f"  - {module}: {stats['failed']} failures, {stats['error']} errors ({pass_rate:.0f}% pass rate)")

print("\n🟡 MODULES À SURVEILLER - Taux de pass 80-95% avec erreurs:")
for module, stats, pass_rate, priority in module_priority:
    if 80 <= pass_rate < 95 and (stats['failed'] + stats['error']) > 0:
        print(f"  - {module}: {stats['failed']} failures, {stats['error']} errors ({pass_rate:.0f}% pass rate)")

print("\n🟢 MODULES OK - Taux de pass > 95%:")
ok_count = 0
for module, stats, pass_rate, priority in module_priority:
    if pass_rate >= 95:
        ok_count += 1
print(f"  {ok_count} modules avec 95%+ pass rate")
