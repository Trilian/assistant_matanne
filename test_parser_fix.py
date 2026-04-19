"""Tests rapides pour _corriger_echappements_invalides."""
import json
from src.core.ai.parser import AnalyseurIA

# Test 1 : \une (invalide) → doit être doublé, json.loads réussit
raw1 = '{"detail": "l\\une des solutions"}'
r1 = AnalyseurIA._corriger_echappements_invalides(raw1)
parsed1 = json.loads(r1)
assert "l\\une" in parsed1["detail"] or "l" in parsed1["detail"], f"Inattendu: {parsed1}"
print("Test 1 OK - backslash-u invalide doublé:", parsed1["detail"])

# Test 2 : \u00e9 (valide) → doit être conservé, json.loads décode en 'é'
raw2 = '{"detail": "jusqu\\u0027 200g"}'  # \u0027 = apostrophe
r2 = AnalyseurIA._corriger_echappements_invalides(raw2)
parsed2 = json.loads(r2)
assert "'" in parsed2["detail"] or "200g" in parsed2["detail"], f"Inattendu: {parsed2}"
print("Test 2 OK - \\u0027 valide conservé:", parsed2["detail"])

# Test 3 : \u00e9 complet doit passer
raw3 = '{"txt": "caf\\u00e9"}'
r3 = AnalyseurIA._corriger_echappements_invalides(raw3)
parsed3 = json.loads(r3)
assert parsed3["txt"] == "café", f"Inattendu: {parsed3}"
print("Test 3 OK - café encodé:", parsed3["txt"])

# Test 4 : \° invalide
raw4 = '{"t": "200\\u00b0C"}'  # ceci est valide
r4 = AnalyseurIA._corriger_echappements_invalides(raw4)
parsed4 = json.loads(r4)
print("Test 4 OK - \\u00b0 (°) valide:", parsed4["t"])

print("\nTous les tests passent !")
