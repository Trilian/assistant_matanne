import json
with open('coverage.json') as f:
    d = json.load(f)
pct = d['totals']['percent_covered']
print(f'Coverage: {pct:.2f}%')
