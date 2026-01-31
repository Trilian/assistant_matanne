#!/usr/bin/env python3
"""Direct byte-level replacement of corrupted emojis"""

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read as binary
with open(file_path, 'rb') as f:
    data = bytearray(f.read())

# The emojis are UTF-8 bytes but the file is UTF-8 (not corrupted at byte level)
# The rendering shows mojibake which means the terminal/viewer is treating UTF-8 as latin-1
# So we DON'T need to fix the file - the emojis are already correct in the file!

# Let's verify by reading UTF-8 correctly
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check what's really in the file
lines = content.split('\n')
for i, line in enumerate(lines[100:120], start=101):
    if 'Suggestions' in line or 'Historique' in line or 'Photos' in line:
        print(f"Line {i}: {repr(line)}")
        print(f"  Display: {line}")
