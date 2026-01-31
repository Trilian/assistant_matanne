#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final comprehensive mojibake cleanup - using byte-level approach"""

from pathlib import Path
import os

# Map mojibake byte patterns to their emoji UTF-8 replacements
# Using unicode character codes to avoid encoding issues
MOJIBAKE_REPLACEMENTS = [
    ('\u00f0\u0178\u00a0\u0084', '❌'),           # 📋´ → ❌
    ('\u00f0\u0178\u00a0\u0093', '📚'),          # 🟢 → 📚
    ('\u00f0\u0178\u00a0\u008f', '📍'),          # 📋 → 📍
    ('\u00f0\u0178\u00a0\u0094', '🔄'),          # 🗑️ → 🔄
    ('\u00f0\u0178\u00a0\u0095', '📥'),          # 📋¥ → 📥
    ('\u00f0\u0178\u00a0\u0092', '📤'),          # 📋¤ → 📤
    ('\u00f0\u0178\u0091\u009c', '💡'),          # 🍽️ → 💡
    ('\u00f0\u0178\u0091\u00a4', '👁️'),         # 📷 → 👁️
    ('\u00f0\u0178\u00a0\u00ac', '🔔'),          # 📋¬ → 🔔
    ('\u00f0\u0178\u00a0\u009b', '📌'),          # 🗑️ → 📌
    ('\u00f0\u0178\u0097\u0091', '🗑️'),        # 💰 → 🗑️
    ('\u00f0\u0178\u009d\u00bd', '🍽️'),        # 👧 → 🍽️
    ('\u00f0\u0178\u00a4\u0096', '🤖'),          # 🌿 → 🤖
    ('\u00f0\u0178\u00a0\u0088', '📈'),          # 💡 → 📈
    ('\u00f0\u0178\u00a0\u0086', '📦'),          # 🔔 → 📦
    ('\u00f0\u0178\u009d\u00bd', '🍽'),          # 💰 → 🍽️
    ('\u00f0\u0178\u00a0\u0091', '📑'),          # 👶 → 📑
    ('\u00f0\u0178\u00a0\u0089', '📊'),          # 👶 → 📊
    ('\u00f0\u0178\u00a0\u0099', '📙'),          # 📅 → 📙
    ('\u00f0\u0178\u00a0\u009a', '📚'),          # 💡 → 📚
    ('\u00f0\u0178\u00a0\u009b', '📋'),          # 🗑️ → 📋
    ('\u00f0\u0178\u00a0\u009c', '📜'),          # ⚫ → 📜
    ('\u00f0\u0178\u00a0\u00b8', '📸'),          # 📤 → 📸
    ('\u00f0\u0178\u0091\u00b6', '👶'),          # 📉 → 👶
    ('\u00f0\u0178\u00a0\u0091', '📱'),          # 👶 → 📱
    ('\u00f0\u0178\u00a0\u0092', '📢'),          # 👶 → 📢
    ('\u00f0\u0178\u00a0\u0093', '📣'),          # 🟢 → 📣
    ('\u00f0\u0178\u00a0\u0085', '📅'),          # 📈 → 📅
    ('\u00f0\u0178\u00a0\u0086', '📆'),          # 🔔 → 📆
    ('\u00f0\u0178\u00a0\u0089', '📉'),          # 👶 → 📉
    ('\u00f0\u0178\u0091\u0092', '🛒'),          # 🍽️ → 🛒
    ('\u00f0\u0178\u0091\u00b0', '💰'),          # 👧 → 💰
    ('\u00f0\u0178\u0091\u00b5', '💵'),          # 📱 → 💵
    ('\u00f0\u0178\u0091\u00a1', '💡'),          # 📷 → 💡
    ('\u00f0\u0178\u0091\u00a7', '👧'),          # 🤖 → 👧
    ('\u00f0\u0178\u0098\u009b', '🎯'),          # 📅 → 🎯
    ('\u00f0\u0178\u0098\u00af', '🎯'),          # 🚀 → 🎯
    ('\u00f0\u0178\u00a0\u00a5', '📥'),          # 📋¥ → 📥
    ('\u00f0\u0178\u00bc\u00bf', '🌿'),          # 🟡 → 🌿
    ('\u00f0\u0178\u00a7\u00b9', '🧹'),          # 🧹 → 🧹
    ('\u00f0\u0178\u0098\u00a8', '🎨'),          # 📥 → 🎨
    ('\u00f0\u0178\u009a\u00a8', '🚨'),          # 🧹 → 🚨
    ('\u00f0\u0178\u009a\u0080', '🚀'),          # 🍽️ → 🚀
    ('\u00f0\u0178\u009f\u0083', '⚫'),          # 📋ƒ → ⚫
    ('\u00f0\u0178\u009f\u0094', '⚪'),          # 📋„ → ⚪
    ('\u00f0\u0178\u009f\u0085', '🟅'),          # 📋… → 🟅
    ('\u00f0\u0178\u009f\u0080', '🟠'),          # 📋  → 🟠
    ('\u00f0\u0178\u009f\u0081', '🟡'),          # 📋¡ → 🟡
    ('\u00f0\u0178\u009f\u0082', '🟢'),          # 📋¢ → 🟢
    ('\u00f0\u0178\u00bc\u00bf', '🌿'),          # 🟡 → 🌿
    ('\u00f0\u0178\u00bc\u00b1', '🌱'),          # 📥  → 🌱
    ('\u00f0\u0178\u0085\u0095', '🍅'),          # 📱 → 🍅
    ('\u00f0\u0178\u00a0\u00b4', '📴'),          # 📋´ → 📴
    ('\u00f0\u0178\u00a0\u00b5', '📵'),          # 🎯 → 📵
]

