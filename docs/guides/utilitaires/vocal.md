# ?? Guide Commandes Vocales

Contr?lez Assistant Matanne ? la voix pour des actions rapides sans toucher le clavier.

## ?? Concept

Les commandes vocales permettent de:

- Ajouter rapidement des articles ? la liste de courses
- Ajouter des articles ? l'inventaire
- Rechercher des recettes
- Naviguer entre les modules

**Id?al quand vous avez les mains occup?es en cuisine!**

## ?? Acc?s

1. Allez dans **Outils > Commandes Vocales** (`/outils/vocal`)
2. Ou utilisez le bouton ?? dans la barre lat?rale

## ?? Commandes support?es

### ?? Liste de courses

```
"Ajouter lait ? la liste"
"Mets des tomates sur la liste"
"Il me faut du pain"
"Courses: 2kg pommes de terre"
```

### ?? Inventaire

```
"Ajouter du sel au stock"
"J'ai 3 yaourts dans le frigo"
"On a du riz dans le placard"
```

### ?? Recherche de recettes

```
"Cherche une recette de lasagnes"
"Comment faire une quiche?"
"Trouve-moi une recette de g?teau au chocolat"
```

### ?? Navigation

```
"Va aux recettes"
"Ouvre l'inventaire"
"Affiche le planning"
```

## ??? Comment ?a marche

### Avec microphone (Web Speech API)

1. Cliquez sur le bouton **?? Cliquez et parlez**
2. Autorisez l'acc?s au microphone
3. Prononcez votre commande clairement
4. La transcription s'affiche automatiquement
5. Cliquez **?? Ex?cuter** pour valider

### Saisie textuelle (fallback)

Si le microphone n'est pas disponible:

1. Tapez votre commande dans le champ texte
2. Cliquez **?? Ex?cuter**

## ?? Astuces pour une meilleure reconnaissance

### ? Bonnes pratiques

- Parlez clairement et ? un rythme normal
- Utilisez des phrases simples
- Pr?cisez les quantit?s si n?cessaire
- Attendez le signal avant de parler

### ? ? ?viter

- Parler trop vite
- Bruit de fond important
- Commandes trop complexes
- Plusieurs actions dans une phrase

## ?? Exemples d?taill?s

### Ajouter aux courses avec quantit?

| Vous dites                            | R?sultat       |
| ------------------------------------- | -------------- |
| "Ajouter 2 litres de lait ? la liste" | Lait: 2L       |
| "Mets 500g de farine"                 | Farine: 500g   |
| "Il me faut 6 ?ufs"                   | ?ufs: 6 unit?s |

### Navigation rapide

| Vous dites             | Destination         |
| ---------------------- | ------------------- |
| "Va aux recettes"      | Module Recettes     |
| "Ouvre le planning"    | Planificateur repas |
| "Affiche l'inventaire" | Gestion stocks      |

## ?? Configuration

### Param?tres disponibles

- **Langue**: Fran?ais (par d?faut)
- **Sensibilit? micro**: Ajustable dans Param?tres
- **Confirmation automatique**: Oui/Non

### Int?grations

Les commandes vocales s'int?grent avec:

- ?? Module Courses
- ?? Module Inventaire
- ??? Module Recettes
- ?? Navigation globale

## ?? D?pannage

### Le microphone ne fonctionne pas

1. V?rifiez que le navigateur a acc?s au micro
2. Utilisez un navigateur compatible (Chrome/Firefox)
3. Essayez de rafra?chir la page
4. Utilisez le mode saisie textuelle en fallback

### La transcription est incorrecte

1. Parlez plus lentement
2. R?duisez le bruit ambiant
3. Rapprochez-vous du microphone
4. Corrigez manuellement si n?cessaire

### La commande n'est pas reconnue

1. Utilisez les formulations sugg?r?es
2. Simplifiez votre phrase
3. V?rifiez la liste des commandes support?es

## ?? Fonctionnalit?s futures

- Reconnaissance de plusieurs langues
- Commandes personnalis?es
- Apprentissage de vos habitudes
- Int?gration avec plus de modules

## ?? Liens utiles

- [Guide Cuisine](../cuisine/README.md) (courses, inventaire)
- [Guide Scanner Codes-barres](barcode.md)
