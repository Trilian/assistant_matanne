import subprocess
import sys
import json

result = subprocess.run([
    sys.executable, '-m', 'pytest',
    'tests/integration/test_phase_16_expanded.py',
    '-v'
], capture_output=True, text=True, cwd=r'd:\Projet_streamlit\assistant_matanne')

# Write all output
with open(r'd:\Projet_streamlit\assistant_matanne\phase16_test_output.txt', 'w') as f:
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(result.stderr)
    f.write(f"\n\nReturn code: {result.returncode}")
