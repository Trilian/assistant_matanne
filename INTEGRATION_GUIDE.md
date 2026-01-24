# 🔧 GUIDE D'INTÉGRATION - Remplacer Anciens Fichiers

## Étape 1: Remplacer les Imports dans app.py

### ❌ Ancien Code
```python
from src.modules.famille.sante import main as sante_main
from src.modules.famille.jules import main as jules_main
from src.modules.famille.activites import main as activites_main
from src.modules.famille.shopping import main as shopping_main
```

### ✅ Nouveau Code
```python
from src.modules.famille.sante import main as sante_main
from src.modules.famille.jules_upgraded import main as jules_main
from src.modules.famille.activites_upgraded import main as activites_main
from src.modules.famille.shopping_upgraded import main as shopping_main
from src.modules.famille.accueil_upgraded import main as accueil_main
from src.modules.famille.integration_cuisine_courses import show_integration_tab
```

---

## Étape 2: Ajouter Accueil au Routeur

### Chercher dans app.py
```python
MODULES = {
    "📚 Cuisine": ...,
    "🍽️ Courses": ...,
    ...
}
```

### Remplacer par
```python
MODULES = {
    "🏠 Accueil": accueil_main,
    "📚 Cuisine": ...,
    "🍽️ Courses": ...,
    "👶 Jules": jules_main,
    "🏃 Santé": sante_main,
    "🎪 Activités": activites_main,
    "🛒 Shopping": shopping_main,
    ...
}
```

---

## Étape 3: Ajouter Onglet Intégration aux Courses

Si vous avez un module `src/modules/courses/main.py`, ajouter:

```python
import streamlit as st
from src.modules.famille.integration_cuisine_courses import show_integration_tab

def main():
    st.set_page_config(page_title="Courses", page_icon="🛒", layout="wide")
    st.title("🛒 Courses")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ma Liste",
        "💡 Suggestions", 
        "💰 Budget",
        "🔗 Intégrations"  # ← NEW
    ])
    
    with tab1:
        # Code existant shopping
        pass
    
    with tab2:
        # Code existant suggestions
        pass
    
    with tab3:
        # Code existant budget
        pass
    
    with tab4:
        # ← NEW
        show_integration_tab()
```

---

## Étape 4: Tester Localement

### Terminal 1: Démarrer Streamlit
```bash
cd /workspaces/assistant_matanne
streamlit run src/app.py
```

### Test Checklist
- [ ] Accueil charge sans erreurs
- [ ] Jules affiche correctement l'âge
- [ ] Jalons s'affichent par catégorie
- [ ] Graphiques Plotly s'affichent (sante, activites, shopping)
- [ ] Budget calcule correctement
- [ ] Suggestions fonctionnent
- [ ] Intégration Cuisine/Courses accessible

---

## Étape 5: Vérifier les Migrations SQL

### Avant déployer sur Supabase

```bash
# Vérifier les migrations existent:
ls -la sql/001_add_famille_models.sql
ls -la sql/002_add_relations_famille.sql

# Vérifier la syntaxe (optionnel):
cat sql/001_add_famille_models.sql | head -20
cat sql/002_add_relations_famille.sql | head -20
```

### Exécuter Migrations sur Supabase

1. Aller sur https://supabase.com/dashboard
2. Sélectionner votre projet
3. Aller à SQL Editor → New Query
4. Copier contenu de `sql/001_add_famille_models.sql`
5. Click Run
6. Répéter avec `sql/002_add_relations_famille.sql`

---

## Étape 6: Archiver Anciens Fichiers (Optionnel)

### Créer folder backup
```bash
mkdir -p src/modules/famille/backup

# Archiver anciens fichiers
mv src/modules/famille/sante_old.py src/modules/famille/backup/ 2>/dev/null || true
mv src/modules/famille/jules.py src/modules/famille/backup/ 2>/dev/null || true
mv src/modules/famille/activites.py src/modules/famille/backup/ 2>/dev/null || true
mv src/modules/famille/shopping.py src/modules/famille/backup/ 2>/dev/null || true

# Listing
ls -la src/modules/famille/backup/
```

---

## 📋 Checklist Déploiement

- [ ] Imports mis à jour dans app.py
- [ ] Accueil ajouté au MODULES dict
- [ ] Répertoire famille a les 7 files *_upgraded.py
- [ ] Tests passent: `pytest tests/test_famille_complete.py -v`
- [ ] Streamlit local fonctionne: `streamlit run src/app.py`
- [ ] SQL migrations testées sur Supabase
- [ ] Cache fonctionne (@st.cache_data visible)
- [ ] Graphiques Plotly affichés
- [ ] Helpers réutilisables appellés correctement

---

## 🆘 Troubleshooting

### Erreur: "ModuleNotFoundError: No module named 'helpers'"
**Solution**: Vérifier import dans app.py:
```python
from src.modules.famille.helpers import get_or_create_julius
```

### Erreur: "relation 'wellbeing_entries' does not exist"
**Solution**: Exécuter migration 002 sur Supabase SQL Editor

### Graphique Plotly ne s'affiche pas
**Solution**: Vérifier pandas et plotly installés:
```bash
pip install pandas plotly --upgrade
```

### Cache ne fonctionne pas
**Solution**: Vérifier `@st.cache_data(ttl=1800)` sur helper functions

### DB connexion error
**Solution**: Vérifier variables d'env Supabase:
```python
# Dans .env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxxxxx
```

---

## 📞 Support

En cas de problème:
1. Lancer `pytest tests/test_famille_complete.py -v` pour tester modèles
2. Vérifier logs Streamlit: voir terminal où `streamlit run` tourne
3. Vérifier Supabase logs: Dashboard → Logs

---

## ✅ Validation Finale

Après déploiement, vérifier:

### Accueil
- [ ] Notifications apparaissent
- [ ] Profil Jules OK
- [ ] Graphiques budget s'affichent

### Jules
- [ ] Âge calculé correctement
- [ ] Jalons groupés par catégorie
- [ ] Activités suggestions visibles

### Santé
- [ ] Graphiques Calories & Énergie/Moral présents
- [ ] Routines et objectifs s'ajoutent

### Activités
- [ ] Timeline Plotly affichée
- [ ] Graphiques budget visibles
- [ ] Budget totaux corrects

### Shopping
- [ ] Suggestions par catégorie
- [ ] Graphiques budget par catégorie
- [ ] Analytics (estimé vs réel)

### Intégrations
- [ ] Recettes suggérées par objectifs
- [ ] Shopping pré-rempli depuis activités
- [ ] Stats nutrition affichées

---

## 🎉 C'est Fini!

Tous les fichiers sont prêts. Il vous suffit de:
1. Mettre à jour les imports dans app.py
2. Exécuter les migrations SQL
3. Lancer `streamlit run src/app.py`
4. Profiter! 🚀
