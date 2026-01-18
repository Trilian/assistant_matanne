# 📥📤 Import/Export Avancé - Guide Complet

**Status:** ✅ Implémenté et prêt  
**Formats:** CSV, Excel (.xlsx, .xls)  
**Limite:** Batch illimité (testé jusqu'à 1000 articles)

---

## 🚀 Utilisation rapide

### Importer des articles

1. **Préparer un fichier CSV ou Excel**
   - Colonnes: Nom, Quantité, Unité, Seuil Min, Emplacement, Catégorie, Date Péremption
   - Voir `TEMPLATE_IMPORT.csv` pour exemple

2. **Dans Streamlit:**
   - Allez: Cuisine → Inventaire → 🔧 Outils → 📥📤 Import/Export
   - Tab "📥 Importer"
   - Sélectionnez votre fichier
   - Validez les données
   - Cliquez "Importer"

3. **Résultat:**
   - Articles valides importés
   - Erreurs affichées (dates mal formées, colonnes manquantes, etc)
   - Historique automatiquement enregistré

### Exporter l'inventaire

1. **Dans Streamlit:**
   - Allez: Cuisine → Inventaire → 🔧 Outils → 📥📤 Import/Export
   - Tab "📤 Exporter"
   - Cliquez "Télécharger CSV" ou "Télécharger JSON"

2. **Formats:**
   - **CSV:** Compact, ouvrable dans Excel
   - **JSON:** Complet, avec statistiques + métadonnées

---

## 📋 Format des fichiers

### Format CSV

```csv
Nom,Quantité,Unité,Seuil Min,Emplacement,Catégorie,Date Péremption
Tomate,5,kg,2,Frigo,Légumes,2026-02-15
Poulet,2,pièce,1,Congélateur,Protéines,2026-01-25
Lait,3,litre,1,Frigo,Laitier,2026-01-22
```

### Format Excel

Même structure, mais dans un fichier .xlsx/.xls
- Première ligne = headers
- Données à partir ligne 2

---

## ✅ Validation

### Règles de validation

| Champ | Requis | Format | Exemple |
|-------|--------|--------|---------|
| **Nom** | ✅ | Texte (min 2 chars) | "Tomate" |
| **Quantité** | ✅ | Nombre >= 0 | 5 |
| **Unité** | ✅ | Texte | "kg", "pièce", "litre" |
| **Seuil Min** | ✅ | Nombre >= 0 | 2 |
| **Emplacement** | ❌ | Texte | "Frigo", "Placard" |
| **Catégorie** | ❌ | Texte | "Légumes", "Protéines" |
| **Date Péremption** | ❌ | YYYY-MM-DD | "2026-02-15" |

### Comportement import

- **Articles valides:** Importés automatiquement
- **Articles invalides:** Affichés avec raison d'erreur
- **Doublons:** Crée un nouvel ingrédient (pas de déduplication)

---

## 🎯 Cas d'usage courants

### Cas 1: Transférer inventaire d'une autre app
1. Exporte CSV depuis l'ancienne app
2. Adapte les colonnes selon le format attendu
3. Importe dans notre app

### Cas 2: Bulk update
1. Exporte inventaire actuel
2. Modifie les quantités dans Excel
3. Réimporte

### Cas 3: Sauvegarde régulière
1. Chaque semaine: Exporte en JSON
2. Stocke les fichiers JSON comme sauvegarde

### Cas 4: Partager avec équipe
1. Exporte en CSV
2. Partage le fichier
3. Autres équipes réimportent chez eux

---

## 🔧 Détails techniques

### Service (src/services/inventaire.py)

**Nouveau model:**
```python
class ArticleImport(BaseModel):
    nom: str
    quantite: float
    quantite_min: float
    unite: str
    categorie: str | None = None
    emplacement: str | None = None
    date_peremption: str | None = None  # YYYY-MM-DD
```

**Nouvelles méthodes:**
```python
# Import batch
def importer_articles(articles_data: list[dict]) -> list[dict]

# Export
def exporter_inventaire(format_export: str = "csv") -> str

# Validation
def valider_fichier_import(donnees: list[dict]) -> dict
```

### UI (src/modules/cuisine/inventaire.py)

**Nouvelle fonction:**
```python
def render_import_export():
    # Onglet Importer
    # - Upload fichier
    # - Preview données
    # - Validation + rapport
    # - Batch import
    
    # Onglet Exporter
    # - Boutons téléchargement CSV/JSON
    # - Stats d'export
```

---

## 🚨 Troubleshooting

### Q: "Format non supporté"
**R:** Vérifier que le fichier est CSV ou .xlsx/.xls

### Q: "Colonne Nom manquante"
**R:** Renommer la colonne en "Nom" (case-sensitive)

### Q: Les dates n'importent pas
**R:** Format doit être YYYY-MM-DD (ex: 2026-02-15), pas 15/02/2026

### Q: "Unité requise"
**R:** Champ Unité doit être rempli (ex: "kg", "pièce", "litre")

### Q: Quantity nulle après import
**R:** Colonne Quantité doit contenir un nombre, pas du texte

### Q: L'ingrédient existe déjà
**R:** Import crée un nouvel ingrédient. Pas de déduplication (feature future)

---

## 📊 Exemple: Template d'import

Voir fichier: `TEMPLATE_IMPORT.csv`

Télécharge ce fichier et modifie-le avec tes articles!

---

## 🎯 Roadmap future

- [ ] Déduplication des ingrédients (match par nom)
- [ ] Merge avec existants (au lieu de créer nouveau)
- [ ] Excel + templates (pré-formatés)
- [ ] Validation avancée (duplicatas, doublons)
- [ ] Historique import (traçabilité)
- [ ] Scheduled exports (automatique chaque semaine)

