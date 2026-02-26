# 🎤 Guide Commandes Vocales

Contrôlez Assistant Matanne à la voix pour des actions rapides sans toucher le clavier.

## 🎯 Concept

Les commandes vocales permettent de:

- Ajouter rapidement des articles à la liste de courses
- Ajouter des articles à l'inventaire
- Rechercher des recettes
- Naviguer entre les modules

**Idéal quand vous avez les mains occupées en cuisine!**

## 🚀 Accès

1. Allez dans **🛠️ Utilitaires > 🎤 Commandes Vocales**
2. Ou utilisez le bouton 🎤 dans la barre latérale

## 📋 Commandes supportées

### 📝 Liste de courses

```
"Ajouter lait à la liste"
"Mets des tomates sur la liste"
"Il me faut du pain"
"Courses: 2kg pommes de terre"
```

### 📦 Inventaire

```
"Ajouter du sel au stock"
"J'ai 3 yaourts dans le frigo"
"On a du riz dans le placard"
```

### 🔍 Recherche de recettes

```
"Cherche une recette de lasagnes"
"Comment faire une quiche?"
"Trouve-moi une recette de gâteau au chocolat"
```

### ↗️ Navigation

```
"Va aux recettes"
"Ouvre l'inventaire"
"Affiche le planning"
```

## 🎙️ Comment ça marche

### Avec microphone (Streamlit 1.40+)

1. Cliquez sur le bouton **🎤 Cliquez et parlez**
2. Autorisez l'accès au microphone
3. Prononcez votre commande clairement
4. La transcription s'affiche automatiquement
5. Cliquez **▶️ Exécuter** pour valider

### Saisie textuelle (fallback)

Si le microphone n'est pas disponible:

1. Tapez votre commande dans le champ texte
2. Cliquez **▶️ Exécuter**

## 💡 Astuces pour une meilleure reconnaissance

### ✅ Bonnes pratiques

- Parlez clairement et à un rythme normal
- Utilisez des phrases simples
- Précisez les quantités si nécessaire
- Attendez le signal avant de parler

### ❌ À éviter

- Parler trop vite
- Bruit de fond important
- Commandes trop complexes
- Plusieurs actions dans une phrase

## 📊 Exemples détaillés

### Ajouter aux courses avec quantité

| Vous dites                            | Résultat       |
| ------------------------------------- | -------------- |
| "Ajouter 2 litres de lait à la liste" | Lait: 2L       |
| "Mets 500g de farine"                 | Farine: 500g   |
| "Il me faut 6 œufs"                   | Œufs: 6 unités |

### Navigation rapide

| Vous dites             | Destination         |
| ---------------------- | ------------------- |
| "Va aux recettes"      | Module Recettes     |
| "Ouvre le planning"    | Planificateur repas |
| "Affiche l'inventaire" | Gestion stocks      |

## ⚙️ Configuration

### Paramètres disponibles

- **Langue**: Français (par défaut)
- **Sensibilité micro**: Ajustable dans Paramètres
- **Confirmation automatique**: Oui/Non

### Intégrations

Les commandes vocales s'intègrent avec:

- 🛒 Module Courses
- 📦 Module Inventaire
- 🍽️ Module Recettes
- ↗️ Navigation globale

## 🔧 Dépannage

### Le microphone ne fonctionne pas

1. Vérifiez que le navigateur a accès au micro
2. Utilisez un navigateur compatible (Chrome/Firefox)
3. Essayez de rafraîchir la page
4. Utilisez le mode saisie textuelle en fallback

### La transcription est incorrecte

1. Parlez plus lentement
2. Réduisez le bruit ambiant
3. Rapprochez-vous du microphone
4. Corrigez manuellement si nécessaire

### La commande n'est pas reconnue

1. Utilisez les formulations suggérées
2. Simplifiez votre phrase
3. Vérifiez la liste des commandes supportées

## 🔮 Fonctionnalités futures

- Reconnaissance de plusieurs langues
- Commandes personnalisées
- Apprentissage de vos habitudes
- Intégration avec plus de modules

## 🔗 Liens utiles

- [Guide Courses](../cuisine/courses.md)
- [Guide Inventaire](../cuisine/inventaire.md)
- [Guide Scanner Codes-barres](barcode.md)
