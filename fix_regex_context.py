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
    (r'📅w]*Stock', '📊 Stock'),
    # Pattern: mojibake + "Alertes"
    (r'📅w]*Alertes', '⚠️ Alertes'),
    # Pattern: mojibake + "Catégories"
    (r'📅w]*Catégories', '🏷️ Catégories'),
    # Pattern: mojibake + "Suggestions"
    (r'📅w]*Suggestions', '🛒 Suggestions'),
    # Pattern: mojibake + "Historique"
    (r'📅w]*Historique', '📋 Historique'),
    # Pattern: mojibake + "Photos"
    (r'📅w]*Photos', '📷 Photos'),
    # Pattern: mojibake + "Notifications"
    (r'📅w]*Notifications', '📢 Notifications'),
    # Pattern: mojibake + "Prévisions"
    (r'📅w]*Prévisions', '🔮 Prévisions'),
    # Pattern: mojibake + "Outils"
    (r'📅w]*Outils', '🔧 Outils'),
    # Pattern: mojibake + "péremption" / "proche"
    (r'💡^\w]*', '📅 '),
    # Pattern: mojibake + "Importer"
    (r'👶^\w]*Importer', '📥 Importer'),
    # Pattern: mojibake + "Exporter"
    (r'💰^\w]*Exporter', '📤 Exporter'),
]

print("Before:", content.count('🎯

for pattern, replacement in patterns:
    count = len(re.findall(pattern, content))
    if count > 0:
        content = re.sub(pattern, replacement, content)
        print(f"  Replaced {count}x: {pattern[:30]}")

print("After:", content.count('🎯

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done!")
