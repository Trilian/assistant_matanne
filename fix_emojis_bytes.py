#!/usr/bin/env python3
"""Fix corrupted emojis in inventaire.py using byte-level replacement"""

file_path = r'd:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py'

with open(file_path, 'rb') as f:
    raw_bytes = f.read()

# Work with raw bytes - mapping corrupted UTF-8 sequences to correct emojis
# Using the actual byte sequences detected in the file (84 occurrences)
replacements_bytes = [
    # Main pattern with different endings
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa6', b'\xf0\x9f\x93\xa6'),  # ðŸ"¦ -> 📦 (package)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc5\xa0', b'\xf0\x9f\x93\x8a'),  # ðŸ"Š -> 📊 (chart)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xe2\x80\x9c', b'\xf0\x9f\x93\x94'),  # ðŸ"" -> 📔 (notebook)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xb8', b'\xf0\x9f\x93\xb8'),  # ðŸ"¸ -> 📸 (camera)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc5\xb0', b'\xf0\x9f\x93\x9c'),  # ðŸ"° -> 📜 (scroll)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xae', b'\xf0\x9f\x93\xae'),  # ðŸ"® -> 📮 (mailbox)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9c\xc2\xa7', b'\xf0\x9f\x93\xa7'),  # ðŸ"§ -> 📧 (email)
    (b'\xc3\xb0\xc5\xb8\xe2\x80\x9b\xe2\x80\x99', b'\xf0\x9f\x9b\x92'),  # ðŸ›' -> 🛒 (shopping cart)
    (b'\xc3\xaa\xc5\xa1\xc2\xa0\xc3\xaf\xc2\xb8', b'\xe2\x9a\xa0\xef\xb8\x8f'),  # êš ï¸ -> ⚠️ (warning)
]

content_bytes = raw_bytes
replaced_count = 0
for broken_bytes, fixed_bytes in replacements_bytes:
    count = content_bytes.count(broken_bytes)
    if count > 0:
        replaced_count += count
        print(f"Replacing {repr(broken_bytes)}: {count} occurrences")
    content_bytes = content_bytes.replace(broken_bytes, fixed_bytes)

with open(file_path, 'wb') as f:
    f.write(content_bytes)

print(f"Fixed {replaced_count} corrupted emoji sequences in inventaire.py")
