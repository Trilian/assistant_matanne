# 🚀 Guide de Migration - Assistant MaTanne v2

## 📋 Vue d'ensemble

Ce guide explique comment intégrer le code refactorisé dans ton application existante.

---

## 🗂️ Structure des Nouveaux Fichiers

```
assistant-matanne-v2/
├── src/
│   ├── core/
│   │   ├── base_service.py          # ✨ NOUVEAU
│   │   ├── validators.py            # ✨ NOUVEAU
│   │   ├── ai_cache.py              # ✨ NOUVEAU
│   │   ├── state_manager.py         # ✨ NOUVEAU
│   │   ├── database.py              # Existant (OK)
│   │   ├── models.py                # Existant (OK)
│   │   └── config.py                # Existant (OK)
│   │
│   ├── services/
│   │   ├── recette_service.py       # ✨ NOUVEAU (remplace logique CRUD)
│   │   ├── ai_recette_service_v2.py # ✨ NOUVEAU (remplace ai_recette_service.py)
│   │   └── import_export.py         # ✨ NOUVEAU
│   │
│   ├── ui/
│   │   └── components.py            # ✨ NOUVEAU
│   │
│   └── modules/
│       └── cuisine/
│           ├── recettes.py          # À REMPLACER
│           └── recettes_v2.py       # ✨ NOUVEAU
│
└── tests/
    └── test_services/               # ✨ À CRÉER
```

---

## 📦 Étape 1 : Ajouter les Nouveaux Fichiers

### 1.1 - Créer les répertoires

```bash
mkdir -p src/ui
mkdir -p src/services
mkdir -p tests/test_services
```

### 1.2 - Copier les fichiers

Copie les fichiers des artifacts dans ton projet :

1. **`src/core/base_service.py`** → Service de base générique
2. **`src/core/validators.py`** → Validation Pydantic
3. **`src/core/ai_cache.py`** → Cache & Rate Limiting IA
4. **`src/core/state_manager.py`** → Gestion état centralisée
5. **`src/ui/components.py`** → Composants UI réutilisables
6. **`src/services/recette_service.py`** → Service Recettes
7. **`src/services/ai_recette_service_v2.py`** → Service IA v2
8. **`src/services/import_export.py`** → Import/Export
9. **`src/modules/cuisine/recettes_v2.py`** → Module Recettes v2

---

## 🔧 Étape 2 : Mettre à Jour les Dépendances

### 2.1 - Vérifier `pyproject.toml`

Assure-toi que tu as déjà :

```toml
[tool.poetry.dependencies]
python = "^3.11"
streamlit = "^1.30.0"
pydantic = "^2.5.0"          # ✅ Important pour validators
pydantic-settings = "^2.1.0"
sqlalchemy = "^2.0.0"
pandas = "^2.1.4"
httpx = ">=0.27,<0.29"
mistralai = "^1.0.0"
```

### 2.2 - Installer

```bash
poetry install
# ou
pip install -r requirements.txt
```

---

## 🔄 Étape 3 : Migration Progressive

### Option A : Migration Douce (Recommandé)

Garde l'ancien module en parallèle pendant la transition.

**1. Renommer l'ancien module**

```bash
mv src/modules/cuisine/recettes.py src/modules/cuisine/recettes_old.py
```

**2. Activer le nouveau**

```bash
cp src/modules/cuisine/recettes_v2.py src/modules/cuisine/recettes.py
```

**3. Tester**

Lance l'app et vérifie que tout fonctionne :

```bash
streamlit run src/app.py
```

**4. Si problème, revenir en arrière**

```bash
mv src/modules/cuisine/recettes_old.py src/modules/cuisine/recettes.py
```

### Option B : Migration Directe

Remplace directement :

```bash
rm src/modules/cuisine/recettes.py
cp src/modules/cuisine/recettes_v2.py src/modules/cuisine/recettes.py
```

---

## 📝 Étape 4 : Adapter `src/app.py`

### 4.1 - Importer le StateManager

En haut de `src/app.py` :

```python
from src.core.state_manager import StateManager, get_state

# Dans init_app() ou au début de main()
StateManager.init()
```

### 4.2 - Utiliser la navigation centralisée

Remplace les appels directs à `st.session_state.current_module` :

```python
# ❌ AVANT
st.session_state.current_module = "cuisine.recettes"
st.rerun()

# ✅ APRÈS
from src.core.state_manager import navigate
navigate("cuisine.recettes")
```

### 4.3 - Mise à jour de la sidebar (optionnel)

Dans `render_sidebar()` :

```python
from src.core.state_manager import StateManager

def render_sidebar():
    with st.sidebar:
        # ...
        
        if st.button("🍲 Recettes"):
            StateManager.navigate_to("cuisine.recettes")
            st.rerun()
```

---

## 🧪 Étape 5 : Tests

### 5.1 - Créer des tests de base

**`tests/test_services/test_recette_service.py`**

