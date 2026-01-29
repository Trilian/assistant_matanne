fp = 'src/domains/cuisine/ui/inventaire.py'
with open(fp, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace broken lines
for i, line in enumerate(lines):
    if 'stock_critique' in line and 'color =' in line:
        lines[i] = '            color = "🔴" if stock_critique > 0 else "✅"\n'
        print(f'Fixed line {i+1}')
    if 'stock_bas' in line and 'color =' in line and 'if ' in line:
        lines[i] = '            color = "🟠" if stock_bas > 0 else "✅"\n'
        print(f'Fixed line {i+1}')
    if 'peremption' in line and 'color =' in line:
        lines[i] = '            color = "📔" if peremption > 0 else "✅"\n'
        print(f'Fixed line {i+1}')

with open(fp, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done')
