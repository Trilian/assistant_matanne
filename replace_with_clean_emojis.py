#!/usr/bin/env python3
"""Replace ALL corrupted emojis with clean, simple alternatives"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

print(f"Original mojibake count: {content.count('ðŸ')}")

# Map corrupted emojis to clean alternatives using word context
replacements = [
    # Use context-based replacement to be more accurate
    ('[PKG]', '📦'),
    ('[CAMERA]', '📷'),
    ('ðŸ"´', '❌'),  # Critical/error
    ('ðŸ""', '⏰'),  # Time/expiration
    ('ðŸ" ', '📍'),  # Location
    ('ðŸ"„', '🔄'),  # Refresh
    ('ðŸ"¥', '📥'),  # Import
    ('ðŸ"¤', '📤'),  # Export
    ('ðŸ›'', '💡'),  # Suggestions (lightbulb)
    ('ðŸ'€', '👁️'),  # View/display
    ('ðŸ—'', '❌'),  # Delete
    ('ðŸ"¬', '🔔'),  # Notifications
]

for old, new in replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  {new} × {count} : {old}")

# Write back as UTF-8 (no BOM)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Final mojibake count: {content.count('ðŸ')}")
print("✅ All emojis replaced with clean alternatives!")
