# 📱 Mise en Place: Code-Barres/QR + Rapports PDF

**Date**: 18 Janvier 2026
**Status**: ✅ Implémentation Complète

## 🎯 Vue d'ensemble

Deux fonctionnalités majeures ajoutées:
1. **Scanner Code-Barres/QR** - Gestion rapide de l'inventaire
2. **Rapports PDF** - Analyse financière et gaspillage

---

## 📱 1. SCANNER CODE-BARRES/QR

### Fichiers créés

#### Service Backend
```
src/services/barcode.py
├── BarcodeService - Service principal
├── Validation checksums (EAN-13, EAN-8, UPC)
├── Scan et détection codes
├── Gestion articles par barcode
├── Import/Export CSV
└── Cache et optimisations
```

#### Interface Streamlit
```
src/modules/barcode.py
├── Tab 1: Scanner (scan codes, affichage)
├── Tab 2: Ajout rapide (créer articles)
├── Tab 3: Vérifier stock (vérification)
├── Tab 4: Gestion (lister, éditer)
└── Tab 5: Import/Export (CSV)
```

#### Migration BD
```
alembic/versions/003_add_barcode_price.py
├── Colonne code_barres (unique, indexed)
├── Colonne prix_unitaire (pour rapports)
└── Contraintes et indexes
```

### Modèle ArticleInventaire (updated)

```python
class ArticleInventaire(Base):
    # ... colonnes existantes ...
    
    # Code-barres (Nouveau)
    code_barres: str | None        # EAN-13, QR, CODE128, etc.
    prix_unitaire: float | None    # Pour calculs rapports
```

### Formats Supportés

| Format | Longueur | Exemple | Checksum |
|--------|----------|---------|----------|
| EAN-13 | 13 chiffres | 5901234123457 | Oui |
| EAN-8 | 8 chiffres | 96385074 | Oui |
| UPC | 12 chiffres | 123456789012 | Oui |
| QR Code | Variable | [QR data] | Non |
| CODE128 | Variable | ABC123 | Optionnel |
| CODE39 | Variable | ABC-123 | Optionnel |

### Fonctionnalités Principales

#### 1. Scanner Code
```python
service = BarcodeService()
resultat = service.scanner_code("5901234123457")
# Retourne: ScanResultat avec détails article
```

**Résultat scan:**
```python
{
    "barcode": "5901234123457",
    "type_scan": "article",  # ou "inconnu"
    "details": {
        "id": 42,
        "nom": "Tomates cerises",
        "quantite": 5.0,
        "unite": "unité",
        "prix_unitaire": 2.50,
        "date_peremption": "2026-02-15",
        "emplacement": "Frigo"
    },
    "timestamp": datetime.now()
}
```

#### 2. Ajout Rapide Article
```python
article = service.ajouter_article_par_barcode(
    code="5901234123457",
    nom="Tomates cerises",
    quantite=1.0,
    unite="unité",
    categorie="Légumes",
    prix_unitaire=2.50,
    date_peremption_jours=14,
    emplacement="Frigo"
)
```

#### 3. Vérification Stock
```python
info = service.verifier_stock_barcode("5901234123457")
# Retourne: état_stock (OK/FAIBLE/CRITIQUE), peremption, etc.
```

**État stock:**
- ✅ **OK**: Stock >= minimum
- ⚠️ **FAIBLE**: Stock < minimum
- 🔴 **CRITIQUE**: Stock = 0

**État péremption:**
- ✅ **OK**: >30 jours
- ⏰ **BIENTÔT**: 7-30 jours
- 🚨 **URGENT**: 0-7 jours
- ❌ **PÉRIMÉ**: Expiré

#### 4. Gestion Mappings
```python
# Lister articles avec barcode
articles = service.lister_articles_avec_barcode()

# Mettre à jour code
service.mettre_a_jour_barcode(article_id, nouveau_code)

# Export/Import CSV
csv_data = service.exporter_barcodes()
resultats = service.importer_barcodes(csv_content)
```

### Cas d'Usage

#### 1️⃣ Ajout rapide au scanner
```
1. Scannez code-barres
2. Si nouveau → Tab "Ajout rapide"
3. Remplissez nom, quantité, catégorie
4. Cliquez "Ajouter article" ✅
```

#### 2️⃣ Vérification stock rapide
```
1. Allez à "Vérifier stock"
2. Scannez code
3. Voir état stock instantanément
4. Ajouter quantité si faible
```

#### 3️⃣ Intégration recettes
- Lier codes-barres aux ingrédients
- Scanner pour ajouter ingrédients recette
- Validation automatique stock
- TODO: À implémenter en phase 2

---

## 📊 2. RAPPORTS PDF

### Fichiers créés

#### Service Backend
```
src/services/rapports_pdf.py
├── RapportsPDFService - Service principal
├── Rapport Stocks Hebdo (RapportStocks)
├── Rapport Budget (RapportBudget)
├── Analyse Gaspillage (AnalyseGaspillage)
└── Export PDF via ReportLab
```

