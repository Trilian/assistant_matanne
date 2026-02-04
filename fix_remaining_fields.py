#!/usr/bin/env python3
"""
Fix remaining jour=jour issues in test file
"""

import re
from pathlib import Path

TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def fix_jour_variable(content):
    """Fix jour=jour cases by replacing with date_repas mapping."""
    count = 0
    
    # Find test functions that use jour=jour pattern
    # Pattern: for jour in jours: ... Repas(..., jour=jour, ...)
    
    # We'll add the mapping dictionary at the beginning of tests that use it
    # Then replace jour=jour with date_repas=jour_to_date[jour]
    
    # First: Replace jour=jour with date_repas=jour_to_date[jour]
    pattern = r'jour\s*=\s*jour\s*([,\)])'
    replacement = r'date_repas=jour_to_date[jour]\1'
    
    matches = list(re.finditer(pattern, content))
    content = re.sub(pattern, replacement, content)
    count = len(matches)
    
    # Now add the jour_to_date mapping to tests that need it
    # Find all test functions that contain jour_to_date[jour]
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is a test definition
        if re.match(r'\s*def\s+test_\w+\(self,\s*db:\s*Session\):', line):
            # Look ahead to find docstring end
            j = i + 1
            docstring_found = False
            while j < len(lines) and j < i + 10:
                new_lines.append(lines[j])
                # Check if docstring ends
                if '"""' in lines[j] and j > i + 1:
                    docstring_found = True
                    # Now check if this test uses jour_to_date[jour]
                    # Look ahead in the test
                    test_content = '\n'.join(lines[j:min(j+50, len(lines))])
                    if 'jour_to_date[jour]' in test_content:
                        # Add the mapping after the docstring
                        indent = '        '
                        new_lines.append(f'{indent}jour_to_date = {{')
                        new_lines.append(f'{indent}    "lundi": date(2025, 2, 3),')
                        new_lines.append(f'{indent}    "mardi": date(2025, 2, 4),')
                        new_lines.append(f'{indent}    "mercredi": date(2025, 2, 5),')
                        new_lines.append(f'{indent}    "jeudi": date(2025, 2, 6),')
                        new_lines.append(f'{indent}    "vendredi": date(2025, 2, 7),')
                        new_lines.append(f'{indent}    "samedi": date(2025, 2, 8),')
                        new_lines.append(f'{indent}    "dimanche": date(2025, 2, 9),')
                        new_lines.append(f'{indent}}}')
                    break
                j += 1
            
            i = j
        else:
            i += 1
    
    return '\n'.join(new_lines), count

def main():
    print(f"📂 Reading file: {TEST_FILE}")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ File read: {len(content)} characters")
    
    # Fix remaining jour=jour
    print("\n🔧 Fixing remaining jour=jour cases...")
    content, count = fix_jour_variable(content)
    print(f"   → {count} jour=jour patterns replaced")
    
    # Check syntax
    print(f"\n💾 Saving file...")
    try:
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ File saved: {TEST_FILE}")
        
        print("\n🔍 Checking Python syntax...")
        try:
            compile(content, str(TEST_FILE), 'exec')
            print("✓ Python syntax valid")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            print(f"   Line: {e.lineno}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n" + "="*60)
        print("✅ Script executed successfully!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Error during execution")
        print("="*60)
        exit(1)
