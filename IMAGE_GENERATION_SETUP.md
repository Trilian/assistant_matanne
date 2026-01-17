# Configuration de la Génération d'Images pour les Recettes

## 🎯 Objectif
Générer automatiquement des images haute qualité pour les recettes en utilisant des APIs **100% gratuites**.

## 📊 Priorité des APIs utilisées

Le système essaie dans cet ordre (toutes **gratuit**):

### 1. 🖼️ **Recherche d'images réelles** (Priorité haute - meilleur résultat)
Ces APIs cherchent des photos réelles dans des banques d'images gratuites:

#### **Unsplash** (Recommandé ⭐⭐⭐)
- Photos de très haute qualité
- 100% gratuit, illimité
- [Créer une clé API](https://unsplash.com/oauth/applications)
- Configuration:
  ```bash
  export UNSPLASH_API_KEY="votre_clé_ici"
  ```

#### **Pexels**
- Excellent banque de photos gratuites
- 100% gratuit, illimité
- [Créer une clé API](https://www.pexels.com/api/)
- Configuration:
  ```bash
  export PEXELS_API_KEY="votre_clé_ici"
  ```

#### **Pixabay**
- Grande banque d'images libres
- 100% gratuit, illimité
- [Créer une clé API](https://pixabay.com/api/)
- Configuration:
  ```bash
  export PIXABAY_API_KEY="votre_clé_ici"
  ```

### 2. 🤖 **Génération d'images IA** (Fallback)

#### **Pollinations.ai** (Automatique)
- ✅ **Pas de clé API requise**
- Rapide et gratuit
- Génère des images IA
- Parfait pour les recettes sans équivalent réel

#### **Replicate** (Optionnel)
- Stable Diffusion XLSD SDXL
- Meilleure qualité IA
- 100 images gratuites/mois
- [Créer un compte](https://replicate.com)
- Configuration:
  ```bash
  export REPLICATE_API_TOKEN="votre_token_ici"
  ```

---

## 🚀 Configuration Rapide

### Option 1: Configuration Minimale (Recommandé pour démarrer)
```bash
# Juste Unsplash + Pollinations (pas de clé pour Pollinations)
export UNSPLASH_API_KEY="ucXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Option 2: Configuration Complète (Meilleur résultat)
```bash
# Toutes les clés pour couvrir tous les cas
export UNSPLASH_API_KEY="ucXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export PEXELS_API_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export PIXABAY_API_KEY="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
export REPLICATE_API_TOKEN="r8_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### Option 3: Fichier `.env` (Déploiement)
```bash
# .env
UNSPLASH_API_KEY=ucXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PEXELS_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
PIXABAY_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
REPLICATE_API_TOKEN=r8_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 📝 Comment obtenir les clés API

### 🔗 Unsplash
1. Aller à [unsplash.com/oauth/applications](https://unsplash.com/oauth/applications)
2. Créer une nouvelle application
3. Copier `Access Key`
4. Utiliser comme `UNSPLASH_API_KEY`

### 🔗 Pexels
1. Aller à [pexels.com/api](https://www.pexels.com/api/)
2. Vous connecter avec un compte gratuit
3. Copier votre clé API
4. Utiliser comme `PEXELS_API_KEY`

### 🔗 Pixabay
1. Aller à [pixabay.com/api](https://pixabay.com/api/)
2. Créer un compte gratuit
3. Aller à votre dashboard
4. Copier votre clé API
5. Utiliser comme `PIXABAY_API_KEY`

### 🔗 Replicate
1. Aller à [replicate.com](https://replicate.com)
2. Créer un compte gratuit
3. Copier votre API token depuis `Account settings`
4. Utiliser comme `REPLICATE_API_TOKEN`

---

## 🧪 Test des APIs

Vérifier que les images s'affichent correctement:

```bash
# Test simple en Python
python3 << 'EOF'
from src.utils.image_generator import generer_image_recette

# Test avec une recette classique
url = generer_image_recette(
    "Pâtes Carbonara",
    "Recette italienne classique avec œufs et guanciale",
    type_plat="déjeuner"
)

if url:
    print(f"✅ Image générée: {url}")
else:
    print("❌ Erreur de génération")
EOF
```

---

## 💰 Coûts

| API | Coût | Limite |
|-----|------|--------|
| **Unsplash** | 🟢 Gratuit | Illimité |
| **Pexels** | 🟢 Gratuit | Illimité |
| **Pixabay** | 🟢 Gratuit | Illimité |
| **Pollinations** | 🟢 Gratuit | Illimité |
| **Replicate** | 🟡 Gratuit + payant | 100 free/mois |

---

## 📊 Résultats Attendus

### Avec Unsplash/Pexels/Pixabay:
- ✅ **Photos réelles** de haute qualité
- ✅ **Instantané** (< 1 sec)
- ✅ **100% fiable** pour les plats populaires

### Avec Pollinations (fallback):
- ✅ **Images générées par IA**
- ✅ **Très rapide** (2-3 sec)
- ✅ **Bon pour les recettes uniques**

---

## 🐛 Dépannage

### "Impossible de générer une image"
1. ✅ Vérifier les clés API dans les variables d'environnement
2. ✅ Vérifier la connexion internet
3. ✅ Vérifier les logs: `grep "Image" logs/app.log`

### Qualité d'image faible
1. ✅ Ajouter une description à la recette
2. ✅ Vérifier le type_plat (petit_déjeuner, déjeuner, etc.)
3. ✅ Utiliser Unsplash pour les meilleurs résultats

### API bloquée/limitée
- Unsplash: max 50 req/hour (gratuit) → utiliser clé avec app registrée
- Pexels: 200 req/hour
- Pixabay: 100 req/hour
- Replicate: 100 générations/mois gratuit

---

## 🎨 Exemple d'utilisation dans le code

```python
from src.utils.image_generator import generer_image_recette

# Générer une image pour une recette
url = generer_image_recette(
    nom_recette="Tarte Tatin",
    description="Délicieuse tarte aux pommes caramélisées",
    ingredients_list=[
        {"nom": "pommes", "quantite": 4, "unite": "pcs"},
        {"nom": "sucre", "quantite": 100, "unite": "g"},
    ],
    type_plat="dessert"
)

# url contient soit:
# - Une URL Unsplash/Pexels (photo réelle)
# - Une URL Pollinations (image IA)
# - None (si pas de clé et pas d'accès internet)

if url:
    st.image(url, caption="Tarte Tatin")
```

---

## 🌟 Recommandations

1. **Au minimum**: Configurer **Unsplash** (meilleur rapport qualité/gratuité)
2. **Optimal**: Avoir au moins 2 APIs (couverture maximum)
3. **Production**: Configurer toutes les clés pour la meilleure couverture

---

**Dernière mise à jour**: 17 janvier 2026
