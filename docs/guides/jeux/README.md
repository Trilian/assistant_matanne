# 🎮 Guide Module Jeux

> Ce guide couvre le module jeux dans MaTanne : paris sportifs, Loto et Euromillions.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Paris sportifs](#paris-sportifs)
3. [Loto](#loto)
4. [Euromillions](#euromillions)
5. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Jeux** permet de suivre et gérer les activités de jeux de hasard et paris sportifs de manière organisée, avec un suivi des gains/pertes et des statistiques.

**URL** : `/jeux`  
**Service backend** : `src/services/jeux/`  
**Route API** : `src/api/routes/jeux.py` (`/api/v1/jeux`)

> ⚠️ Ce module est conçu pour un usage personnel de suivi. MaTanne ne réalise pas de paris réels — il s'agit uniquement d'un outil de gestion et d'analyse.

---

## Paris sportifs

### Fonctionnalités

- Saisie des paris (événement, cote, mise, résultat)
- Calcul automatique des gains/pertes
- Tableau de bord financier (total misé, total gagné, ROI)
- Historique filtrable par sport, statut, période
- Statistiques : taux de réussite, mise moyenne, meilleure cote
- Import CSV depuis le fichier `data/parisSportifs - Recapitulatif.csv`

### Usage

```
/jeux/paris
```

### Structure d'un pari

| Champ        | Type    | Description                               |
|-------------|---------|-------------------------------------------|
| `evenement`  | string  | Description du match/événement            |
| `sport`      | string  | Sport concerné (football, tennis…)        |
| `mise`       | decimal | Montant misé                              |
| `cote`       | decimal | Cote offerte                              |
| `gain_potentiel` | decimal | Calculé automatiquement (mise × cote) |
| `statut`     | enum    | `en_attente` / `gagné` / `perdu`          |
| `date`       | date    | Date du pari                              |

### Import CSV

```bash
# Format attendu : data/TEMPLATE_IMPORT.csv
python scripts/db/import_recettes.py --file data/parisSportifs\ -\ Recapitulatif.csv --type paris
```

---

## Loto

### Fonctionnalités

- Saisie des grilles jouées (6 numéros + numéro chance)
- Comparaison automatique avec les résultats officiels
- Historique des participations et gains
- Statistiques des numéros les plus joués

### Usage

```
/jeux/loto
```

### Structure d'une grille Loto

| Champ        | Type         | Description                      |
|-------------|--------------|----------------------------------|
| `numeros`    | int[5]       | 5 numéros entre 1 et 49          |
| `numero_chance` | int       | Numéro chance entre 1 et 10      |
| `mise`       | decimal      | Montant joué                     |
| `date_tirage` | date        | Date du tirage                   |
| `gains`      | decimal      | Gains obtenus (0 si perdant)     |

---

## Euromillions

### Fonctionnalités

- Saisie des grilles Euromillions (5 numéros + 2 étoiles)
- Suivi des participations et résultats
- Statistiques de fréquence des numéros tirés
- Historique avec calcul du solde global

### Usage

```
/jeux/euromillions
```

### Structure d'une grille Euromillions

| Champ      | Type       | Description                         |
|-----------|------------|-------------------------------------|
| `numeros`  | int[5]     | 5 numéros entre 1 et 50             |
| `etoiles`  | int[2]     | 2 étoiles entre 1 et 12             |
| `mise`     | decimal    | Montant joué                        |
| `date_tirage` | date   | Date du tirage                      |
| `gains`    | decimal    | Gains obtenus                       |

---

## API Reference

### Endpoints principaux

| Méthode | URL                           | Description                       |
|--------|-------------------------------|-----------------------------------|
| GET    | `/api/v1/jeux/paris`          | Lister les paris                  |
| POST   | `/api/v1/jeux/paris`          | Ajouter un pari                   |
| PUT    | `/api/v1/jeux/paris/{id}`     | Modifier un pari (résultat)       |
| GET    | `/api/v1/jeux/paris/stats`    | Statistiques paris                |
| GET    | `/api/v1/jeux/loto`           | Lister les grilles loto           |
| POST   | `/api/v1/jeux/loto`           | Ajouter une grille                |
| GET    | `/api/v1/jeux/euromillions`   | Lister les grilles euromillions   |
| POST   | `/api/v1/jeux/euromillions`   | Ajouter une grille                |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
