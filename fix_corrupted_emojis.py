#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted emojis in inventaire.py"""

import codecs

# Read the file with correct encoding
file_path = "src/domains/cuisine/ui/inventaire.py"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Map of corrupted emoji strings to correct ones (using Unicode escapes)
emoji_replacements = {
    "\udcf0\udcb9\udc9b\udca0": "\U0001f6d2",  # ðŸ›' -> shopping cart
    "\udcf0\udcb9\udca0\udcb9": "\U0001f4cb",  # ðŸ"" -> clipboard  
    "[CAMERA]": "\U0001f4f7",                   # [CAMERA] -> camera
    "\udcf0\udcb9\udca0": "\U0001f4e2",        # ðŸ"" -> megaphone
    "\udcf0\udcb9\udca0\udcae": "\U0001f52e",  # ðŸ"® -> crystal ball
    "\udcf0\udcb9\udca0\udca7": "\U0001f527",  # ðŸ"§ -> wrench
}

# Replace each corrupted emoji
for corrupted, correct in emoji_replacements.items():
    content = content.replace(corrupted, correct)

# Write back with UTF-8 encoding
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed corrupted emojis in inventaire.py")

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[100:120], start=101):
        if "Suggestions" in line or "Historique" in line or "Photos" in line:
            print(f"Line {i}: {line.strip()}")
