"""
Plan d'action détaillé pour améliorer la couverture de tests
Génère les recommandations par fichier
"""

import json
from pathlib import Path


def generate_action_plan():
    """Génère le plan d'action détaillé"""
    
    # Load coverage analysis
    with open('coverage_analysis.json', 'r') as f:
        data = json.load(f)
    
    print("\n" + "="*80)
    print("PLAN D'ACTION DÉTAILLÉ - AMÉLIORATION COUVERTURE")
    print("="*80)
    
    print("\n📋 PHASE 1: FICHIERS CRITIQUES (0% - 30%) - 8 SEMAINES")
    print("-" * 80)
    
    critical_files = [
        ("src/utils/image_generator.py", 312, 0.0, "Créer test complet"),
        ("src/domains/maison/ui/depenses.py", 271, 0.0, "Créer test complet"),
        ("src/domains/planning/ui/components/__init__.py", 110, 0.0, "Créer test complet"),
        ("src/utils/helpers/helpers.py", 102, 0.0, "Créer test complet"),
        ("src/domains/famille/ui/jules_planning.py", 163, 0.0, "Améliorer significativement"),
        ("src/domains/cuisine/ui/planificateur_repas.py", 375, 0.0, "Créer test complet"),
        ("src/domains/jeux/setup.py", 76, 0.0, "Créer test complet"),
        ("src/domains/jeux/integration.py", 15, 0.0, "Créer test complet"),
        ("src/domains/cuisine/ui/recettes.py", 825, 2.48, "Réécrire test complet"),
        ("src/domains/cuisine/ui/inventaire.py", 825, 3.86, "Améliorer significativement"),
    ]
    
    print("\n🔴 GROUPE 1: 0% couverture (8 fichiers) - 15 jours")
    for filepath, statements, coverage, action in critical_files[:8]:
        priority = "🚨 URGENT" if statements > 200 else "⚠️ IMPORTANT"
        print(f"\n{priority} {filepath}")
        print(f"   Statements: {statements}")
        print(f"   Couverture: {coverage:.1f}%")
        print(f"   Action: {action}")
        print(f"   Test file: {filepath.replace('src/', 'tests/').replace('.py', '')}")
    
    print("\n\n🟠 GROUPE 2: <5% couverture (12 fichiers) - 20 jours")
    for filepath, statements, coverage, action in critical_files[8:10]:
        priority = "🚨 URGENT" if statements > 500 else "⚠️ IMPORTANT"
        print(f"\n{priority} {filepath}")
        print(f"   Statements: {statements}")
        print(f"   Couverture: {coverage:.1f}%")
        print(f"   Action: {action}")
    
    print("\n\n📋 PHASE 2: MODULES FAIBLES (30-80%) - 4 SEMAINES")
    print("-" * 80)
    
    modules = [
        ("services/", 30.1, "Augmenter à 60%", "+30%"),
        ("ui/", 37.5, "Augmenter à 70%", "+32.5%"),
        ("domains/", 38.7, "Augmenter à 70%", "+31.3%"),
    ]
    
    for module, current, target, impact in modules:
        print(f"\n📦 {module}")
        print(f"   Couverture actuelle: {current:.1f}%")
        print(f"   Cible: {target}")
        print(f"   Impact potentiel: {impact}")
    
    print("\n\n📋 PHASE 3: TESTS E2E - 2 SEMAINES")
    print("-" * 80)
    
    e2e_tests = [
        ("test_cuisine_flow.py", "Flux complet: recette → planning → courses"),
        ("test_famille_flow.py", "Flux: ajout membre → suivi activités"),
        ("test_planning_flow.py", "Flux: créer événement → synchroniser"),
        ("test_auth_flow.py", "Flux: login → authentification → multi-tenant"),
        ("test_maison_flow.py", "Flux: ajouter projet → gérer budget"),
    ]
    
    print("\nFichiers E2E à créer (tests/e2e/):")
    for test_file, description in e2e_tests:
        print(f"  ✓ {test_file}: {description}")
    
    print("\n\n✅ STRATÉGIE DE TEST RECOMMANDÉE")
    print("-" * 80)
    
    print("""
1. TESTS UNITAIRES (70% de l'effort)
   - Un test par fonction/méthode
   - Mocks pour dépendances externes
   - Fixtures réutilisables

2. TESTS D'INTÉGRATION (20% de l'effort)
   - Tests avec BD réelle (sqlite in-memory)
   - Tests services combinés
   - Tests avec API simulées

3. TESTS E2E (10% de l'effort)
   - Flux utilisateur complets
   - Tests de navigation
   - Tests de synchronisation

4. COUVERTURE DE BRANCHEMENT
   - Toutes les conditions if/else
   - Gestion d'erreurs
   - Cas limites (empty, null, etc)
    """)
    
    print("\n\n📊 TIMELINE RÉALISTE")
    print("-" * 80)
    print("""
Semaine 1-2: Fichiers 0% (8 fichiers)
            Fichiers <100 statements
            Impact: +3-5% couverture

Semaine 3-4: Fichiers <5% (12 fichiers)
            Focus UI composants
            Impact: +5-8% couverture

Semaine 5-6: Services (30.1%)
            base_ai_service, auth, etc
            Impact: +10-15% couverture

Semaine 7-8: Tests E2E
            Flux complets
            Impact: +2-3% couverture

CIBLE FINALE: >80% (8 semaines)
    """)
    
    print("\n\n💾 FICHIERS DE CONFIGURATION À METTRE À JOUR")
    print("-" * 80)
    print("""
1. pytest.ini
   - Ajouter @e2e pour marker tests
   - Ajouter @integration
   
2. pyproject.toml
   - [tool.pytest.ini_options]
   - testpaths = ["tests"]
   - Markers configuration

3. .github/workflows/*.yml
   - Ajouter step coverage check
   - Fail si coverage < 80%

4. conftest.py
   - Améliorer fixtures
   - Ajouter fixtures pour Streamlit
   - Ajouter fixtures pour BD
    """)
    
    print("\n\n📌 RESSOURCES ET BONNES PRATIQUES")
    print("-" * 80)
    print("""
PATTERNS À UTILISER:

1. Mock Streamlit:
   @patch('streamlit.write')
   def test_component(mock_write):
       pass

2. Fixtures DB:
   @pytest.fixture
   def test_db():
       # SQLite in-memory
       
3. Parametrize tests:
   @pytest.mark.parametrize("input,expected", [
       ("a", 1), ("b", 2)
   ])
   
4. Check exceptions:
   with pytest.raises(ValueError):
       dangerous_function()
    """)
    
    print("\n" + "="*80)
    print("RÉSUMÉ: Effort total estimé ~200-250 heures")
    print("Gain: +50% points de couverture (29% → 80%)")
    print("="*80 + "\n")


if __name__ == '__main__':
    generate_action_plan()
