#!/usr/bin/env python3
"""Quick fix for manage.py emoji issues"""

with open(r'd:\Projet_streamlit\assistant_matanne\manage.py', 'rb') as f:
    content = f.read()

# Replace emoji bytes with text equivalents
fixes = [
    (b'\xe2\x9d\x8c', b'[ERROR]'),  # ❌
    (b'\xf0\x9f\x9a\x80', b'[RUN]'),  # 🚀
    (b'\xf0\x9f\xa7\xaa', b'[TEST]'),  # 🧪
    (b'\xf0\x9f\x93\x8a', b'[CHART]'),  # 📊
    (b'\xe2\x9c\xa8', b'[STAR]'),  # ✨
    (b'\xf0\x9f\x94\x8d', b'[SEARCH]'),  # 🔍
    (b'\xf0\x9f\x97\x84\xef\xb8\x8f', b'[DB]'),  # 🗄️
    (b'\xf0\x9f\x93\x9d', b'[EDIT]'),  # 📝
    (b'\xf0\x9f\x93\xa6', b'[PKG]'),  # 📦
    (b'\xe2\x9c\x85', b'[OK]'),  # ✅
    (b'\xf0\x9f\xa7\xb9', b'[CLEAN]'),  # 🧹
    (b'\xf0\x9f\x94\xa5', b'[FIRE]'),  # 🔥
]

for broken, fixed in fixes:
    content = content.replace(broken, fixed)

with open(r'd:\Projet_streamlit\assistant_matanne\manage.py', 'wb') as f:
    f.write(content)

print("manage.py fixed")
