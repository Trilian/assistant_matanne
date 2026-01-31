#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL comprehensive mojibake cleanup - ALL production files - No emoji literals"""

from pathlib import Path

# Use ONLY unicode escape sequences - NO emoji literals
# Pattern: 📅 (mojibake) -> Unicode emoji code point
EMOJI_FIXES = {
    '\u00f0\u0178\u00a0\u0084': '\u274c',           # Stop/Error
    '\u00f0\u0178\u00a0\u0093': '\ud83d\udcda',           # Books
    '\u00f0\u0178\u00a0\u008f': '\ud83d\udded',           # Location  
    '\u00f0\u0178\u00a0\u0094': '\ud83d\udd04',           # Refresh
    '\u00f0\u0178\u00a0\u0095': '\ud83d\udce5',           # Import
    '\u00f0\u0178\u00a0\u0092': '\ud83d\udce4',           # Export
    '\u00f0\u0178\u00a0\u00ac': '\ud83d\udd14',           # Bell
    '\u00f0\u0178\u00a0\u009b': '\ud83d\udccb',           # Clipboard
    '\u00f0\u0178\u00a0\u009c': '\ud83d\udcdc',           # Document
    '\u00f0\u0178\u00a0\u009a': '\ud83d\udcda',           # Books
    '\u00f0\u0178\u00a0\u00b8': '\ud83d\udcf8',           # Camera
    '\u00f0\u0178\u00a0\u0091': '\ud83d\udcf1',           # Phone
    '\u00f0\u0178\u00a0\u0092': '\ud83d\udce2',           # Megaphone
    '\u00f0\u0178\u00a0\u0093': '\ud83d\udce3',           # Speaker
    '\u00f0\u0178\u00a0\u0085': '\ud83d\udcc5',           # Calendar
    '\u00f0\u0178\u00a0\u0086': '\ud83d\udcc6',           # Calendar
    '\u00f0\u0178\u00a0\u0088': '\ud83d\udcc8',           # Chart Up
    '\u00f0\u0178\u00a0\u0089': '\ud83d\udcc9',           # Chart Down
    '\u00f0\u0178\u00a0\u009b': '\ud83d\udccb',           # Clipboard
    '\u00f0\u0178\u00a0\u00a7': '\ud83d\udce7',           # Email
    '\u00f0\u0178\u00a0\u00ae': '\ud83d\udcae',           # Mailbox
    '\u00f0\u0178\u00a0\u00b5': '\ud83d\udcf5',           # No Phone
    '\u00f0\u0178\u00a0\u00b7': '\ud83d\udcf7',           # Camera
    '\u00f0\u0178\u00a0\u00ba': '\ud83d\udcfa',           # TV
    '\u00f0\u0178\u00a0\u008c': '\ud83c\udccf',           # Flags
    '\u00f0\u0178\u00a0\u0096': '\ud83d\udcd6',           # Book
    '\u00f0\u0178\u00a0\u0084': '\ud83d\udcc4',           # Document
    '\u00f0\u0178\u00a0\u009b': '\ud83d\udccc',           # Pushpin
    '\u00f0\u0178\u009d\u00bd': '\ud83c\udf7d',           # Plate
    '\u00f0\u0178\u00a4\u0096': '\ud83e\udd16',           # Robot
    '\u00f0\u0178\u0091\u00b0': '\ud83d\udcb0',           # Money
    '\u00f0\u0178\u0091\u00b5': '\ud83d\udcb5',           # Dollar Bill
    '\u00f0\u0178\u0091\u00a1': '\ud83d\udca1',           # Lightbulb
    '\u00f0\u0178\u0091\u00a4': '\ud83d\udc41',           # Eye
    '\u00f0\u0178\u0091\u00a7': '\ud83d\udc67',           # Girl
    '\u00f0\u0178\u0091\u00b6': '\ud83d\udc76',           # Baby
    '\u00f0\u0178\u0091\u00ac': '\ud83d\udc6c',           # Boys
    '\u00f0\u0178\u0091\u00a8': '\ud83d\udc68',           # Man
    '\u00f0\u0178\u0091\u00aa': '\ud83d\udc6a',           # Family
    '\u00f0\u0178\u0091\u00be': '\ud83d\udcbe',           # Floppy Disk
    '\u00f0\u0178\u0091\u008a': '\ud83d\udc8a',           # Pill
    '\u00f0\u0178\u0091\u009a': '\ud83d\udc9a',           # Heart
    '\u00f0\u0178\u0091\u0095': '\ud83d\udc95',           # Hearts
    '\u00f0\u0178\u0097\u0091': '\ud83d\uddd1',           # Trash
    '\u00f0\u0178\u0097\u009f': '\ud83d\udcdb',           # Trash
    '\u00f0\u0178\u0097\u00a1': '\ud83d\udde1',           # Sword
    '\u00f0\u0178\u0097\u00a3': '\ud83d\udde3',           # Speaking
    '\u00f0\u0178\u0097\u0094': '\ud83d\uddd4',           # Notepad
    '\u00f0\u0178\u0097\u0084': '\ud83d\uddc4',           # Filing
    '\u00f0\u0178\u0096\u008f': '\ud83d\ude4b',           # Hand
    '\u00f0\u0178\u0096\u00a5': '\ud83d\udda5',           # Desktop
    '\u00f0\u0178\u009f\u0080': '\ud83d\udfe0',           # Orange Circle
    '\u00f0\u0178\u009f\u0081': '\ud83d\udfe1',           # Yellow Circle
    '\u00f0\u0178\u009f\u0082': '\ud83d\udfe2',           # Green Circle
    '\u00f0\u0178\u009f\u0083': '\ud83d\udfe3',           # Purple Circle
    '\u00f0\u0178\u009f\u0083': '\u26ab',            # Black Circle
    '\u00f0\u0178\u009f\u0084': '\u26aa',            # White Circle
    '\u00f0\u0178\u0098\u00af': '\ud83c\udfaf',           # Target
    '\u00f0\u0178\u0098\u009b': '\ud83c\udffb',           # Target
    '\u00f0\u0178\u0098\u00a8': '\ud83c\udfa8',           # Art
    '\u00f0\u0178\u0098\u009b': '\ud83c\udf9b',           # Control Panel
    '\u00f0\u0178\u0098\u00aa': '\ud83c\udfaa',           # Circus
    '\u00f0\u0178\u0098\u00ae': '\ud83c\udfae',           # Game
    '\u00f0\u0178\u009a\u00a8': '\ud83d\udea8',           # Alarm
    '\u00f0\u0178\u009a\u0080': '\ud83d\ude80',           # Rocket
    '\u00f0\u0178\u009a\u00b5': '\ud83d\udeb5',           # Mountain Biker
    '\u00f0\u0178\u009a\u00b6': '\ud83d\udeb6',           # Walking
    '\u00f0\u0178\u009a\u0097': '\ud83d\ude97',           # Car
    '\u00f0\u0178\u00bc\u00bf': '\ud83c\udf3f',           # Herb
    '\u00f0\u0178\u00bc\u00b1': '\ud83c\udf31',           # Sprout
    '\u00f0\u0178\u00bc\u00b2': '\ud83c\udf32',           # Pine
    '\u00f0\u0178\u00bc\u00b3': '\ud83c\udf33',           # Deciduous Tree
    '\u00f0\u0178\u0085\u0095': '\ud83c\udf45',           # Tomato
    '\u00f0\u0178\u0085\u0095': '\ud83c\udf55',           # Pizza
    '\u00f0\u0178\u00a5\u0092': '\ud83e\udd92',           # Pickle
    '\u00f0\u0178\u00a7\u00b9': '\ud83e\uddf9',           # Broom
    '\u00f0\u0178\u00a7\u00ba': '\ud83e\uddfa',           # Basket
    '\u00f0\u0178\u00a7\u00bc': '\ud83e\uddfc',           # Sponge
    '\u00f0\u0178\u00a7\u00b8': '\ud83e\uddf8',           # Meditation
    '\u00f0\u0178\u00a5\u0097': '\ud83e\udd57',           # Salad
    '\u00f0\u0178\u0091\u0092': '\ud83d\uded2',           # Cart
    '\u00f0\u0178\u0098\u0080': '\ud83d\ude00',           # Smile
    '\u00f0\u0178\u0098\u00b4': '\ud83d\ude34',           # Sleep
    '\u00f0\u0178\u0098\u008a': '\ud83d\ude0a',           # Smile
    '\u00f0\u0178\u0098\u009e': '\ud83d\ude1e',           # Sad
    '\u00f0\u0178\u0087\u00ab': '\ud83c\uddfb',           # France
    '\u00f0\u0178\u0087\u00ac': '\ud83c\uddec',           # UK
    '\u00f0\u0178\u0087\u00aa': '\ud83c\uddea',           # Spain
    '\u00f0\u0178\u0087\u00a9': '\ud83c\udde9',           # Germany
    '\u00f0\u0178\u0099\u0089': '\ud83c\udf1f',           # Star
    '\u00c2\u00b1': '\u00b1',           # Plus-minus (fix encoding error)
}

