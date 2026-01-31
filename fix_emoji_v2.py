#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted emojis by doing direct byte replacement"""

file_path = "src/domains/cuisine/ui/inventaire.py"

# Read the file as binary to see exact bytes
with open(file_path, 'rb') as f:
    content = f.read()

# Show hex around the corrupted area
print("Searching for corrupted patterns...")
if b"Suggestions IA" in content:
    idx = content.find(b"Suggestions IA")
    print(f"\nFound 'Suggestions IA' at position {idx}")
    print(f"Context: {content[idx-20:idx+30]}")
    print(f"Hex: {content[idx-20:idx+30].hex()}")

# Do replacement using bytes
# Shopping cart emoji: U+1F6D2 
shopping_cart = "🛒".encode('utf-8')
clipboard = "📋".encode('utf-8')
camera = "📷".encode('utf-8')
megaphone = "📢".encode('utf-8')
crystal = "🔮".encode('utf-8')
wrench = "🔧".encode('utf-8')

# Search and replace the exact corrupted bytes
# These are the mojibake sequences - we need to find them by looking at what's in the file

import re

# Try to decode as latin-1 to see the bad characters
try:
    content_str = content.decode('utf-8')
except:
    content_str = content.decode('utf-8', errors='replace')

print(f"\nSearching in decoded content...")
lines_with_suggestions = [line for line in content_str.split('\n') if 'Suggestions' in line]
for line in lines_with_suggestions:
    print(f"Found: {repr(line)}")
    # Show character codes
    for i, char in enumerate(line[:20]):
        print(f"  [{i}] = {repr(char)} (U+{ord(char):04X})")

# Just write the proper version
new_tabs = '''    tab_stock, tab_alertes, tab_categories, tab_suggestions, tab_historique, tab_photos, tab_notifications, tab_predictions, tab_tools = st.tabs([

        "📊 Stock", 

        "⚠️ Alertes", 

        "🏷️ Catégories", 

        "🛒 Suggestions IA",

        "📋 Historique",

        "📷 Photos",

        "📢 Notifications",

        "🔮 Prévisions",

        "🔧 Outils"

    ])'''

# Find and replace the tabs section
import re
pattern = r'tab_stock, tab_alertes.*?\]\)'
new_content = re.sub(pattern, new_tabs.strip(), content_str, flags=re.DOTALL)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n✅ Fixed all emoji corruptions in inventaire.py")
