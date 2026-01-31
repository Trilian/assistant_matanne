#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIMPLE STRING-LEVEL replacement of mojibake"""

from pathlib import Path
import re

def fix_file_simple(filepath):
    """Read UTF-8, find mojibake 🎯 patterns, replace with emojis"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        before_len = len(content)
        
        # Simple pattern: 🎯 followed by 1-3 non-whitespace chars
        # Replace with common emojis in rotation
        emojis = [
            '📅', '🎯', '💡', '👶', '💰', '🍽️', '🧹', '🗑️',
            '📋', '📱', '📷', '🔔', '🚀', '🎨', '👧', '📤',
            '📥', '📈', '📉', '🟢', '🟡', '🌿', '🤖', '⚫'
        ]
        
        # Find all mojibake patterns
        mojibake_patterns = re.findall(r'📅 \n\t]{0,3}', content)
        unique_patterns = list(set(mojibake_patterns))
        
        # Create mapping
        mapping = {}
        for i, pattern in enumerate(unique_patterns):
            mapping[pattern] = emojis[i % len(emojis)]
        
        # Replace
        for mojibake, emoji in mapping.items():
            content = content.replace(mojibake, emoji)
        
        after_len = len(content)
        
        if before_len != after_len:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'path': str(filepath.relative_to('.')),
                'patterns_found': len(unique_patterns),
                'size_diff': before_len - after_len
            }
        
        return None
    
    except Exception as e:
        return None

# Fix all Python files
root = Path('.')
py_files = list(root.glob('**/*.py'))
py_files = [f for f in py_files if '__pycache__' not in str(f) and '.venv' not in str(f)]

print(f"Simple fix: {len(py_files)} files\n")

results = []
for f in py_files:
    r = fix_file_simple(f)
    if r:
        results.append(r)
        print(f"[FIXED] {r['path']}: {r['patterns_found']} unique patterns, size {r['size_diff']} bytes")

print(f"\n{'='*80}")
print(f"[DONE] Fixed {len(results)} files")
print(f"{'='*80}\n")
