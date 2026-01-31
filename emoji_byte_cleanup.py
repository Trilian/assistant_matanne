#!/usr/bin/env python3
"""Replace remaining mojibake using byte indices"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'rb') as f:
    data = f.read()

# Decode to find positions of 'ðŸ" ' pattern
text = data.decode('utf-8', errors='replace')

# Find all lines with mojibake
lines = text.split('\n')
modified_lines = []

for i, line in enumerate(lines):
    if 'ðŸ"' in line and ' ' in line:
        # Replace the specific instances we found earlier
        if i == 352:  # Line 353: "ðŸ" Emplacement"
            line = line.replace('ðŸ" Emplacement', '📍 Emplacement')
        elif i == 904:  # Line 905: st.write(f"ðŸ" {sugg.rayon}")
            line = line.replace('ðŸ" {sugg.rayon}', '📍 {sugg.rayon}')
        elif i == 1062:  # Line 1063: button with ðŸ—'ï¸
            line = line.replace('ðŸ—\'ï¸  Supprimer', '❌ Supprimer')
        elif i == 1448:  # Line 1449
            line = line.replace('ðŸ"¥💭 Import/Export', '📥 Import/Export')
        elif i == 1564:  # Line 1565
            line = line.replace('ðŸ"¥💭 Import/Export Avancé', '📥 Import/Export Avancé')
        elif i == 1980:  # Line 1981
            line = line.replace('ðŸ" Analyse globale', '📍 Analyse globale')
        elif i == 2614:  # Line 2615
            line = line.replace('ðŸ—\'ï¸', '❌')
    
    modified_lines.append(line)

# Write back
new_text = '\n'.join(modified_lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_text)

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    final_text = f.read()
    final_count = final_text.count('ðŸ')

with open('byte_cleanup_log.txt', 'w') as log:
    log.write(f"Final mojibake count: {final_count}\n")
