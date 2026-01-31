#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final cleanup: replace all mojibake with clean emojis"""

import re

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Before: {content.count('ðŸ')} mojibake chars")

# Replace mojibake with clean emojis
replacements = [
    (r'ðŸ"´', u'❌'),    # Critical
    (r'ðŸ""', u'⏰'),    # Time
    (r'ðŸ" ', u'📍'),    # Location
    (r'ðŸ"„', u'🔄'),    # Refresh
    (r'ðŸ"¥', u'📥'),    # Import
    (r'ðŸ"¤', u'📤'),    # Export
    (r'ðŸ›\'', u'💡'),    # Suggestions
    (r'ðŸ\'€', u'👁'),   # View
    (r'ðŸ—\'', u'❌'),    # Delete  
    (r'ðŸ"¬', u'🔔'),    # Notifications
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"After: {content.count('ðŸ')} mojibake chars")
print("✅ Done!")
