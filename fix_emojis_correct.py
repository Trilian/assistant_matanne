#!/usr/bin/env python3
"""Fix emoji lines with correct indices"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix lines (0-indexed: subtract 1)
fixes = {
    110: '        "🛒 Suggestions IA",\n',
    112: '        "📋 Historique",\n',
    114: '        "📷 Photos",\n',
    116: '        "📢 Notifications",\n',
    118: '        "🔮 Prévisions",\n',
    120: '        "🔧 Outils"\n',
}

for idx, new_line in fixes.items():
    old = lines[idx]
    lines[idx] = new_line
    print(f"Line {idx+1}: Changed")
    print(f"  Old: {repr(old)}")
    print(f"  New: {repr(new_line)}")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ All emojis fixed!")

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in [110, 112, 114, 116, 118, 120]:
        print(f"✓ Line {i+1}: {lines[i].strip()}")
