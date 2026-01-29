#!/usr/bin/env python3
"""Fix ALL remaining emojis in core files"""

from pathlib import Path

base_dir = Path(r'd:\Projet_streamlit\assistant_matanne')

# Map emojis to text (using bytes to avoid Python encoding issues)
emoji_byte_fixes = [
    # Common emojis in logging
    (b'\xe2\x9c\x85', b'[OK]'),  # ✅
    (b'\xe2\x9d\x8c', b'[ERROR]'),  # ❌
    (b'\xe2\x9a\xa0\xef\xb8\x8f', b'[!]'),  # ⚠️
    (b'\xf0\x9f\x93\x8a', b'[CHART]'),  # 📊
    (b'\xf0\x9f\x94\x8d', b'[SEARCH]'),  # 🔍
]

# Scan src/core files
for py_file in (base_dir / 'src' / 'core').rglob('*.py'):
    try:
        with open(py_file, 'rb') as f:
            content = f.read()
        
        original = content
        for broken, fixed in emoji_byte_fixes:
            content = content.replace(broken, fixed)
        
        if content != original:
            with open(py_file, 'wb') as f:
                f.write(content)
            print(f"Fixed {py_file.name}")
    except Exception as e:
        print(f"Error {py_file.name}: {e}")

print("Core files fixed")
