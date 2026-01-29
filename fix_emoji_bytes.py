#!/usr/bin/env python3
"""Fix corrupted emojis in inventaire.py by replacing byte sequences"""

# Read the file in binary mode
with open('src/domains/cuisine/ui/inventaire.py', 'rb') as f:
    content = f.read()

# Convert to text for debugging
text_content = content.decode('utf-8', errors='replace')

# Define ALL replacements as byte pairs
fixes = [
    # Tabs - simple replacements first
    (b'[CAMERA] Photos', b'\xF0\x9F\x93\xB7 Photos'),  # 📷
    (b'[PKG] Articles', b'\xF0\x9F\x93\xA6 Articles'),  # 📦
    (b'### [!] MOYENNES', b'### \xE2\x9A\xA0\xEF\xB8\x8F MOYENNES'),  # ⚠️
    (b'[!] Statut', b'\xE2\x9A\xA0\xEF\xB8\x8F Statut'),  # ⚠️
]

# Apply replacements
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f'✅ Fixed: {old} -> {new}')
    else:
        print(f'⚠️ Not found: {old}')

# Write back
with open('src/domains/cuisine/ui/inventaire.py', 'wb') as f:
    f.write(content)

print('Done!')
