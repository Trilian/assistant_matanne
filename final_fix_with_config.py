#!/usr/bin/env python3
"""Final fix: correct encoding and replace emojis"""

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read the file as UTF-8-sig (handles BOM)
with open(file_path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# Map of corrupted lines - find by keyword, replace the emoji part
fixes = {
    # Line 311: [PKG] is OK, but search for it anyway
    # Line 353: "ðŸ" Emplacement" -> "📅 Emplacement"
    # Line 383: "[!] Statut" -> "⚠️ Statut"
    # etc.
}

# Direct line-by-line fixes using line numbers
replacements = [
    (310, lambda l: l.replace('[PKG]', '📦')),
    (353, lambda l: l.replace('"ðŸ"', '"📅')),
    (382, lambda l: l.replace('"[!]', '"⚠️')),
    (490, lambda l: l.replace('"ðŸ"¥', '"📥')),
    (712, lambda l: l.replace('f"ðŸ""', 'f"📅')),
    (1422, lambda l: l.replace('st.metric("ðŸ""', 'st.metric("📅')),
    (1568, lambda l: l.replace('"ðŸ"¥', '"📥').replace('"ðŸ"¤', '"📤')),
    (956, lambda l: l.replace("a['nom']", "a['ingredient_nom']")),
]

for line_idx, func in replacements:
    if line_idx < len(lines):
        old_line = lines[line_idx]
        lines[line_idx] = func(old_line)
        if old_line != lines[line_idx]:
            print(f"✓ Line {line_idx + 1}: Fixed")

# Write back without BOM
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\n✅ All fixes applied!")
print("📝 Don't forget: VS Code now configured to use UTF-8 (see .vscode/settings.json)")
