# 📚 Guide Complet du Module Recettes

## Vue d'ensemble

Le module **Recettes** d'Assistant MaTanne est une plateforme complète de gestion des recettes de cuisine avec:
- 📋 Catalogue de 50 recettes standards
- ✍️ Création manuelle de recettes
- 🤖 Génération IA de recettes personnalisées
- 🔍 Recherche et filtrage avancé
- 📊 Nutrition complète
- 🤖 Compatibilité multi-robots

## Navigation Principale

### 📋 Onglet 1: Liste des Recettes

#### Recherche et Filtres Rapides
Toujours visibles en haut:
- **Type de repas**: Petit-déj, Déjeuner, Dîner, Goûter, Dessert, Entrée
- **Difficulté**: Facile, Moyen, Difficile
- **Temps max**: Slider de 0 à 300 minutes

#### Filtres Avancés
Cliquez sur **"⚙️ Filtres avancés"** pour accéder à:

**Scores Nutritionnels:**
- 🌱 Score bio min (0-100%)
- 📍 Score local min (0-100%)

**Robots Compatibles:**
- Cookeo
- Monsieur Cuisine
- Airfryer
- Multicooker
(Cochez ceux que vous avez)

**Caractéristiques:**
- ⚡ Rapide (< 30min)
- 💪 Équilibré
- ❄️ Congélable

#### Carte Recette
Pour chaque recette affichée:
```
╔══════════════════════════════════════╗
║ Nom Recette                          ║
║ Description courte...                ║
║                                      ║
║ 🌱 Bio • 📍 Local • ⚡ Rapide       ║
║ 🌱 Bio 85% | 📍 Local 75%            ║
║ Compatible: 🤖 🌪️ ⏲️              ║
║                                      ║
║ ⏱️ 30min | 👥 4 | 🔥 250kcal        ║
║                                      ║
║ [📊 Nutrition] [Voir détails]       ║
╚══════════════════════════════════════╝
```

**Légende des badges:**
- 🟢 Difficulté Facile
- 🟡 Difficulté Moyen
- 🔴 Difficulté Difficile
- 🌱 Bio / Organique
- 📍 Local / Régional
- ⚡ Rapide à préparer
- 💪 Nutritionnellement équilibré
- ❄️ Peut être congelée

**Robots:**
- 🤖 Cookeo
- 👨‍🍳 Monsieur Cuisine
- 🌪️ Airfryer
- ⏲️ Multicooker

### 📄 Onglet 2: Ajouter Manuellement

Formulaire complet pour créer votre propre recette:

**Section 1 - Informations Basiques:**
- Nom de la recette
- Description courte
- Type de repas
- Difficulté (facile/moyen/difficile)
- Portions

**Section 2 - Timings:**
- Temps de préparation (min)
- Temps de cuisson (min)

**Section 3 - Ingrédients (Dynamique)**
- Ajouter autant d'ingrédients que nécessaire
- Pour chaque ingrédient: Nom, Quantité, Unité

**Section 4 - Étapes (Dynamique)**
- Ajouter autant d'étapes que nécessaire
- Description détaillée de chaque étape

**Section 5 - Caractéristiques:**
- ☑️ Rapide (< 30 min)
- ☑️ Équilibré
- ☑️ Compatible bébé
- ☑️ Bio
- ☑️ Local
- ☑️ Peut être congelée

**Section 6 - Scores (Optionnel):**
- Score bio (0-100%)
- Score local (0-100%)

**Section 7 - Robots (Optionnel):**
- ☑️ Cookeo
- ☑️ Monsieur Cuisine
- ☑️ Airfryer
- ☑️ Multicooker

**Section 8 - Nutrition (Optionnel):**
- Calories
- Protéines (g)
- Lipides (g)
- Glucides (g)

### 🤖 Onglet 3: Générer par IA

Laissez Claude générer des recettes personnalisées:

**Entrées IA:**
- Nombre de suggestions (3-5 par défaut)
- Critères préférés (rapide, équilibré, bio, etc.)

