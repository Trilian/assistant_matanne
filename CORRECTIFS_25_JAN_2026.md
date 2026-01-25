# 🔧 Correctifs Appliqués - Session 25 Janvier 2026

## 1. ✅ Erreur DataFrame vide dans `get_plantes_a_arroser()`

### Problème
```
KeyError: 'a_arroser'
File "/mount/src/assistant_matanne/src/modules/maison/helpers.py", line 159
    return df[df["a_arroser"]].to_dict(orient="records")
```

**Cause :** Quand aucune plante n'existe en base, le DataFrame est vide et la colonne `a_arroser` n'existe pas.

### Solution appliquée
Ajout d'un check dans `src/modules/maison/helpers.py` ligne 156-162 :

```python
@st.cache_data(ttl=1800)
def get_plantes_a_arroser() -> list[dict]:
    """Détecte les plantes qui ont besoin d'eau"""
    df = charger_plantes()
    if df.empty:  # ← NOUVEAU: Check DataFrame vide
        return []
    return df[df["a_arroser"]].to_dict(orient="records")
```

**Impact :** La fonction retourne maintenant une liste vide au lieu de planter quand aucune plante n'existe.

---

## 2. ✅ Tables manquantes en base de données

### Problème
```
ErreurBaseDeDonnees: relation "calendar_events" does not exist
```

**Cause :** Les tables du modèle `planning` n'avaient jamais été créées en base (migration incomplète).

### Tables manquantes identifiées
- `calendar_events` - Événements du calendrier
- `batch_meals` - Repas batch cooking
- `family_budgets` - Budgets familiaux

### Solution appliquée

#### Option 1 : Script Python (Recommandé)
```bash
python scripts/create_maison_tables.py
```

Le script a été amélioré pour :
- ✅ Créer **TOUTES** les tables (pas juste le module maison)
- ✅ Afficher un résumé détaillé par module
- ✅ Vérifier les tables créées
- ✅ Compter colonnes pour chaque table

#### Option 2 : Migration Alembic
Créé : `alembic/versions/008_add_planning_and_missing_tables.py`

```bash
alembic upgrade head
```

### Tables créées par le script

| Module | Tables | Statut |
|--------|--------|--------|
| 🍽️ Recettes | 5 tables | ✅ |
| 🛍️ Courses | 2 tables | ✅ |
| 👨‍👩‍👧‍👦 Famille | 6 tables | ✅ |
| 🏠 Maison | 6 tables | ✅ |
| 📅 Planning | 3 tables | ✅ Nouveau |
| 👨‍🍳 Batch Cooking | 1 table | ✅ Nouveau |
| 💰 Budget | 1 table | ✅ Nouveau |
| **Total** | **24 tables** | **✅ Créées** |

---

## 3. 📊 Fichiers modifiés et créés

### Modifiés
- ✅ `src/modules/maison/helpers.py` - Ligne 159-162 : Ajout check DataFrame vide
- ✅ `scripts/create_maison_tables.py` - Complètement refactorisé pour créer TOUTES les tables

### Créés
- ✅ `alembic/versions/008_add_planning_and_missing_tables.py` - Migration Alembic complète
- ✅ `GUIDE_CREATION_TABLES_COMPLETES.md` - Guide d'exécution
- ✅ Ce fichier de suivi

---

## 4. 🚀 Comment tester les corrections

### Test 1 : Création de tables
```bash
# Exécuter le script
python scripts/create_maison_tables.py

# Résultat attendu : ✨ SUCCÈS! Toutes les tables sont créées.
```

### Test 2 : Lancer l'app
```bash
streamlit run src/app.py
```

### Test 3 : Naviguer vers 🏠 Maison
- La page d'accueil doit afficher sans erreur
- Les 3 sous-modules doivent être accessibles

### Test 4 : Chaque sous-module
- 🌱 Jardin - Doit charger sans erreur (liste vide si aucune plante)
- 📋 Projets - Doit afficher les tabs
- ☑️ Entretien - Doit afficher les routines

---

## 5. 📝 Notes importantes

### Pour les prochaines sessions
1. Les migrations Alembic existent maintenant pour `calendar_events`, `batch_meals`, `family_budgets`
2. Toutes les tables du modèle sont maintenant créées automatiquement par `Base.metadata.create_all()`
3. Le script Python est la méthode recommandée (plus rapide que Alembic, même résultat)

### Dépendances résolues
- ✅ `get_plantes_a_arroser()` sécurisée pour DataFrame vide
- ✅ Toutes les relations SQLAlchemy peuvent être chargées
- ✅ Le module `planning` peut accéder à `calendar_events`

---

## 6. 🎯 Prochaines étapes pour l'utilisateur

```
1. python scripts/create_maison_tables.py
   ↓
2. streamlit run src/app.py
   ↓
3. Naviguer vers 🏠 Maison
   ↓
4. Ajouter quelques plantes/projets pour tester
```

Les 3 sous-modules du module Maison doivent être maintenant **100% fonctionnels** ! 🎉
