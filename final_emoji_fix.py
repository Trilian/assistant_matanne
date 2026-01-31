#!/usr/bin/env python3
"""Final emoji fixer - using byte replacement"""

import os
from pathlib import Path

# File-specific replacements for accueil.py
accueil_replacements = [
    (b'\xc3\xa9\xc2\xb0\xc2\xb3', b'\xf0\x9f\x93\x83'),  # 🎯 -> 📃
    (b'\xc3\xa9', b'\xc3\xa9'),  # Keep é as é  
    (b'\xc3\xa0', b'\xc3\xa0'),  # Keep à as à
    (b'\xc3\x87', b'\xc3\x87'),  # Keep Ç as Ç
]

def fix_file_accueil():
    """Fix accueil.py specifically"""
    filepath = Path('src/domains/shared/ui/accueil.py')
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    original = content
    
    # These are the actual corrupted byte sequences we need to replace
    replacements = [
        # (corrupted_bytes, fixed_bytes)
        (b'\xc3\xb0\xc2\x9f\xc2\xbd\xc3\xaf\xc2\xb8', b'\xf0\x9f\x8d\xbd'),  # 📅 -> 🍽
        (b'\xc3\xa9\xc2\xb0\xc2\xb3', b'\xf0\x9f\x93\x8e'),  # â°³ -> 📎 (probably)
    ]
    
    for corrupted, fixed in replacements:
        if corrupted in content:
            content = content.replace(corrupted, fixed)
            print(f"Replaced: {corrupted} -> {fixed}")
    
    if content != original:
        with open(filepath, 'wb') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

if __name__ == '__main__':
    # Just report what corruptions exist
    accueil = Path('src/domains/shared/ui/accueil.py')
    with open(accueil, 'rb') as f:
        content = f.read()
    
    # Print unique byte sequences that start with c3 (UTF-8 continuation)
    print("Checking file for corrupted sequences...")
    if b'\xc3\xa9' in content:
        print("  Found: c3 a9 (likely part of corrupted emoji)")
    
    print("\nNote: Emojis are complex. Manual fixes may be needed.")
    print("Consider opening the file in an IDE and replacing visually corrupted text.")