**Processus:**
1. IA génère 3-5 suggestions
2. Chaque suggestion en **expander** (accordéon)
3. Cliquez pour voir détails
4. Bouton **"➕ Ajouter à ma collection"**
5. Recette sauvegardée dans votre base

## Affichage des Détails

Quand vous cliquez sur **"Voir détails"**, écran complet:

### En-tête
```
╔════════════════════════════════════════════╗
║ Nom Recette                           🔴  ║
║ 🌱 Bio • 📍 Local • ⚡ Rapide • 💪      ║
╚════════════════════════════════════════════╝
```

### Scores et Compatibilité
```
🌱 Score Bio: 85%  |  📍 Score Local: 80%

🤖 Compatible avec:
🤖 Cookeo | 👨‍🍳 Monsieur Cuisine | 🌪️ Airfryer
```

### Infos Principales
```
⏱️ Préparation: 30 min  |  🍳 Cuisson: 45 min
👥 Portions: 4         |  🔥 Calories: 250kcal
```

### Nutrition (Expander)
```
Cliquez sur "📊 Nutrition détaillée" pour voir:
├─ Calories: 250 kcal
├─ Protéines: 25g
├─ Lipides: 8g
└─ Glucides: 30g
```

### Description
```
📝 Description
Texte descriptif complet de la recette...
```

### Ingrédients
```
🛒 Ingrédients
┌────────────────┬──────────┬──────┐
│ Ingrédient     │ Quantité │ Unité│
├────────────────┼──────────┼──────┤
│ Farine         │ 250      │ g    │
│ Œufs           │ 3        │      │
│ Lait           │ 500      │ ml   │
└────────────────┴──────────┴──────┘
```

### Étapes
```
👨‍🍳 Étapes de préparation
Étape 1: Mélanger la farine et les œufs
Étape 2: Ajouter le lait progressivement
Étape 3: Laisser reposer 30 minutes
...
```

## Filtres - Exemples Pratiques

### ✅ Exemple 1: Repas Rapide & Équilibré
```
Type: Tous
Difficulté: Facile
Temps max: 30
Score bio: 0
Score local: 0
Rapide: ✓
Équilibré: ✓
Robots: (aucun)
→ Affiche toutes les recettes < 30min équilibrées
```

### ✅ Exemple 2: Recettes Locales/Bio
```
Type: Tous
Score bio: 80%
Score local: 75%
→ Affiche recettes très locales ET bio
```

### ✅ Exemple 3: Compatibles avec mon Cookeo
```
Robots: ✓ Cookeo
→ Affiche seulement recettes Cookeo
```

### ✅ Exemple 4: Déjeuner Congélable
```
Type: Déjeuner
Temps max: 60
Congélable: ✓
→ Recettes de déj congélables < 60min
```

## Significances des Scores

### 🌱 Score Bio
- **0-25%**: Produits non-bio
- **25-50%**: Peu d'ingrédients bio
- **50-75%**: Majoritairement bio
- **75-100%**: 100% ingrédients bio

### 📍 Score Local
- **0-25%**: Produits importés
- **25-50%**: Peu de produits locaux
- **50-75%**: Majoritairement local
- **75-100%**: 100% ingrédients locaux

## Robots Expliqués

### 🤖 Cookeo (Moulinex)
- Autocuiseur électrique
- Recettes rapides (10-30min)
- Idéal pour: Ragouts, pâtes, riz
- Restrictions: Pas de friture, grillage limité

### 👨‍🍳 Monsieur Cuisine
- Robot multi-fonction
- Cuisson, vapeur, cuisson lente
- Idéal pour: Soupes, purées, plats préparés
- Restrictions: Volumétrie limitée

### 🌪️ Airfryer
- Cuisson par air chaud
- Recettes croustillantes et saines
- Idéal pour: Frites, ailes, nuggets
- Restrictions: Peu adapté aux liquides

