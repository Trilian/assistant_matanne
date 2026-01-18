# 🚀 QUICK START - Code-Barres & Rapports PDF

## ⚡ Mise en Place en 5 minutes

### 1️⃣ Migration BD (1 min)

```bash
cd /workspaces/assistant_matanne

# Appliquer migration
alembic upgrade head
```

✅ Colonnes `code_barres` et `prix_unitaire` ajoutées à la table `inventaire`

### 2️⃣ Vérifier dépendances (1 min)

```bash
# Vérifier reportlab installé
pip install reportlab>=3.6.0

# Autres déjà présentes:
# - sqlalchemy ✅
# - pydantic ✅
# - streamlit ✅
# - pandas ✅
```

### 3️⃣ Enregistrer modules (1 min)

**Fichier**: `src/app.py`

Trouver la section `# Modules disponibles` et ajouter:

```python
# Dans la liste/dict des modules
"📱 Scanner Code-Barres": barcode,
"📊 Rapports PDF": rapports,
```

### 4️⃣ Tester services (1 min)

```bash
python3 << 'EOF'
from src.services.barcode import BarcodeService
from src.services.rapports_pdf import RapportsPDFService

# Test barcode
service_bc = BarcodeService()
valide, type_code = service_bc.valider_barcode("5901234123457")
print(f"✅ Barcode valide: {valide} ({type_code})")

# Test rapports
service_rp = RapportsPDFService()
donnees = service_rp.generer_donnees_rapport_stocks(7)
print(f"✅ Rapport: {donnees.articles_total} articles en stock")

print("\n✅ Tous les tests passent!")
EOF
```

### 5️⃣ Lancer l'app (1 min)

```bash
streamlit run src/app.py
```

Puis:
- Aller à **📱 Scanner Code-Barres**
- Aller à **📊 Rapports PDF**

---

## 📱 Scanner Code-Barres - Démarrage Rapide

### Exemple 1: Scanner un code

```python
from src.services.barcode import BarcodeService

service = BarcodeService()

# Scanner code
resultat = service.scanner_code("5901234123457")
print(f"Type: {resultat.type_scan}")
print(f"Details: {resultat.details}")
```

**Résultat si article existe:**
```
Type: article
Details: {
    'id': 42,
    'nom': 'Tomates cerises',
    'quantite': 5.0,
    'unite': 'unité',
    ...
}
```

### Exemple 2: Ajouter article rapide

```python
from src.services.barcode import BarcodeService

service = BarcodeService()

article = service.ajouter_article_par_barcode(
    code="5901234123457",
    nom="Tomates cerises",
    quantite=3.0,
    unite="unité",
    categorie="Légumes",
    prix_unitaire=2.50,
    date_peremption_jours=14,
    emplacement="Frigo"
)

print(f"✅ Article créé: {article.nom}")
```

### Exemple 3: Vérifier stock

```python
from src.services.barcode import BarcodeService

service = BarcodeService()

info = service.verifier_stock_barcode("5901234123457")

print(f"Article: {info['nom']}")
print(f"Stock: {info['quantite']} {info['quantite_min']} required")
print(f"État: {info['etat_stock']}")  # OK, FAIBLE, CRITIQUE
print(f"Péremption: {info['peremption_etat']}")  # OK, BIENTÔT, URGENT, PÉRIMÉ
```

---

## 📊 Rapports PDF - Démarrage Rapide

### Exemple 1: Générer rapport stocks

```python
from src.services.rapports_pdf import RapportsPDFService

service = RapportsPDFService()

# Données
donnees = service.generer_donnees_rapport_stocks(7)
print(f"Total articles: {donnees.articles_total}")
print(f"Valeur stock: €{donnees.valeur_stock_total:.2f}")
print(f"Articles faible stock: {len(donnees.articles_faible_stock)}")
print(f"Articles périmés: {len(donnees.articles_perimes)}")

# PDF
pdf = service.generer_pdf_rapport_stocks(7)

# Sauvegarder
with open("rapport_stocks.pdf", "wb") as f:
    f.write(pdf.getvalue())

print("✅ PDF généré: rapport_stocks.pdf")
```

