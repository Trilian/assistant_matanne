# 👨‍👩‍👦 Guide Module Famille

> Ce guide couvre le suivi familial dans MaTanne : développement de Jules, activités, budget, routines, album, contacts, journal, anniversaires, documents.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Jules — Suivi développement enfant](#jules--suivi-développement-enfant)
3. [Activités familiales](#activités-familiales)
4. [Budget familial](#budget-familial)
5. [Routines](#routines)
6. [Week-end](#week-end)
7. [Album photo](#album-photo)
8. [Contacts](#contacts)
9. [Journal](#journal)
10. [Anniversaires](#anniversaires)
11. [Documents](#documents)
12. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Famille** centralise le suivi du développement de l'enfant et la vie familiale.

**URL** : `/famille`  
**Service backend** : `src/services/famille/`  
**Route API** : `src/api/routes/famille.py` (`/api/v1/famille`)

---

## Jules — Suivi développement enfant

### Fonctionnalités

- Suivi des **jalons de développement** (motricité, langage, social) par rapport aux normes OMS
- **Courbes de croissance** (poids, taille, périmètre crânien) avec visualisation graphique
- **Carnet de santé** : vaccinations, consultations, ordonnances
- **Diversification alimentaire** : suivi des aliments introduits et réactions
- Suggestions IA personnalisées sur le développement
- Alertes sur les jalons en retard

### Usage

```
/famille/jules
```

### Données de référence

- `data/reference/normes_oms.json` — normes de croissance OMS (0-5 ans)
- `data/reference/calendrier_vaccinal_fr.json` — calendrier vaccinal France 2026

### Services IA

```python
from src.services.famille.jules_ai import JulesAIService
service = JulesAIService()
# Analyse développement et suggestions personnalisées
analyse = service.analyser_developpement(age_mois=18, jalons_atteints=[...])
```

---

## Activités familiales

### Fonctionnalités

- Planification et suivi des activités (sorties, sports, loisirs)
- Catégorisation (sport, culture, plein-air, créatif…)
- Association à des membres de la famille
- Vue calendrier des activités planifiées

### Usage

```
/famille/activites
```

---

## Budget familial

### Fonctionnalités

- Saisie des revenus et dépenses par catégorie
- Graphiques de répartition du budget (diagramme camembert)
- Suivi mensuel avec comparaison aux mois précédents
- Alertes quand les dépenses dépassent un budget défini
- Export CSV des transactions

### Usage

```
/famille/budget
```

### Composant graphique

```tsx
// src/composants/graphiques/camembert-budget.tsx
import CamembertBudget from "@/composants/graphiques/camembert-budget"

<CamembertBudget
  depenses={depensesParCategorie}
  totalBudget={2000}
/>
```

---

## Routines

### Fonctionnalités

- Définition des routines quotidiennes (matin, soir, semaine)
- Cases à cocher interactives pour valider chaque étape
- Suivi de la régularité (score de cohérence sur 30 jours)
- Routines dédiées enfant (bain, lecture, coucher) et adulte

### Usage

```
/famille/routines
```

---

## Week-end

### Fonctionnalités

- Suggestions d'activités pour le week-end générées par IA
- Basé sur la météo locale, la saison, l'âge de Jules
- Filtrage par rayon géographique et budget
- Sauvegarde des activités favorites

### Usage

```
/famille/weekend
```

### Service IA

```python
from src.services.famille.weekend_ai import WeekendAIService
service = WeekendAIService()
suggestions = service.suggerer_activites_weekend(
    météo="ensoleillé", rayon_km=30, budget=50
)
```

---

## Album photo

### Fonctionnalités

- Galerie photo organisée par date et tags
- Upload d'images (Supabase Storage)
- Légendes et commentaires
- Vue chronologique / vue mosaïque

### Usage

```
/famille/album
```

---

## Contacts

### Fonctionnalités

- Carnet de contacts familial (famille élargie, amis, professionnels de santé)
- Catégorisation (médecin, école, garderie, famille, amis)
- Recherche rapide
- Notes personnalisées par contact

### Usage

```
/famille/contacts
```

---

## Journal

### Fonctionnalités

- Journal de bord familial (texte libre, anecdotes, moments forts)
- Entrées associées à une date et un auteur
- Recherche dans les entrées passées
- Synthèse hebdomadaire générée par IA

### Usage

```
/famille/journal
```

---

## Anniversaires

### Fonctionnalités

- Calendrier des anniversaires avec alertes J-7 et J-1
- Idées de cadeaux (suggestions IA)
- Historique des fêtes passées

### Usage

```
/famille/anniversaires
```

---

## Documents

### Fonctionnalités

- Archivage des documents administratifs familiaux (actes de naissance, passeports, CAF…)
- Catégorisation par type et membre de la famille
- Aperçu en ligne (PDF, images)
- Alertes d'expiration pour les documents temporaires

### Usage

```
/famille/documents
```

---

## API Reference

### Endpoints principaux

| Méthode | URL                              | Description                         |
|--------|----------------------------------|-------------------------------------|
| GET    | `/api/v1/famille/jules/profil`   | Profil et données de Jules          |
| POST   | `/api/v1/famille/jules/jalons`   | Enregistrer un jalon                |
| GET    | `/api/v1/famille/activites`      | Lister les activités                |
| POST   | `/api/v1/famille/budget`         | Ajouter une dépense/revenu          |
| GET    | `/api/v1/famille/budget/resume`  | Résumé budgétaire mensuel           |
| GET    | `/api/v1/famille/routines`       | Lister les routines                 |
| GET    | `/api/v1/famille/contacts`       | Lister les contacts                 |
| POST   | `/api/v1/famille/journal`        | Nouvelle entrée journal             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
