#!/usr/bin/env python3
"""Fix all corrupted emojis in inventaire.py"""

file_path = 'd:\\Projet_streamlit\\assistant_matanne\\src\\domains\\cuisine\\ui\\inventaire.py'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all corrupted emojis
fixes = {
    'ðŸ"¦': '📦',
    'ðŸ"Š': '📊',
    'êš ï¸': '⚠️',
    'ðŸ›'': '🛒',
    'ðŸ"œ': '📜',
    'ðŸ"¸': '📸',
    'ðŸ""': '📔',
    'ðŸ"®': '📮',
    'ðŸ"§': '📧',
    'êš™ï¸': '⚙️',
    'ðŸ"¬': '📬',
    'ðŸ"š': '📚',
}

for broken, fixed in fixes.items():
    content = content.replace(broken, fixed)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all emoji corruptions in inventaire.py")
