#!/usr/bin/env python3
"""Safe emoji replacements - simple mojibake to emoji only, no regex, no complexity"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Count mojibake before
before_mojibake = sum(line.count('ðŸ') for line in lines)

# List of lines with mojibake to replace
replacements = {
    315: {'old': 'ðŸ"´', 'new': '❌'},      # color = "ðŸ"´"
    327: {'old': 'ðŸ""', 'new': '⏰'},      # color = "ðŸ"""
    353: {'old': 'ðŸ" ', 'new': '📍'},      # "ðŸ" Emplacement"
    481: {'old': 'ðŸ"„', 'new': '🔄'},      # button with Rafraîchir
    491: {'old': 'ðŸ"¥', 'new': '📥'},      # button with Importer
    537: {'old': 'ðŸ""', 'new': '🔔'},      # metric Notifications
    543: {'old': 'ðŸ"„', 'new': '🔄'},      # button Actualiser
    673: {'old': 'ðŸ"´', 'new': '❌'},      # error with critique
    713: {'old': 'ðŸ""', 'new': '⏰'},      # warning with peremption
    849: {'old': "ðŸ›'", 'new': '💡'},      # button Générer suggestions
    887: {'old': 'ðŸ"´', 'new': '❌'},      # icon with high priority
    905: {'old': 'ðŸ" ', 'new': '📍'},      # write with rayon
    977: {'old': 'ðŸ"¤', 'new': '📤'},      # tabs - first pattern
    977b: {'old': "ðŸ'€", 'new': '👁️'},   # tabs - second pattern (same line, different col)
    1063: {'old': "ðŸ—'", 'new': '❌'},     # button delete photo (corrected line based on current file)
    1143: {'old': 'ðŸ""', 'new': '🔔'},    # subheader Notifications et Alertes
    1155: {'old': 'ðŸ"¬', 'new': '🔔'},    # tabs center notifications
    1169: {'old': 'ðŸ"„', 'new': '🔄'},    # button Actualiser les alertes
    1177: {'old': 'ðŸ""', 'new': '⏰'},     # toast détectées
    1189: {'old': 'ðŸ"¬', 'new': '🔔'},    # metric Non lues
    1375: {'old': 'ðŸ""', 'new': '⏰'},     # markdown Alertes actives
    1249: {'old': 'ðŸ†•', 'new': '📌'},    # unread status
}

# Do replacements (using 1-indexed line numbers, but lists are 0-indexed)
replacements_done = 0
for line_num, replacement_info in replacements.items():
    if isinstance(line_num, str):  # Skip the 977b marker - we'll handle it separately
        continue
    
    idx = line_num - 1  # Convert to 0-indexed
    if idx < len(lines):
        old_str = replacement_info['old']
        new_str = replacement_info['new']
        if old_str in lines[idx]:
            lines[idx] = lines[idx].replace(old_str, new_str)
            replacements_done += 1

# Handle 977 special case (both patterns in same line)
idx = 977 - 1
if idx < len(lines):
    lines[idx] = lines[idx].replace('ðŸ"¤', '📤')
    lines[idx] = lines[idx].replace("ðŸ'€", '👁️')

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
