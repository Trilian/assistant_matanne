#!/usr/bin/env python3
"""Brute force - just replace ALL mojibake prefix"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

before = content.count('ðŸ')

# Super simple: just replace the mojibake prefix with something sensible
# ðŸ" → 📍 (location for most cases)
# ðŸ"¥ → 📥 (import)

content = content.replace('ðŸ"', '📍')
content = content.replace('ðŸ"¥', '📥')

after = content.count('ðŸ')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

with open('brute_force_log.txt', 'w') as log:
    log.write(f"Before: {before}\n")
    log.write(f"After: {after}\n")
