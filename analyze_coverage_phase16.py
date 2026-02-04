#!/usr/bin/env python3
"""
Analyse complète de la couverture de test Phase16
"""

import json
import os

# Load coverage data
with open('coverage.json') as f:
    data = json.load(f)

# Global coverage
total_pct = data['totals']['percent_covered']
print(f'=' * 80)
print(f'GLOBAL PROJECT COVERAGE: {total_pct:.2f}%')
print(f'=' * 80)
print()

# Parse modules
modules = {}
for filepath, filedata in data['files'].items():
    # Filter for src files (using backslashes on Windows)
    if not filepath.startswith('src\\'):
        continue
    
    # Extract module path from Windows path
    parts = filepath.split('\\')
    # parts[0] = 'src', parts[1] = module, parts[2:] = submodule/file
    
    if len(parts) == 2:
        # Just src\file.py
        module = 'root'
        filename = parts[1]
    else:
        module = parts[1]
        filename = '\\'.join(parts[2:])
    
    if module not in modules:
        modules[module] = {
            'files': {},
            'total_lines': 0,
            'covered_lines': 0
        }
    
    coverage_pct = filedata['summary'].get('percent_covered', 0)
    num_statements = filedata['summary'].get('num_statements', 0)
    covered_lines = filedata['summary'].get('covered_lines', 0)
    
    modules[module]['files'][filename] = {
        'coverage': coverage_pct,
        'lines': num_statements,
        'covered': covered_lines
    }
    
    modules[module]['total_lines'] += num_statements
    modules[module]['covered_lines'] += covered_lines

# Print module summary sorted by coverage
print('MODULE SUMMARY (sorted by coverage %):')
print('-' * 80)
module_list = []
for module, mod_data in modules.items():
    if mod_data['total_lines'] == 0:
        continue
    pct = (mod_data['covered_lines'] / mod_data['total_lines']) * 100
    module_list.append((module, pct, mod_data))

module_list.sort(key=lambda x: x[1], reverse=True)

for module, pct, mod_data in module_list:
    print(f'{module:20s}: {pct:7.2f}% ({mod_data["covered_lines"]:5d}/{mod_data["total_lines"]:5d} lines)')

print()
print('=' * 80)
print('TOP 10 MODULES BY COVERAGE:')
print('=' * 80)
for i, (module, pct, mod_data) in enumerate(module_list[:10], 1):
    print(f'{i:2d}. {module:20s}: {pct:7.2f}%')

print()
print('=' * 80)
print('FILES WITH COVERAGE < 60% (sorted by coverage):')
print('=' * 80)

all_files = []
for module, mod_data in modules.items():
    for filename, file_stats in mod_data['files'].items():
        all_files.append({
            'module': module,
            'file': filename,
            'coverage': file_stats['coverage'],
            'lines': file_stats['lines'],
            'covered': file_stats['covered']
        })

# Sort by coverage
all_files.sort(key=lambda x: x['coverage'])

# Print files < 60%
under_60 = [f for f in all_files if f['coverage'] < 60]
print(f'\nTotal files < 60%: {len(under_60)} / {len(all_files)}\n')

for f in under_60[:20]:  # Print first 20
    full_path = f"{f['module']}/{f['file']}"
    print(f"{f['coverage']:6.2f}%  |  {f['covered']:4d}/{f['lines']:4d} lines  |  {full_path}")

if len(under_60) > 20:
    print(f"\n... and {len(under_60) - 20} more files < 60%")

print()
print('=' * 80)
print('SUMMARY:')
print('=' * 80)
print(f'Total tests coverage: {total_pct:.2f}%')
print(f'Total modules: {len(module_list)}')
print(f'Total files: {len(all_files)}')
print(f'Files < 60% coverage: {len(under_60)}')
print(f'Files >= 60% coverage: {len(all_files) - len(under_60)}')
