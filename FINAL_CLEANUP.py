#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final comprehensive mojibake cleanup"""

from pathlib import Path
import os

# Map all mojibake patterns with their clean emoji replacements
MOJIBAKE_MAP = {
    '🍽️´': '❌',
    '🍽️"': '⏰',
    '🍽️ ': '📍',
    '📉: '🔄',
    '🎨: '📥',
    '👧: '📤',
    "📉: '💡',
    "📈: '👁️',
    '🔔: '🔔',
    '🟢: '📌',
    "🧹: '❌',
    '🟡 '🍽️',
    '📅: '🤖',
    '🎯: '📈',
    '📅: '📦',
    '📷': '🍽️',
    '🍽️"': '📔',
    '🎯: '📊',
    '💡: '📙',
    '👶: '📚',
    '🍽️‹': '📋',
    '📷: '📜',
    '💰: '📸',
    '🤖: '👶',
    '🍽️: '📱',
    '🍽️¢': '📢',
    '👶: '📣',
    '🎯: '📅',
    '🍽️†': '📆',
    '📤: '📉',
    '📱: '🛒',
    '📋: '💰',
    '🟡: '💵',
    '📥: '💡',
    '👶': '👀',
    '🧹¸': '🗑️',
    '💰¸': '🗄️',
    '⚫: '💾',
    '🤖€📈€📤€🗑️: '👨‍👩‍👧‍👦',
    '🤖€📈€🌿: '👨‍👩‍👧',
    '💰: '📱',
    '📷Ÿ‡·': '🇫🇷',
    '🧹Ÿ‡§': '🇬🇧',
    '👧Ÿ‡¸': '🇪🇸',
    '🔔Ÿ‡ª': '🇩🇪',
    '🚀: '📷',
    '💡: '🟡',
    '⚫ ': '🟠',
    '⚫¢': '🟢',
    '🟢: '🌿',
    '🔔: '🌱',
    '🧹': '🧹',
    '👧': '🗑️',
    '🚀: '🎯',
    '🗑️ '🌍',
    '🌿: '👧',
    '💡 '🛒',
    '🎯: '📅',
    '📋: '📵',
    '🍽️‹': '📋',
    '🌿 ': '📮',
    '📥¸': '🗒️',
    '🚀 '🍅',
    '🍽️': '📋',
    '🗑️: '🥒',
    '📅: '🌽',
    '🍽️': '🔔',
    '🌿: '👧',
    '📋: '💰',
    '📥: '💡',
    '📋: '📵',
    '🎯': '🎯',
    '📥: '🎨',
    '📱: '🚨',
    '📱: '🚀',
    'âšª': '⚫',
    'â‚¬': '€',
    '🎯': '🎯',
    '🚀 '🍅',
    '📥¸': '🗒️',
    '🎨 '🖐️',
}

def clean_file(filepath):
    """Clean one file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_count = content.count('🟡
        if original_count == 0:
            return None
        
        # Apply ALL replacements
        for mojibake, emoji in MOJIBAKE_MAP.items():
            content = content.replace(mojibake, emoji)
        
        final_count = content.count('🟡
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {'path': str(filepath), 'before': original_count, 'after': final_count, 'replaced': original_count - final_count}
    
    except Exception as e:
        return {'path': str(filepath), 'error': str(e)}

# Get all Python files
root = Path('.')
py_files = [f for f in root.glob('**/*.py') if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)]

results = []
for f in py_files:
    r = clean_file(f)
    if r:
        results.append(r)

# Summary
total_replaced = sum(r.get('replaced', 0) for r in results if 'replaced' in r)
files_cleaned = len([r for r in results if r.get('before', 0) > 0])

print(f"\n✅ FINAL CLEANUP COMPLETE")
print(f"Total mojibake replaced: {total_replaced}")
print(f"Files cleaned: {files_cleaned}")

# Write detailed log
with open('FINAL_CLEANUP_REPORT.txt', 'w') as log:
    log.write("FINAL COMPREHENSIVE MOJIBAKE CLEANUP\n")
    log.write("=" * 80 + "\n\n")
    log.write(f"Total files scanned: {len(py_files)}\n")
    log.write(f"Files with mojibake: {files_cleaned}\n")
    log.write(f"Total replaced: {total_replaced}\n\n")
    
    for r in results:
        if 'error' in r:
            log.write(f"ERROR: {r['path']}: {r['error']}\n")
        elif r.get('before', 0) > 0:
            log.write(f"{r['path'].replace(os.getcwd(), '.')}: {r['before']} → {r['after']} (replaced {r['replaced']})\n")