#### Interface Streamlit
```
src/modules/rapports.py
├── Tab 1: Stocks (hebdo)
├── Tab 2: Budget (7j-1an)
├── Tab 3: Gaspillage (7j-3m)
└── Tab 4: Historique & Planification
```

### Dépendances

```
reportlab>=3.6.0  # PDF generation
```

Déjà dans `requirements.txt`:
- PyPDF2≥3.0.0 (pour manipulation PDF)
- pandas (pour tableaux)
- streamlit (pour UI)

### 📦 Rapport Stocks (Hebdomadaire)

**Données collectées:**
```python
{
    "articles_total": 47,
    "articles_faible_stock": [
        {
            "nom": "Tomates",
            "quantite": 2,
            "quantite_min": 5,
            "unite": "unité",
            "emplacement": "Frigo"
        }
    ],
    "articles_perimes": [
        {
            "nom": "Yaourt",
            "date_peremption": "2026-01-15",
            "jours_perime": 3,
            "quantite": 2,
            "unite": "pot"
        }
    ],
    "categories_resumee": {
        "Légumes": {
            "quantite": 25,
            "articles": 12,
            "valeur": 45.50
        },
        # ...
    },
    "valeur_stock_total": 234.50
}
```

**Utilisation:**
```python
service = RapportsPDFService()

# Aperçu données
donnees = service.generer_donnees_rapport_stocks(periode_jours=7)

# PDF
pdf = service.generer_pdf_rapport_stocks(periode_jours=7)
# Télécharger...
```

**Contenu PDF:**
- 📊 Résumé général (total articles, valeur, alertes)
- ⚠️ Articles faible stock
- ❌ Articles périmés
- 📦 Stock par catégorie

### 💰 Rapport Budget

**Données collectées:**
```python
{
    "depenses_total": 234.50,
    "depenses_par_categorie": {
        "Légumes": 45.50,
        "Protéines": 80.00,
        # ...
    },
    "articles_couteux": [
        {
            "nom": "Fromage Camembert",
            "categorie": "Laitier",
            "quantite": 2,
            "unite": "unité",
            "prix_unitaire": 8.50,
            "cout_total": 17.00
        }
    ],
    "evolution_semaine": []  # TODO
}
```

**Utilisation:**
```python
# Périodes supportées: 7, 14, 30, 90, 365 jours
donnees = service.generer_donnees_rapport_budget(periode_jours=30)
pdf = service.generer_pdf_rapport_budget(periode_jours=30)
```

**Contenu PDF:**
- 💵 Résumé financier (total, moyenne/jour)
- 📊 Dépenses par catégorie (tableau + graphique)
- ⭐ Articles les plus coûteux

### 🗑️ Analyse Gaspillage

**Données collectées:**
```python
{
    "articles_perimes_total": 5,
    "valeur_perdue": 45.25,
    "categories_gaspillage": {
        "Légumes": {
            "articles": 3,
            "valeur": 15.50
        }
    },
    "articles_perimes_detail": [
        {
            "nom": "Tomates",
            "date_peremption": "2026-01-10",
            "jours_perime": 8,
            "quantite": 3,
            "unite": "unité",
            "valeur_perdue": 7.50
        }
    ],
    "recommandations": [
        "⚠️ Gaspillage important: améliorer planification",
        "💰 Valeur perdue: €45.25 - Optimiser l'inventaire",
        "📅 Mettre en place FIFO (First In First Out)"
    ]
}
```

**Utilisation:**
```python
# Périodes: 7, 14, 30, 90 jours
analyse = service.generer_analyse_gaspillage(periode_jours=30)
pdf = service.generer_pdf_analyse_gaspillage(periode_jours=30)
```

**Contenu PDF:**
- 🗑️ Résumé gaspillage (total items, valeur perdue)
- 💡 Recommandations automatiques
- ❌ Articles périmés (détail)
- 📊 Gaspillage par catégorie

### Utilisation UI Streamlit

```python
# Dans src/modules/rapports.py
from src.services.rapports_pdf import RapportsPDFService

service = RapportsPDFService()

# Aperçu + Téléchargement
donnees = service.generer_donnees_rapport_stocks(7)  # Affichage
pdf = service.generer_pdf_rapport_stocks(7)           # Téléchargement

# Ou en une ligne
pdf, filename = service.telecharger_rapport_pdf("stocks", 7)
```

---

## 🔧 Installation & Configuration

### 1. Migration BD

```bash
# Dans /workspaces/assistant_matanne

# Créer migration
alembic revision --autogenerate -m "Add barcode and price fields"

# Ou utiliser la migration fournie
alembic upgrade head
```

### 2. Vérifier dépendances

```bash
# Vérifier requirements.txt contient:
pip install reportlab>=3.6.0  # Si non présent

# Autres (déjà installées):
- sqlalchemy
- pydantic
- streamlit
- pandas
- PyPDF2
```

### 3. Initialiser Services

```python
# Dans src/services/__init__.py (à créer si absent)

from .barcode import BarcodeService
from .rapports_pdf import RapportsPDFService

__all__ = [
    "BarcodeService",
    "RapportsPDFService"
]
```

