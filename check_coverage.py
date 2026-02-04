import json

data = json.load(open('coverage.json'))
print(f"Total files: {len(data['files'])}")
print(f"Totals: {data['totals']}")
print(f"\nFirst 30 files:")
for f in list(data['files'].keys())[:30]:
    print(f"  {f}")
