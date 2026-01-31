#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ULTIMATE mojibake cleanup - Generic replacement strategy"""

from pathlib import Path
import re

def clean_file_with_emoji_map(filepath):
    """Read, detect mojibake patterns, and replace them with clean emojis"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_len = len(content)
        
        # Massive string replacement of known mojibake sequences
        # Using the actual characters as Python read them from the file
        
        replacements = {
            '🧹: '🎯',   # Target
            '🎨': '🎨',   # Art  
            '🗑️': '🍽️',   # Plate
            '👧 '🍽️',    # Plate  
            '📤: '👶',   # Baby
            '🍽️: '💰',   # Money
            '🔔: '💡',   # Lightbulb
            '🎨: '👧',   # Girl
            '⚫: '👨',   # Man
            '📅: '👩',   # Woman
            '🌿: '👪',   # Family
            '📥: '👬',   # Boys
            '📉: '📱',   # Phone
            '📅: '📵',   # No Phone
            '📋: '📷',   # Camera
            '🟢: '📈',   # Chart Up
            '🗑️: '📉',   # Chart Down
            '🎯: '📅',   # Calendar
            '👧: '📆',   # Calendar
            '🟡: '📋',   # Clipboard
            '🔔 ': '📍',  # Location
            '👶: '🔔',   # Bell
            '🧹: '📮',   # Mailbox
            '💡: '📜',   # Document
            '💡: '📚',   # Books
            '🚀: '📸',   # Photo
            '📋: '📤',   # Export
            '📱: '📥',   # Import
            '📷Ÿ"¤': '📥📤',   # Import/Export
            '📉': '🗑️',   # Trash
            '🤖¸': '🗑️',  # Trash
            '🟢¸': '🗒️',  # Notepad
            '🧹': '🧹',   # Broom
            '📈¢': '🟢',   # Green Circle
            '👶: '🟡',   # Yellow Circle
            '📈 ': '🟠',   # Orange Circle
            '📈£': '🟣',   # Purple Circle
            '🤖: '🌿',   # Herb
            '💰: '🌱',   # Sprout
            '📤: '🌱',   # Sprout
            '🟡: '🌽',   # Corn
            '📈 '🍅',   # Tomato
            '🚀: '🍕',   # Pizza
            '🎨: '🥒',   # Pickle
            '📱: '🤖',   # Robot
            '🎯: '🚨',   # Alarm
            '💰: '🚀',   # Rocket
            '📥': '🛒',   # Cart
            '📥: '🛒',   # Cart
            '🍽️': '🛒',   # Cart
            'âš«': '⚫',    # Black Circle
            'â‚¬': '€',     # Euro
        }
        
        for mojibake, emoji in replacements.items():
            content = content.replace(mojibake, emoji)
        
        final_len = len(content)
        replaced = original_len - final_len
        
        if replaced > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'path': str(filepath.relative_to('.')), 'replaced': replaced}
        return None
    
    except Exception as e:
        return None

# Process all Python files
root = Path('.')
py_files = [
    f for f in root.glob('**/*.py')
    if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)
]

print(f"Ultimate cleanup: {len(py_files)} files...\n")

results = []
total_chars_replaced = 0

for f in py_files:
    r = clean_file_with_emoji_map(f)
    if r:
        results.append(r)
        total_chars_replaced += r['replaced']
        if r['replaced'] > 10:
            print(f"[CLEANED] {r['path']}")

print(f"\n{'='*80}")
print(f"[FINAL RESULT] {len(results)} files cleaned")
print(f"Total characters replaced: {total_chars_replaced}")
print(f"{'='*80}\n")