### 4. Enregistrer Modules UI

Dans `src/app.py` ou fichier de routing:

```python
# Ajouter aux modules disponibles
modules = {
    "📱 Scanner Code-Barres": "barcode",
    "📊 Rapports PDF": "rapports",
    # ... autres modules
}
```

---

## 📈 Intégration avec Modules Existants

### Accueil (Dashboard)

```python
# src/modules/accueil.py - Ajouter alertes

def render_critical_alerts():
    # ... code existant ...
    
    # Nouveau: Alertes barcode
    service = BarcodeService()
    articles_perimes = service.verifier_stock_barcode_multiples()
    if articles_perimes:
        st.warning(f"⚠️ {len(articles_perimes)} articles périmés détectés")
```

### Inventaire (Integration)

```python
# src/modules/accueil.py / inventaire module

# Ajouter bouton "Scanner"
if st.button("📱 Scannez pour ajouter"):
    st.switch_page("pages/barcode.py")

# Afficher code-barres dans tableau articles
df["Code-barres"] = articles_data["code_barres"]
```

### Paramètres (Configuration)

```python
# Futures améliorations:
- ⚙️ Configurer formats acceptés
- 🔔 Alertes automatiques
- 📅 Planification rapports
- 📧 Envoi rapports par email
```

---

## 📚 Exemples d'Utilisation

### Exemple 1: Scanner rapide au démarrage

```python
# Interface Streamlit
st.title("📱 Scanner Rapide")

code = st.text_input("Scannez un code:")
if code:
    service = BarcodeService()
    try:
        resultat = service.scanner_code(code)
        if resultat.type_scan == "article":
            st.success(f"✅ {resultat.details['nom']}")
            # Afficher options (ajouter quantité, etc)
    except ErreurValidation as e:
        st.error(f"Code invalide: {e}")
```

### Exemple 2: Rapport automatique hebdo

```python
# À mettre dans job/scheduler
from datetime import datetime, timedelta
from src.services.rapports_pdf import RapportsPDFService

def generer_rapport_hebdo():
    service = RapportsPDFService()
    
    # Générer
    pdf, filename = service.telecharger_rapport_pdf("stocks", 7)
    
    # Envoyer email ou stocker
    with open(f"/reports/{filename}", "wb") as f:
        f.write(pdf.getvalue())
    
    return filename
```

### Exemple 3: Validation avant utilisation recette

```python
# Futur: Intégration recettes
from src.services.barcode import BarcodeService

service = BarcodeService()

# Avant de faire une recette
ingredients_requis = [
    ("5901234123457", "Tomates"),  # barcode, nom
    ("5901234567890", "Oignons")
]

for barcode, nom in ingredients_requis:
    info = service.verifier_stock_barcode(barcode)
    if info["etat_stock"] == "CRITIQUE":
        st.warning(f"⚠️ {nom} en stock critique!")
```

---

## ✅ Checklist Implémentation

- [x] Service `BarcodeService` complet
  - [x] Validation checksums (EAN-13, EAN-8, UPC)
  - [x] Scanner codes
  - [x] Gestion articles
  - [x] Import/Export CSV

- [x] Service `RapportsPDFService` complet
  - [x] Rapport stocks
  - [x] Rapport budget
  - [x] Analyse gaspillage
  - [x] Export PDF via ReportLab

- [x] UI Streamlit
  - [x] Module scanner (barcode.py)
  - [x] Module rapports (rapports.py)
  - [x] 5 onglets scanner
  - [x] 4 onglets rapports

- [x] Modèle BD
  - [x] Colonne `code_barres` (unique, indexed)
  - [x] Colonne `prix_unitaire`
  - [x] Migration Alembic

- [ ] Futures améliorations
  - [ ] Intégration recettes (scanner ingrédients)
  - [ ] API caméra/webcam (vs scan manuel)
  - [ ] Rapports automatiques (job scheduler)
  - [ ] Export email
  - [ ] Graphiques avancés (Plotly)
  - [ ] Historique périodes multiples

---

## 🐛 Dépannage

### Code-barres non reconnu
```python
# Vérifier format
service = BarcodeService()
valide, msg = service.valider_barcode("mon_code")
print(msg)  # Affiche raison d'erreur
```

### PDF ne se génère pas
```bash
# Vérifier reportlab
pip install --upgrade reportlab

# Vérifier droits d'écriture /tmp
```

### Performance rapports
```python
# Utiliser cache
@with_cache(ttl=3600)
def generer_donnees_rapport_stocks(...):
    # Cache 1 heure
```

---

## 📖 Documentation Complète

Voir:
- `src/services/barcode.py` - Docstrings complets
- `src/services/rapports_pdf.py` - Docstrings complets
- `src/modules/barcode.py` - UI Streamlit
- `src/modules/rapports.py` - UI Streamlit

---

**Prochaines étapes:**
1. Tester l'intégration complète
2. Mettre en place intégration recettes
3. Ajouter rapports automatiques (scheduler)
4. Optimiser PDF (graphiques, couleurs)
5. Ajouter support caméra temps réel
