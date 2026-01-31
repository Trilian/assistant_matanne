#!/usr/bin/env python3
"""Surgical replacement - rebuild the exact lines"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace lines 102-115 (0-indexed: 101-114)
# Lines with tabs definition

tab_lines = {
    107: '        "🛒 Suggestions IA",\n',     # Line 108 (0-indexed 107)
    109: '        "📋 Historique",\n',         # Line 110
    111: '        "📷 Photos",\n',             # Line 112
    113: '        "📢 Notifications",\n',      # Line 114
    115: '        "🔮 Prévisions",\n',         # Line 116
    117: '        "🔧 Outils"\n',              # Line 118
}

for line_idx, new_line in tab_lines.items():
    print(f"Replacing line {line_idx}: {repr(lines[line_idx-1])}")
    print(f"  With:  {repr(new_line)}")
    lines[line_idx-1] = new_line

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ Fixed all emoji lines!")

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')
    for i, line in enumerate(lines[100:120], start=101):
        if 'Suggestions' in line or 'Historique' in line or 'Photos' in line or 'Notifications' in line or 'Prévisions' in line or 'Outils' in line:
            print(f"✓ Line {i}: {line.strip()}")
