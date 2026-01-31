#!/usr/bin/env python3
"""Safe emoji replacements - line-by-line"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

before_mojibake = sum(line.count('📷 for line in lines)

# Replacements for specific lines
# Dictionary: (line_num, old_str) -> new_str
direct_replacements = [
    ((315, '🎯´'), '❌'),
    ((327, '🎯"'), '⏰'),
    ((353, '🎯 '), '📍'),
    ((481, '🎯„'), '🔄'),
    ((491, '🎯¥'), '📥'),
    ((537, '🎯"'), '🔔'),
    ((543, '🎯„'), '🔄'),
    ((673, '🎯´'), '❌'),
    ((713, '🎯"'), '⏰'),
    ((849, "📋), '💡'),
    ((887, '🎯´'), '❌'),
    ((905, '🎯 '), '📍'),
    ((977, '📅), '📤'),
    ((977, "💡), '👁️'),
    ((1063, "💰), '❌'),
    ((1143, '🎯"'), '🔔'),
    ((1155, '🎯¬'), '🔔'),
    ((1169, '🎯„'), '🔄'),
    ((1177, '🎯"'), '⏰'),
    ((1189, '🎯¬'), '🔔'),
    ((1375, '🎯"'), '⏰'),
    ((1249, '📌'), '📌'),
]

replacements_done = 0
for (line_num, old_str), new_str in direct_replacements:
    idx = line_num - 1  # Convert to 0-indexed
    if idx < len(lines):
        if old_str in lines[idx]:
            lines[idx] = lines[idx].replace(old_str, new_str)
            replacements_done += 1

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    final_lines = f.readlines()
    after_mojibake = sum(line.count('📷 for line in final_lines)

# Log
with open('safe_replacement_log.txt', 'w') as log:
    log.write(f"Mojibake before: {before_mojibake}\n")
    log.write(f"Mojibake after: {after_mojibake}\n")
    log.write(f"Replacements made: {replacements_done}\n")
    log.write(f"Improvement: {before_mojibake - after_mojibake}\n")
