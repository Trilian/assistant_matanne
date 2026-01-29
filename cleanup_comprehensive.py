#!/usr/bin/env python3
"""Comprehensive UTF-8 corruption cleanup for inventaire.py"""

import re

file_path = r'd:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py'

with open(file_path, 'rb') as f:
    raw_bytes = f.read()

content = raw_bytes.decode('utf-8', errors='replace')

# Define the replacements using Unicode codepoints (avoids source code emoji issues)
replacements_unicode = [
    # Main series ðŸ* (0xC3B0C5B8 prefix variations)
    ('ðŸ"¦', chr(0x1F4E6)),  # package
    ('ðŸ"Š', chr(0x1F4CA)),  # chart  
    ('ðŸ›\'', chr(0x1F6D2)),  # shopping cart
    ('ðŸ"œ', chr(0x1F4DC)),  # scroll
    ('ðŸ"°', chr(0x1F4F0)),  # newspaper
    ('ðŸ"¸', chr(0x1F4F8)),  # camera
    ('ðŸ"­', chr(0x1F4AD)),  # thought bubble
    ('ðŸ"¬', chr(0x1F4AC)),  # speech bubble
    ('ðŸ""', chr(0x1F4D4)),  # notebook
    ('ðŸ"®', chr(0x1F4AE)),  # mailbox
    ('ðŸ"§', chr(0x1F4A7)),  # email/water drop
    ('ðŸ"¡', chr(0x1F4A1)),  # lightbulb
    ('ðŸ"ƒ', chr(0x1F4C3)),  # page with curl
    ('ðŸ"„', chr(0x1F4C4)),  # page facing up
    ('ðŸ"…', chr(0x1F4C5)),  # calendar
    # êš series (warning/settings)
    ('êš ï¸', chr(0x26A0) + chr(0xFE0F)),  # warning sign
    ('êš™ï¸', chr(0x2699) + chr(0xFE0F)),  # gear/settings
]

for broken, fixed in replacements_unicode:
    content = content.replace(broken, fixed)

# Also try regex patterns for remaining corrupted sequences
# Pattern: bytes that look like broken UTF-8 emoji
content = re.sub(r'ðŸ[\"\'\w]', '', content, flags=re.IGNORECASE)  # Remove remaining ðŸ patterns

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Comprehensive cleanup complete")
