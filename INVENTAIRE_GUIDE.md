# 📦 Guide Complet du Module Inventaire

## Table des matières
1. [Aperçu](#aperçu)
2. [Fonctionnalités](#fonctionnalités)
3. [Architecture](#architecture)
4. [Guide d'utilisation](#guide-dutilisation)
5. [API Service](#api-service)
6. [Tests](#tests)
7. [Troubleshooting](#troubleshooting)

---

## Aperçu

Le module **Inventaire** est un système complet de gestion de stock pour l'application. Il permet de:

- ✅ Gérer le stock d'ingrédients
- ✅ Détecter les alertes (stock bas, critique, péremption)
- ✅ Organiser par emplacement et catégorie
- ✅ Générer des suggestions d'achats avec IA
- ✅ Exporter/importer les données
- ✅ Visualiser des statistiques détaillées

---

## Fonctionnalités

### 1️⃣ Gestion du Stock

**Vue d'ensemble du stock:**
- Affichage de tous les articles avec quantités
- Filtrage par emplacement (Frigo, Congélateur, Placard, Cave, Garde-manger)
- Filtrage par catégorie d'ingrédient
- Filtrage par statut (critique, stock_bas, peremption_proche, ok)
- Tri et recherche avancée

**Statistiques globales:**
- Nombre total d'articles
- Articles en stock critique
- Articles avec stock faible
- Articles proches de la péremption

### 2️⃣ Système d'Alertes

Trois niveaux d'alertes:

```
🔴 CRITIQUE: Stock < 50% du seuil minimum
   └─ Action: Achat urgent recommandé

🟠 STOCK BAS: Stock < seuil minimum
   └─ Action: À surveiller, achat prévu

🔔 PÉREMPTION PROCHE: Reste < 7 jours
   └─ Action: Utiliser en priorité
```

**Vue alertes:**
- Affichage groupé par type d'alerte
- Détails article (nom, catégorie, quantité, problème)
- Actions rapides depuis chaque alerte

### 3️⃣ Gestion par Catégories

Organisez votre inventaire par catégories:

```
🏷️ Légumes (12 articles)
🏷️ Fruits (8 articles)
🏷️ Protéines (15 articles)
🏷️ Laitier (10 articles)
... (6 catégories au total)
```

**Pour chaque catégorie:**
- Nombre d'articles
- Quantité totale en stock
- Seuil moyen
- Nombre d'alertes actives

### 4️⃣ Suggestions IA

Génération automatique de listes de courses via IA:

```
🤖 Analyse votre inventaire
📊 Identifie les articles critiques
🛒 Génère 15 suggestions prioritaires
🎯 Groupe par rayon magasin
```

**Priorités générées:**
- 🔴 HAUTE: Articles critiques à acheter immédiatement
- 🟠 MOYENNE: Articles dont vous aurez besoin
- 🟢 BASSE: Articles pour optimiser votre stock

### 5️⃣ Outils d'Administration

**Export:**
- Téléchargement en CSV de tout l'inventaire
- Utile pour sauvegarde ou partage

**Statistiques:**
- Graphiques de répartition par statut
- Graphiques de répartition par catégorie
- Données complètes pour analyse

---

## Architecture

### Structure des fichiers

```
src/
├── modules/
│   └── cuisine/
│       └── inventaire.py          # 🎨 UI Streamlit (350+ lignes)
├── services/
│   └── inventaire.py              # 🔧 Service métier (470+ lignes)
└── core/
    └── models.py                  # 📦 Modèle ArticleInventaire

tests/
└── test_inventaire.py             # ✅ Tests complets (200+ lignes)
```

### Architecture en couches

```
┌─────────────────────────────────────────┐
│  UI STREAMLIT (inventaire.py)           │
│  - Tabs, widgets, dataframes            │
├─────────────────────────────────────────┤
│  SERVICE (inventaire.py)                │
│  - Logique métier, cache, IA            │
├─────────────────────────────────────────┤
│  DATABASE (models.py)                   │
│  - ArticleInventaire SQLAlchemy         │
└─────────────────────────────────────────┘
```

### Flux de données

```
User Input (UI)
    ↓
InventaireService (Business Logic)
    ├─ @with_cache (30 min TTL)
    ├─ @with_db_session (Auto DB)
    ├─ @with_error_handling
    └─ @with_rate_limiting (IA only)
    ↓
ArticleInventaire (Database)
    ↓
Response → Display (UI)
```

---

## Guide d'utilisation

### 📊 Onglet Stock

```
1. Voir tous les articles
2. Utiliser les filtres:
   - 📍 Emplacement (où stocker?)
   - 🏷️ Catégorie (quel type?)
   - ⚠️ Statut (critère d'alerte?)
3. Tableau affiche:
   - Statut (icône + label)
   - Nom article
   - Catégorie
   - Quantité actuelle
   - Seuil minimum
   - Emplacement
   - Jours avant péremption
   - Dernière mise à jour
```

### ⚠️ Onglet Alertes

```
1. Voir articles à problèmes
2. Trois sections:
   - 🔴 Critique (< 50% seuil)
   - 🟠 Stock bas (< seuil)
   - 🔔 Péremption (< 7 jours)
3. Chaque section montre:
   - Article
   - Catégorie
   - Quantité vs seuil
   - Type de problème
```

### 🏷️ Onglet Catégories

```
1. Voir inventaire organisé par catégorie
2. Chaque catégorie est un onglet
3. Affiche:
   - Statistiques (articles, quantité, seuil)
   - Tableau détaillé
4. Cliquer sur catégorie = focus sur celle-ci
```

### 🛒 Onglet Suggestions IA

```
1. Cliquer "Générer les suggestions"
2. Attendre 3-5 secondes
3. Voir 15 items groupés par priorité
4. Pour chaque item:
   - Nom
   - Quantité suggérée
   - Rayon magasin
   - Bouton "Ajouter aux courses"
```

### 🔧 Onglet Outils

**Export:**
```
1. Cliquer "Télécharger en CSV"
2. Fichier "inventaire.csv" téléchargé
3. Ouvrir dans Excel/Google Sheets
```

**Statistiques:**
```
1. Voir 4 métriques principales
2. 2 graphiques de répartition
3. Analyser votre stock
```

---

## API Service

### InventaireService

Classe principale pour l'accès métier à l'inventaire.

#### Récupération de données

```python
from src.services.inventaire import get_inventaire_service

service = get_inventaire_service()

# Tous les articles
inventaire = service.get_inventaire_complet()

# Avec filtres
inventaire = service.get_inventaire_complet(
    emplacement="Frigo",
    categorie="Légumes",
    include_ok=False  # Seulement alertes
)

# Alertes
alertes = service.get_alertes()
# → {"critique": [...], "stock_bas": [...], "peremption_proche": [...]}
```

#### Créer/modifier/supprimer

```python
# Ajouter article
result = service.ajouter_article(
    ingredient_nom="Tomate",
    quantite=5.0,
    quantite_min=2.0,
    emplacement="Frigo",
    date_peremption=date(2026, 2, 15)
)

# Mettre à jour
service.mettre_a_jour_article(
    article_id=123,
    quantite=3.0,  # Optionnel
    quantite_min=1.0,  # Optionnel
    emplacement="Placard",  # Optionnel
)

# Supprimer
service.supprimer_article(article_id=123)
```

#### Suggestions IA

```python
# Générer suggestions courses
suggestions = service.suggerer_courses_ia()
# → [SuggestionCourses, ...]

for sugg in suggestions:
    print(f"{sugg.nom}: {sugg.quantite} {sugg.unite}")
    print(f"  Priorité: {sugg.priorite}")
    print(f"  Rayon: {sugg.rayon}")
```

#### Statistiques

```python
# Stats globales
stats = service.get_statistiques()
# → {
#     "total_articles": 50,
#     "total_quantite": 245.5,
#     "emplacements": 5,
#     "categories": 8,
#     "alertes_totales": 7,
#     ...
# }

# Stats par catégorie
cat_stats = service.get_stats_par_categorie()
# → {
#     "Légumes": {"articles": 12, "quantite_totale": 50, ...},
#     "Fruits": {...},
#     ...
# }

# Articles à utiliser en priorité (FIFO)
a_prelever = service.get_articles_a_prelever(
    date_limite=date(2026, 2, 1)
)
```

### Schémas Pydantic

```python
class SuggestionCourses(BaseModel):
    nom: str              # "Tomates"
    quantite: float       # 2.5
    unite: str           # "kg"
    priorite: str        # "haute", "moyenne", "basse"
    rayon: str          # "Fruits & légumes"
```

---

## Tests

### Exécuter les tests

```bash
# Tous les tests inventaire
pytest tests/test_inventaire.py -v

# Seulement les tests unitaires
pytest tests/test_inventaire.py -v -m unit

# Seulement les tests d'intégration
pytest tests/test_inventaire.py -v -m integration

# Avec couverture
pytest tests/test_inventaire.py --cov=src/services/inventaire
```

### Couverture des tests

- ✅ TestInventaireComplet (5 tests)
  - Récupération complète
  - Filtres par emplacement/catégorie
  - Champs requis

- ✅ TestAlertes (9 tests)
  - Structure des alertes
  - Calcul des statuts (critique, bas, péremption, ok)
  - Calcul des jours avant péremption

- ✅ TestSuggestionsCourses (2 tests)
  - Existence méthode
  - Type de retour

- ✅ TestCRUDOperations (4 tests)
  - Existence des méthodes CRUD
  - Mise à jour article

- ✅ TestStatistics (6 tests)
  - Existence des méthodes stats
  - Types de retour
  - Stats par catégorie
  - FIFO

- ✅ TestInventaireIntegration (3 tests)
  - Workflow complet
  - Filters et tri
  - Stats workflow

**Total: 29 tests complets**

---

## Modèle de données

### ArticleInventaire

```python
class ArticleInventaire:
    id: int                          # Clé primaire
    ingredient_id: int               # FK → Ingredient
    quantite: float                  # Stock actuel
    quantite_min: float             # Seuil d'alerte
    emplacement: str | None         # Où ranger?
    date_peremption: date | None    # Quand périmé?
    derniere_maj: datetime          # Dernière modification
    
    # Relation
    ingredient: Ingredient           # Article référencé
    
    # Propriétés calculées
    est_stock_bas: bool             # quantite < quantite_min
    est_critique: bool              # quantite < (quantite_min * 0.5)
```

### Ingrédient

```python
class Ingredient:
    id: int
    nom: str                         # Unique
    categorie: str                   # "Légumes", etc
    unite: str                       # "kg", "L", etc
    # ...
```

---

## Décorateurs et patterns

### @with_db_session
Injection automatique de la session DB
```python
@with_db_session
def ma_fonction(self, param1, db: Session | None = None):
    # db est injecté automatiquement
    query = db.query(...)
```

### @with_cache
Cache avec TTL configurable
```python
@with_cache(ttl=1800, key_func=lambda self, x: f"key_{x}")
def ma_fonction(self, param):
    # Résultat cachée 30 minutes
    return result
```

### @with_error_handling
Gestion d'erreurs automatique
```python
@with_error_handling(default_return=[])
def ma_fonction(self):
    # Erreurs loggées, [[] retourné en cas d'erreur
    return list
```

---

## Troubleshooting

### ❌ "Service inventaire indisponible"

**Cause:** Service n'a pas pu être initialisé
```python
service = get_inventaire_service()
if service is None:
    # Vérifier:
    # 1. Database connectée
    # 2. Models importés correctement
    # 3. Logs pour plus de détails
```

**Solution:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### ❌ "Article 'Tomate' existe déjà"

**Cause:** Article déjà dans inventaire
```python
# Vérifier d'abord
existing = service.get_inventaire_complet()
items = [a["ingredient_nom"] for a in existing]
if "Tomate" in items:
    # Déjà existant, mettre à jour au lieu d'ajouter
```

### ❌ Suggestions IA ne s'affichent pas

**Cause 1:** Inventaire vide
```python
# Au moins 1 article requis
inventaire = service.get_inventaire_complet()
if not inventaire:
    st.warning("Ajoutez des articles d'abord")
```

**Cause 2:** Clé IA non configurée
```bash
# Vérifier MISTRAL_API_KEY dans .env
export MISTRAL_API_KEY="your_key"
```

### ⚠️ Performance: Requêtes lentes

**Cause:** Cache expiré ou trop de données
```python
# Cache est 30 minutes par défaut
# Les requêtes BD sont optimisées avec joinedload

# Forcer rafraîchir cache:
service.invalidate_cache()
```

### 🔄 Export CSV vide

**Cause:** Dataframe vide
```python
# Vérifier que inventaire n'est pas vide
if not inventaire_filtres:
    st.warning("Aucun article à exporter")
```

---

## Améliorations futures

- [ ] Historique des modifications
- [ ] Prévisions de stock (ML)
- [ ] Notifications push
- [ ] API REST externe
- [ ] Multi-utilisateurs avec rôles
- [ ] Photos articles
- [ ] Code-barres/QR codes
- [ ] Intégration liste courses
- [ ] Rapports PDF

---

## Ressources

- 📁 [Module inventaire](src/modules/cuisine/inventaire.py)
- 🔧 [Service inventaire](src/services/inventaire.py)
- 📦 [Modèle ArticleInventaire](src/core/models.py#L332)
- ✅ [Tests complets](tests/test_inventaire.py)

---

**Dernière mise à jour:** 18 janvier 2026
**Version:** 2.0 - Refactoring complet avec IA et stats
