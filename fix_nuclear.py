#!/usr/bin/env python3
"""Nuclear option: replace ALL ðŸ + next char with emoji based on what follows"""

file_path = "src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Before: {content.count('ðŸ')} mojibake")

# Split by ðŸ and analyze what follows
import re

# Very aggressive: replace ðŸ"" with 📅
content = re.sub(r'ðŸ""', '📅', content)
# ðŸ" -> 📅
content = re.sub(r'ðŸ"([^"])', r'📅\1', content)
# [PKG] -> 📦
content = content.replace('[PKG]', '📦')
# [!] -> ⚠️
content = content.replace('[!]', '⚠️')
# [CAMERA] -> 📷
content = content.replace('[CAMERA]', '📷')

print(f"After: {content.count('ðŸ')} mojibake")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done!")
