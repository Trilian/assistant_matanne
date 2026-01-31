#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct inventory emoji fixes - saves without using print with emojis
"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

# Open and read with UTF-8
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track changes
changes = 0

for i, line in enumerate(lines):
    # Line 315: critical stock
    if i == 314 and 'color = "ðŸ"´"' in line:
        lines[i] = line.replace('ðŸ"´', '❌')
        changes += 1

    # Line 327: expiration  
    elif i == 326 and 'color = "ðŸ""' in line:
        lines[i] = line.replace('ðŸ""', '⏰')
        changes += 1

    # Line 353: location
    elif i == 352 and '"ðŸ" Emplacement"' in line:
        lines[i] = line.replace('ðŸ" ', '📍')
        changes += 1

    # Line 481: refresh button
    elif i == 480 and 'ðŸ"„ Rafraîchir' in line:
        lines[i] = line.replace('ðŸ"„', '🔄')
        changes += 1

    # Line 491: import button
    elif i == 490 and 'ðŸ"¥ Importer' in line:
        lines[i] = line.replace('ðŸ"¥', '📥')
        changes += 1

    # Line 537: notifications metric
    elif i == 536 and 'ðŸ"" Notifications' in line:
        lines[i] = line.replace('ðŸ""', '🔔')
        changes += 1

    # Line 543: refresh notifications button
    elif i == 542 and 'ðŸ"„ Actualiser' in line:
        lines[i] = line.replace('ðŸ"„', '🔄')
        changes += 1

    # Line 673: critical error
    elif i == 672 and 'ðŸ"´' in line:
        lines[i] = line.replace('ðŸ"´', '❌')
        changes += 1

    # Line 713: expiration warning
    elif i == 712 and 'ðŸ""' in line:
        lines[i] = line.replace('ðŸ""', '⏰')
        changes += 1

    # Line 849: suggestions button
    elif i == 848 and 'ðŸ›' in line:
        lines[i] = line.replace("ðŸ›'", '💡')
        changes += 1

    # Line 887: priority icon
    elif i == 886 and 'icon = "ðŸ"´"' in line:
        lines[i] = line.replace('ðŸ"´', '❌')
        changes += 1

    # Line 905: location text
    elif i == 904 and 'ðŸ"' in line:
        lines[i] = line.replace('ðŸ" ', '📍')
        changes += 1

    # Line 977: tabs (two occurrences)
    elif i == 976 and 'st.tabs' in line:
        lines[i] = line.replace('ðŸ"¤', '📤').replace("ðŸ'€", '👁️')
        changes += 2

    # Line 1063: delete photo button
    elif i == 1062 and 'ðŸ—' in line:
        lines[i] = line.replace("ðŸ—'", '❌')
        changes += 1

    # Line 1143: subheader
    elif i == 1142 and 'ðŸ""' in line:
        lines[i] = line.replace('ðŸ""', '🔔')
        changes += 1

    # Line 1155: tabs
    elif i == 1154 and 'ðŸ"¬' in line:
        lines[i] = line.replace('ðŸ"¬', '🔔')
        changes += 1

    # Line 1169: refresh alerts button
    elif i == 1168 and 'ðŸ"„' in line:
        lines[i] = line.replace('ðŸ"„', '🔄')
        changes += 1

    # Line 1177: toast notification
    elif i == 1176 and 'ðŸ""' in line:
        lines[i] = line.replace('ðŸ""', '⏰')
        changes += 1

    # Line 1189: unread notifications metric
    elif i == 1188 and 'ðŸ"¬' in line:
        lines[i] = line.replace('ðŸ"¬', '🔔')
        changes += 1

    # Line 1375: alerts header
    elif i == 1374 and 'ðŸ""' in line:
        lines[i] = line.replace('ðŸ""', '⏰')
        changes += 1

    # Line 1249: unread status
    elif i == 1248 and 'ðŸ†•' in line:
        lines[i] = line.replace('ðŸ†•', '📌').replace('ê€', ' ')
        changes += 1

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Write results to file instead of printing
with open('emoji_fix_log.txt', 'w') as log:
    log.write(f"Changes made: {changes}\n")
    log.write("Emoji replacements completed\n")
