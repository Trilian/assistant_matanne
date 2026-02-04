#!/usr/bin/env python3
"""
Comprehensive fix for all test_phase16_extended.py issues
Starting fresh with a robust approach
"""

import re
from pathlib import Path
from datetime import date, timedelta

TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def comprehensive_fix(content):
    """Apply all fixes with proper indentation handling."""
    
    lines = content.split('\n')
    new_lines = []
    replacements_count = {
        'planning_fixed': 0,
        'repas_jour_literal': 0,
        'repas_jour_variable': 0,
        'mappings_added': 0
    }
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Pattern 1: Fix Planning(semaine=...) calls
        if 'Planning(semaine=' in line and 'Planning(nom=' not in line:
            # Extract indentation
            indent_match = re.match(r'^(\s*)', line)
            indent = indent_match.group(1) if indent_match else ''
            
            # Try to match the Planning call
            match = re.search(r'Planning\s*\(\s*semaine\s*=\s*([^,)]+)(?:,\s*(notes\s*=\s*[^)]+))?\s*\)', line)
            if match:
                semaine_expr = match.group(1).strip()
                notes_part = match.group(2)
                
                # Determine the nom value
                # If it's a simple date, extract the date components
                date_match = re.match(r'date\((\d+),\s*(\d+),\s*(\d+)\)', semaine_expr)
                if date_match:
                    year, month, day = date_match.groups()
                    week_num = (int(day) - 1) // 7 + 1
                    nom = f'"Planning Week {week_num}"'
                    semaine_debut = semaine_expr
                    semaine_fin = f'date({year}, {month}, {day}) + timedelta(days=6)'
                else:
                    # For variables or expressions
                    nom = '"Planning"'
                    semaine_debut = semaine_expr
                    semaine_fin = f'{semaine_expr} + timedelta(days=6)'
                
                # Build the new line
                new_line = f'{indent}planning = Planning(nom={nom}, semaine_debut={semaine_debut}, semaine_fin={semaine_fin}, actif=True'
                if notes_part:
                    new_line += f', {notes_part}'
                new_line += ')'
                
                new_lines.append(new_line)
                replacements_count['planning_fixed'] += 1
                i += 1
                continue
        
        # Pattern 2: Fix jour="..." to date_repas=date(...)
        if 'jour=' in line and 'jour_to_date' not in line and 'filter_by' not in line:
            jour_to_date_map = {
                "lundi": "date(2025, 2, 3)",
                "mardi": "date(2025, 2, 4)",
                "mercredi": "date(2025, 2, 5)",
                "jeudi": "date(2025, 2, 6)",
                "vendredi": "date(2025, 2, 7)",
                "samedi": "date(2025, 2, 8)",
                "dimanche": "date(2025, 2, 9)",
            }
            
            # Handle jour="..."
            literal_match = re.search(r'jour\s*=\s*["\']([^"\']+)["\']', line)
            if literal_match:
                jour = literal_match.group(1)
                date_val = jour_to_date_map.get(jour, "date(2025, 2, 3)")
                line = re.sub(
                    r'jour\s*=\s*["\']([^"\']+)["\']',
                    f'date_repas={date_val}',
                    line
                )
                replacements_count['repas_jour_literal'] += 1
        
        # Pattern 3: Fix filter_by(jour=...)
        if 'filter_by(jour=' in line:
            line = re.sub(r'filter_by\s*\(\s*jour\s*=', 'filter_by(date_repas=', line)
        
        new_lines.append(line)
        i += 1
    
    return '\n'.join(new_lines), replacements_count

def main():
    print(f"📂 Reading file: {TEST_FILE}")
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ File read: {len(content)} characters")
    
    print(f"\n🔧 Applying comprehensive fixes...")
    content, counts = comprehensive_fix(content)
    
    print(f"   → Planning calls fixed: {counts['planning_fixed']}")
    print(f"   → Repas with jour=\"...\" fixed: {counts['repas_jour_literal']}")
    print(f"   → Repas with jour=variable fixed: {counts['repas_jour_variable']}")
    
    total = sum(counts.values())
    print(f"\n✅ Total fixes applied: {total}")
    
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
            # Print context
            lines = content.split('\n')
            if e.lineno and e.lineno > 0:
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                for j in range(start, end):
                    prefix = ">>>" if j == e.lineno - 1 else "   "
                    print(f"{prefix} {j+1}: {lines[j][:80]}")
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
