#!/usr/bin/env python3
"""Extract actual hex patterns from the file"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'rb') as f:
    data = f.read()

# Find all instances of mojibake by looking for the ð character (0xC3 0xB0) followed by Ÿ (0xC2 0x9F)
mojibake_indices = []
for i in range(len(data) - 3):
    if data[i:i+2] == b'\xc3\xb0':  # ð
        if data[i+2:i+4] == b'\xc2\x9f':  # Ÿ
            # Found "📅 - extract the next few bytes
            pattern = data[i:i+10]
            mojibake_indices.append((i, pattern.hex()))

# Write patterns to file
with open('mojibake_patterns_hex.txt', 'w') as f:
    f.write(f"Total mojibake patterns found: {len(mojibake_indices)}\n\n")
    for idx, hex_str in mojibake_indices[:50]:  # First 50
        f.write(f"Offset {idx}: {hex_str}\n")
