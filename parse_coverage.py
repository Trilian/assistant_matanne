"""Script pour parser le rapport HTML de couverture."""
import re
from pathlib import Path

html_file = Path("htmlcov/index.html")
if not html_file.exists():
    print("❌ Fichier index.html non trouvé")
    exit(1)

content = html_file.read_text(encoding="utf-8")

# Parser les lignes de tableau
pattern = r'<tr class="region">.*?<a href="[^"]+">([^<]+)</a>.*?data-ratio="(\d+) (\d+)">([^<]+)</td>'
matches = re.findall(pattern, content, re.DOTALL)

files_coverage = []
for match in matches:
    file_path = match[0].replace("&#8201;\\&#8201;", "\\").replace("&#8201;", "")
    covered = int(match[1])
    total = int(match[2])
    coverage_pct = float(match[3].replace("%", ""))
    missing = total - covered
    
    if file_path.startswith("src") and "test" not in file_path.lower():
        files_coverage.append({
            "path": file_path,
            "coverage": coverage_pct,
            "total": total,
            "missing": missing,
            "covered": covered
        })

# Trier par couverture
files_coverage.sort(key=lambda x: x["coverage"])

print("\n" + "="*90)
print("📊 TOP 30 FICHIERS AVEC LA PLUS FAIBLE COUVERTURE")
print("="*90 + "\n")

print(f"{'Fichier':<55} {'Couv.':<8} {'Total':<7} {'Manque':<8}")
print("-" * 90)

for i, file_info in enumerate(files_coverage[:30], 1):
    path = file_info["path"]
    cov = file_info["coverage"]
    total = file_info["total"]
    missing = file_info["missing"]
    
    # Coloration
    if cov == 0:
        color = "🔴"
    elif cov < 30:
        color = "🟠"
    elif cov < 60:
        color = "🟡"
    else:
        color = "🟢"
    
    # Raccourcir le chemin si trop long
    display_path = path if len(path) < 52 else "..." + path[-49:]
    print(f"{color} {display_path:<52} {cov:>6.1f}%  {total:>5}  {missing:>5}")

print("\n" + "="*90)
print(f"Total fichiers analysés: {len(files_coverage)}")
print("="*90 + "\n")

# Statistiques
zero_cov = [f for f in files_coverage if f["coverage"] == 0]
low_cov = [f for f in files_coverage if 0 < f["coverage"] < 30]
med_cov = [f for f in files_coverage if 30 <= f["coverage"] < 60]

print("🎯 STATISTIQUES:\n")
print(f"🔴 Fichiers à 0%:     {len(zero_cov):>3} ({sum(f['missing'] for f in zero_cov):>5} lignes manquantes)")
print(f"🟠 Fichiers <30%:     {len(low_cov):>3} ({sum(f['missing'] for f in low_cov):>5} lignes manquantes)")
print(f"🟡 Fichiers 30-60%:   {len(med_cov):>3} ({sum(f['missing'] for f in med_cov):>5} lignes manquantes)")

total_missing = sum(f['missing'] for f in files_coverage)
total_lines = sum(f['total'] for f in files_coverage)
print(f"\n📊 Total: {total_missing} lignes manquantes sur {total_lines} ({100*total_missing/total_lines:.1f}%)")

# Impact potentiel
print("\n🎯 IMPACT POUR ATTEINDRE 40%:\n")
print("Si on teste 500 lignes parmi les fichiers prioritaires ci-dessus,")
print(f"on passerait de 35.98% à environ {35.98 + (500/total_lines)*100:.1f}% de couverture.")
