"""Analyse des opportunités de tests restantes."""
import re
from pathlib import Path

html = Path('htmlcov/index.html').read_text(encoding='utf-8')
pattern = r'<td class="name"><a href="[^"]+">([^<]+)</a></td>.*?<td>(\d+)</td>\s*<td>(\d+)</td>'

print("=" * 70)
print("ANALYSE DES OPPORTUNITÉS DE TESTS RESTANTES")
print("=" * 70)

# 1. Fichiers à 0% avec logique pure potentielle
print("\n1. FICHIERS À 0% (pas encore importés dans les tests):")
print("-" * 70)
zero_cover = []
for match in re.finditer(pattern, html, re.DOTALL):
    name, stmts, miss = match.groups()
    name = name.replace('&#8201;', '').replace('\\', '/')
    stmts, miss = int(stmts), int(miss)
    if miss == stmts and stmts > 50:  # 0% couverture
        zero_cover.append((stmts, name))

zero_cover.sort(reverse=True)
for stmts, name in zero_cover[:10]:
    testable = "⭐" if any(x in name for x in ['utils/', 'helpers', 'validators', 'formatters']) else ""
    print(f"  {stmts:4} stmts: {name} {testable}")

# 2. Fichiers avec couverture partielle (déjà importés)
print("\n2. FICHIERS PARTIELLEMENT COUVERTS (faciles à améliorer):")
print("-" * 70)
partial = []
for match in re.finditer(pattern, html, re.DOTALL):
    name, stmts, miss = match.groups()
    name = name.replace('&#8201;', '').replace('\\', '/')
    stmts, miss = int(stmts), int(miss)
    cover = round((stmts - miss) / stmts * 100) if stmts > 0 else 0
    if 10 <= cover <= 85 and miss > 15:
        partial.append((miss, cover, name))

partial.sort(reverse=True)
for miss, cover, name in partial[:10]:
    print(f"  {cover:2}% cover, {miss:3} miss: {name}")

# 3. Fichiers core/ pas encore testés
print("\n3. FICHIERS CORE/ NON TESTÉS (haute valeur):")
print("-" * 70)
core_untested = [n for s, n in zero_cover if '/core/' in n and 'models' not in n]
for name in core_untested[:8]:
    print(f"  {name}")

print("\n" + "=" * 70)
print("RECOMMANDATIONS PRIORITAIRES:")
print("=" * 70)
print("""
✅ DÉJÀ FAIT:
- test_formatters.py (utils/formatters/)
- test_helpers.py (utils/helpers/)
- test_utils_validators.py (utils/validators/)
- test_notifications_pure.py (core/notifications.py dataclass)
- test_inventaire_schemas.py (services/inventaire.py Pydantic)
- test_errors_base.py (core/errors_base.py)

🎯 PROCHAINS TESTS FACILES (logique pure):
1. src/core/constants.py - Constantes, pas de logique
2. src/utils/helpers/food.py - Fonctions pures (21 stmts)
3. src/utils/helpers/dates.py - Fonctions de dates (29 stmts)
4. src/core/validators_pydantic.py - Validators Pydantic (159 stmts, 59% cover)
5. src/services/types.py - Types/BaseService (204 stmts, 9% cover)

⚠️ TESTS MOYENS (nécessitent mocks):
- src/core/cache.py - Cache avec st.session_state mock
- src/core/ai/*.py - Clients IA avec mocks

❌ TESTS DIFFICILES (Streamlit UI, DB):
- src/modules/* - Tous les modules UI
- src/services/* avec DB - Nécessitent fixtures DB
""")
