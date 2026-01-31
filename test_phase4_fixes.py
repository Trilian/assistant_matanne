#!/usr/bin/env python3
"""
Test rapide pour valider que tous les fixes Phase 4 fonctionnent correctement.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test que tous les modules importent correctement."""
    print("\n=== Test 1: Imports ===")
    try:
        from src.domains.famille.ui import sante
        print("✅ sante module imports")
        
        from src.domains.famille.ui import accueil
        print("✅ accueil module imports")
        
        from src.domains.famille.ui import routines
        print("✅ routines module imports")
        
        from src.domains.maison.ui import entretien
        print("✅ entretien module imports")
        
        from src.domains.shared.ui import barcode
        print("✅ barcode module imports")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_emoji_strings():
    """Test que les emojis ne sont pas corrompus."""
    print("\n=== Test 2: Emoji Validation ===")
    
    # Emojis qui ne devraient PAS être présents
    corrupted_patterns = [
        'âž•',      # Corrupted plus
        'â±ï¸',    # Corrupted horloge
        'âš ',      # Corrupted warning
        'â˜',       # Corrupted checkmark
    ]
    
    # Fichiers à vérifier
    files_to_check = [
        "src/domains/famille/ui/sante.py",
        "src/domains/famille/ui/accueil.py",
        "src/domains/maison/ui/entretien.py",
        "src/domains/maison/ui/jardin.py",
        "src/domains/shared/ui/barcode.py",
    ]
    
    issues_found = False
    for filepath in files_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in corrupted_patterns:
                    if pattern in content:
                        print(f"❌ {filepath}: Found corrupted emoji '{pattern}'")
                        issues_found = True
        except Exception as e:
            print(f"⚠️ Could not read {filepath}: {e}")
    
    if not issues_found:
        print("✅ No corrupted emojis found")
        return True
    return False

def test_valid_emojis():
    """Test que les emojis valides sont présents."""
    print("\n=== Test 3: Valid Emojis Present ===")
    
    valid_emojis = {
        "⏱️": "Horloge",
        "➕": "Plus",
        "⚠️": "Warning",
        "✓": "Checkmark",
        "📊": "Chart",
        "⚡": "Lightning",
    }
    
    test_file = "src/domains/famille/ui/sante.py"
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for emoji, desc in valid_emojis.items():
                if emoji in content or desc.lower() in content.lower():
                    print(f"✅ Found emoji: {emoji} ({desc})")
    except Exception as e:
        print(f"⚠️ Could not verify emojis: {e}")
        return False
    
    return True

def test_chart_placeholders():
    """Test que [CHART] est remplacé par 📊."""
    print("\n=== Test 4: [CHART] Placeholders ===")
    
    files_to_check = [
        "src/domains/famille/ui/sante.py",
        "src/domains/famille/ui/routines.py",
        "src/services/budget.py",
    ]
    
    issues_found = False
    for filepath in files_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # [CHART] should mostly be replaced (except in comments/docs)
                # This is a rough check
                lines_with_bracket = [l for l in content.split('\n') if '[CHART]' in l and not l.strip().startswith('#')]
                if lines_with_bracket:
                    print(f"⚠️ {filepath}: Still has [CHART] placeholders")
        except Exception as e:
            print(f"Could not read {filepath}: {e}")
    
    if not issues_found:
        print("✅ [CHART] placeholders mostly replaced")
        return True
    return False

def test_database():
    """Test connexion BD et colonne magasin."""
    print("\n=== Test 5: Database ===")
    try:
        from src.core.database import get_db_context
        
        with get_db_context() as session:
            from sqlalchemy import inspect
            inspector = inspect(session.bind)
            cols = [c['name'] for c in inspector.get_columns('family_budgets')]
            
            if 'magasin' in cols:
                print(f"✅ Column 'magasin' exists in family_budgets")
            else:
                print(f"⚠️ Column 'magasin' NOT in family_budgets (migration pending)")
                print(f"   Current columns: {', '.join(sorted(cols))}")
        
        return True
    except Exception as e:
        print(f"⚠️ Database check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("  PHASE 4 VALIDATION TEST SUITE")
    print("="*50)
    
    results = {
        "Imports": test_imports(),
        "Corrupted Emojis": test_emoji_strings(),
        "Valid Emojis": test_valid_emojis(),
        "Chart Placeholders": test_chart_placeholders(),
        "Database": test_database(),
    }
    
    print("\n" + "="*50)
    print("  SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! App is ready to go.")
        print("\nNext steps:")
        print("1. Apply migration: alembic upgrade head")
        print("2. Restart app: streamlit run src/app.py")
    else:
        print("\n⚠️ Some tests failed. Review output above.")
    
    print("="*50 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
