#!/usr/bin/env python3
"""Analyze coverage gaps and identify priority areas for Phase 17."""
import json
from pathlib import Path
from collections import defaultdict

print("\n" + "="*70)
print("PHASE 17: COVERAGE GAP ANALYSIS")
print("="*70)

# Load coverage data
coverage_file = Path("coverage.json")
data = json.loads(coverage_file.read_text())

# Group by module
modules = defaultdict(lambda: {"files": [], "covered": 0, "total": 0})
files = data.get('files', {})

for filepath, info in files.items():
    if not filepath.startswith('src/'):
        continue
    
    # Parse module path: src/api/... -> api, src/core/... -> core, etc.
    parts = filepath.replace('src/', '').split('/')
    module = parts[0]
    
    summary = info['summary']
    covered = summary['covered_lines']
    total = summary['num_statements']
    
    modules[module]['files'].append({
        'path': filepath,
        'covered': covered,
        'total': total,
        'percent': 100 * covered / total if total > 0 else 0
    })
    
    modules[module]['covered'] += covered
    modules[module]['total'] += total

# Sort by coverage (lowest first - highest priority)
sorted_modules = sorted(
    modules.items(),
    key=lambda x: x[1]['covered'] / max(x[1]['total'], 1)
)

print("\nMODULE COVERAGE (sorted by coverage %):\n")
print(f"{'Module':<15} {'Coverage':<12} {'Lines':<15} {'Priority':<10}")
print("-"*60)

for module, stats in sorted_modules:
    if stats['total'] == 0:
        continue
    
    percent = 100 * stats['covered'] / stats['total']
    line_ratio = f"{stats['covered']}/{stats['total']}"
    
    if percent < 5:
        priority = "🔴 CRITICAL"
    elif percent < 15:
        priority = "🟠 HIGH"
    elif percent < 30:
        priority = "🟡 MEDIUM"
    else:
        priority = "🟢 OK"
    
    print(f"{module:<15} {percent:>6.1f}%      {line_ratio:<15} {priority:<10}")

print("-"*60)

total_covered = data['totals']['covered_lines']
total_lines = data['totals']['num_statements']
global_percent = 100 * total_covered / total_lines

print(f"\n{'TOTAL':<15} {global_percent:>6.1f}%      {total_covered}/{total_lines}")

print("\n" + "="*70)
print("PRIORITY RECOMMENDATIONS FOR PHASE 17:")
print("="*70)

print("\n🔴 CRITICAL (0-5% coverage) - Must test:")
for module, stats in sorted_modules:
    if stats['total'] > 0:
        percent = 100 * stats['covered'] / stats['total']
        if percent < 5:
            print(f"  • {module:<15} {percent:>5.1f}% - Create {stats['total']//10}-{stats['total']//5} tests")

print("\n🟠 HIGH PRIORITY (5-15% coverage) - Should test:")
for module, stats in sorted_modules:
    if stats['total'] > 0:
        percent = 100 * stats['covered'] / stats['total']
        if 5 <= percent < 15:
            print(f"  • {module:<15} {percent:>5.1f}% - Create {stats['total']//20}-{stats['total']//10} tests")

print("\n" + "="*70)
