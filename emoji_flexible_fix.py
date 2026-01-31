#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Flexible emoji replacement using text pattern matching"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

initial_mojibake = content.count('📷

# All replacements using text patterns
replacements = [
    ('🎯´', '❌'),  # Critical
    ('🎯"', '⏰'),  # Time/Expiration
    ('🎯 ', '📍'),  # Location
    ('🎯„', '🔄'),  # Refresh
    ('🎯¥', '📥'),  # Import
    ("📋, '💡'),  # Suggestions
    ("💡, '👁️'),  # View
    ('📅, '📤'),  # Export
    ("💰, '❌'),  # Delete
    ('🎯¬', '🔔'),  # Notifications/Bell
    ('📌', '📌'),  # Unread/marker
]

replaced = []
for old, new in replacements:
    if old in content:
        count_before = content.count(old)
        content = content.replace(old, new)
        count_after = content.count(old)
        actual = count_before - count_after
        if actual > 0:
            replaced.append((old, new, actual))

final_mojibake = content.count('📷

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Log results
with open('emoji_replacement_log.txt', 'w') as log:
    log.write(f"Initial mojibake count: {initial_mojibake}\n")
    log.write(f"Final mojibake count: {final_mojibake}\n")
    log.write(f"Replacements made: {len(replaced)}\n\n")
    for old, new, count in replaced:
        log.write(f"  {repr(old)} → {repr(new)}: {count} occurrences\n")
    log.write(f"\nTotal mojibake characters replaced: {initial_mojibake - final_mojibake}\n")
