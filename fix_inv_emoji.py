#!/usr/bin/env python3
import sys

# Read file
with open('src/domains/cuisine/ui/inventaire.py', 'rb') as f:
    data = f.read()

# Simple byte-level replacements for broken UTF-8
# These are the exact byte sequences from the file
replacements = [
    # Tabs
    (b'[CAMERA] Photos', b'📷 Photos'),
    (b'[PKG] Articles', b'📦 Articles'),
    (b'[CHART] Stock', b'📊 Stock'),
    (b'[!] Alertes', b'⚠️ Alertes'),
    (b'### [!] MOYENNES', b'### ⚠️ MOYENNES'),
    (b'[!] Statut', b'⚠️ Statut'),
    (b'ðŸ\"œ Historique', b'📜 Historique'),
    (b'ðŸ\"\" Notifications', b'🔔 Notifications'),
    (b'ðŸ\"® Prévisions', b'🔮 Prévisions'),
    (b'ðŸ\"§ Outils', b'🔧 Outils'),
    (b'ðŸ›' Suggestions IA', b'🛍️ Suggestions IA'),
    # Metrics and buttons
    (b'ðŸ\"„ Rafra', b'🔄 Rafra'),
    (b'ðŸ\"¥ Importer', b'📥 Importer'),
    (b'ðŸ\"¤ Ajouter', b'📸 Ajouter'),
    (b'ðŸ'€ Afficher', b'👀 Afficher'),
    # Alerts
    (b'ðŸ\"´', b'🔴'),
    (b'ðŸ\"', b'🟡'),
    (b'ðŸ\" Emplacement', b'📝 Emplacement'),
    (b'ðŸ\"® Prévisions', b'🔮 Prévisions'),
]

for old, new in replacements:
    data = data.replace(old, new)

# Write back
with open('src/domains/cuisine/ui/inventaire.py', 'wb') as f:
    f.write(data)

print('✅ Fixed emojis')
