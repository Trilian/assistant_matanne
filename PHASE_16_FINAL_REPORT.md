#!/usr/bin/env python3
"""
PHASE 16 - RAPPORT FINAL COMPLET
================================
Tests execution and coverage measurement report
"""

import json

# Load coverage data

with open('coverage.json') as f:
data = json.load(f)

print(f"""
{'='*80}
PHASE 16 - FINAL TEST & COVERAGE REPORT
{'='*80}

DATE: February 3, 2026
PROJECT: Assistant Matanne Family Hub
PYTHON: 3.11+
FRAMEWORK: Streamlit + SQLAlchemy 2.0

{'='\*80}

1. TEST EXECUTION SUMMARY
   {'='\*80}

Total Tests Run: 352 (from 376 planned)
• Phase 14-15 Tests: 149 PASSED ✓
• Phase 16 Extended Tests: 203 FAILED ✗

RESULT: 149 passed, 203 failed (42.3% pass rate)

Reason for Phase 16 failures:

- Model field names mismatch (nom, semaine, jour, etc.)
- IntegrityError: NOT NULL constraint violations
- Invalid keyword arguments in model instantiation

Status: Phase 16 extended tests require model fixes before full pass.
The basic Phase 14-15 tests (149/149) are passing successfully.

{'='*80} 2. GLOBAL COVERAGE METRICS
{'='*80}

Overall Project Coverage: {data['totals']['percent_covered']:.2f}%

Detailed Coverage Stats:
• Covered Lines: {data['totals']['covered_lines']:,}
• Total Statements: {data['totals']['num_statements']:,}
• Missing Lines: {data['totals']['missing_lines']:,}
• Excluded Lines: {data['totals']['excluded_lines']:,}

Branch Coverage:
• Covered Branches: {data['totals']['covered_branches']}
• Total Branches: {data['totals']['num_branches']:,}
• Branch Coverage: {data['totals']['percent_branches_covered']:.2f}%

Files Measured: {len(data['files'])} modules

{'='*80} 3. MODULE COVERAGE ANALYSIS
{'='*80}
""")

# Parse modules

modules = {}
for filepath, filedata in data['files'].items(): # Filter for src files (using backslashes on Windows)
if not filepath.startswith('src\\'):
continue

    # Extract module path from Windows path
    parts = filepath.split('\\')

    if len(parts) == 2:
        module = 'root'
        filename = parts[1]
    else:
        module = parts[1]
        filename = '\\'.join(parts[2:])

    if module not in modules:
        modules[module] = {
            'files': {},
            'total_lines': 0,
            'covered_lines': 0
        }

    coverage_pct = filedata['summary'].get('percent_covered', 0)
    num_statements = filedata['summary'].get('num_statements', 0)
    covered_lines = filedata['summary'].get('covered_lines', 0)

    modules[module]['files'][filename] = {
        'coverage': coverage_pct,
        'lines': num_statements,
        'covered': covered_lines
    }

    modules[module]['total_lines'] += num_statements
    modules[module]['covered_lines'] += covered_lines

# Print module summary sorted by coverage

module_list = []
for module, mod_data in modules.items():
if mod_data['total_lines'] == 0:
continue
pct = (mod_data['covered_lines'] / mod_data['total_lines']) \* 100
module_list.append((module, pct, mod_data))

module_list.sort(key=lambda x: x[1], reverse=True)

print("MODULE COVERAGE BREAKDOWN (sorted by coverage %):")
print(f"{'Module':<20} {'Coverage':<12} {'Lines':<20}")
print("-" \* 52)

for module, pct, mod_data in module_list:
status = "🟢" if pct >= 40 else "🟡" if pct >= 20 else "🔴"
print(f"{module:<20} {pct:>6.2f}% {mod_data['covered_lines']:>5}/{mod_data['total_lines']:<5} lines")

print()
print("=" _ 80)
print("4. TOP 10 MODULES BY COVERAGE")
print("=" _ 80)
for i, (module, pct, mod_data) in enumerate(module_list[:10], 1):
bar_length = int(pct / 5)
bar = "█" _ bar_length + "░" _ (20 - bar_length)
print(f"{i:2d}. {module:<15} {pct:>6.2f}% [{bar}]")

print()
print("=" _ 80)
print("5. FILES < 60% COVERAGE ANALYSIS")
print("=" _ 80)

all_files = []
for module, mod_data in modules.items():
for filename, file_stats in mod_data['files'].items():
all_files.append({
'module': module,
'file': filename,
'coverage': file_stats['coverage'],
'lines': file_stats['lines'],
'covered': file_stats['covered']
})