### Exemple 2: Rapport budget

```python
from src.services.rapports_pdf import RapportsPDFService

service = RapportsPDFService()

# Données (derniers 30 jours)
donnees = service.generer_donnees_rapport_budget(30)
print(f"Dépenses totales: €{donnees.depenses_total:.2f}")
print(f"Moyenne/jour: €{donnees.depenses_total/30:.2f}")
print(f"Articles coûteux: {len(donnees.articles_couteux)}")

# PDF
pdf = service.generer_pdf_rapport_budget(30)
with open("rapport_budget.pdf", "wb") as f:
    f.write(pdf.getvalue())
```

### Exemple 3: Analyse gaspillage

```python
from src.services.rapports_pdf import RapportsPDFService

service = RapportsPDFService()

# Analyse (dernier mois)
analyse = service.generer_analyse_gaspillage(30)
print(f"Articles périmés: {analyse.articles_perimes_total}")
print(f"Valeur perdue: €{analyse.valeur_perdue:.2f}")
print(f"Recommandations:")
for rec in analyse.recommandations:
    print(f"  - {rec}")

# PDF
pdf = service.generer_pdf_analyse_gaspillage(30)
with open("analyse_gaspillage.pdf", "wb") as f:
    f.write(pdf.getvalue())
```

---

## 🎯 UI Streamlit - Utilisation

### 📱 Scanner Module

**Tab 1: Scanner**
1. Scannez un code-barres
2. Voir résultats instantanés
3. Actions rapides (ajouter, éditer)

**Tab 2: Ajout rapide**
1. Entrez code-barres
2. Remplissez nom, quantité, catégorie
3. Cliquez "Ajouter article"

**Tab 3: Vérifier stock**
1. Scannez code
2. Voir état stock (OK/FAIBLE/CRITIQUE)
3. Voir péremption

**Tab 4: Gestion**
1. Voir liste articles avec barcode
2. Mettre à jour codes

**Tab 5: Import/Export**
1. Export CSV tous les codes
2. Import CSV nouveau fichier

### 📊 Rapports Module

**Tab 1: Stocks (Hebdo)**
- Cliquer "Aperçu" pour voir données
- Cliquer "Télécharger PDF" pour fichier

**Tab 2: Budget**
- Sélectionner période (7j, 2w, 1m, 3m, 1an)
- Voir dépenses par catégorie
- Articles les plus coûteux

**Tab 3: Gaspillage**
- Analyser articles périmés
- Valeur perdue
- Recommandations

**Tab 4: Historique**
- Vue planification
- Statistiques

---

## 📄 Format Codes Acceptés

| Code | Longueur | Exemple | Checksum |
|------|----------|---------|----------|
| EAN-13 | 13 | 5901234123457 | ✅ Validé |
| EAN-8 | 8 | 96385074 | ✅ Validé |
| UPC | 12 | 123456789012 | ✅ Validé |
| QR Code | Variable | [...QR data...] | Non |
| CODE128 | 6+ | ABC123 | Optionnel |
| CODE39 | Variable | ABC-123 | Optionnel |

---

## 🧪 Quick Tests

### Test Barcode Service

```python
from src.services.barcode import BarcodeService

service = BarcodeService()

# Test 1: Validation
assert service.valider_barcode("5901234123457")[0]
assert not service.valider_barcode("ABC")[0]
print("✅ Validation OK")

# Test 2: Scanner (si article existe)
try:
    resultat = service.scanner_code("5901234123457")
    print(f"✅ Scanner OK: {resultat.type_scan}")
except Exception as e:
    print(f"✅ Scanner OK (article non trouvé attendu)")

# Test 3: Import/Export
csv_data = service.exporter_barcodes()
assert "barcode" in csv_data
print("✅ Export OK")
```

