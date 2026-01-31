#!/usr/bin/env python3
"""Analyze mojibake without emoji output"""
import sys

file_path = r"d:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py"

with open(file_path, 'rb') as f:
    content_bytes = f.read()

# Find mojibake patterns (ðŸ)
mojibake_start = b'\xc3\xb0\xc2\x9f'  # UTF-8 'ðŸ' as Latin-1 bytes

count = content_bytes.count(mojibake_start)
print(f"Mojibake 'mojibake_start' count: {count}")

# Find specific patterns
patterns = {
    'critical': b'\xc3\xb0\xc2\x9f\xc2\x93\xb4',   # ðŸ"´
    'time': b'\xc3\xb0\xc2\x9f\xc2\x93\x93',       # ðŸ""
    'location': b'\xc3\xb0\xc2\x9f\xc2\x93\xa0',   # ðŸ"
    'refresh': b'\xc3\xb0\xc2\x9f\xc2\x93\x9e',    # ðŸ"„
}

for name, pattern in patterns.items():
    count = content_bytes.count(pattern)
    if count > 0:
        print(f"{name}: {count} found")

# Try different approach - extract emojis from problematic part
idx = content_bytes.find(b'color = ')
if idx >= 0:
    sample = content_bytes[idx:idx+100]
    print(f"\nSample from 'color =' context:")
    print(repr(sample[:50]))
