# 🚀 QUICK START - Module Famille Upgraded

Démarrez en **5 minutes**!

---

## 📋 Prérequis

- ✅ Python 3.8+
- ✅ Streamlit installé (`pip install streamlit`)
- ✅ Plotly installé (`pip install plotly`)
- ✅ Supabase configuré

---

## 🎯 ÉTAPE 1: Vérifier les Fichiers (1 min)

```bash
cd /workspaces/assistant_matanne

# Vérifier tous les fichiers créés existent
ls -la src/modules/famille/helpers.py
ls -la src/modules/famille/sante.py
ls -la src/modules/famille/jules_upgraded.py
ls -la src/modules/famille/activites_upgraded.py
ls -la src/modules/famille/shopping_upgraded.py
ls -la src/modules/famille/accueil_upgraded.py
ls -la src/modules/famille/integration_cuisine_courses.py
ls -la tests/test_famille_complete.py
```

✅ Tous les fichiers existent? Continuez!

---

## 🔧 ÉTAPE 2: Mettre à Jour app.py (2 min)

### Ouvrir `src/app.py`

**Chercher** (Ctrl+F):
```python
from src.modules.famille import
```

**Remplacer par**:
```python
from src.modules.famille.sante import main as sante_main
from src.modules.famille.jules_upgraded import main as jules_main
from src.modules.famille.activites_upgraded import main as activites_main
from src.modules.famille.shopping_upgraded import main as shopping_main
from src.modules.famille.accueil_upgraded import main as accueil_main
from src.modules.famille.integration_cuisine_courses import show_integration_tab
```

**Chercher** (Ctrl+F):
```python
MODULES = {
```

**Remplacer par**:
```python
MODULES = {
    "🏠 Accueil": accueil_main,
    "👶 Jules": jules_main,
    "🏃 Santé": sante_main,
    "🎪 Activités": activites_main,
    "🛒 Shopping": shopping_main,
    # ... autres modules
}
```

✅ Fichier sauvegardé? Continuez!

---

## 🗄️ ÉTAPE 3: Exécuter les Migrations SQL (1 min)

### Option A: Supabase Dashboard

1. Aller à https://supabase.com/dashboard
2. Sélectionner votre projet
3. Cliquer **SQL Editor** → **New Query**
4. Copier/coller contenu de `sql/001_add_famille_models.sql`
5. Click **Run**
6. Répéter avec `sql/002_add_relations_famille.sql`

### Option B: Terminal psql (si accès direct)

```bash
# Migration 1
psql -h your-db.supabase.co -U postgres -d postgres < sql/001_add_famille_models.sql

# Migration 2
psql -h your-db.supabase.co -U postgres -d postgres < sql/002_add_relations_famille.sql
```

✅ Migrations exécutées? Continuez!

---

## 🧪 ÉTAPE 4: Lancer les Tests (1 min)

```bash
# Installer pytest (si pas fait)
pip install pytest

# Lancer les tests
pytest tests/test_famille_complete.py -v
```

**Résultat attendu**:
```
test_famille_complete.py::TestChildProfile::test_create_child_profile PASSED
test_famille_complete.py::TestMilestones::test_create_milestone PASSED
... (14 tests)

====== 14 passed in 0.45s ======
```

✅ 14 tests passent? Excellent!

---

## 🎬 ÉTAPE 5: Démarrer l'App (1 min)

```bash
# Terminal 1: Streamlit
streamlit run src/app.py

# Ou pour démarrer sur un port spécifique
streamlit run src/app.py --server.port 8501
```

**Résultat**: L'app démarre à http://localhost:8501

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Tester les Modules

1. **🏠 Accueil**
   - [ ] Notifications s'affichent
   - [ ] Profil Jules visible
   - [ ] Graphiques affichés

2. **👶 Jules**
   - [ ] Âge calculé (19 mois)
   - [ ] Jalons groupés par catégorie
   - [ ] Suggestions activités visibles

3. **🏃 Santé**
   - [ ] Graphiques Calories & Énergie/Moral visibles
   - [ ] Form ajout routine/objectif fonctionne
   - [ ] Tracking enregistre entrées

4. **🎪 Activités**
   - [ ] Timeline Plotly affichée
   - [ ] Graphiques budget visibles
   - [ ] Planning semaine fonctionnel

5. **🛒 Shopping**
   - [ ] Suggestions affichées
   - [ ] Articles s'ajoutent au shopping
   - [ ] Graphiques budget visibles

✅ Tout fonctionne? Vous êtes prêt!

---

## 🎨 Vérifiques les Graphiques

