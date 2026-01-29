#!/usr/bin/env python3
"""Detect the actual byte sequences of corrupted emojis"""

with open(r'd:\Projet_streamlit\assistant_matanne\src\domains\cuisine\ui\inventaire.py', 'rb') as f:
    content = f.read()

# Show hex representation of first 200 bytes around line 40
start = content.find(b'page_title')
if start >= 0:
    section = content[start:start+100]
    print("Section with page_title:")
    print(repr(section))
    print("\nAs hex:")
    print(section.hex())
