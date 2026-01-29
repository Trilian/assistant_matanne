#!/usr/bin/env python3
"""Fix specific corrupted emoji sequences in inventaire.py"""

file_path = r'd:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py'

with open(file_path, 'rb') as f:
    content_bytes = f.read()

content = content_bytes.decode('utf-8', errors='replace')

# Define very specific replacements - only the ones we found
specific_fixes = [
    ('ðŸ"¦', chr(0x1F4E6)),  # package emoji
    ('ðŸ"Š', chr(0x1F4CA)),  # chart emoji
    ('ðŸ›\'', chr(0x1F6D2)),  # shopping cart
    ('ðŸ"œ', chr(0x1F4DC)),  # scroll
    ('ðŸ"¸', chr(0x1F4F8)),  # camera
    ('ðŸ""', chr(0x1F4D4)),  # notebook
    ('ðŸ"®', chr(0x1F4AE)),  # mailbox
    ('ðŸ"§', chr(0x1F4A7)),  # email/water
    ('êš ï¸', chr(0x26A0) + chr(0xFE0F)),  # warning
    ('êš™ï¸', chr(0x2699) + chr(0xFE0F)),  # settings gear
    ('êŒ', chr(0x274C)),  # cross/X mark
    ('êž•', chr(0x2795)),  # plus sign
]

for broken, fixed in specific_fixes:
    content = content.replace(broken, fixed)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed specific emoji sequences")
