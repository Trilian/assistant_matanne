#!/usr/bin/env python3
"""Brute force emoji cleanup - replace all mojibake prefixes"""

file_path = r"src/domains/cuisine/ui/inventaire.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Map of mojibake patterns to better emojis
# These patterns include the ðŸ prefix and the next character

import re

# Replace all "ðŸ?? " patterns where ?? is any 2 chars
def replace_mojibake_icon(match):
    """Replace mojibake emoji icons with their meaning"""
    full = match.group(0)
    
    # Extract the 2 chars after ðŸ
    suffix = full[2:4] if len(full) > 3 else ""
    
    #Map suffix to real emoji
    mapping = {
        '"´': '❌',   # Critical
        '""': '⏰',   # Time
        '" ': '📍',   # Location
        '"„': '🔄',   # Refresh
        '"¥': '📥',   # Import
        '›\'': '💡',  # Suggestions
        '\'€': '👁️',  # View
        '"¤': '📤',   # Export
        '—\'': '❌',  # Delete
        '"¬': '🔔',   # Notifications
        '†•': '📌',   # Unread
    }
    
    # Default: use generic thinking emoji if not in map
    replacement = mapping.get(suffix, '💭')
    
    # Return just the emoji, dropping the mojibake
    return replacement

# Find and replace all patterns
# Look for: ðŸ followed by any 2 characters then a space or quote
content_before = content.count('ðŸ')
content = re.sub(r'ðŸ..(?=[\s"\'])', replace_mojibake_icon, content)
content_after = content.count('ðŸ')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

with open('emoji_cleanup_log.txt', 'w') as log:
    log.write(f"Mojibake before: {content_before}\n")
    log.write(f"Mojibake after: {content_after}\n") 
    log.write(f"Removed: {content_before - content_after}\n")
