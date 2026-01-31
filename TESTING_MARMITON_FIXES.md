# 📝 GUIDE POUR TESTER LES FIXES D'IMPORT MARMITON

## Lancer l'application

```bash
cd d:\Projet_streamlit\assistant_matanne
streamlit run src/app.py
```

## Étapes pour tester

### 1. Naviguer à l'onglet "Cuisine" → "Recettes"

Dans le menu latéral:

- Cliquez sur "🍽️ Cuisine"
- Puis "📖 Recettes"

### 2. Aller à l'onglet "Import"

Vous verrez 3 onglets:

- **Liste** (recettes existantes)
- **Ajouter manuellement** (création manuelle)
- **📥 Importer** ← CLIQUEZ ICI

### 3. Tester l'import URL

#### Test 1: Vérifier le bouton clair

- Vous devriez voir: **"📊 Extraire la recette du site"** (plus clair qu'avant)

#### Test 2: URL Marmiton Bricks au thon

1. Cliquez sur l'onglet "🌐 URL/Site Web"
2. Collez cette URL:
   ```
   https://www.marmiton.org/recettes/recette_bricks-au-thon-faciles_92390.aspx
   ```
3. Cliquez sur **"📊 Extraire la recette du site"**

#### Test 3: Vérifier l'extraction

Le formulaire d'aperçu doit afficher:

**Données correctes:**

- ✅ Nom: "Bricks au thon faciles"
- ✅ Type de repas: Devrait être "dîner" (détecté automatiquement, pas "petit_déjeuner"!)
- ✅ Temps préparation: 15 min (pas 0!)
- ✅ Temps cuisson: 10 min (pas 0!)
- ✅ Image: Devrait afficher une URL Afcdn.com
  - Vous pouvez voir le lien (modifiable)
  - Bouton pour uploader une autre image
- ✅ Ingrédients: 8 items corrects:
  - "10 feuilles de brick"
  - "280 g de thon au naturel"
  - "80 g d'oignon coupés"
  - (etc...)
- ✅ Étapes: 5 étapes correctes avec texte complet

#### Test 4: Vérifier le type de repas intelligent

1. Essayez avec d'autres recettes pour vérifier la détection:
   - Recette dessert → devrait détecter "dessert"
   - Recette petit-déj → devrait détecter "petit_déjeuner"
   - Recette avec entrée → devrait détecter "apéritif"

#### Test 5: Tester l'image upload

1. Dans le formulaire d'aperçu, section "🖼️ Image de la recette":
   - L'URL extraite est affichée (modifiable)
   - Vous pouvez cliquer sur "Choisissez une image" pour uploader une autre
   - Testez: upload une image locale (jpg/png)

#### Test 6: Vérifier la sauvegarde

1. Cliquez sur **"✅ Importer cette recette"**
2. Vous devriez voir:
   - ✅ Message "Recette 'Bricks au thon faciles' importée avec succès!"
   - ✅ Ballons d'animation
   - ✅ **IMPORTANT: Rester sur l'onglet import** (pas de redirection vers la liste!)

#### Test 7: Vérifier la recette sauvegardée

1. Allez à l'onglet "Liste"
2. Cherchez "Bricks au thon faciles"
3. Vérifiez:
   - ✅ Nom correct
   - ✅ Type de repas correct ("dîner", pas "petit_déjeuner")
   - ✅ Temps affichés (15 min + 10 min)
   - ✅ Ingrédients présents
   - ✅ Étapes présentes
   - ✅ Image affichée (si extraite ou uploadée)

## Cas de test supplémentaires

### Test avec autres sites

Essayez d'autres recettes sur:

- ✅ RecettesTin
- ✅ CuisineAZ
- ✅ Marmiton (autres recettes)

### Test des formats de temps

L'extracteur supporte maintenant:

- "PT15M" (ISO 8601)
- "PT1H30M" (ISO 8601)
- "1h 30" (français)
- "1 heure 30 minutes" (français)
- "30min" (français court)

## Problèmes potentiels et solutions

### Problème: L'image ne s'affiche pas

**Solution**: Vérifiez que:

1. L'URL commence par "https://"
2. L'URL est absolue (pas relative)
3. Le site n'a pas bloqué l'accès à l'image

### Problème: Type de repas incorrect

**Solution**: Le type est détecté intelligemment mais reste modifiable:

1. Vérifiez le nom de la recette
2. Si la détection n'est pas correcte, changez manuellement dans le selectbox

### Problème: Ingrédients mal extraits

**Solution**: Cela dépend du site:

1. Marmiton: Utilise JSON-LD (très fiable)
2. Autres sites: Peuvent avoir des structures différentes
3. Si incorrect, modifiez manuellement les ingrédients

### Problème: Tab redirige à la liste

**Solution**: Ce problème a été CORRIGÉ

1. La fonction `st.rerun()` a été supprimée
2. Après import, vous restez sur l'onglet import

## Architecture des changements

```
recettes_import.py (UI)
├─ Bouton clarifié: "📊 Extraire la recette du site"
├─ Détection type_repas intelligent (analyse nom + description)
├─ Image uploader dans le preview
└─ St.rerun() supprimé (reste sur tab)

recipe_importer.py (Backend)
├─ JSON-LD schema.org (priorité #1 - très fiable)
├─ Image extraction (og:image > twitter:image)
├─ Time parser amélioré (ISO 8601 + français)
└─ Fallback HTML (pour sites sans JSON-LD)
```

## Fichiers modifiés

- `src/domains/cuisine/ui/recettes_import.py` (UI)
- `src/utils/recipe_importer.py` (Backend)

## Support

Si vous rencontrez des problèmes:

1. Vérifiez que BeautifulSoup4 et requests sont installés
2. Vérifiez la connexion internet (nécessaire pour télécharger les pages)
3. Vérifiez que l'URL est correcte et accessible
4. Consultez les logs Streamlit (terminal) pour les détails d'erreur
