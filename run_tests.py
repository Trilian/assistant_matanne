#!/usr/bin/env python
import subprocess
import sys
import json

# Task 1: Phase 16 tests
print("=" * 80)
print("TASK 1: RUNNING PHASE 16 TESTS")
print("=" * 80)

result1 = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tests/integration/test_phase_16_expanded.py',
    '-v', '--tb=short'
], capture_output=True, text=True)

print(result1.stdout)
print(result1.stderr)

# Task 2: Coverage analysis
print("\n" + "=" * 80)
print("TASK 2: RUNNING COMBINED COVERAGE TESTS")
print("=" * 80)

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

print(result2.stdout)
print(result2.stderr)

# Read coverage.json
try:
    with open('.coverage/coverage.json', 'r') as f:
        coverage_data = json.load(f)
except FileNotFoundError:
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: Could not find coverage.json")
        coverage_data = None

if coverage_data:
    print("\n" + "=" * 80)
    print("COVERAGE DATA")
    print("=" * 80)
    print(json.dumps(coverage_data.get('totals', {}), indent=2))
