#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final binary-level mojibake cleanup"""

from pathlib import Path

# Byte-level replacements: mojibake UTF-8 bytes -> clean emoji UTF-8 bytes
BYTE_FIXES = {
    # Format: (mojibake_bytes, emoji_bytes)
    # 👧 prefix = b'\xc3\xb0\xc5\xb8', followed by various second parts
    
    # Basic structure: b'\xc3\xb0\xc5\xb8XXXX' -> emoji bytes
    
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x84': '❌'.encode(),           # 👧"´ -> ❌
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x93': '📚'.encode(),           # 👧"" -> 📚
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x8f': '📍'.encode(),           # 👧" -> 📍
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x94': '🔄'.encode(),           # 💰 -> 🔄
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x95': '📥'.encode(),           # 👧"¥ -> 📥
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x92': '📤'.encode(),           # 👧"¤ -> 📤
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\xac': '🔔'.encode(),           # 🧹 -> 🔔
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x9b': '📋'.encode(),           # 👧"› -> 📋
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x9c': '📜'.encode(),           # 👧"œ -> 📜
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x9a': '📚'.encode(),           # 👧"š -> 📚
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\xb8': '📸'.encode(),           # 📷 -> 📸
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x91': '📱'.encode(),           # 👧"' -> 📱
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x92': '📢'.encode(),           # 👧"' -> 📢
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x93': '📣'.encode(),           # 👧"" -> 📣
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x85': '📅'.encode(),           # 🎨 -> 📅
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x86': '📆'.encode(),           # 🗑️ -> 📆
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x88': '📈'.encode(),           # 🎯 -> 📈
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\x89': '📉'.encode(),           # 💡 -> 📉
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\xb5': '📵'.encode(),           # 📅 -> 📵
    b'\xc3\xb0\xc5\xb8\xc2\xa0\xc2\xb7': '📷'.encode(),           # 👧"· -> 📷
    b'\xc3\xb0\xc5\xb8\xc2\x91\xc2\xb6': '👶'.encode(),           # 👧'¶ -> 👶
    b'\xc3\xb0\xc5\xb8\xc2\x91\xc2\xb0': '💰'.encode(),           # 👧'° -> 💰
    b'\xc3\xb0\xc5\xb8\xc2\x91\xc2\xb5': '💵'.encode(),           # 🍽️ -> 💵
    b'\xc3\xb0\xc5\xb8\xc2\x91\xc2\xa1': '💡'.encode(),           # 👧'¡ -> 💡
    b'\xc3\xb0\xc5\xb8\xc2\x91\xc2\xa7': '👧'.encode(),           # 👧'§ -> 👧
    b'\xc3\xb0\xc5\xb8\xc2\x98\xc2\xaf': '🎯'.encode(),           # 📋 -> 🎯
    b'\xc3\xb0\xc5\xb8\xc2\x98\xc2\xa8': '🎨'.encode(),           # 🔔 -> 🎨
    b'\xc3\xb0\xc5\xb8\xc2\x9a\xc2\xa8': '🚨'.encode(),           # 👶 -> 🚨
    b'\xc3\xb0\xc5\xb8\xc2\x9a\xc2\x80': '🚀'.encode(),           # 👧š€ -> 🚀
    b'\xc3\xb0\xc5\xb8\xc2\x9f\xc2\x81': '🟡'.encode(),           # 👧Ÿ¡ -> 🟡
    b'\xc3\xb0\xc5\xb8\xc2\x9f\xc2\x82': '🟢'.encode(),           # 📱 -> 🟢
    b'\xc3\xb0\xc5\xb8\xc2\xbc\xc2\xbf': '🌿'.encode(),           # 👧Ō¿ -> 🌿
    b'\xc3\xb0\xc5\xb8\xc2\xa7\xc2\xb9': '🧹'.encode(),           # 🧹 -> 🧹
    b'\xc3\xb0\xc5\xb8\xc2\x97\xc2\x91': '🗑️'.encode(),          # 👧—' -> 🗑️
    b'\xc3\xb0\xc5\xb8\xc2\x9d\xc2\xbd': '🍽️'.encode(),          # 🚀 -> 🍽️
    b'\xc3\xb0\xc5\xb8\xc2\xa4\xc2\x96': '🤖'.encode(),           # 👧¤– -> 🤖
}

def clean_file_binary(filepath):
    """Clean file using binary replacement"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        mojibake_count_before = sum(content.count(pattern) for pattern in BYTE_FIXES.keys())
        if mojibake_count_before == 0:
            return None
        
        # Apply replacements
        for mojibake_bytes, emoji_bytes in BYTE_FIXES.items():
            content = content.replace(mojibake_bytes, emoji_bytes)
        
        mojibake_count_after = sum(content.count(pattern) for pattern in BYTE_FIXES.keys())
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        return {
            'path': str(filepath.relative_to('.')),
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

print(f"Binary cleanup: {len(py_files)} files, {len(BYTE_FIXES)} patterns...\n")

results = []
total_replaced = 0

for f in py_files:
    r = clean_file_binary(f)
    if r and 'error' not in r and r.get('replaced', 0) > 0:
        results.append(r)
        total_replaced += r['replaced']
        print(f"[{total_replaced}] {r['path']}: {r['replaced']} replaced")

print(f"\n{'='*80}")
print(f"[OK] BINARY CLEANUP: {total_replaced} patterns fixed in {len(results)} files")
print(f"{'='*80}\n")
