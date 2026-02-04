import subprocess
import sys
import os

os.chdir(r'd:\Projet_streamlit\assistant_matanne')

# Run Phase 16 tests
print("Running Phase 16 tests...", file=sys.stderr)
result = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tests/integration/test_phase_16_expanded.py',
    '-v', '--tb=short'
], capture_output=False, text=True)

print(f"\nReturn code: {result.returncode}")
