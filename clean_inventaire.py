#!/usr/bin/env python3
"""Clean UTF-8 corruption in inventaire.py using Unicode codepoints"""

file_path = r'd:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py'

with open(file_path, 'rb') as f:
    raw_bytes = f.read()

# Decode with error handling
content = raw_bytes.decode('utf-8', errors='replace')

# Manually define replacements using Unicode codepoints (avoid embedding emojis in source)
replacements = [
    ('ðŸ"¦', chr(0x1F4E6)),  # package
    ('ðŸ"Š', chr(0x1F4CA)),  # chart
    ('ðŸ›\'', chr(0x1F6D2)),  # shopping cart  
    ('ðŸ"œ', chr(0x1F4DC)),  # scroll
    ('ðŸ"¸', chr(0x1F4F8)),  # camera
    ('ðŸ""', chr(0x1F4D4)),  # notebook
    ('ðŸ"®', chr(0x1F4AE)),  # mailbox
    ('ðŸ"§', chr(0x1F4A7)),  # email
    ('êš ï¸', chr(0x26A0) + chr(0xFE0F)),  # warning
    ('êš™ï¸', chr(0x2699) + chr(0xFE0F)),  # settings
]

for broken, fixed in replacements:
    content = content.replace(broken, fixed)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed inventaire.py UTF-8 corruption")