### ⏲️ Multicooker
- Cuisine lente + pression + sauté
- Polyvalent et flexible
- Idéal pour: Tous types de plats
- Restrictions: Aucune

## Tags Expliqués

### ⚡ Rapide
Recette complète en < 30 minutes (prep + cuisson)

### 💪 Équilibré
Ratio correct de protéines/glucides/lipides
- Protéines: 20-30%
- Glucides: 40-50%
- Lipides: 20-30%

### ❄️ Congélable
Peut être congelée et dégélée sans problème
- Bonne pour: Batch cooking
- Durée: 2-3 mois

### 👨‍👧‍👦 Compatible Bébé
Sans allergènes majeurs, digestion facile

## Astuces d'Utilisation

### 💡 Créer une Semaine Type
1. Allez à "Liste"
2. Filtrez par type (petit-déj, déjeuner, dîner)
3. Sélectionnez vos favoris
4. Notez-les ou marquez-les comme favoris

### 💡 Batch Cooking
1. Filtrez: "Congélable: ✓"
2. Filtrez: "Bio: 75%+"
3. Choisissez des recettes de 4-6 portions
4. Préparez le week-end, congelez

### 💡 Repas Rapides
1. Filtrez: "Temps max: 30"
2. Filtrez: "Rapide: ✓"
3. Choisissez selon vos robots disponibles

### 💡 Repas Santé
1. Filtrez: "Équilibré: ✓"
2. Filtrez: "Calories < 300" (optionnel)
3. Vérifiez nutrition en détails

### 💡 Cuisiner avec Robot
1. Allez à "Filtres avancés"
2. Cochez votre robot
3. Toutes les recettes affichées sont compatibles

## Données Nutritionnelles

### Où les voir
- Listing: Affichage rapide en "🔥 250kcal"
- Détails: Section "📊 Nutrition détaillée"

### Interprétation
```
Besoins quotidiens (moyenne):
├─ Calories: 2000 kcal
├─ Protéines: 50-60g
├─ Lipides: 50-70g
└─ Glucides: 250-300g
```

### Pour régimes spécifiques
- **Hyperprotéiné**: Filtrez protéines > 25g
- **Faible carb**: Filtrez glucides < 20g
- **Light**: Filtrez calories < 200

## Bibliothèque Standard

Au démarrage, 50 recettes sont pré-chargées:

**Petit-déjeuner:** 6 recettes
- Crêpes, omelettes, œufs, pain grillé, etc.

**Déjeuner/Dîner:** 20 recettes
- Poulet rôti, pâtes, poisson, légumes, etc.

**Goûter:** 15 recettes
- Yaourt, fruits, fromage blanc, noix, etc.

**Accompagnements:** 9 recettes
- Riz, purée, lentilles, compote, etc.

## Modification et Suppression

### Éditer une recette
- (À ajouter) Bouton "✏️ Éditer" sur détails

### Supprimer une recette
- (À ajouter) Bouton "🗑️ Supprimer" avec confirmation

## FAQ

**Q: Peut-je modifier les recettes standard?**
A: Oui, vous pouvez les dupliquer et les modifier.

**Q: Comment partager une recette?**
A: (À ajouter) Bouton partage avec email/lien

**Q: Puis-je ajouter des recettes en masse?**
A: Oui, par import JSON (pour admin)

**Q: Les calories sont-elles exactes?**
A: Base Ciqual, peuvent varier selon marques

**Q: Les scores bio/local sont arbitraires?**
A: Basés sur ingrédients typiques, ajustables manuellement

**Q: Puis-je avoir des recettes sans scores?**
A: Oui, laischez blanc et n'appliquez pas le filtre

## Support

Pour problèmes ou suggestions:
- Contactez l'admin de l'app
- Proposez de nouvelles recettes
- Signalez erreurs de nutrition

---

**Version:** 1.0
**Dernière mise à jour:** Phase 4
**Recettes disponibles:** 50+
**Status:** ✅ Prêt pour utilisation
