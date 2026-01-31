#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace mojibake emojis - file-based approach"""

import sys
import os

# Absolute path
file_path = r"d:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py"

# Read with UTF-8
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

print(f"File size: {len(content)} chars")
before = content.count('📷
print(f"Mojibake count before: {before}")

# Simple replacements - using unicode escape sequences
replacements = [
    # Pattern → Replacement
    ('🎯´', '❌'),      # Line 315
    ('🎯"', '⏰'),      # Lines 327, 537, 713, 1143, 1177 
    ('🎯 ', '📍'),      # Line 353
    ('🎯„', '🔄'),      # Lines 481, 543, 1169
    ('🎯¥', '📥'),      # Line 491
    ("📋, '💡'),      # Line 849
    ("💡, '👁️'),     # Line 977
    ('📅, '📤'),      # Line 977
    ("💰, '❌'),      # Line 1063 (corrected mojibake)
    ('🎯¬', '🔔'),      # Lines 1155, 1189
]

for old_str, new_str in replacements:
    count_before = content.count(old_str)
    content = content.replace(old_str, new_str)
    if count_before > 0:
        print(f"  Replaced '{old_str}' → '{new_str}': {count_before} occurrences")

after = content.count('📷
print(f"\nMojibake count after: {after}")

# Write back with UTF-8 (no BOM)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done!")
