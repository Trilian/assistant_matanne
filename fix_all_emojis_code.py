#!/usr/bin/env python3
import os

EMOJI_MAP = {
    'êœ…': '✨',
    'ðŸ"´': '🔴',
    'ðŸ"': '📔',
    'ðŸŸ¢': '🟢',
    'ðŸŸ¡': '🟡',
    'ðŸ"…': '📅',
    'ðŸŽ¯': '🎯',
    'ðŸ˜Œ': '😌',
    'ðŸ™‚': '🙂',
    'ðŸ˜': '😐',
    'ðŸ˜°': '😰',
    'ðŸ"¥': '🔥',
    'ðŸ"ˆ': '📈',
    'ðŸ"‰': '📉',
}

files = [
    'src/domains/cuisine/ui/planning.py',
    'src/domains/cuisine/ui/inventaire.py',
    'src/domains/planning/ui/__init__.py',
    'src/domains/planning/logic/vue_ensemble_logic.py',
]

for fp in files:
    if not os.path.exists(fp):
        print(f'NOT FOUND: {fp}')
        continue
    
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in EMOJI_MAP.items():
        if old in content:
            content = content.replace(old, new)
    
    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'FIXED: {fp}')
    else:
        print(f'OK: {fp}')

# Also fix inventaire for the missing ones
with open('src/domains/cuisine/ui/inventaire.py', 'r', encoding='utf-8') as f:
    content = f.read()

original = content
content = content.replace('color = "ðŸ"´"', 'color = "🔴"')
content = content.replace('color = "ðŸ""', 'color = "📔"')

if content != original:
    with open('src/domains/cuisine/ui/inventaire.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('EXTRA FIXES: inventaire.py')

print('\nDONE')
