#!/usr/bin/env python3
"""Replace mojibake by finding patterns around keywords"""

import re

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Find mojibake by looking for the corrupted string patterns
# Instead of exact byte match, use regex to find "corrupted_emoji + text" patterns

patterns = [
    # Pattern: mojibake + "Stock"
    (r'ðŸ[^\w]*Stock', '📊 Stock'),
    # Pattern: mojibake + "Alertes"
    (r'ðŸ[^\w]*Alertes', '⚠️ Alertes'),
    # Pattern: mojibake + "Catégories"
    (r'ðŸ[^\w]*Catégories', '🏷️ Catégories'),
    # Pattern: mojibake + "Suggestions"
    (r'ðŸ[^\w]*Suggestions', '🛒 Suggestions'),
    # Pattern: mojibake + "Historique"
    (r'ðŸ[^\w]*Historique', '📋 Historique'),
    # Pattern: mojibake + "Photos"
    (r'ðŸ[^\w]*Photos', '📷 Photos'),
    # Pattern: mojibake + "Notifications"
    (r'ðŸ[^\w]*Notifications', '📢 Notifications'),
    # Pattern: mojibake + "Prévisions"
    (r'ðŸ[^\w]*Prévisions', '🔮 Prévisions'),
    # Pattern: mojibake + "Outils"
    (r'ðŸ[^\w]*Outils', '🔧 Outils'),
    # Pattern: mojibake + "péremption" / "proche"
    (r'ðŸ""[^\w]*', '📅 '),
    # Pattern: mojibake + "Importer"
    (r'ðŸ"¥[^\w]*Importer', '📥 Importer'),
    # Pattern: mojibake + "Exporter"
    (r'ðŸ"¤[^\w]*Exporter', '📤 Exporter'),
]

print("Before:", content.count('ðŸ'))

for pattern, replacement in patterns:
    count = len(re.findall(pattern, content))
    if count > 0:
        content = re.sub(pattern, replacement, content)
        print(f"  Replaced {count}x: {pattern[:30]}")

print("After:", content.count('ðŸ'))

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done!")