```
Module Santé:
├─ Calories vs Durée (Bar + Scatter)
└─ Énergie & Moral (Dual Lines)

Module Activités:
├─ Timeline activités (Calendar view)
├─ Budget par type (Bar chart)
└─ Timeline coûts (Scatter 30j)

Module Shopping:
├─ Budget par catégorie (Bar chart)
└─ Estimé vs Réel (Dual bars)

Module Accueil:
├─ Timeline activités (Calendar)
├─ Budget pie chart (7j)
└─ Budget cumul (Line 30j)
```

---

## 🆘 Problèmes Courants & Solutions

### ❌ Erreur: "ModuleNotFoundError: No module named 'helpers'"
**Solution**: Vérifier import dans app.py correct
```bash
grep -n "from src.modules.famille" src/app.py
```

### ❌ Erreur: "relation 'wellbeing_entries' does not exist"
**Solution**: Exécuter migration 002 sur Supabase SQL Editor

### ❌ Graphiques ne s'affichent pas
**Solution**: 
```bash
pip install plotly --upgrade
pip install pandas --upgrade
```

### ❌ Tests échouent
**Solution**:
```bash
# Vérifier syntaxe des fichiers
python3 -m py_compile src/modules/famille/*.py

# Vérifier imports
python3 -c "from src.modules.famille.helpers import get_or_create_julius"
```

### ❌ Cache warning: "Streamlit does not support caching of [...]"
**Solution**: Normal! @st.cache_data gère automatiquement

---

## 📊 Architecture Overview

```
Famille Module Structure:

┌─ Helpers (Couche Réutilisable)
│  └─ 12 fonctions avec cache + error handling
│
├─ Modules Streamlit
│  ├─ accueil_upgraded.py (Dashboard hub)
│  ├─ jules_upgraded.py (Profil enfant)
│  ├─ sante.py (Santé parent)
│  ├─ activites_upgraded.py (Planning)
│  ├─ shopping_upgraded.py (Courses)
│  └─ integration_cuisine_courses.py (Connexions)
│
├─ Database
│  ├─ 8 modèles SQLAlchemy
│  ├─ 2 migrations SQL
│  └─ Supabase PostgreSQL
│
└─ Tests
   └─ 14 pytest tests complets
```

---

## 📚 Documentation Available

- `FAMILLE_COMPLETION_SUMMARY.md` - Vue complète
- `INTEGRATION_GUIDE.md` - Guide détaillé
- `FILES_INVENTORY.md` - Inventaire tous fichiers
- `GRAPHIQUES_PLOTLY.md` - Détail graphiques
- `QUICK_START.md` - Ce fichier (5 min setup)

---

## 🎯 Next Steps

### Court Terme (Jour 1)
- ✅ Setup terminé (5 min)
- ✅ Tests passent
- ✅ App démarre sans erreurs

### Moyen Terme (Semaine 1)
- ✅ Ajouter données Jules (jalons, activités)
- ✅ Logger santé parent (routines, énergie)
- ✅ Configurer budget famille

### Long Terme (Mois 1)
- ✅ Utiliser suggestions recettes
- ✅ Analyser trends graphiques
- ✅ Partager avec famille (grandes-parents)

---

## 🚀 Déploiement Optionnel

### Streamlit Cloud
```bash
# 1. Créer repo GitHub
git init
git add .
git commit -m "Famille module complete"
git push origin main

# 2. Sur https://streamlit.io/cloud
# Connecter repo → Deploy
```

### Heroku (Optionnel)
```bash
# Crée Procfile + requirements.txt
# `git push heroku main`
```

---

## ✅ Validation Finale

```bash
# Checklist avant production:

[ ] python3 -m py_compile src/modules/famille/*.py  # ✅ Syntaxe OK
[ ] pytest tests/test_famille_complete.py -v  # ✅ 14/14 tests pass
[ ] streamlit run src/app.py  # ✅ App démarre
[ ] curl http://localhost:8501  # ✅ Frontend accessible
[ ] grep "accueil_main" src/app.py  # ✅ app.py updated
```

Si tout ✅, vous êtes **PRÊT POUR PRODUCTION**! 🎉

---

## 📞 Support Rapide

| Problème | Solution Rapide |
|----------|-----------------|
| Syntaxe error | `python3 -m py_compile file.py` |
| Import error | Vérifier `from src.modules.famille import` |
| SQL error | Exécuter migrations 001 + 002 |
| Cache warning | Normal, caching fonctionne |
| Graphique vide | `pip install plotly --upgrade` |

---

## 🎉 Félicitations!

Vous avez maintenant un **module Famille complet et production-ready** avec:

✅ 7 modules Streamlit intégrés
✅ 12 helpers réutilisables
✅ 10+ graphiques Plotly
✅ 8 modèles database
✅ 14 tests pytest
✅ 2 migrations SQL
✅ Documentation complète

**Durée setup**: ~5 minutes ⏱️

**Bon développement!** 🚀
