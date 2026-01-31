#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect ALL unique mojibake patterns"""

import re
from pathlib import Path

mojibake_prefix = b'\xc3\xb0\xc5\xb8'
suffixes = set()

for filepath in Path('.').glob('**/*.py'):
    if '__pycache__' not in str(filepath) and '.venv' not in str(filepath):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            matches = re.finditer(mojibake_prefix + b'[^\x00-\x1f\x7f]{1,6}', content)
            for match in matches:
                full_pattern = match.group()
                suffix = full_pattern[len(mojibake_prefix):]
                suffixes.add(suffix)
        except:
            pass

print(f'Found {len(suffixes)} unique mojibake patterns:\n')
for s in sorted(suffixes):
    print(f'  Hex: {s.hex():20s} ({len(s)} bytes)')

# Try to determine what emoji each should be based on common ones
emoji_guess = {
    'c5bdc2af': '🎯',
    'c5bdc2a8': '🎨',
    'c29dbdcda2a08' : '🍽️',
    'c29da8': '👀',
    'c291': '👶 or family',
}

print('\n\nKnown patterns:')
for hex_pattern, guess in emoji_guess.items():
    if any(s.hex().startswith(hex_pattern) for s in suffixes):
        print(f'  {hex_pattern}: {guess}')
