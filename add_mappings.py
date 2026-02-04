#!/usr/bin/env python3
"""
Add jour_to_date mappings to all tests that use it
"""

import re
from pathlib import Path

TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def add_missing_jour_to_date_mappings(content):
    """Add jour_to_date mapping to tests that use jour_to_date[jour] but don't have the mapping."""
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    mapping_dict = [
        '        jour_to_date = {',
        '            "lundi": date(2025, 2, 3),',
        '            "mardi": date(2025, 2, 4),',
        '            "mercredi": date(2025, 2, 5),',
        '            "jeudi": date(2025, 2, 6),',
        '            "vendredi": date(2025, 2, 7),',
        '            "samedi": date(2025, 2, 8),',
        '            "dimanche": date(2025, 2, 9),',
        '        }',
    ]
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is a test definition
        if re.match(r'\s*def\s+test_\w+\(self,\s*db:\s*Session\):', line):
            # Look ahead to find the docstring and check if the test uses jour_to_date[jour]
            j = i + 1
            docstring_end = -1
            uses_jour_to_date = False
            has_mapping = False
            
            # Scan ahead to find docstring end and check usage
            while j < len(lines) and j < i + 100:
                if '"""' in lines[j] and j > i + 1:
                    docstring_end = j
                    break
                j += 1
            
            if docstring_end > 0:
                # Check the test content for jour_to_date[jour] usage
                test_content = '\n'.join(lines[docstring_end:min(docstring_end + 50, len(lines))])
                uses_jour_to_date = 'jour_to_date[jour]' in test_content
                has_mapping = 'jour_to_date = {' in test_content
                
                # If it uses jour_to_date but doesn't have the mapping, add it after docstring
                if uses_jour_to_date and not has_mapping:
                    # Add the docstring line
                    new_lines.append(lines[docstring_end])
                    # Add the mapping
                    for mapping_line in mapping_dict:
                        new_lines.append(mapping_line)
                    # Now continue with the rest
                    for k in range(docstring_end + 1, len(lines)):
                        if k > docstring_end and re.match(r'\s*def\s+test_', lines[k]):
                            # Next test definition found
                            i = k - 1
                            break
                        new_lines.append(lines[k])
                        if k == len(lines) - 1:
                            i = k
                    if i >= len(lines) - 1:
                        break
                elif docstring_end > 0:
                    # Add docstring and continue normally
                    for k in range(docstring_end + 1, min(docstring_end + 50, len(lines))):
                        new_lines.append(lines[k])
                        if re.match(r'\s*def\s+test_', lines[k]):
                            i = k - 1
                            break
                    else:
                        i = docstring_end
        
        i += 1
    
    return '\n'.join(new_lines)

def main():
    print(f"📂 Reading file: {TEST_FILE}")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ File read: {len(content)} characters")
    
    # Count current usage
    current_uses = len(re.findall(r'jour_to_date\[jour\]', content))
    current_mappings = len(re.findall(r'jour_to_date = \{', content))
    
    print(f"   → Current jour_to_date[jour] usages: {current_uses}")
    print(f"   → Current jour_to_date = {{ mappings: {current_mappings}")
    
    # This is complex - let's just use a simpler approach
    # Add mappings using regex more carefully
    
    # Pattern: find "def test_planning_...\n    """..."""\n    planning = Planning"
    # Add the mapping right after the closing """
    
    pattern = r'(def test_planning_\w+\(self, db: Session\):\s*"""[^"]*""")\n(\s*)(.*?jour_to_date\[jour\])'
    
    def add_mapping(match):
        docstring_part = match.group(1)
        indent = match.group(2)
        rest = match.group(3)
        
        # Check if mapping already exists in this block
        block_text = match.group(0)
        if 'jour_to_date = {' in block_text:
            return match.group(0)
        
        # Add the mapping
        mapping = f'\n{indent}jour_to_date = {{\n{indent}    "lundi": date(2025, 2, 3),\n{indent}    "mardi": date(2025, 2, 4),\n{indent}    "mercredi": date(2025, 2, 5),\n{indent}    "jeudi": date(2025, 2, 6),\n{indent}    "vendredi": date(2025, 2, 7),\n{indent}    "samedi": date(2025, 2, 8),\n{indent}    "dimanche": date(2025, 2, 9),\n{indent}}}\n{indent}'
        
        return f'{docstring_part}\n{mapping}{rest}'
    
    # This regex approach is complex. Let's do a simpler line-by-line approach
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Look for tests that use jour_to_date[jour]
        if i < len(lines) - 5:
            # Check if next 5 lines contain jour_to_date[jour] 
            next_block = '\n'.join(lines[i:min(i+20, len(lines))])
            
            # If this is docstring end and next block uses jour_to_date[jour]
            if '"""' in line and re.match(r'\s{8}"""', line) and 'jour_to_date[jour]' in next_block:
                # Check if mapping already exists in next few lines
                if not any('jour_to_date = {' in lines[j] for j in range(i+1, min(i+10, len(lines)))):
                    # Add the mapping
                    mapping_lines = [
                        '        jour_to_date = {',
                        '            "lundi": date(2025, 2, 3),',
                        '            "mardi": date(2025, 2, 4),',
                        '            "mercredi": date(2025, 2, 5),',
                        '            "jeudi": date(2025, 2, 6),',
                        '            "vendredi": date(2025, 2, 7),',
                        '            "samedi": date(2025, 2, 8),',
                        '            "dimanche": date(2025, 2, 9),',
                        '        }',
                    ]
                    for ml in mapping_lines:
                        new_lines.append(ml)
        
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    # Count new usage
    new_uses = len(re.findall(r'jour_to_date\[jour\]', new_content))
    new_mappings = len(re.findall(r'jour_to_date = \{', new_content))
    
    print(f"\n   → New jour_to_date[jour] usages: {new_uses}")
    print(f"   → New jour_to_date = {{ mappings: {new_mappings}")
    
    # Save
    print(f"\n💾 Saving file...")
    try:
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ File saved: {TEST_FILE}")
        
        print("\n🔍 Checking Python syntax...")
        try:
            compile(new_content, str(TEST_FILE), 'exec')
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
