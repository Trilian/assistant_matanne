#!/usr/bin/env python
import json

with open('coverage.json') as f:
    data = json.load(f)

print(f'Total Coverage: {data["totals"]["percent_covered"]:.2f}%')
print(f'Total Lines: {data["totals"]["num_statements"]}')
print(f'Lines Covered: {data["totals"]["covered_lines"]}')

# Show sample paths to understand structure
print('\nSample paths in coverage.json:')
for i, path in enumerate(list(data['files'].keys())[:10]):
    print(f'  {path}')

# Module breakdown - better handling
modules = {}
for path, filedata in data['files'].items():
    # Normalize to forward slashes
    path_normalized = path.replace('\\', '/')
    if 'src/' in path_normalized:
        # Get the part after 'src/'
        if path_normalized.startswith('src/'):
            remaining = path_normalized[4:]  # Skip 'src/'
            mod = remaining.split('/')[0]
            if mod not in modules:
                modules[mod] = {'lines': 0, 'covered': 0, 'files': 0}
            modules[mod]['lines'] += filedata['summary'].get('num_statements', 0)
            modules[mod]['covered'] += filedata['summary'].get('covered_lines', 0)
            modules[mod]['files'] += 1

print('\nModule Breakdown:')
if not modules:
    print('  No modules found with /src/ in path')
else:
    for mod in sorted(modules):
        pct = (modules[mod]['covered'] / modules[mod]['lines'] * 100) if modules[mod]['lines'] > 0 else 0
        print(f'  {mod:15s}: {pct:6.2f}% ({modules[mod]["covered"]}/{modules[mod]["lines"]} lines) - {modules[mod]["files"]} files')
