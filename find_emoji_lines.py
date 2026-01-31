#!/usr/bin/env python3
"""Find exact line numbers for emoji replacement"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all tab-related lines
for i, line in enumerate(lines):
    if ('Suggestions IA' in line or 'Historique' in line or 'Photos' in line or
        'Notifications' in line or 'Prévisions' in line or 'Outils' in line) and (
        '        "' in line or 'st.tabs' in line):
        print(f"Line {i} (1-indexed: {i+1}): {repr(line)}")