def clean_file(filepath):
    """Clean one file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        original_mojibake_count = sum(content.count(old) for old, _ in MOJIBAKE_REPLACEMENTS)
        if original_mojibake_count == 0:
            return None
        
        # Apply all replacements
        for old, new in MOJIBAKE_REPLACEMENTS:
            content = content.replace(old, new)
        
        final_mojibake_count = sum(content.count(old) for old, _ in MOJIBAKE_REPLACEMENTS)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        replaced = original_mojibake_count - final_mojibake_count
        return {
            'path': str(filepath.relative_to('.')),
            'before': original_mojibake_count,
            'after': final_mojibake_count,
            'replaced': replaced
        }
    
    except Exception as e:
        return {'path': str(filepath.relative_to('.')), 'error': str(e)}

# Scan all Python files
root = Path('.')
py_files = [f for f in root.glob('**/*.py') if '__pycache__' not in str(f) and '.venv' not in str(f) and '.git' not in str(f)]

print(f"Scanning {len(py_files)} Python files...")

results = []
for f in py_files:
    r = clean_file(f)
    if r and 'error' not in r:
        results.append(r)
        if r.get('replaced', 0) > 0:
            print(f"✓ {r['path']}: replaced {r['replaced']} mojibake")

# Summary
total_replaced = sum(r.get('replaced', 0) for r in results)
files_cleaned = len([r for r in results if r.get('before', 0) > 0])

print(f"\n{'='*80}")
print(f"✅ FINAL CLEANUP COMPLETE")
print(f"Total files scanned: {len(py_files)}")
print(f"Files with mojibake: {files_cleaned}")
print(f"Total mojibake patterns replaced: {total_replaced}")
print(f"{'='*80}\n")

# Save detailed report
with open('FINAL_CLEANUP_REPORT.txt', 'w', encoding='utf-8') as log:
    log.write("FINAL COMPREHENSIVE MOJIBAKE CLEANUP REPORT\n")
    log.write("=" * 80 + "\n\n")
    log.write(f"Total files scanned: {len(py_files)}\n")
    log.write(f"Files with mojibake: {files_cleaned}\n")
    log.write(f"Total mojibake patterns replaced: {total_replaced}\n\n")
    log.write("DETAILS BY FILE:\n")
    log.write("-" * 80 + "\n")
    
    for r in results:
        if r.get('before', 0) > 0:
            log.write(f"{r['path']}: {r['replaced']} replaced (before: {r['before']}, after: {r['after']})\n")

print("Report saved to FINAL_CLEANUP_REPORT.txt")
