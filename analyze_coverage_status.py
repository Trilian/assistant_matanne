# Script pour analyser la couverture depuis status.json
import json

with open('htmlcov/status.json') as f:
    data = json.load(f)

print('=' * 70)
print('COUVERTURE DES MODULES PRIORITAIRES (src/core/)')
print('=' * 70)
print(f"{'Module':<35} {'Stmts':>6} {'Miss':>6} {'Cover':>8}")
print('-' * 70)

results = []

for key, info in data['files'].items():
    file = info['index']['file']
    if 'src\\core\\' in file and 'models' not in file and 'ai\\' not in file:
        nums = info['index']['nums']
        stmts = nums['n_statements']
        miss = nums['n_missing']
        if stmts > 0:
            cover = (stmts - miss) / stmts * 100
        else:
            cover = 100
        name = file.split('\\')[-1]
        results.append((name, stmts, miss, cover))

# Sort by coverage descending
results.sort(key=lambda x: -x[3])

total_stmts = 0
total_miss = 0
for name, stmts, miss, cover in results:
    status = '✅' if cover >= 80 else '❌'
    print(f'{status} {name:<32} {stmts:>6} {miss:>6} {cover:>7.1f}%')
    total_stmts += stmts
    total_miss += miss

print('-' * 70)
total_cov = (total_stmts - total_miss) / total_stmts * 100 if total_stmts > 0 else 0
print(f"{'TOTAL core (hors models/ai)':<35} {total_stmts:>6} {total_miss:>6} {total_cov:>7.1f}%")
print('=' * 70)

# Afficher le résumé des modules prioritaires
priority_modules = ['decorators', 'validation', 'errors.py', 'errors_base', 
                   'cache.py', 'lazy_loader', 'state', 'logging', 'constants']

print('\n📊 MODULES PRIORITAIRES >= 80%:')
achieved = 0
for name, stmts, miss, cover in results:
    for p in priority_modules:
        if p in name.lower():
            status = '✅' if cover >= 80 else '❌'
            if cover >= 80:
                achieved += 1
            print(f'  {status} {name}: {cover:.1f}%')
            break

print(f'\nObjectif: {achieved}/{len(priority_modules)} modules prioritaires >= 80%')
