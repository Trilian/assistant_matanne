#!/usr/bin/env python3
"""Safe emoji replacements - line-by-line"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

before_mojibake = sum(line.count('ðŸ') for line in lines)

# Replacements for specific lines
# Dictionary: (line_num, old_str) -> new_str
direct_replacements = [
    ((315, 'ðŸ"´'), '❌'),
    ((327, 'ðŸ""'), '⏰'),
    ((353, 'ðŸ" '), '📍'),
    ((481, 'ðŸ"„'), '🔄'),
    ((491, 'ðŸ"¥'), '📥'),
    ((537, 'ðŸ""'), '🔔'),
    ((543, 'ðŸ"„'), '🔄'),
    ((673, 'ðŸ"´'), '❌'),
    ((713, 'ðŸ""'), '⏰'),
    ((849, "ðŸ›'"), '💡'),
    ((887, 'ðŸ"´'), '❌'),
    ((905, 'ðŸ" '), '📍'),
    ((977, 'ðŸ"¤'), '📤'),
    ((977, "ðŸ'€"), '👁️'),
    ((1063, "ðŸ—'"), '❌'),
    ((1143, 'ðŸ""'), '🔔'),
    ((1155, 'ðŸ"¬'), '🔔'),
    ((1169, 'ðŸ"„'), '🔄'),
    ((1177, 'ðŸ""'), '⏰'),
    ((1189, 'ðŸ"¬'), '🔔'),
    ((1375, 'ðŸ""'), '⏰'),
    ((1249, 'ðŸ†•'), '📌'),
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
    after_mojibake = sum(line.count('ðŸ') for line in final_lines)

# Log
with open('safe_replacement_log.txt', 'w') as log:
    log.write(f"Mojibake before: {before_mojibake}\n")
    log.write(f"Mojibake after: {after_mojibake}\n")
    log.write(f"Replacements made: {replacements_done}\n")
    log.write(f"Improvement: {before_mojibake - after_mojibake}\n")
