#!/usr/bin/env python3
"""Fix all corrupted emojis in cuisine UI files"""

import os

files_to_fix = [
    "src/domains/cuisine/ui/inventaire.py",
    "src/domains/cuisine/ui/planning.py",
]

# Using unicode escapes to avoid encoding issues
emoji_map = {
    'ðŸ"¦': '\U0001f4e6',  # 📦
    'ðŸ"Š': '\U0001f4ca',  # 📊
    'ðŸ"š': '\U0001f4da',  # 📚
    'ðŸ"œ': '\U0001f4dc',  # 📜
    'ðŸ"¸': '\U0001f4f8',  # 📸
    'ðŸ""': '\U0001f4de',  # 📞
    'ðŸ"§': '\U0001f4e7',  # 📧
    'ðŸ"®': '\U0001f4ee',  # 📮
    'ðŸ"ˆ': '\U0001f4c8',  # 📈
    'ðŸ"‰': '\U0001f4c9',  # 📉
    'ðŸ"Œ': '\U0001f4cc',  # 📌
    'ðŸ"„': '\U0001f4c4',  # 📄
    'ðŸ"¥': '\U0001f4e5',  # 📥
    'ðŸ"¤': '\U0001f4e4',  # 📤
    'ðŸ"³': '\U0001f4f3',  # 📳
    'ðŸ"¬': '\U0001f4ec',  # 📬
    'ðŸ"´': '\U0001f534',  # 🔴
    'ðŸŸ ': '\U0001f7e0',  # 🟠
    'ðŸŸ¡': '\U0001f7e1',  # 🟡
    'ðŸŸ¢': '\U0001f7e2',  # 🟢
    'ðŸŸ£': '\U0001f7e3',  # 🟣
    'âœ¨': '\u2728',  # ✨
    'âš ï¸': '\u26a0\ufe0f',  # ⚠️
    'ðŸ·ï¸': '\U0001f3f7\ufe0f',  # 🏷️
    'ðŸ›'': '\U0001f6cd',  # 🛍
    'âœ…': '\u2705',  # ✅
    'âŒ': '\u274c',  # ❌
    'âœï¸': '\u270f\ufe0f',  # ✏️
    'ðŸ—'ï¸': '\U0001f5d1\ufe0f',  # 🗑️
    'ðŸ'€': '\U0001f440',  # 👀
    'ðŸ¤–': '\U0001f916',  # 🤖
    'ðŸš¨': '\U0001f6a8',  # 🚨
    'ðŸ†•': '\U0001f195',  # 🆕
    'ðŸš€': '\U0001f680',  # 🚀
    'âœ"': '\u2714',  # ✔
    'â€¢': '\u2022',  # •
    'â„¹ï¸': '\u2139\ufe0f',  # ℹ️
    'ðŸ'¡': '\U0001f4a1',  # 💡
}

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"File {filepath} not found")
        continue
    
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for corrupted, correct in emoji_map.items():
        content = content.replace(corrupted, correct)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"{filepath} already clean")

print("Done!")
