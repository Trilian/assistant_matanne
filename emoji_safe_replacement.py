#!/usr/bin/env python3
"""Safe emoji replacements - simple mojibake to emoji only, no regex, no complexity"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Count mojibake before
before_mojibake = sum(line.count('🚀 for line in lines)

# List of lines with mojibake to replace
replacements = {
    315: {'old': '🎯´', 'new': '❌'},      # color = "🎯´"
    327: {'old': '🎯"', 'new': '⏰'},      # color = "🎯""
    353: {'old': '🎯 ', 'new': '📍'},      # "🎯 Emplacement"
    481: {'old': '🎯„', 'new': '🔄'},      # button with Rafraîchir
    491: {'old': '🎯¥', 'new': '📥'},      # button with Importer
    537: {'old': '🎯"', 'new': '🔔'},      # metric Notifications
    543: {'old': '🎯„', 'new': '🔄'},      # button Actualiser
    673: {'old': '🎯´', 'new': '❌'},      # error with critique
    713: {'old': '🎯"', 'new': '⏰'},      # warning with peremption
    849: {'old': "📷, 'new': '💡'},      # button Générer suggestions
    887: {'old': '🎯´', 'new': '❌'},      # icon with high priority
    905: {'old': '🎯 ', 'new': '📍'},      # write with rayon
    977: {'old': '📅, 'new': '📤'},      # tabs - first pattern
    977b: {'old': "💡, 'new': '👁️'},   # tabs - second pattern (same line, different col)
    1063: {'old': "🍽️, 'new': '❌'},     # button delete photo (corrected line based on current file)
    1143: {'old': '🎯"', 'new': '🔔'},    # subheader Notifications et Alertes
    1155: {'old': '🎯¬', 'new': '🔔'},    # tabs center notifications
    1169: {'old': '🎯„', 'new': '🔄'},    # button Actualiser les alertes
    1177: {'old': '🎯"', 'new': '⏰'},     # toast détectées
    1189: {'old': '🎯¬', 'new': '🔔'},    # metric Non lues
    1375: {'old': '🎯"', 'new': '⏰'},     # markdown Alertes actives
    1249: {'old': '📌', 'new': '📌'},    # unread status
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
    lines[idx] = lines[idx].replace('📅, '📤')
    lines[idx] = lines[idx].replace("💡, '👁️')

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    final_lines = f.readlines()
    after_mojibake = sum(line.count('🚀 for line in final_lines)

# Log
with open('safe_replacement_log.txt', 'w') as log:
    log.write(f"Mojibake before: {before_mojibake}\n")
    log.write(f"Mojibake after: {after_mojibake}\n")
    log.write(f"Replacements made: {replacements_done}\n")
    log.write(f"Improvement: {before_mojibake - after_mojibake}\n")