# Sort by coverage

all_files.sort(key=lambda x: x['coverage'])

# Files < 60%

under_60 = [f for f in all_files if f['coverage'] < 60]

print(f"Total files < 60%: {len(under_60)} / {len(all_files)}")
print(f"Total files >= 60%: {len(all_files) - len(under_60)} / {len(all_files)}")
print()
print("Bottom 15 files (lowest coverage):")
print(f"{'Coverage':<12} {'Lines':<20} {'File Path':<50}")
print("-" \* 82)

for f in under_60[:15]:
full_path = f"{f['module']}/{f['file']}"
line_info = f"{f['covered']}/{f['lines']}"
print(f"{f['coverage']:>6.2f}% {line_info:>18} {full_path:<50}")

if len(under_60) > 15:
print(f"\n... and {len(under_60) - 15} more files < 60%")

print()
print("=" _ 80)
print("6. COVERAGE BREAKDOWN BY SEVERITY")
print("=" _ 80)

coverage_ranges = [
(80, 100, "Excellent"),
(60, 80, "Good"),
(40, 60, "Fair"),
(20, 40, "Poor"),
(0, 20, "Critical")
]

for min_cov, max_cov, label in coverage_ranges:
count = len([f for f in all_files if min_cov <= f['coverage'] < max_cov])
pct_of_total = (count / len(all_files)) \* 100 if all_files else 0
print(f"{label:<12} ({min_cov:>2d}-{max_cov:<2d}%): {count:>3d} files ({pct_of_total:>5.1f}%)")

print()
print("=" _ 80)
print("7. KEY INSIGHTS & RECOMMENDATIONS")
print("=" _ 80)

highest_covered = max(module_list, key=lambda x: x[1])
lowest_covered = min(module_list, key=lambda x: x[1])

print(f"""
✓ Best Performing Module: {highest_covered[0]} ({highest_covered[1]:.2f}%)
✗ Worst Performing Module: {lowest_covered[0]} ({lowest_covered[1]:.2f}%)

📊 Coverage Distribution:
• Strong Core (>40%): {len([f for f in all_files if f['coverage'] >= 40])} files
• Moderate (20-40%): {len([f for f in all_files if 20 <= f['coverage'] < 40])} files  
 • Critical (<20%): {len([f for f in all_files if f['coverage'] < 20])} files

🎯 Priority Actions:

1. Fix Phase 16 model errors (field name mismatches)
2. Increase 'domains' module coverage (currently 1.00%)
3. Add API endpoint tests (currently 0% coverage)
4. Add UI component tests (currently 0% coverage)
5. Strengthen utils module tests (currently 12.57%)

📈 Expected After Fixes:
• With Phase 16 fixes: Coverage should reach 15-20%
• With API tests: Coverage could reach 25-30%
• With full UI coverage: Coverage could reach 40%+

{'='*80} 8. TEST FILE SUMMARY
{'='*80}

Executed Test Files:
✓ tests/services/test_services_basic.py
✓ tests/services/test_services_integration.py
✓ tests/models/test_models_basic.py
✓ tests/core/test_decorators_basic.py
✓ tests/utils/test_utils_basic.py
✓ tests/integration/test_domains_integration.py
✓ tests/integration/test_business_logic.py
⚠ tests/integration/test_phase16_extended.py (203 failures - model issues)

{'='*80} 9. NEXT STEPS
{'='*80}

Phase 16 Issues to Resolve:

1. Review src/core/models/ for field naming inconsistencies
2. Update test_phase16_extended.py model instantiation
3. Fix NOT NULL constraint violations
4. Re-run full test suite after model fixes

Expected Timeline:
• Fix model issues: 1-2 hours
• Re-run tests: 10-15 minutes
• Validate coverage increase: 5 minutes
• Generate final Phase 16 report: 5 minutes

{'='\*80}
""")

# Summary statistics

print(f"FINAL STATISTICS:")
print(f" Total Source Files: {len(all_files)}")
print(f" Total Lines of Code: {sum(f['lines'] for f in all_files):,}")
print(f" Total Covered Lines: {sum(f['covered'] for f in all_files):,}")
print(f" Global Coverage: {data['totals']['percent_covered']:.2f}%")
print(f" Tests Passed: 149/352 (42.3%)")
print(f" Tests Failed: 203/352 (57.7%)")
print()
print("=" _ 80)
print("Report generated: February 3, 2026")
print("=" _ 80)
