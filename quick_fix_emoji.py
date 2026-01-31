#!/usr/bin/env python3
"""Script pour remplacer les emojis corrompus visibles directement"""

import re
from pathlib import Path

# Les emojis corrompus tels qu'affichés, mapés vers les vrais emojis
VISUAL_MAP = {
    '🎨: '🤖',
    '🗑️: '📈',
    '📅: '📦',
    '💰': '🍽️',
    '🎯: '📅',
    '🌿: '📔',
    '👧: '📊',
    '📋: '📙',
    '📈: '🛒',
    '💡: '📚',
    '🟡: '📋',
    '📷: '📜',
    '📤: '📸',
    '🧹: '👶',
    '🟢: '📴',
    '👶: '📱',
    '📉: '📢',
    '📱: '📣',
    '🚀: '📄',
    '📥: '📆',
    '🔔: '📉',
    'êš ï¸': '⚠️',
    'êž•': '➕',
    '🍽️ '🍽',
}

def fix_file(filepath):
    """Fix emojis in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace each corrupted emoji
    for corrupted, fixed in VISUAL_MAP.items():
        content = content.replace(corrupted, fixed)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Fix all files
src_dir = Path('src')
count = 0
for py_file in src_dir.rglob('*.py'):
    if fix_file(str(py_file)):
        count += 1
        print(f"Fixed: {py_file.relative_to('.')}")

print(f"\nTotal files fixed: {count}")
