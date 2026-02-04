import json

file_path = r'd:\Projet_streamlit\assistant_matanne\coverage.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# Vérifier la structure
if 'totals' in data:
    totals = data['totals']
    print(f"percent_covered: {totals.get('percent_covered')}")
    print(f"covered_lines: {totals.get('covered_lines')}")
    print(f"num_statements: {totals.get('num_statements')}")
else:
    print("Keys in JSON:", list(data.keys()))
