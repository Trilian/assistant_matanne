#!/usr/bin/env python3
"""Binary approach to emoji replacement"""
import sys
import os

file_path = r"d:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py"

# Read as UTF-8 bytes
with open(file_path, 'rb') as f:
    content_bytes = f.read()

print(f"File size: {len(content_bytes)} bytes")

# Decode with 'replace' errors to see actual bytes
content_str = content_bytes.decode('utf-8', errors='replace')
print(f"Mojibake count: {content_str.count(chr(0xd8) + chr(0x9f))}")

# Build exact mojibake patterns (UTF-8 bytes for 'ðŸ' combinations)
# When UTF-8 is interpreted as Latin-1, you get mojibake
# UTF-8 encoding of emoji: 4 bytes starting with F0 9F (actually it's mixed encoding)

# The actual bytes in the file are UTF-8 interpreted as Latin-1
# So we need to find those byte sequences and replace them

# For example: 📅 in UTF-8 is: F0 9F 93 85
# Interpreted as Latin-1: ðŸ"…

# Let's see what bytes are actually there
print("\nSample mojibake bytes from line 315:")
sample = content_bytes[5000:5050]
print(repr(sample))

# Now let's find the actual byte patterns
patterns = [
    (b'\xc3\xb0\xc2\x9f\xc2\x93\xb4', b'\xe2\x9d\x8c'),   # ðŸ"´ → ❌
    (b'\xc3\xb0\xc2\x9f\xc2\x93\x93', b'\xe2\x8f\xb0'),   # ðŸ"" → ⏰
    (b'\xc3\xb0\xc2\x9f\xc2\x93\xa0', b'\xf0\x9f\x93\x8d'),  # ðŸ"  → 📍
]

for old_bytes, new_bytes in patterns:
    count = content_bytes.count(old_bytes)
    if count > 0:
        print(f"Found {count} occurrences of {repr(old_bytes)}")
        content_bytes = content_bytes.replace(old_bytes, new_bytes)

# Write back
with open(file_path, 'wb') as f:
    f.write(content_bytes)

print("\nDone!")
