#!/usr/bin/env python3
"""Extract coverage report summary"""
import subprocess
import re

result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--cov=src", "--cov-report=term", "-q", "--tb=no"],
    capture_output=True,
    text=True,
    cwd=r"d:\Projet_streamlit\assistant_matanne"
)

# Print last 150 lines which should contain coverage report
lines = result.stdout.split('\n')
print('\n'.join(lines[-150:]))
