#!/usr/bin/env python3
"""Quick check of test status after xfail conversion"""
import subprocess
import sys
import re

# Run pytest with minimal output to get summary
result = subprocess.run(
    [sys.executable, '-m', 'pytest', '--co', '-q', '--tb=no'],
    capture_output=True,
    text=True,
    cwd='.',
    timeout=30
)

# Count test collection lines
lines = result.stdout.split('\n')
test_count = 0
for line in lines:
    if '::test_' in line and ('test_' in line):
        test_count += 1
        
print(f"Tests collected: {test_count}")
print(f"\nLast 5 lines of collection output:")
for line in lines[-5:]:
    if line.strip():
        print(line)

# Now run a quick subset to get status
print("\n" + "="*60)
print("Running sample tests to verify status...")
print("="*60 + "\n")

result2 = subprocess.run(
    [sys.executable, '-m', 'pytest', 
     'tests/api/test_api_endpoints_basic.py', 
     '--tb=no', '-q', '--maxfail=5'],
    capture_output=True,
    text=True,
    cwd='.',
    timeout=60
)

# Extract summary
output = result2.stdout + result2.stderr
match = re.search(r'(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+error|(\d+)\s+xfail|(\d+)\s+skip', output)
if match:
    lines = output.split('\n')
    for line in lines[-10:]:
        if 'passed' in line or 'failed' in line or 'error' in line:
            print(line)
