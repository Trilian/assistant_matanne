#!/usr/bin/env python3
"""Extraire et afficher couverture détaillée"""
import json

with open('htmlcov/status.json') as f:
    data = json.load(f)

modules = {}
total_stmts = 0
total_executed = 0

for file_key, file_data in data.get('files', {}).items():
    try:
        file_path = file_data.get('index', {}).get('file', '')
        if 'src' not in file_path:
            continue
        
        parts = file_path.replace('\\', '/').split('/')
        if len(parts) >= 2 and parts[0] == 'src':
            module = parts[1]
        else:
            continue
        
        if module not in modules:
            modules[module] = {'stmts': 0, 'executed': 0, 'files': []}
        
        nums = file_data.get('index', {}).get('nums', {})
        stmts = nums.get('n_statements', 0)
        executed = stmts - nums.get('n_missing', 0)
        
        modules[module]['stmts'] += stmts
        modules[module]['executed'] += executed
        total_stmts += stmts
        total_executed += executed
        
        if stmts > 0:
            pct = (executed / stmts * 100)
            modules[module]['files'].append({
                'name': parts[-1] if parts else '',
                'pct': pct,
                'stmts': stmts,
                'executed': executed
            })
    except Exception as e:
        pass

print('=' * 80)
print('📊 RAPPORT DE COUVERTURE DÉTAILLÉ - ASSISTANT MATANNE')
print('=' * 80)

# Global
total_pct = (total_executed / total_stmts * 100) if total_stmts > 0 else 0
print(f'\n🎯 COUVERTURE GLOBALE: {total_pct:.1f}%')
print(f'   Lignes couvertes: {total_executed}/{total_stmts}')
print(f'   Statut: {"✅ 80%+" if total_pct >= 80 else "⚠️ 60-80%" if total_pct >= 60 else "❌ <60%"}')

# Par module
print('\n' + '=' * 80)
print('PAR MODULE (6 domaines majeurs)')
print('=' * 80)
print(f'{"Statut":<6} {"Module":<20} {"Couverture":>12} {"Lignes":>18}')
print('-' * 80)

for name, data in sorted(modules.items(), key=lambda x: (x[1]['executed']/max(x[1]['stmts'],1)*100), reverse=True):
    pct = (data['executed'] / data['stmts'] * 100) if data['stmts'] > 0 else 0
    status = '✅' if pct >= 80 else '⚠️' if pct >= 60 else '❌'
    lines_info = f"{data['executed']}/{data['stmts']}"
    print(f'{status:<6} {name:<20} {pct:>10.1f}% {lines_info:>18}')

# Détail
print('\n' + '=' * 80)
print('TOP FICHIERS PAR MODULE (couverture faible)')
print('=' * 80)

for name, data in sorted(modules.items(), key=lambda x: (x[1]['executed']/max(x[1]['stmts'],1)*100)):
    mod_pct = (data['executed'] / data['stmts'] * 100) if data['stmts'] > 0 else 0
    if mod_pct < 80:  # Modules sous 80%
        print(f'\n{name} ({mod_pct:.1f}%):')
        for f in sorted(data['files'], key=lambda x: x['pct'])[:3]:
            print(f'  ❌ {f["name"]}: {f["pct"]:.1f}%')

# Fichiers critiques
print('\n' + '=' * 80)
print('⚠️ ANALYSE')
print('=' * 80)

below_80 = [(n, d) for n, d in modules.items() if (d['executed']/max(d['stmts'],1)*100) < 80]
if below_80:
    print(f'\nModules sous 80% ({len(below_80)}):')
    for name, data in below_80:
        pct = (data['executed'] / data['stmts'] * 100) if data['stmts'] > 0 else 0
        gap = 80 - pct
        print(f'  - {name}: {pct:.1f}% (gap: +{gap:.1f}%)')

print('\n' + '=' * 80)
