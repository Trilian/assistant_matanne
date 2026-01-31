#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted emojis using raw hex replacement"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'rb') as f:
    data = f.read()

# The corrupted emojis are UTF-8 sequences incorrectly interpreted as latin-1
# When a UTF-8 emoji like 🛒 (F0 9F 9B 92) is read as latin-1, we get mojibake
# We need to find and replace these byte sequences

# Shopping cart emoji 🛒 = U+1F6D2 = F0 9F 9B 92 in UTF-8
# When misinterpreted as latin-1: 🎯
# Original latin-1 bytes: D0 9F 9B 92

# Let me check what's actually in the file
print("Looking for the problematic strings...")
if b"Suggestions IA" in data:
    idx = data.find(b"Suggestions IA")
    print(f"Found bytes before 'Suggestions IA': {data[idx-30:idx].hex()}")
    snippet = data[idx-30:idx]
    print(f"ASCII representation: {snippet}")
    print()

# The real issue: The bytes are Latin-1 encoded mojibake
# D0 = 'ð' (U+00D0 in unicode)
# 9F = ' ' + some control char, becomes 'Ÿ'  (U+0178)
# 9B = ' ' + control, becomes '›' (U+203A)
# 92 = ' ' + control, becomes ''' (U+2019)

# So the byte sequence is: [0xd0, 0x9f, 0x9b, 0x92] = "📅

# But we need the actual bytes from the file
import re

# Read as latin-1 to preserve the mojibake bytes
with open(file_path, 'r', encoding='latin-1') as f:
    content = f.read()

# Now replace the mojibake with proper emojis
# The mojibake patterns are the UTF-8 byte sequences interpreted as latin-1
mojibake_to_emoji = {
    '\xd0\x9f\x9b\x92': '🛒',  # Shopping cart (bytes D0 9F 9B 92)
    '\xd0\x9f\x92\x9b': '📋',  # Clipboard  (checking pattern)
    '\xd0\x9f\x92\x97': '📗',  # Green book? (checking)
    '\xd0\x9f\x92\x98': '📘',  # Blue book? (checking)
    '[CAMERA]': '📷',
}

# Actually, let me just search for the specific mojibake patterns we know are there
# by finding lines with "Suggestions IA"
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'Suggestions' in line and 'Tab' not in line:
        print(f"Line {i+1}: {repr(line)}")
        # Extract the emoji part
        if line.startswith('        "'):
            emoji_part = line[8:15]  # Get the emoji + space
            print(f"  Emoji bytes: {emoji_part.encode('utf-8').hex()}")
            print(f"  As latin-1: {emoji_part}")

# Let me try a different approach - looking for the actual byte patterns
print("\n\nSearching file for mojibake patterns...")
for pattern_bytes in [b'\xd0\x9f\x9b\x92', b'\xd0\x9f\x92\x9b', b'\xd0\x9f\x92\x97']:
    count = data.count(pattern_bytes)
    if count > 0:
        print(f"Found {count} occurrences of {pattern_bytes.hex()}")

# Check for "[CAMERA]"
camera_count = data.count(b'[CAMERA]')
print(f"Found {camera_count} occurrences of [CAMERA]")
