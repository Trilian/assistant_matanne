#!/usr/bin/env python3
"""Find and replace using hex pattern extraction"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

# Read file as bytes
with open(file_path, 'rb') as f:
    data = f.read()

# Find actual hex patterns in the file by looking for mojibake context
# Look for: 'ðŸ' pattern which is 0xC3 0xB0 0xC2 0x9F when UTF-8 is mis-decoded as Latin-1

# Extract the problematic bytes
sample_hex = data[5000:5100]

# Find all occurrences of UTF-8 bytes misinterpreted as Latin-1
# UTF-8 emoji 📅 is F0 9F 93 85
# Interpreted as Latin-1: ðŸ"…  which is C3 B0 C2 9F C2 93 C2 85

import struct

def find_mojibake_patterns(data, sample_count=10):
    """Find patterns of mojibake emoji bytes"""
    mojibake_marker = b'\xc3\xb0\xc2\x9f'  # ðŸ prefix
    
    indices = []
    start = 0
    while True:
        idx = data.find(mojibake_marker, start)
        if idx == -1:
            break
        # Get 10 bytes for context
        pattern = data[idx:idx+10]
        indices.append((idx, pattern))
        start = idx + 1
        if len(indices) > sample_count:
            break
    
    return indices

patterns = find_mojibake_patterns(data)
with open('hex_patterns.txt', 'wb') as f:
    for idx, pattern in patterns:
        f.write(f"Index {idx}: {repr(pattern)}\n".encode())

# Now replace using byte sequences
# The key insight: each emoji-as-mojibake follows the pattern:
# C3 B0 (ð) + C2 9F (Ÿ) + [2 more bytes]

replacements_hex = [
    (b'\xc3\xb0\xc2\x9f\xc2\x93\xb4', b'\xe2\x9d\x8c'),    # ðŸ"´ → ❌
    (b'\xc3\xb0\xc2\x9f\xc2\x93\x93', b'\xe2\x8f\xb0'),    # ðŸ"" → ⏰
    (b'\xc3\xb0\xc2\x9f\xc2\x93\xa0', b'\xf0\x9f\x93\x8d'), # ðŸ"  → 📍
    (b'\xc3\xb0\xc2\x9f\xc2\x93\x9e', b'\xf0\x9f\x94\x84'),  # ðŸ"„ → 🔄
    (b'\xc3\xb0\xc2\x9f\xc2\x93\xa5', b'\xf0\x9f\x93\xa5'), # ðŸ"¥ → 📥
]

replaced_count = 0
for old_hex, new_hex in replacements_hex:
    if old_hex in data:
        old_count = data.count(old_hex)
        data = data.replace(old_hex, new_hex)
        replaced_count += old_count

# Write back as binary
with open(file_path, 'wb') as f:
    f.write(data)

with open('hex_replacement_result.txt', 'w') as log:
    log.write(f"Hex replacements made: {replaced_count}\n")
