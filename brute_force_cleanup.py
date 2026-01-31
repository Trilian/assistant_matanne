#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Brute force binary replacement of mojibake patterns"""

from pathlib import Path

def cleanup_all_files():
    """Replace mojibake patterns at byte level across all files"""
    
    # This is the MOJIBAKE PREFIX byte sequence
    #  📈 in UTF-8 = C3 B0 C5 B8
    mojibake_prefix = b'\xc3\xb0\xc5\xb8'
    
    # Common emojis in UTF-8
    emoji_map = {
        # Format: (suffix_bytes, replacement_emoji_bytes)
        (b'\xc5\xbd\xc2\xaf',): '🎯'.encode('utf-8'),  # 📱
        (b'\xc5\xbd\xc2\xa8',): '🎨'.encode('utf-8'),  # 📤
        (b'\xc2\x9d\xc2\xbd',): '🍽️'.encode('utf-8'),  # 👧
        (b'\xc2\x91\xc2\xb6',): '👶'.encode('utf-8'),  # 🚀
        (b'\xc2\x91\xc2\xb0',): '💰'.encode('utf-8'),  # 📈'°
        (b'\xc2\x91\xc2\xa1',): '💡'.encode('utf-8'),  # 📈'¡
        (b'\xc2\x91\xc2\xa7',): '👧'.encode('utf-8'),  # 📈'§
        (b'\xc2\xa0\xc2\xb1',): '📱'.encode('utf-8'),  # 📈"±
        (b'\xc2\xa0\xc2\xb5',): '📵'.encode('utf-8'),  # 📅
        (b'\xc2\xa0\xc2\xb7',): '📷'.encode('utf-8'),  # 📈"·
        (b'\xc2\xa0\xc2\x88',): '📈'.encode('utf-8'),  # 💡
        (b'\xc2\xa0\xc2\x89',): '📉'.encode('utf-8'),  # 👶
        (b'\xc2\xa0\xc2\x85',): '📅'.encode('utf-8'),  # 📥
        (b'\xc2\xa0\xc2\x86',): '📆'.encode('utf-8'),  # 📋
        (b'\xc2\xa0\xc2\x9b',): '📋'.encode('utf-8'),  # 📈"›
        (b'\xc2\xa0\xc2\x9c',): '📜'.encode('utf-8'),  # 📈"œ
        (b'\xc2\xa0\xc2\x9a',): '📚'.encode('utf-8'),  # 📈"š
        (b'\xc2\xa0\xc2\xb8',): '📸'.encode('utf-8'),  # 🎨
        (b'\xc2\xa0\xc2\x92',): '📤'.encode('utf-8'),  # 📈"¤
        (b'\xc2\xa0\xc2\x95',): '📥'.encode('utf-8'),  # 📈"¥
        (b'\xc2\x97\xc2\x91',): '🗑️'.encode('utf-8'),   # 📈—'
        (b'\xc2\x97\xc2\x9f',): '🗑️'.encode('utf-8'),   # 🍽️
        (b'\xc2\x97\xc2\x94',): '🗒️'.encode('utf-8'),   # 🔔
        (b'\xc2\xa7\xc2\xb9',): '🧹'.encode('utf-8'),  # 🧹
        (b'\xc2\x9f\xc2\x82',): '🟢'.encode('utf-8'),  # 🧹¢
        (b'\xc2\x9f\xc2\x81',): '🟡'.encode('utf-8'),  # 🧹¡
        (b'\xc2\x9f\xc2\x80',): '🟠'.encode('utf-8'),  # 🧹 
        (b'\xc2\x9f\xc2\x83',): '🟣'.encode('utf-8'),  # 🧹£
        (b'\xc2\xbc\xc2\xbf',): '🌿'.encode('utf-8'),  # 📈Ō¿
        (b'\xc2\xbc\xc2\xb1',): '🌱'.encode('utf-8'),  # 🗑️
        (b'\xc2\xbc\xc2\xb2',): '🌲'.encode('utf-8'),  # 🎯
        (b'\xc2\x85\xc2\x95',): '🍅'.encode('utf-8'),  # 📈…•
        (b'\xc2\x9a\xc2\xa8',): '🚨'.encode('utf-8'),  # 💰
        (b'\xc2\x9a\xc2\x80',): '🚀'.encode('utf-8'),  # 📈š€
        (b'\xc2\xa4\xc2\x96',): '🤖'.encode('utf-8'),  # 📈¤–
        (b'\xc2\xa5\xc2\x92',): '🛒'.encode('utf-8'),  # 📈¥'
    }
    
    root = Path('.')
    py_files = [
        f for f in root.glob('**/*.py')
        if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)
    ]
    
    print(f"Binary cleanup: {len(py_files)} files\n")
    
    total_replaced = 0
    files_touched = 0
    
    for filepath in py_files:
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            original = content
            
            # Replace each mojibake pattern
            for (suffix,), emoji_bytes in emoji_map.items():
                mojibake_full = mojibake_prefix + suffix
                count_before = content.count(mojibake_full)
                content = content.replace(mojibake_full, emoji_bytes)
                count_after = content.count(mojibake_full)
                if count_before > count_after:
                    total_replaced += (count_before - count_after)
            
            if content != original:
                with open(filepath, 'wb') as f:
                    f.write(content)
                files_touched += 1
                print(f"✓ {str(filepath.relative_to('.'))}")
        
        except Exception as e:
            pass
    
    print(f"\n{'='*80}")
    print(f"[COMPLETE] Replaced {total_replaced} mojibake in {files_touched} files")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    cleanup_all_files()
