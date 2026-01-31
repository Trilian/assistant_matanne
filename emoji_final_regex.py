#!/usr/bin/env python3
"""Final attempt - replace mojibake with regex that finds the pattern and removes it"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

before = content.count('ðŸ')

# Use regex to find and replace remaining mojibake patterns
# These don't have a space immediately after, so simpler pattern

import re

# Pattern: ðŸ followed by any 2-4 characters that are not alphanumeric 
# This should catch all remaining mojibake

# Match ðŸ followed by non-alnum chars but keep the following word/content
def replace_final_mojibake(text):
    """Replace final mojibake instances by looking at context"""
    
    # All these start with ðŸ" 
    patterns_to_fix = [
        (r'ðŸ"(.*?Emplacement)', r'📍\1'),  # ðŸ" at start of Emplacement
        (r'ðŸ"(.*?rayon)', r'📍\1'),         # ðŸ" at start of location context
        (r'ðŸ—.*?Supprimer', '❌ Supprimer'), # ðŸ—' with delete
        (r'ðŸ"¥.*?Import', '📥 Import'),     # ðŸ"¥ with import
        (r'ðŸ"¥.*?Export', '📥 Export'),     # ðŸ"¥ with export  
        (r'ðŸ"(.*?Analyse)', r'📍\1'),       # ðŸ" with Analyse
        (r'ðŸ—', '❌'),                       # Any remaining ðŸ—
    ]
    
    for pattern, replacement in patterns_to_fix:
        text = re.sub(pattern, replacement, text)
    
    return text

content = replace_final_mojibake(content)
after = content.count('ðŸ')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

with open('final_regex_log.txt', 'w') as log:
    log.write(f"Before: {before}\n")
    log.write(f"After: {after}\n")
    log.write(f"Success: {before > after}\n")
