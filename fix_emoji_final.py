#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Properly fix the emoji corruption by encoding/decoding correctly"""

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read file as binary
with open(file_path, 'rb') as f:
    data = f.read()

# The data is actually UTF-8 bytes that got decoded as latin-1 back to strings
# So the mojibake strings like "Ã°Å¸" are the latin-1 interpretation of UTF-8 bytes

# To fix: re-encode as latin-1, decode as UTF-8, then fix specific patterns
try:
    corrupted_str = data.decode('utf-8')
except:
    # If it's really corrupted, try latin-1 first then we'll fix
    corrupted_str = data.decode('latin-1')

# Find and replace corrupted patterns using regex
import re

# Pattern 1: "Ã°Å¸â€ºâ€™ Suggestions IA" - this is 🛒
# Pattern 2: [CAMERA] - should be 📷
# Pattern 3: "Ã°Å¸â€" Notifications" - should be 📢
# etc

replacements = [
    (r'Ã°Å¸â\x80ºâ\x80\x99', '🛒'),     # Shopping cart
    (r'Ã°Å¸â\x80œ', '📋'),              # Clipboard/Historique
    (r'\[CAMERA\]', '📷'),               # Camera/Photos
    (r'Ã°Å¸â\x80\x9c', '📢'),            # Megaphone/Notifications
    (r'Ã°Å¸â\x80®', '🔮'),              # Crystal ball/Prévisions
    (r'Ã°Å¸â\x80§', '🔧'),              # Wrench/Outils
]

fixed_str = corrupted_str
for pattern, replacement in replacements:
    fixed_str = re.sub(pattern, replacement, fixed_str)

# Write back as UTF-8
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_str)

print("✅ Fixed all corrupted emojis")

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    for line in content.split('\n')[100:115]:
        if 'Suggestions' in line or 'Historique' in line or 'Photos' in line or 'Notifications' in line:
            print(f"✓ {line.strip()}")
