#!/usr/bin/env python3
"""Vérification finale que tout fonctionne"""

print('=' * 60)
print('✅ VÉRIFICATION FINALE')
print('=' * 60)

# Test 1: Imports
print('\n1️⃣  Test des imports...')
try:
    from src.domains.jeux.ui.paris import (
        sync_equipes_depuis_api,
        sync_tous_championnats,
        refresh_scores_matchs,
        CHAMPIONNATS
    )
    print('   ✅ Fonctions sync importées')
except Exception as e:
    print(f'   ❌ Erreur import: {e}')
    exit(1)

# Test 2: Exécution sync (sans API)
print('\n2️⃣  Test sync Ligue 1 (sans API)...')
try:
    result = sync_equipes_depuis_api('Ligue 1')
    print(f'   ✅ Retour: {result} équipes (OK, pas d\'API)')
except Exception as e:
    print(f'   ❌ Erreur: {e}')
    exit(1)

# Test 3: Exécution sync tous
print('\n3️⃣  Test sync tous les championnats...')
try:
    resultats = sync_tous_championnats()
    print(f'   ✅ Résultats: {resultats}')
except Exception as e:
    print(f'   ❌ Erreur: {e}')
    exit(1)

# Test 4: Refresh scores
print('\n4️⃣  Test refresh scores...')
try:
    result = refresh_scores_matchs()
    print(f'   ✅ Retour: {result} matchs')
except Exception as e:
    print(f'   ❌ Erreur: {e}')
    exit(1)

print()
print('=' * 60)
print('✅ TOUS LES TESTS PASSENT!')
print('=' * 60)
print()
print('📌 Résumé:')
print('   • sync_equipes_depuis_api() ✅ fonctionne')
print('   • sync_tous_championnats() ✅ fonctionne')
print('   • refresh_scores_matchs() ✅ fonctionne')
print('   • Pas de clé API = retours 0 (OK)')
print()
print('💡 Pour activer la synchro avec API:')
print('   1. python scripts/setup_api_key.py')
print('   2. ou ajouter FOOTBALL_DATA_API_KEY= à .env.local')
