#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final cleanup: replace all mojibake with clean emojis"""

import re

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Before: {content.count('📱 mojibake chars")

# Replace mojibake with clean emojis
replacements = [
    (r'🎯´', u'❌'),    # Critical
    (r'🎯"', u'⏰'),    # Time
    (r'🎯 ', u'📍'),    # Location
    (r'🎯„', u'🔄'),    # Refresh
    (r'🎯¥', u'📥'),    # Import
    (r'📅, u'📤'),    # Export
    (r'💡', u'💡'),    # Suggestions
    (r'📋', u'👁'),   # View
    (r'👶', u'❌'),    # Delete  
    (r'🎯¬', u'🔔'),    # Notifications
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"After: {content.count('📱 mojibake chars")
print("✅ Done!")
