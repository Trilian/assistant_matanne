#!/usr/bin/env python3
"""Final emoji cleanup - handle remaining patterns"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

before_count = content.count('ðŸ')

# Direct replacements for remaining patterns
remaining = [
    ('ðŸ" Emplacement', '📍 Emplacement'),
    ('ðŸ" {sugg.rayon}', '📍 {sugg.rayon}'),
    ('ðŸ—\'ï¸  Supprimer', '❌ Supprimer'),
    ('ðŸ"¥💭 Import/Export', '📥 Import/Export'),
    ('ðŸ"¥💭 Import/Export Avancé', '📥 Import/Export Avancé'),
    ('ðŸ" Analyse globale', '📍 Analyse globale'),
    ('ðŸ—\'ï¸', '❌'),
]

for old, new in remaining:
    if old in content:
        content = content.replace(old, new)

after_count = content.count('ðŸ')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

with open('final_cleanup_log.txt', 'w') as log:
    log.write(f"Before: {before_count} mojibake\n")
    log.write(f"After: {after_count} mojibake\n")
    log.write(f"Replaced: {len(remaining)} patterns\n")
