#!/usr/bin/env python3
"""Fix ALL corrupted emojis across entire codebase"""

import os
from pathlib import Path

base_dir = Path(r'd:\Projet_streamlit\assistant_matanne')

# Build emoji fixes using byte patterns to avoid source encoding issues
emoji_fixes = []

# Use byte sequences instead of strings to avoid Python source encoding
import re

# Scan all Python files
fixed_files = []
for py_file in base_dir.rglob('*.py'):
    # Skip venv, __pycache__, etc.
    if '.venv' in py_file.parts or '__pycache__' in py_file.parts or '.git' in py_file.parts:
        continue
    
    try:
        with open(py_file, 'rb') as f:
            content = f.read()
        
        original = content
        
        # Replace corrupted byte sequences (detected from earlier analysis)
        # Using raw bytes to avoid Python encoding issues
        fixes = [
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa6', b'[PKG]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc5\xa0', b'[CHART]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9b\xe2\x80\x99', b'[CART]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc5\xb0', b'[SCROLL]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xb8', b'[CAMERA]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xe2\x80\x9c', b'[NOTE]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xae', b'[MAIL]'),
            (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa7', b'[WATER]'),
            (b'\xc3\xaa\xc5\xa1\xc2\xa0\xc3\xaf\xc2\xb8', b'[!]'),
        ]
        
        for broken, fixed in fixes:
            content = content.replace(broken, fixed)
        
        if content != original:
            with open(py_file, 'wb') as f:
                f.write(content)
            fixed_files.append(str(py_file.relative_to(base_dir)))
    except Exception as e:
        print(f"Error processing {py_file}: {e}")

if fixed_files:
    for f in fixed_files[:20]:  # Show first 20
        print(f"Fixed {f}")
    if len(fixed_files) > 20:
        print(f"... and {len(fixed_files) - 20} more files")
else:
    print("No corrupted emojis found or all already fixed")

