#!/usr/bin/env python3
"""Fix corrupted emojis using Unicode escapes"""

import re

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read with UTF-8-sig
with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

print(f"File size: {len(content)} chars")
print(f"Mojibake count: {content.count('ðŸ')}")

# Map mojibake to Unicode using escapes
emoji_fixes = [
    ('ðŸ›\x27', '\U0001f6d2'),   # Shopping cart
    ('ðŸ\x93', '\U0001f4c5'),   # Calendar
    ('ðŸ\x94', '\U0001f4cb'),   # Clipboard
    ('ðŸ\x95', '\U0001f4e5'),   # Inbox
    ('ðŸ\x96', '\U0001f4e4'),   # Outbox  
    ('ðŸ\x97', '\U0001f4de'),   # Phone
    ('ðŸ\x98', '\U0001f4ca'),   # Chart
]

print("\nReplacing mojibake:")
for mojibake, unicode_emoji in emoji_fixes:
    count = content.count(mojibake)
    if count > 0:
        content = content.replace(mojibake, unicode_emoji)
        print(f"  Replaced {count}x")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Done! Remaining mojibake: {content.count('ðŸ')}")
