#!/usr/bin/env python
"""Test runner that captures output to file"""
import subprocess
import sys
import json
import os

os.chdir(r'd:\Projet_streamlit\assistant_matanne')

output = []

# Task 1: Phase 16 tests
output.append("="*80)
output.append("TASK 1: RUNNING PHASE 16 TESTS")
output.append("="*80)

result1 = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tests/integration/test_phase_16_expanded.py',
    '-v', '--tb=short'
], capture_output=True, text=True)

output.append(result1.stdout)
if result1.stderr:
    output.append("STDERR:")
    output.append(result1.stderr)

# Task 2: Coverage analysis
output.append("")
output.append("="*80)
output.append("TASK 2: RUNNING COMBINED COVERAGE TESTS")
output.append("="*80)

test_files = [
    'tests/services/test_services_basic.py',
    'tests/services/test_services_integration.py',
    'tests/models/test_models_basic.py',
    'tests/core/test_decorators_basic.py',
    'tests/utils/test_utils_basic.py',
    'tests/integration/test_domains_integration.py',
    'tests/integration/test_business_logic.py',
    'tests/integration/test_phase_16_expanded.py'
]

result2 = subprocess.run([
    sys.executable, '-m', 'pytest'
] + test_files + [
    '--cov=src',
    '--cov-report=json',
    '-q'
], capture_output=True, text=True)

output.append(result2.stdout)
if result2.stderr:
    output.append("STDERR:")
    output.append(result2.stderr)

# Read coverage.json
output.append("")
output.append("="*80)
output.append("LOOKING FOR COVERAGE DATA")
output.append("="*80)

coverage_file = None
for fname in ['.coverage/coverage.json', 'coverage.json']:
    if os.path.exists(fname):
        coverage_file = fname
        break

if coverage_file:
    output.append(f"Found coverage file: {coverage_file}")
    with open(coverage_file, 'r') as f:
        coverage_data = json.load(f)
    output.append(json.dumps(coverage_data.get('totals', {}), indent=2))
else:
    output.append("ERROR: Could not find coverage.json")

# Write output
with open('test_execution_results.txt', 'w') as f:
    f.write('\n'.join(output))

print("Results written to test_execution_results.txt")
