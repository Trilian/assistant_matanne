#!/usr/bin/env python3
"""Strategic test sampling to check status without running all 3210 tests"""
import subprocess
import sys
import time

def run_test_module(module_path, description):
    """Run tests in a module and return summary stats"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"File: {module_path}")
    print('='*60)
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', module_path, '--tb=no', '-q'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd='.'
    )
    elapsed = time.time() - start
    
    # Parse output
    output = result.stdout
    lines = output.split('\n')
    
    # Find summary line
    for line in reversed(lines):
        if 'passed' in line or 'failed' in line or 'error' in line:
            print(f"Result: {line.strip()}")
            print(f"Time: {elapsed:.1f}s")
            return line.strip()
    
    return "Could not parse result"

# Strategic test sampling
test_modules = [
    ('tests/api/test_api_endpoints_basic.py', 'Week 1 Endpoints (78 tests)'),
    ('tests/services/test_maison_extended.py', 'Budget Extended (36 tests) - NOW XFAIL'),
    ('tests/services/test_planning_extended.py', 'Planning Extended (27 tests) - NOW XFAIL'),
]

print("\nSTRATEGIC TEST SAMPLING")
print("="*60)
results = {}
for module, desc in test_modules:
    try:
        summary = run_test_module(module, desc)
        results[desc] = summary
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT on {desc}")
        results[desc] = "TIMEOUT"
    except Exception as e:
        print(f"ERROR on {desc}: {e}")
        results[desc] = f"ERROR: {e}"

print("\n" + "="*60)
print("SUMMARY OF SAMPLING")
print("="*60)
for desc, result in results.items():
    print(f"{desc:50} => {result}")
