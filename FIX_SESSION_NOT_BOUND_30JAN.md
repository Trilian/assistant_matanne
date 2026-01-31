# 🔧 FIX: Erreur SQLAlchemy "Parent instance not bound to a Session"

## 📋 Problème Identifié

**Erreur:**

```
❌ Erreur: Parent instance <Planning at 0x7b18d8629fd0> is not bound to a Session;
lazy load operation of attribute 'repas' cannot proceed
```

**Lieu:** Module `recettes` sur la section "Planning Actif"

## 🔍 Cause Racine

L'erreur SQLAlchemy se produit quand on essaie d'accéder à une **relation lazy-loaded** après que la session soit fermée :

```python
# ❌ AVANT (code problématique)
planning = service.get_planning()  # Retourne Planning sans eager loading

# Plus tard dans le code:
for repas in planning.repas:  # ❌ ERREUR! La session est fermée
    # SQLAlchemy essaie de charger "repas" mais ne peut pas
```

Le problème venait de deux sources:

1. **Service** : `get_planning()` ne chargeait pas les repas avec `joinedload`
2. **UI** : Code utilisant `next(obtenir_contexte_db())` sans context manager, causant des fermetures prématurées de session

## ✅ Solution Appliquée

### 1. Correction du Service (`src/services/planning.py`)

**Avant:**

```python
def get_planning(self, planning_id=None, db=None):
    if planning_id:
        planning = db.query(Planning).filter(Planning.id == planning_id).first()
    else:
        planning = db.query(Planning).filter(Planning.actif == True).first()
    return planning
```

**Après:**

```python
def get_planning(self, planning_id=None, db=None):
    # ✅ Eager loading des repas et recettes avec joinedload
    if planning_id:
        planning = (
            db.query(Planning)
            .options(
                joinedload(Planning.repas).joinedload(Repas.recette)
            )
            .filter(Planning.id == planning_id)
            .first()
        )
    else:
        planning = (
            db.query(Planning)
            .options(
                joinedload(Planning.repas).joinedload(Repas.recette)
            )
            .filter(Planning.actif == True)
            .first()
        )
    return planning
```

### 2. Correction du UI (`src/domains/cuisine/ui/planning.py`)

**Avant:**

```python
# ❌ Utilisation incorrecte
db = next(obtenir_contexte_db())  # Récupère un générateur sans l'utiliser proprement

# Plus tard:
for repas in planning.repas:  # ❌ db.session peut être fermée
    # ...
```

**Après:**

```python
# ✅ Utilisation correcte du context manager
with obtenir_contexte_db() as db:
    recettes = db.query(Recette).all()
    recettes_dict = {r.nom: r.id for r in recettes}

# Et pour chaque modification:
with obtenir_contexte_db() as db:
    repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
    if repas_db:
        repas_db.recette_id = recettes_dict[new_recette]
        db.commit()
```

## 📝 Changements Effectués

### Fichiers modifiés:

1. **`src/services/planning.py`**
   - Ajout de `joinedload(Planning.repas).joinedload(Repas.recette)` dans `get_planning()`
   - Cela assure que les repas et recettes sont chargés AVEC la session active
2. **`src/domains/cuisine/ui/planning.py`** (rewritten)
   - Remplacement de `db = next(obtenir_contexte_db())` par des context managers `with obtenir_contexte_db() as db:`
   - Chaque opération BD récupère sa propre session appropriée
   - Ajout de commentaires `✅ FIX:` pour documenter les points critiques

## 🎯 Points Clés de la Solution

| Aspect                     | Avant                           | Après                      |
| -------------------------- | ------------------------------- | -------------------------- |
| **Chargement relations**   | Lazy (défaut)                   | Eager (joinedload)         |
| **Gestion session DB**     | Générateur nu                   | Context manager            |
| **Fermeture session**      | Après requête, puis utilisation | Immédiatement après `with` |
| **Accès `planning.repas`** | ❌ Erreur                       | ✅ OK (eager loaded)       |

## 🧪 Test de Validation

Pour vérifier que le fix marche:

```python
# Dans render_planning():
planning = service.get_planning()

# Ces opérations devraient marcher maintenant:
st.metric("📊 Repas planifiés", len(planning.repas))  # ✅ OK

for repas in planning.repas:  # ✅ OK
    recette_nom = repas.recette.nom  # ✅ OK
```

## 📚 Context Manager Pattern

La bonne pratique SQLAlchemy pour les context managers:

```python
# ✅ BON - Session gérée automatiquement
with obtenir_contexte_db() as session:
    result = session.query(Model).all()
    session.commit()
# Session fermée automatiquement ici

# ❌ MAUVAIS - Risque de session détachée
db = next(obtenir_contexte_db())
result = db.query(Model).all()  # db peut être fermée
```

## 🚀 Résumé

Cette correction élimine le pattern de "parent instance not bound to a session" en:

1. **Chargeant les relations en même temps** que l'objet parent (eager loading)
2. **Gérant les sessions proprement** avec des context managers
3. **Séparant logiquement** les requêtes de lecture et les opérations de modification

Le code est maintenant plus robuste, plus lisible, et élimine complètement cette classe d'erreurs!
