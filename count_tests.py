import re
from pathlib import Path

tests_dir = Path('tests')
total = 0
results = {}

for layer in ['core', 'api', 'ui', 'utils', 'services', 'modules', 'e2e']:
    layer_dir = tests_dir / layer
    if layer_dir.exists():
        count = 0
        for f in layer_dir.glob('test_*.py'):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                count += len(re.findall(r'def test_\w+', content))
            except:
                pass
        results[layer] = count
        total += count

print('=' * 60)
print('RESUME TESTS CREES')
print('=' * 60)
for layer, count in sorted(results.items()):
    print(f'{layer.upper():<15} {count:>5} tests')
print('=' * 60)
print(f'TOTAL           {total:>5} tests')
print('=' * 60)