def clean_file(filepath):
    """Clean a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        mojibake_count_before = 0
        for pattern in EMOJI_FIXES.keys():
            mojibake_count_before += content.count(pattern)
        
        if mojibake_count_before == 0:
            return None
        
        # Apply replacements
        for mojibake, emoji in EMOJI_FIXES.items():
            content = content.replace(mojibake, emoji)
        
        mojibake_count_after = 0
        for pattern in EMOJI_FIXES.keys():
            mojibake_count_after += content.count(pattern)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'path': str(filepath.relative_to('.')),
            'before': mojibake_count_before,
            'after': mojibake_count_after,
            'replaced': mojibake_count_before - mojibake_count_after
        }
    except Exception as e:
        return {'path': str(filepath.relative_to('.')), 'error': str(e)}

# Process all Python files
root = Path('.')
py_files = [
    f for f in root.glob('**/*.py')
    if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)
]

print(f"Processing {len(py_files)} files with {len(EMOJI_FIXES)} replacement patterns...\n")

results = []
total_replaced = 0

for f in py_files:
    r = clean_file(f)
    if r and 'error' not in r and r.get('replaced', 0) > 0:
        results.append(r)
        total_replaced += r['replaced']
        print(f"[OK] {r['path']}: {r['replaced']} patterns replaced")

print(f"\n{'='*80}")
print(f"[SUCCESS] COMPREHENSIVE CLEANUP COMPLETE")
print(f"Total files scanned: {len(py_files)}")
print(f"Files cleaned: {len(results)}")
print(f"Total patterns replaced: {total_replaced}")
print(f"{'='*80}\n")

# Save report
with open('CLEANUP_REPORT.txt', 'w', encoding='utf-8') as log:
    log.write("COMPREHENSIVE FINAL MOJIBAKE CLEANUP REPORT\n")
    log.write("=" * 80 + "\n\n")
    log.write(f"Patterns mapped: {len(EMOJI_FIXES)}\n")
    log.write(f"Total files scanned: {len(py_files)}\n")
    log.write(f"Files cleaned: {len(results)}\n")
    log.write(f"Total replaced: {total_replaced}\n\n")
    log.write("FILES CLEANED:\n")
    log.write("-" * 80 + "\n")
    for r in sorted(results, key=lambda x: x['replaced'], reverse=True):
        log.write(f"{r['path']}: {r['replaced']} patterns replaced\n")

print("[DONE] Report saved to CLEANUP_REPORT.txt")
