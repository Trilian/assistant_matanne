#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean all mojibake emojis from all Python files"""

import os
from pathlib import Path

# Define replacements using unicode escapes to avoid mojibake in this file itself
replacements = [
    (u'\u00f0\u0178\u201d\u00b4', u'❌'),      # Critical
    (u'\u00f0\u0178\u201d\u201d', u'⏰'),      # Time
    (u'\u00f0\u0178\u201d ', u'📍'),          # Location
    (u'\u00f0\u0178\u201d\u201e', u'🔄'),     # Refresh
    (u'\u00f0\u0178\u201d\u00a5', u'📥'),     # Import
    (u'\u00f0\u0178\u201d\u00a4', u'📤'),     # Export
    (u'\u00f0\u0178\u203a\u2018', u'💡'),     # Lightbulb
    (u'\u00f0\u0178\u2018\u20ac', u'👁️'),    # Eye
    (u'\u00f0\u0178\u201d\u00ac', u'🔔'),     # Bell
    (u'\u00f0\u0178\u2020\u2022', u'📌'),     # Pin
]

def clean_file(filepath):
    """Clean mojibake from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Count total mojibake (📅 prefix)
        original_count = content.count(u'\u00f0\u0178')
        
        if original_count == 0:
            return None
        
        # Apply replacements
        for old, new in replacements:
            content = content.replace(old, new)
        
        final_count = content.count(u'\u00f0\u0178')
        
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

# Filter out cache and venv
py_files = [f for f in py_files if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)]

results = []
for py_file in py_files:
    result = clean_file(py_file)
    if result:
        results.append(result)

# Write log without emojis
total_before = sum(r.get('before', 0) for r in results if 'before' in r)
total_replaced = sum(r.get('replaced', 0) for r in results if 'replaced' in r)
files_cleaned = len([r for r in results if r.get('before', 0) > 0])

with open('all_files_cleanup_log.txt', 'w') as log:
    log.write("Cleanup Report\n")
    log.write("=" * 80 + "\n")
    log.write(f"Total files: {len(py_files)}\n")
    log.write(f"Files with mojibake: {files_cleaned}\n")
    log.write(f"Total mojibake chars replaced: {total_replaced}\n\n")
    
    for result in results:
        if 'error' in result:
            log.write(f"ERROR: {result['path']}: {result['error']}\n")
        elif result.get('before', 0) > 0:
            log.write(f"{result['path']}: {result['before']} -> {result['after']} (replaced {result['replaced']})\n")

print("Cleanup complete!")
