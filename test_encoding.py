#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-encode files from Latin-1 (mojibake) to proper UTF-8"""

from pathlib import Path

def fix_file_encoding(filepath):
    """Read file as Latin-1 (which gives us the mojibake bytes),
       decode those bytes as UTF-8 (which reveals the real emoji),
       then write back as UTF-8"""
    try:
        # Read as binary
        with open(filepath, 'rb') as f:
            content_bytes = f.read()
        
        try:
            # Try to decode as UTF-8 first (if file is already correct)
            decoded = content_bytes.decode('utf-8')
            # Check if it has mojibake
            if '📅 not in decoded:
                return None  # Already OK
            
            # Has mojibake - need to fix
            # The mojibake was created by: UTF-8 bytes read as Latin-1
            # To fix: decode as Latin-1, encode as UTF-8
            decoded_as_latin1 = content_bytes.decode('latin-1')
            # Now the mojibake characters should become real emoji when encoded
            fixed_bytes = decoded_as_latin1.encode('utf-8')
            
            # But wait - that won't work because latin-1 encoding creates NEW mojibake
            # The real solution: the mojibake bytes ARE the UTF-8 bytes
            # So: read as binary, write as binary (no change needed)
            # Actually the problem is: the file contains UTF-8 bytes that were DECODED as Latin-1
            
            # Real fix: 
            # The mojibake "🎯 = bytes [c3 b0 c5 b8]
            # These bytes when decoded as UTF-8 would give: "🎯 (the mojibake we see)
            # When decoded as UTF-8-THROUGH-LATIN1 gives: emoji
            # So:
            # 1. Decode bytes as Latin-1 -> get "💡"  string with mojibake
            # 2. Encode that string as UTF-8 -> get bytes [c3 ... - the mojibake representation]
            # WRONG approach
            
            # CORRECT approach:
            # Mojibake means: bytes meant to be UTF-8 emoji were interpreted as Latin-1
            # The bytes in file are: UTF-8 emoji bytes
            # They're displayed wrong because editor thought they were Latin-1
            # Solution: read as binary, write as binary (file is actually correct!)
            # But if we re-save in UTF-8 encoding, it might double-encode
            
            # Test: let's see what we get
            print(f"File {filepath}:")
            print(f"  Bytes (hex): {content_bytes[1500:1530].hex()}")
            print(f"  Read as UTF-8: {content_bytes[1500:1530].decode('utf-8', errors='replace')}")
            print(f"  Read as Latin-1: {content_bytes[1500:1530].decode('latin-1')}")
            return None
            
        except UnicodeDecodeError:
            # File can't be decoded as UTF-8
            # Try Latin-1 (which always works)
            text = content_bytes.decode('latin-1')
            
            if '📅 not in text:
                return None  # No mojibake
            
            # Has mojibake - fix it
            # The mojibake was created by UTF-8 bytes being read as Latin-1 chars
            # Solution: encode back to bytes using UTF-8 (which gives UTF-8 bytes)
            # Then decode as UTF-8 (which gives emoji)
            # NO - that creates double encoding
            
            # Real solution: The UTF-8 bytes are in the file
            # We just need to ensure the file is saved as UTF-8
            # Since we read as Latin-1, we need to:
            # 1. Get the original bytes (which are UTF-8 emoji bytes)
            # 2. Write them back directly
            
            with open(filepath, 'wb') as f:
                f.write(content_bytes)
            
            return {'path': str(filepath.relative_to('.')), 'status': 'rewritten_binary'}
    
    except Exception as e:
        print(f"ERROR {filepath}: {e}")
        return None

# Just test first
root = Path('.')
test_files = [
    root / 'src/domains/shared/ui/barcode.py',
    root / 'src/domains/shared/ui/rapports.py',
]

for f in test_files:
    if f.exists():
        fix_file_encoding(f)
