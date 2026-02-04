#!/usr/bin/env python3
"""
Fix remaining Planning calls with variables instead of date literals
"""

import re
from pathlib import Path

TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def fix_planning_with_variables(content):
    """Fix Planning calls that use variables or expressions for semaine."""
    count = 0
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Pattern: Planning(semaine=VARIABLE) or Planning(semaine=EXPRESSION)
        # where VARIABLE is not "date(...)"
        
        if 'Planning(semaine=' in line and 'Planning(nom=' not in line:
            # Extract the content between Planning( and )
            match = re.search(r'Planning\s*\(\s*semaine\s*=\s*([^,)]+)(?:,\s*(notes\s*=\s*[^)]+))?\s*\)', line)
            if match:
                semaine_expr = match.group(1).strip()
                notes_part = match.group(2)
                
                # Skip if it's already corrected (has nom=)
                if 'nom=' in line:
                    new_lines.append(line)
                    continue
                
                # Generate the new Planning call
                # For variables like target_date, week_date, test_date, we need to handle them
                # We'll assume they are valid dates and build accordingly
                
                # For expressions like date(2025, 2, 3) + timedelta(weeks=i)
                if 'timedelta' in semaine_expr:
                    # This is complex, just use a generic name
                    nom = '"Planning"'
                else:
                    nom = f'f"Planning {{{semaine_expr.replace("date(", "").replace(")", "")}[:10]}}"'
                
                new_line = f'planning = Planning(nom={nom}, semaine_debut={semaine_expr}, semaine_fin={semaine_expr} + timedelta(days=6), actif=True'
                
                if notes_part:
                    new_line += f', {notes_part}'
                
                new_line += ')'
                new_lines.append(new_line)
                count += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), count

def main():
    print(f"📂 Reading file: {TEST_FILE}")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ File read: {len(content)} characters")
    
    # Count remaining issues
    bad_count = len(re.findall(r'Planning\(semaine=(?!Planning)', content))
    print(f"   → Found {bad_count} remaining Planning(semaine=...) calls")
    
    print(f"\n🔧 Fixing remaining Planning calls...")
    content, count = fix_planning_with_variables(content)
    print(f"   → Fixed {count} calls")
    
    # Save
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
