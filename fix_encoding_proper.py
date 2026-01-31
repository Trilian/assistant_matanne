#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted emojis in inventaire.py by re-encoding the entire file"""

import re

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read with UTF-8-sig to handle BOM
with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

print(f"File size: {len(content)} chars")
print(f"Mojibake count: {content.count('ðŸ')}")

# Now fix ALL mojibake patterns by replacing them with proper Unicode emojis
# These are the actual Unicode codepoints for the intended emojis

emoji_fixes = {
    # The mojibake sequences we see
    'ðŸ›'': '🛒',   # Shopping cart U+1F6D2
    'ðŸ"': '📅',    # Calendar U+1F4C5
    'ðŸ" ': '📋',   # Clipboard U+1F4CB
    'ðŸ"¥': '📥',   # Inbox arrow down U+1F4E5
    'ðŸ"¤': '📤',   # Outbox arrow up U+1F4E4
    'ðŸ"': '📞',    # Telephone U+1F4DE
    'ðŸ"': '📊',    # Bar chart U+1F4CA
    'ðŸ'': '⚠️',    # Warning sign U+26A0
}

print("\nReplacing mojibake:")
for mojibake, emoji in emoji_fixes.items():
    count = content.count(mojibake)
    if count > 0:
        content = content.replace(mojibake, emoji)
        print(f"  {emoji} × {count} : {repr(mojibake)}")

# Also catch any remaining single char patterns
# Replace ðŸ followed by anything that's not alphanumeric
content = re.sub(r'ðŸ[^\w\s]', '', content)

# Write back WITHOUT BOM (Streamlit handles UTF-8 fine without it)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Fixed! Remaining mojibake: {content.count('ðŸ')}")
