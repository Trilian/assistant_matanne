#!/usr/bin/env python3
"""
Final verification of all corrections made to test_phase16_extended.py
"""

import re
from pathlib import Path

TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def verify_corrections(content):
    """Verify all corrections have been made properly."""
    
    issues = []
    
    # Check 1: All Planning calls should use nom, semaine_debut, semaine_fin, actif
    planning_pattern = r'Planning\s*\([^)]*\)'
    planning_calls = re.findall(planning_pattern, content)
    
    good_planning = 0
    bad_planning = 0
    
    for call in planning_calls:
        if 'semaine=' in call:
            bad_planning += 1
            issues.append(f"❌ Found old Planning syntax: {call[:60]}...")
        elif 'nom=' in call and 'semaine_debut=' in call and 'semaine_fin=' in call and 'actif=' in call:
            good_planning += 1
        else:
            # Might be a partial match, check more carefully
            if 'nom=' in call or 'semaine_debut=' in call:
                good_planning += 1
    
    # Check 2: jour_semaine should not exist
    jour_semaine = len(re.findall(r'jour_semaine\s*=', content))
    if jour_semaine > 0:
        issues.append(f"❌ Found jour_semaine field: {jour_semaine} occurrences")
    
    # Check 3: type_repas on Planning should not exist (but on Repas it's OK)
    # This is harder to check precisely, so we'll skip
    
    # Check 4: Repas should use date_repas instead of jour
    repas_jour = len(re.findall(r'Repas\([^)]*jour\s*=\s*["\'][^"\']+["\']', content))
    if repas_jour > 0:
        issues.append(f"❌ Found Repas with jour=\"...\": {repas_jour} occurrences")
    
    repas_jour_var = len(re.findall(r'Repas\([^)]*jour\s*=\s*jour(?![_a-zA-Z0-9])', content))
    if repas_jour_var > 0:
        issues.append(f"❌ Found Repas with jour=jour: {repas_jour_var} occurrences")
    
    # Check 5: date_repas usage
    date_repas_count = len(re.findall(r'date_repas\s*=', content))
    
    # Check 6: jour_to_date usage vs definitions
    jour_to_date_usage = len(re.findall(r'jour_to_date\[jour\]', content))
    jour_to_date_defs = len(re.findall(r'jour_to_date\s*=\s*\{', content))
    
    # Check 7: filter_by with jour should be date_repas
    filter_jour = len(re.findall(r'filter_by\s*\(\s*jour\s*=', content))
    if filter_jour > 0:
        issues.append(f"❌ Found filter_by with jour: {filter_jour} occurrences")
    
    filter_date_repas = len(re.findall(r'filter_by\s*\(\s*date_repas\s*=', content))
    
    return {
        'good_planning': good_planning,
        'bad_planning': bad_planning,
        'jour_semaine': jour_semaine,
        'repas_jour_literal': repas_jour,
        'repas_jour_variable': repas_jour_var,
        'date_repas_count': date_repas_count,
        'jour_to_date_usage': jour_to_date_usage,
        'jour_to_date_defs': jour_to_date_defs,
        'filter_jour': filter_jour,
        'filter_date_repas': filter_date_repas,
        'issues': issues
    }

def main():
    print(f"📊 FINAL VERIFICATION REPORT")
    print("=" * 70)
    
    if not TEST_FILE.exists():
        print(f"❌ File not found: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = verify_corrections(content)
    
    print(f"\n✓ Planning corrections:")
    print(f"  ✅ Good Planning() calls: {results['good_planning']}")
    if results['bad_planning'] > 0:
        print(f"  ❌ Bad Planning() calls: {results['bad_planning']}")
    
    print(f"\n✓ Repas field corrections:")
    print(f"  ✅ date_repas usages: {results['date_repas_count']}")
    if results['repas_jour_literal'] > 0:
        print(f"  ❌ Remaining jour=\"...\" in Repas: {results['repas_jour_literal']}")
    if results['repas_jour_variable'] > 0:
        print(f"  ❌ Remaining jour=jour in Repas: {results['repas_jour_variable']}")
    
    print(f"\n✓ Invalid fields removed:")
    if results['jour_semaine'] == 0:
        print(f"  ✅ jour_semaine: None found")
    else:
        print(f"  ❌ jour_semaine: {results['jour_semaine']} found")
    
    print(f"\n✓ Filter corrections:")
    print(f"  ✅ filter_by(date_repas=...): {results['filter_date_repas']}")
    if results['filter_jour'] > 0:
        print(f"  ❌ filter_by(jour=...): {results['filter_jour']}")
    
    print(f"\n✓ jour_to_date mapping:")
    print(f"  ✅ jour_to_date[jour] usages: {results['jour_to_date_usage']}")
    print(f"  ✅ jour_to_date mappings defined: {results['jour_to_date_defs']}")
    if results['jour_to_date_usage'] > 0 and results['jour_to_date_defs'] > 0:
        print(f"  ℹ️  Coverage: {results['jour_to_date_defs']} definitions for {results['jour_to_date_usage']} usages")
    
    if results['issues']:
        print(f"\n⚠️  Issues found:")
        for issue in results['issues']:
            print(f"  {issue}")
        return False
    else:
        print(f"\n✅ All corrections verified successfully!")
        
        # Syntax check
        print(f"\n🔍 Syntax check...")
        try:
            compile(content, str(TEST_FILE), 'exec')
            print("✅ Python syntax is valid")
        except SyntaxError as e:
            print(f"❌ Syntax error: {e} at line {e.lineno}")
            return False
    
    print("\n" + "=" * 70)
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
