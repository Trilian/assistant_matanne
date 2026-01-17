# 🎨 Génération d'Images pour les Recettes

## ⚡ Démarrage Rapide (2 minutes)

### Étape 1: Obtenir une clé Unsplash (Gratuit)
1. Aller à https://unsplash.com/oauth/applications
2. Se connecter ou créer un compte (gratuit)
3. Cliquer "Create new application"
4. Remplir le formulaire simplement
5. Copier votre **Access Key**

### Étape 2: Configurer la variable d'environnement
```bash
# En local (terminal)
export UNSPLASH_API_KEY="votre_clé_ici"

# Ou dans un fichier .env
echo "UNSPLASH_API_KEY=votre_clé_ici" >> .env
```

### Étape 3: Tester
```bash
python3 test_image_generation.py
```

---

## 🎯 Résultat

Les images des recettes seront maintenant:
- ✅ Des **photos réelles** de Unsplash (excellent)
- ✅ Ou des **images IA** de Pollinations (très bon fallback)
- ✅ **Instantanées** (< 1 seconde)
- ✅ **100% gratuites**

---

## 📊 Qualité par source

| Source | Qualité | Temps | Coût | Configuration |
|--------|---------|-------|------|----------------|
| **Unsplash** | ⭐⭐⭐⭐⭐ | < 1s | 🟢 Gratuit | 1 clé API |
| **Pexels** | ⭐⭐⭐⭐ | < 1s | 🟢 Gratuit | 1 clé API |
| **Pixabay** | ⭐⭐⭐⭐ | < 1s | 🟢 Gratuit | 1 clé API |
| **Pollinations** | ⭐⭐⭐ | 2-3s | 🟢 Gratuit | ✅ Automatique |

---

## 🔧 Configuration Complète (Optionnel)

Pour avoir **plus de couverture**, configurer toutes les APIs:

```bash
# .env
UNSPLASH_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here
PIXABAY_API_KEY=your_key_here
REPLICATE_API_TOKEN=r8_your_token_here
```

Voir [IMAGE_GENERATION_SETUP.md](IMAGE_GENERATION_SETUP.md) pour les détails complets.

---

## 🚀 Utilisation dans le Code

```python
from src.utils.image_generator import generer_image_recette

# Générer une image
url = generer_image_recette(
    nom_recette="Pâtes Carbonara",
    description="Recette italienne classique",
    type_plat="déjeuner"
)

if url:
    st.image(url)
```

---

## ✅ Vérifier que ça marche

Dans l'interface Streamlit:
1. Aller dans "Mes Recettes" → "✨ Générer IA"
2. Générer des recettes
3. Dans la recette détaillée, cliquer "✨ Générer l'image"
4. L'image s'affiche immédiatement ✅

---

## ❓ Problèmes?

### "Aucune image générée"
→ Vérifier que `UNSPLASH_API_KEY` est défini:
```bash
echo $UNSPLASH_API_KEY
```

### "Qualité faible"
→ Ajouter une description à la recette pour améliorer la recherche

### API limitée
→ Configurer plusieurs APIs pour plus de couverture

---

Pour plus d'infos: [IMAGE_GENERATION_SETUP.md](IMAGE_GENERATION_SETUP.md)
