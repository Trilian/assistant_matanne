# 🍽️ Guide Module Cuisine

> Gérez vos recettes, planifiez les repas, organisez les courses et optimisez vos stocks depuis un seul module.

---

## Vue d'ensemble

Le module **Cuisine** centralise tout ce qui touche à l'alimentation de la famille :

| Sous-module | Accès | Description |
|-------------|-------|-------------|
| Recettes | Cuisine → Recettes | Bibliothèque de recettes avec recherche, tags et notes |
| Planning repas | Cuisine → Ma Semaine | Planification hebdomadaire avec suggestions IA |
| Courses | Cuisine → Courses | Listes de courses intelligentes |
| Frigo & Stock | Cuisine → Frigo & Stock | Inventaire avec dates de péremption |
| Batch Cooking | Cuisine → Batch Cooking | Sessions de préparation groupées |
| Anti-Gaspillage | — | Suggestions automatiques pour utiliser les restes |

---

## Recettes

### Consulter les recettes

1. Depuis le dashboard, cliquez sur **Cuisine** dans la sidebar
2. Cliquez sur **Recettes**
3. Parcourez la liste ou utilisez la **barre de recherche** pour filtrer par nom, ingrédient ou tag

<!-- Screenshot: Liste des recettes avec barre de recherche et filtres -->

### Ajouter une recette

1. Sur la page Recettes, cliquez sur **Ajouter une recette**
2. Remplissez le formulaire :
   - **Nom** de la recette
   - **Ingrédients** avec quantités
   - **Instructions** pas à pas
   - **Tags** (ex : « rapide », « végétarien », « Jules »)
   - **Temps de préparation** et **cuisson**
   - **Nombre de portions**
3. Cliquez sur **Enregistrer**

> **Astuce** : Vous pouvez importer une recette depuis une URL ou un PDF via le bouton **Importer**.

### Adapter une recette pour Jules

Les recettes sont automatiquement adaptées quand Jules est inclus dans le planning. L'IA génère une version « Jules » = pas salé, pas d'alcool, pas de morceaux durs — la recette est simplifiée/mixée selon l'âge.

<!-- Screenshot: Recette avec version Jules adaptée -->

---

## Planning repas

### Planifier la semaine

1. Allez dans **Cuisine → Ma Semaine**
2. Cliquez sur **Planifier la semaine** (ou utilisez le raccourci dashboard)
3. L'IA propose un planning équilibré basé sur :
   - Vos **préférences** alimentaires
   - Votre **inventaire** actuel (frigo & stock)
   - La **saisonnalité** des ingrédients
   - L'**historique** des repas récents (pour varier)
4. **Validez**, **modifiez** ou **remplacez** chaque repas
5. Cliquez sur **Valider le planning**

<!-- Screenshot: Planning hebdomadaire avec drag-and-drop -->

### Modifier un repas

- Cliquez sur un repas dans le planning
- Choisissez **Remplacer** pour que l'IA propose des alternatives
- Ou sélectionnez directement une recette depuis votre bibliothèque

### Générer les courses depuis le planning

1. Une fois le planning validé, cliquez sur **Générer les courses**
2. L'IA analyse les recettes et votre inventaire
3. Seuls les ingrédients **manquants** sont ajoutés à la liste
4. Validez la liste générée

---

## Courses

### Gérer une liste de courses

1. Allez dans **Cuisine → Courses**
2. Consultez la liste active
3. **Cochez** les articles achetés
4. **Ajoutez** un article manuellement via le champ de saisie

<!-- Screenshot: Liste de courses avec articles cochés et catégories -->

### Pré-remplissage intelligent

L'IA détecte les articles **toujours achetés** (lait, pain, etc.) et les pré-coche automatiquement dans votre liste. Vous pouvez :
- **Garder** les articles pré-cochés
- **Décocher** ceux dont vous n'avez pas besoin cette semaine

### Collaboration temps réel

Les listes de courses sont partagées en **temps réel** (WebSocket). Si votre partenaire modifie la liste depuis un autre appareil, les changements apparaissent instantanément.

### Prédictions d'achat

L'IA analyse votre historique d'achats et prédit les articles à acheter cette semaine selon :
- La **fréquence** habituelle d'achat
- Les **quantités** moyennes
- Le **jour** habituel de courses

---

## Frigo & Stock (Inventaire)

### Ajouter un article au stock

1. Allez dans **Cuisine → Frigo & Stock**
2. Cliquez sur **Ajouter**
3. Renseignez le **nom**, la **quantité**, la **date de péremption**
4. L'article apparaît dans votre inventaire

### Alertes péremption

L'application vérifie automatiquement les dates de péremption :
- **Alerte jaune** : expire dans les 3 prochains jours
- **Alerte rouge** : expiré

Les articles proches de l'expiration sont automatiquement suggérés dans le **module anti-gaspillage**.

<!-- Screenshot: Inventaire avec indicateurs de péremption -->

---

## Batch Cooking

### Créer une session de batch cooking

1. Allez dans **Cuisine → Batch Cooking**
2. Cliquez sur **Nouvelle session**
3. L'IA propose un plan optimisé pour préparer plusieurs repas en une session :
   - **Regroupement** des préparations similaires
   - **Ordre optimal** de cuisson
   - **Temps total** estimé
4. Suivez les étapes pas à pas

<!-- Screenshot: Plan de batch cooking avec timeline de préparation -->

---

## Anti-Gaspillage

Le module anti-gaspillage fonctionne automatiquement :
- Il détecte les articles proches de la péremption dans votre inventaire
- Il suggère des recettes utilisant ces ingrédients
- Les suggestions apparaissent sur le dashboard et dans le module Cuisine

---

## Flux en 3 clics

Les actions les plus courantes sont accessibles rapidement :

| Action | Chemin |
|--------|--------|
| « Qu'est-ce qu'on mange ? » | Dashboard → bouton rapide → suggestion IA → 1 clic pour valider |
| Planifier la semaine | Dashboard → Planifier semaine → IA génère → Valider |
| Ajouter aux courses | Depuis une recette → Ajouter aux courses |
| Voir les stocks | Cuisine → Frigo & Stock |

---

## Intégrations IA

| Fonctionnalité | Description |
|----------------|-------------|
| **Suggestion de recettes** | Basée sur inventaire, préférences et saisonnalité |
| **Planning adaptatif** | Adapté à la météo, l'énergie et le budget |
| **Score écologique** | Évalue l'empreinte écologique d'un repas |
| **Analyse nutritionnelle** | Analyse macro/micro-nutriments d'un repas |