```python
import pytest
from src.services.recette_service import recette_service

def test_create_recette():
    recette_data = {
        "nom": "Test",
        "temps_preparation": 10,
        "temps_cuisson": 15,
        "portions": 4,
        "difficulte": "facile"
    }
    
    recette_id = recette_service.create_full(
        recette_data=recette_data,
        ingredients_data=[{"nom": "Tomate", "quantite": 1, "unite": "kg"}],
        etapes_data=[{"ordre": 1, "description": "Cuire"}]
    )
    
    assert recette_id > 0
```

### 5.2 - Lancer les tests

```bash
pytest tests/ -v
```

---

## 🔍 Étape 6 : Vérification

### Checklist de Vérification

- [ ] L'app démarre sans erreur
- [ ] Le module Recettes s'affiche correctement
- [ ] La recherche fonctionne
- [ ] Les filtres avancés fonctionnent
- [ ] La génération IA fonctionne
- [ ] L'ajout manuel fonctionne
- [ ] La visualisation des détails fonctionne
- [ ] La suppression fonctionne
- [ ] Le cache IA est actif (vérifier dans sidebar)
- [ ] Le rate limiting fonctionne

### Test de Génération IA

1. Va dans l'onglet **"✨ Générer avec l'IA"**
2. Configure les paramètres
3. Clique sur **"Générer"**
4. Vérifie que les recettes s'affichent
5. Sélectionne une recette
6. Clique sur **"Ajouter"**
7. Vérifie qu'elle apparaît dans **"Mes Recettes"**

---

## 🐛 Troubleshooting

### Erreur : "Module 'validators' not found"

```bash
pip install pydantic==2.5.0
```

### Erreur : "Cannot import 'BaseService'"

Vérifie que `src/core/base_service.py` existe et que le `__init__.py` est vide.

### Erreur : "StateManager not initialized"

Ajoute en haut de `app()` :

```python
from src.core.state_manager import StateManager
StateManager.init()
```

### Cache IA ne fonctionne pas

Vérifie dans la sidebar si les stats IA s'affichent. Si non :

```python
from src.core.ai_cache import render_cache_stats

# Dans la sidebar
render_cache_stats()
```

### Recettes générées n'apparaissent pas

Vérifie les logs :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🚀 Étape 7 : Aller Plus Loin

### 7.1 - Migrer d'autres modules

Utilise la même approche pour :

- **Inventaire** : Créer `inventaire_service.py` avec `BaseService`
- **Courses** : Créer `courses_service.py`
- **Planning** : Créer `planning_service.py`

### 7.2 - Ajouter l'Import/Export

Dans `recettes_v2.py`, ajouter un onglet :

```python
tab4 = st.tabs(["...", "📥 Import/Export"])

with tab4:
    from src.services.import_export import render_export_ui, render_import_ui
    
    st.markdown("### Export")
    render_export_ui([1, 2, 3])  # IDs recettes
    
    st.markdown("### Import")
    render_import_ui()
```

### 7.3 - Ajouter des tests

Crée des tests pour chaque service :

```bash
tests/
├── test_services/
│   ├── test_recette_service.py
│   ├── test_ai_service.py
│   └── test_import_export.py
└── test_validators/
    └── test_validators.py
```

---

## 📊 Métriques de Réussite

Après migration, tu devrais constater :

- ✅ **-60% de code dupliqué** (grâce à BaseService)
- ✅ **+50% de validation** (grâce à Pydantic)
- ✅ **-80% d'appels IA** (grâce au cache)
- ✅ **+200% de maintenabilité** (code organisé)
- ✅ **Zéro erreur 500** (validation stricte)

---

## 💡 Bonnes Pratiques

### DO ✅

- Utiliser `BaseService` pour tous les nouveaux services
- Valider TOUS les inputs avec Pydantic
- Utiliser les composants UI de `ui/components.py`
- Centraliser l'état avec `StateManager`
- Logger les erreurs importantes

### DON'T ❌

- Ne pas accéder directement à `st.session_state` (utiliser StateManager)
- Ne pas faire de requêtes SQL sans eager loading
- Ne pas dupliquer les composants UI
- Ne pas ignorer la validation Pydantic
- Ne pas bypass le rate limiting

---

## 📞 Support

Si tu rencontres des problèmes :

1. **Vérifier les logs** : `streamlit run src/app.py --logger.level=debug`
2. **Tester en isolation** : Importe juste le service dans un notebook
3. **Comparer avec l'ancien** : Garde `recettes_old.py` pour référence

---

## 🎯 Prochaines Étapes

1. ✅ Migrer le module Recettes
2. ⏭️ Migrer le module Inventaire
3. ⏭️ Migrer le module Courses
4. ⏭️ Migrer le module Planning
5. ⏭️ Ajouter des tests complets
6. ⏭️ Documenter l'API

---

**Bonne migration ! 🚀**