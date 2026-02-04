#!/usr/bin/env python3
"""Fix conftest.py by removing broken characters."""
import re
from pathlib import Path

conftest_path = Path("tests/conftest.py")
content = conftest_path.read_text(encoding='utf-8')

# Replace all broken box-drawing characters with proper ===
pattern = r'#+â•[â•]*'
cleaned = re.sub(pattern, '# ' + '='*80, content)

# Also fix any remaining UTF-8 mojibake with Ã‰
cleaned = cleaned.replace('Ã‰pices', 'Epices')

conftest_path.write_text(cleaned, encoding='utf-8')
print("✓ conftest.py cleaned successfully")
