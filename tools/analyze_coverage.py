"""Script pour identifier les fichiers avec la plus faible couverture."""
import json
from pathlib import Path

# Lire le fichier JSON de status de couverture
status_file = Path("htmlcov/status.json")
if not status_file.exists():
    print("❌ Fichier status.json non trouvé. Exécutez d'abord: python manage.py coverage")
    exit(1)

with open(status_file, "r") as f:
    data = json.load(f)

# Extraire les fichiers avec leur couverture
files_coverage = []
for file_info in data.get("files", {}).values():
    file_path = file_info.get("index", {}).get("relative_filename", "")
    
    # Filtrer seulement les fichiers src/ (pas les tests)
    if file_path.startswith("src") and "test" not in file_path:
        pct_covered = file_info.get("index", {}).get("nums", {}).get("pc_covered", 0)
        num_statements = file_info.get("index", {}).get("nums", {}).get("n_statements", 0)
        num_missing = file_info.get("index", {}).get("nums", {}).get("n_missing", 0)
        
        files_coverage.append({
            "path": file_path,
            "coverage": pct_covered,
            "statements": num_statements,
            "missing": num_missing
        })

# Trier par couverture croissante
files_coverage.sort(key=lambda x: x["coverage"])

print("\n" + "="*80)
print("📊 TOP 30 FICHIERS AVEC LA PLUS FAIBLE COUVERTURE")
print("="*80 + "\n")

print(f"{'Fichier':<60} {'Couv.':<8} {'Manque':<8}")
print("-" * 80)

for i, file_info in enumerate(files_coverage[:30], 1):
    path = file_info["path"]
    cov = file_info["coverage"]
    missing = file_info["missing"]
    
    # Coloration selon le niveau
    if cov == 0:
        color = "🔴"
    elif cov < 30:
        color = "🟠"
    elif cov < 60:
        color = "🟡"
    else:
        color = "🟢"
    
    print(f"{color} {path:<57} {cov:>6.1f}%  {missing:>5} lignes")

print("\n" + "="*80)
print(f"Total fichiers analysés: {len(files_coverage)}")
print("="*80 + "\n")

# Recommandations
print("🎯 RECOMMANDATIONS pour atteindre 40% de couverture:\n")
print("1. Prioriser les fichiers 🔴 (0% couverture) avec beaucoup de lignes manquantes")
print("2. Cibler les fichiers 🟠 (<30%) des modules critiques")
print("3. Focus sur: UI components, services non testés, helpers\n")

# Calculer l'impact potentiel
zero_coverage = [f for f in files_coverage if f["coverage"] == 0]
low_coverage = [f for f in files_coverage if 0 < f["coverage"] < 30]

print(f"📈 Fichiers à 0%: {len(zero_coverage)} ({sum(f['missing'] for f in zero_coverage)} lignes)")
print(f"📈 Fichiers <30%: {len(low_coverage)} ({sum(f['missing'] for f in low_coverage)} lignes)")
