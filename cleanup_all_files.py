#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean all mojibake emojis from all Python files in the project"""

import os
import re
from pathlib import Path

# Define the replacements
replacements = [
    ('📤´', '❌'),     # Critical
    ('🔔, '⏰'),     # Time/Calendar
    ('📤 ', '📍'),     # Location
    ('🧹, '🔄'),     # Refresh
    ('🔔, '📥'),     # Import
    ('👶, '📤'),     # Export
    ("📥, '💡'),     # Lightbulb/Suggestions
    ("🍽️, '👁️'),    # Eye/View
    ('💡, '🔔'),     # Bell/Notifications
    ('📌', '📌'),     # Unread marker
    ("🧹, '❌'),     # Delete
    ('⚫ '🍽️'),     # Plate with cutlery
    ('📷, '🤖'),     # Robot
    ('🟢, '📈'),     # Chart
    ('📅, '📦'),     # Package
    ('📋', '🍽️'),   # Plate
    ('🔔, '📔'),     # Notebook
    ('🚀, '📊'),     # Bar chart
    ('🟡, '📙'),     # Brown book
    ('👶, '📚'),     # Books
    ('📤‹', '📋'),     # Clipboard
    ('🎯, '📜'),     # Scroll
    ('👧, '📸'),     # Camera
    ('📉, '👶'),     # Baby
    ('🍽️, '📱'),     # Phone
    ('📤¢', '📢'),     # Megaphone
    ('🌿, '📣'),     # Loudspeaker
    ('🎯, '📅'),     # Calendar
    ('📤†', '📆'),     # Calendar grid
    ('💰, '📉'),     # Declining chart
    ('📉, '🛒'),     # Shopping cart
    ('🗑️, '💰'),     # Money
    ('🗑️, '💵'),     # Dollar
    ('📈, '💣'),     # Bomb
    ('👧, '💡'),     # Lightbulb
    ('🎨', '👀'),    # Eyes
    ('⚫¸', '🗑️'),   # Trash
    ('💰¸', '🗄️'),   # Filing cabinet
    ('📱, '💾'),     # Disk
    ('📋€📤€🎨€📅, '👨‍👩‍👧‍👦'),  # Family
    ('🤖, '📱'),     # Mobile phone
    ('â„¹ï¸', 'ℹ️'),     # Info
    ('🟢Ÿ‡·', '🇫🇷'),     # France flag
    ('📥Ÿ‡§', '🇬🇧'),     # UK flag
    ('🚀Ÿ‡¸', '🇪🇸'),     # Spain flag
    ('📱Ÿ‡ª', '🇩🇪'),     # Germany flag
    ('📷, '📷'),     # Camera
    ('🤖, '📱'),     # Phone
    ('💡, '🟡'),     # Yellow circle
]

def clean_file(filepath):
    """Clean mojibake from a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_count = content.count('📅
        
        if original_count == 0:
            return None
        
        # Apply all replacements
        for old, new in replacements:
            content = content.replace(old, new)
        
        final_count = content.count('📅
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'path': str(filepath),
            'before': original_count,
            'after': final_count,
            'replaced': original_count - final_count
        }
    except Exception as e:
        return {'path': str(filepath), 'error': str(e)}

# Find all Python files
project_root = Path('.')
py_files = list(project_root.glob('**/*.py'))

# Filter out __pycache__ and venv
py_files = [f for f in py_files if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)]

print(f"Found {len(py_files)} Python files to check...")

# Process all files
results = []
for py_file in py_files:
    result = clean_file(py_file)
    if result:
        results.append(result)

# Log results
total_before = 0
total_replaced = 0
files_with_mojibake = 0

with open('all_files_cleanup_log.txt', 'w') as log:
    log.write(f"Cleanup Report - {len(py_files)} files scanned\n")
    log.write("=" * 80 + "\n\n")
    
    for result in results:
        if 'error' in result:
            log.write(f"ERROR: {result['path']}: {result['error']}\n")
        else:
            log.write(f"File: {result['path']}\n")
            log.write(f"  Before: {result['before']} mojibake chars\n")
            log.write(f"  After: {result['after']} mojibake chars\n")
            log.write(f"  Replaced: {result['replaced']}\n\n")
            total_before += result['before']
            total_replaced += result['replaced']
            if result['before'] > 0:
                files_with_mojibake += 1
    
    log.write("=" * 80 + "\n")
    log.write(f"SUMMARY:\n")
    log.write(f"Files with mojibake: {files_with_mojibake}\n")
    log.write(f"Total mojibake before: {total_before}\n")
    log.write(f"Total replaced: {total_replaced}\n")
    log.write(f"Remaining: {total_before - total_replaced}\n")

print(f"\n✅ Cleanup complete!")
print(f"Files processed: {len(results)}")
print(f"Total mojibake replaced: {total_replaced}")
print(f"Log saved to: all_files_cleanup_log.txt")
