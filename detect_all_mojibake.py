#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect ALL unique mojibake patterns and create comprehensive mapping"""

from pathlib import Path
import re

# Collect all unique mojibake sequences
mojibake_patterns = set()

root = Path('.')
py_files = [f for f in root.glob('**/*.py') if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)]

print("Scanning for ALL unique mojibake patterns...")

for filepath in py_files:
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            # Find all patterns starting with 🎯
            matches = re.findall(r'📅s,;.\'")\]\}]*', content)
            for match in matches:
                mojibake_patterns.add(match)
    except:
        pass

print(f"\nFound {len(mojibake_patterns)} unique mojibake patterns:")
for pattern in sorted(mojibake_patterns):
    print(f"  '{pattern}'")

# Save for analysis
with open('mojibake_patterns_found.txt', 'w', encoding='utf-8') as f:
    for pattern in sorted(mojibake_patterns):
        # Try to get bytes
        try:
            f.write(f"{pattern}\n")
        except:
            pass
