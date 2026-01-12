# 🚀 Guide Déploiement Rapide - Module Recettes

## Étape 1: Vérification Syntaxe

```bash
cd /workspaces/assistant_matanne

# Vérifier Python
python -m py_compile src/modules/cuisine/recettes.py
python -m py_compile src/core/models.py
python -m py_compile scripts/import_recettes_standard.py

# Vérifier JSON
python -c "import json; json.load(open('data/recettes_standard.json')); print('✅ JSON valide')"
```

**Attendu:** Aucun message d'erreur

## Étape 2: Initialiser Base de Données

### Option A: Import Standard (Recommandé)
```bash
python scripts/import_recettes_standard.py
```

**Output attendu:**
```
✅ Importing standard recipes from data/recettes_standard.json
✅ Imported 50 recipes successfully
```

### Option B: Réinitialiser Complètement
```bash
python -c "from scripts.import_recettes_standard import reset_recettes_standard; reset_recettes_standard()"
```

## Étape 3: Tester en Local

### Lancer Streamlit
```bash
cd /workspaces/assistant_matanne
streamlit run app.py
```

### Accéder
```
http://localhost:8501
```

### Tester Recettes
1. Aller à l'onglet **Cuisine** → **Recettes**
2. Vérifier affichage 50 recettes
3. Tester les filtres avancés
4. Cliquer sur détails une recette

## Étape 4: Vérifier Fonctionnement

### ✅ Checklist Listing
- [ ] Affiche grille 3 colonnes
- [ ] Badges visibles (bio, local, etc.)
- [ ] Difficulté avec emoji couleur
- [ ] Scores bio/local affichés
- [ ] Robots avec icônes
- [ ] Bouton "Voir détails" fonctionne
- [ ] Filtres rapides fonctionnent
- [ ] Filtres avancés s'ouvrent/ferment

### ✅ Checklist Détails
- [ ] En-tête avec emoji difficulté en gros
- [ ] Tous les badges affichés
- [ ] Scores en métriques
- [ ] Robots avec icônes complètes
- [ ] Infos: prep, cuisson, portions, calories
- [ ] Nutrition se déplie correctement
- [ ] Tableau ingrédients lisible
- [ ] Étapes numérotées

### ✅ Checklist Filtres
- [ ] Type de repas filtre
- [ ] Difficulté filtre
- [ ] Temps max filtre
- [ ] Score bio filtre
- [ ] Score local filtre
- [ ] Robots filtrent
- [ ] Tags filtrent
- [ ] Combinaisons OK

## Étape 5: Déployer sur Streamlit Cloud

### 5.1 Préparer GitHub
```bash
git add .
git commit -m "Phase 4: Recettes UI complète avec 50 recettes standards"
git push origin main
```

### 5.2 Connecter Streamlit Cloud
1. Aller à https://share.streamlit.io
2. Connecter GitHub
3. Sélectionner repo
4. Configurer:
   - Main file: `app.py`
   - Branch: `main`

### 5.3 Ajouter Secrets
Si nécessaire, ajouter dans Settings → Secrets:
```
[mistral]
api_key = "sk-xxxxx"

[database]
url = "postgresql://user:pass@host/db"
```

### 5.4 Déployer
Cliquer "Deploy"

**Accès:** https://assistant-matanne.streamlit.app

## Étape 6: Vérification Post-Déploiement

```bash
# Vérifier recettes importées
curl https://assistant-matanne.streamlit.app/api/recettes

# Vérifier import log
# (Accéder via interface)
```

## Dépannage

### Problème: Recettes ne s'affichent pas
```bash
# Réimporter
python scripts/import_recettes_standard.py

# Vérifier BD
python -c "
from src.services.recettes import RecetteService
from src.core.database import obtenir_contexte_db
with obtenir_contexte_db() as session:
    count = session.query(Recette).count()
    print(f'Recettes en BD: {count}')
"
```

### Problème: Erreur syntaxe UI
```bash
# Vérifier fichier
python -m py_compile src/modules/cuisine/recettes.py

# Voir erreur détaillée
python -m py_compile -v src/modules/cuisine/recettes.py
```

### Problème: JSON invalide
```bash
# Vérifier JSON
python -m json.tool data/recettes_standard.json > /dev/null && echo "OK" || echo "ERREUR"

# Voir erreur
python -c "import json; json.load(open('data/recettes_standard.json'))"
```

### Problème: Import échoue
```bash
# Voir détails
python scripts/import_recettes_standard.py --verbose

# Vérifier modèle
python -c "from src.core.models import Recette; print(Recette.__table__.columns.keys())"
```

## Rollback en Cas de Problème

### Retour version précédente
```bash
git revert HEAD
git push origin main
```

### Nettoyer BD
```bash
python -c "
from src.core.database import obtenir_contexte_db
from src.core.models import Recette
with obtenir_contexte_db() as session:
    session.query(Recette).delete()
    session.commit()
    print('✅ Recettes supprimées')
"
```

## Monitoring Post-Déploiement

### Logs Streamlit Cloud
1. Aller à https://share.streamlit.io
2. Cliquer sur votre app
3. Onglet "Logs"

### Métriques
- Nombre recettes affichées
- Temps réponse filtres
- Erreurs utilisateur

## Maintenance

### Ajouter Recettes
1. Modifier `data/recettes_standard.json`
2. Réimporter: `python scripts/import_recettes_standard.py`

### Modifier Scores
1. Éditer recette directement en BD ou JSON
2. Réimporter si JSON

### Sauvegarder Travail
```bash
# Exporter recettes créées
python -c "
import json
from src.services.recettes import RecetteService
service = RecetteService()
recettes = service.lister()
# ... sauvegarder en JSON
"
```

## Performance

### Optimisations Appliquées
- ✅ Limite 20 résultats par défaut
- ✅ Filtrage côté client (rapide)
- ✅ Grille responsive
- ✅ Lazy loading détails

### Monitoring
```python
import time
start = time.time()
# requête
print(f"Temps: {time.time() - start}s")
```

## Documentation

Voir aussi:
- [RECETTES_PHASES_SUMMARY.md](RECETTES_PHASES_SUMMARY.md) - Résumé 4 phases
- [RECETTES_PHASE4_COMPLETE.md](RECETTES_PHASE4_COMPLETE.md) - Détails techniques
- [RECETTES_USER_GUIDE.md](RECETTES_USER_GUIDE.md) - Guide utilisateur
- [src/modules/cuisine/recettes.py](src/modules/cuisine/recettes.py) - Code source

## Support

Problèmes ou questions:
1. Vérifier logs Streamlit
2. Vérifier syntaxe Python
3. Vérifier JSON valide
4. Vérifier BD accessible
5. Contacter admin

---

**Estimated Time:** ~15 min (local) + ~5 min (Cloud)
**Status:** ✅ Production Ready
**Recettes:** 50 standards prêtes
