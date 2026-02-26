# 🍳 Guide Batch Cooking

Le module Batch Cooking vous permet de préparer tous vos repas de la semaine en une seule session de cuisine efficace.

## 🎯 Concept

Le **batch cooking** (ou "meal prep") consiste à:

1. Planifier vos repas de la semaine
2. Préparer tout en une seule session (dimanche matin par exemple)
3. Stocker les préparations (frigo/congélateur)
4. N'avoir plus qu'à réchauffer/assembler chaque jour

## 📋 Étapes d'utilisation

### 1. Préparer la session

1. Allez dans **🍽️ Cuisine > 🍳 Batch Cooking**
2. Dans l'onglet **📋 Préparer**:
   - Choisissez le type de session (Dimanche Solo, Express, Familial avec Jules)
   - Sélectionnez la date et l'heure de début
   - Vérifiez les recettes du planning

3. Cliquez sur **🚀 Générer les instructions de batch**
   - L'IA analyse vos recettes
   - Génère les étapes optimisées
   - Calcule les temps de préparation

### 2. Session de cuisson

Dans l'onglet **👩‍🍳 Session Batch**:

- **Timeline**: Vue chronologique de toutes les étapes
- **Conseils d'organisation**: Astuces pour être efficace
- **Moments Jules**: Si activé, périodes calmes pour bébé
- **Recettes détaillées**: Ingrédients et étapes par recette

#### Métriques affichées

- ⏱️ Durée estimée
- 🕐 Heure de début/fin
- 📦 Instructions de stockage

### 3. Exécution Live (NOUVEAU!)

L'onglet **🎬 Exécution Live** utilise `st.status()` pour:

- Suivre la progression en temps réel
- Marquer chaque étape comme terminée
- Voir le temps restant
- Recevoir des notifications entre les étapes

```
▶️ Démarrer le Batch Cooking
   ↓
📋 Phase 1: Préparation (vérification ingrédients)
   ↓
👩‍🍳 Phase 2: Cuisson & Préparation (étapes chronométrées)
   ↓
📦 Phase 3: Stockage (rangement frigo/congélateur)
   ↓
✅ Terminé!
```

### 4. Finitions Jour J

Dans l'onglet **🍽️ Finitions Jour J**:

- Instructions pour chaque jour de la semaine
- Ce qu'il reste à faire (réchauffer, assembler, assaisonner)
- Temps de préparation final (< 15 min généralement)

## 💡 Types de sessions

| Type                  | Durée | Pour qui                        |
| --------------------- | ----- | ------------------------------- |
| **Dimanche Solo**     | 2-3h  | Une personne, cuisine intensive |
| **Dimanche Familial** | 3-4h  | Avec Jules, pauses intégrées    |
| **Express**           | 1h    | Préparations rapides uniquement |
| **Soirée**            | 1.5h  | Après le travail                |

## 🤖 Conseils IA

L'IA génère des conseils personnalisés:

- Ordre optimal des tâches
- Parallélisation (ex: pendant que X cuit, préparer Y)
- Utilisation des robots (Cookeo, Air Fryer...)
- Moments calmes si bébé présent

## 📦 Stockage

Chaque recette inclut:

- **Où stocker**: Frigo ou Congélateur
- **Durée de conservation**: En jours
- **Contenants recommandés**: Boîtes, sachets...

## 🛒 Liste de courses

Bouton **🛒 Envoyer aux courses**:

- Génère automatiquement la liste d'ingrédients
- Agrège les quantités (ex: 3 recettes avec oignons → total)
- Envoyée vers le module Courses

## ⌨️ Raccourcis

| Action                   | Raccourci    |
| ------------------------ | ------------ |
| Générer les instructions | `Ctrl+G`     |
| Démarrer l'exécution     | `Ctrl+Enter` |
| Imprimer                 | `Ctrl+P`     |

## ❓ FAQ

**Q: Puis-je modifier les étapes générées?**
R: Oui, chaque étape est éditable avant l'exécution.

**Q: Comment gérer les imprévus?**
R: L'exécution live permet de passer des étapes ou ajouter des pauses.

**Q: Les temps sont-ils précis?**
R: Les temps sont estimés. L'IA apprend de vos sessions passées.

## 🔗 Liens utiles

- [Guide Planificateur de Repas](planificateur.md)
- [Guide Courses](courses.md)
- [Guide Inventaire](inventaire.md)