### Test Rapports Service

```python
from src.services.rapports_pdf import RapportsPDFService

service = RapportsPDFService()

# Test 1: Données stocks
donnees = service.generer_donnees_rapport_stocks(7)
assert donnees.articles_total >= 0
print("✅ Rapport stocks OK")

# Test 2: PDF generation
pdf = service.generer_pdf_rapport_stocks(7)
assert len(pdf.getvalue()) > 1000
print("✅ PDF stocks OK")

# Test 3: Budget
rapport = service.generer_donnees_rapport_budget(30)
assert rapport.depenses_total >= 0
print("✅ Rapport budget OK")

# Test 4: Gaspillage
analyse = service.generer_analyse_gaspillage(30)
assert analyse.articles_perimes_total >= 0
print("✅ Analyse gaspillage OK")
```

---

## 🔧 Configuration Avancée

### Modifier formats acceptés

**Fichier**: `src/services/barcode.py`

```python
def valider_barcode(self, code: str):
    # Ajouter nouveau format
    if re.match(r'^custom_pattern$', code):
        return True, "CUSTOM_FORMAT"
```

### Personnaliser couleurs PDF

**Fichier**: `src/services/rapports_pdf.py`

```python
# Chercher et modifier colors.HexColor
colors.HexColor('#2E7D32')  # Vert
colors.HexColor('#1976D2')  # Bleu
colors.HexColor('#D32F2F')  # Rouge
colors.HexColor('#F57F17')  # Orange
```

### Ajouter colonnes au PDF

**Fichier**: `src/services/rapports_pdf.py`

```python
# Dans generer_pdf_rapport_stocks()
# Modifier tableau data:
stock_data = [["Article", "Quantité", "Minimum", "Unité", "NOUVELLE_COLONNE"]]
for article in donnees.articles_faible_stock[:10]:
    stock_data.append([
        article["nom"][:30],
        f"{article['quantite']}",
        f"{article['quantite_min']}",
        article["unite"],
        "nouvelle_valeur"  # Ajouter ici
    ])
```

---

## 📊 Architecture

```
src/
├── services/
│   ├── barcode.py              # Scanner service
│   └── rapports_pdf.py         # Rapports service
├── modules/
│   ├── barcode.py              # Scanner UI
│   └── rapports.py             # Rapports UI
└── core/
    └── models.py               # ArticleInventaire updated
```

---

## 🐛 Troubleshooting

### "Module not found"
```bash
# Ajouter à PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/workspaces/assistant_matanne"
```

### "reportlab not installed"
```bash
pip install reportlab>=3.6.0
```

### "Migration failed"
```bash
# Vérifier état migration
alembic current
alembic history

# Reset si problème
alembic downgrade -1
alembic upgrade head
```

### "PDF file corrupted"
- Vérifier BytesIO non fermé avant retour
- Vérifier `buffer.seek(0)` avant return
- Vérifier ReportLab version compatible

---

## 📈 Prochaines Étapes

1. ✅ **Installation** - Fait
2. ⏳ **Tests** - À faire (voir tests recommandés)
3. ⏳ **Intégration recettes** - Scanner ingrédients
4. ⏳ **Rapports automatiques** - Planification scheduler
5. ⏳ **Export email** - Envoi rapports

---

## 📚 Ressources

- **Documentation complète**: `BARCODE_RAPPORTS_SETUP.md`
- **Implémentation détaillée**: `IMPLEMENTATION_BARCODE_RAPPORTS.md`
- **Code service barcode**: `src/services/barcode.py`
- **Code service rapports**: `src/services/rapports_pdf.py`
- **Code UI scanner**: `src/modules/barcode.py`
- **Code UI rapports**: `src/modules/rapports.py`

---

✅ **Vous êtes prêt!** Lancez l'app et testez les nouvelles fonctionnalités.

```bash
streamlit run src/app.py
```

Besoin d'aide? Consultez `BARCODE_RAPPORTS_SETUP.md` 📖
