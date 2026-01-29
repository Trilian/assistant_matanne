#!/usr/bin/env python3
"""Fix all corrupted emojis across the entire codebase"""

import os
from pathlib import Path

# Base directory
base_dir = Path(r'd:\Projet_streamlit\assistant_matanne')

# Emoji mappings using Unicode codepoints (no emojis in source to avoid encoding issues)
emoji_fixes = [
    # Use hex patterns to avoid encoding issues in Python source
    ('ðŸ"¦', chr(0x1F4E6)),  # package
    ('ðŸ"Š', chr(0x1F4CA)),  # chart
    ('ðŸ›\'', chr(0x1F6D2)),  # shopping cart
    ('ðŸ"œ', chr(0x1F4DC)),  # scroll
    ('ðŸ"¸', chr(0x1F4F8)),  # camera
    ('ðŸ""', chr(0x1F4D4)),  # notebook
    ('ðŸ"®', chr(0x1F4AE)),  # mailbox
    ('ðŸ"§', chr(0x1F4A7)),  # email
    ('ðŸ' + chr(0xb0), chr(0x1F4B0)),  # money bag
    ('ðŸ' + chr(0xb8), chr(0x1F4B8)),  # money wings
    ('ðŸ' + chr(0xb5), chr(0x1F4B5)),  # dollar
    ('ðŸ"ˆ', chr(0x1F4C8)),  # chart up
    ('ðŸ' + chr(0xbe), chr(0x1F4BE)),  # save
    ('ðŸ"´', chr(0x1F4F4)),  # red circle
    ('ðŸ"¢', chr(0x1F4A2)),  # warning
    ('ðŸ•', chr(0x1F355)),  # pizza
    ('êš ï¸', chr(0x26A0) + chr(0xFE0F)),  # warning sign
    ('êš™ï¸', chr(0x2699) + chr(0xFE0F)),  # settings gear
    ('êŒ', chr(0x274C)),  # cross X
    ('êž•', chr(0x2795)),  # plus sign
]

# Files to process
python_files = [
    'src/services/planning.py',
    'src/services/budget.py',
    'src/services/recipes.py',
    'src/domains/cuisine/ui/planning.py',
]

fixed_count = 0
for file_path in python_files:
    full_path = base_dir / file_path
    if not full_path.exists():
        continue
    
    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    original = content
    for broken, fixed in emoji_fixes:
        content = content.replace(broken, fixed)
    
    if content != original:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_path}")
        fixed_count += 1

print(f"Total files fixed: {fixed_count}")
