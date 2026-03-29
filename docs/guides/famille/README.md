# 👨‍👩‍👦 Guide Module Famille

> Ce guide couvre le suivi familial dans MaTanne : développement de Jules, activités, budget, routines, contacts, journal, anniversaires, documents.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Jules — Suivi développement enfant](#jules--suivi-développement-enfant)
3. [Activités familiales](#activités-familiales)
4. [Budget familial](#budget-familial)
5. [Routines](#routines)
6. [Week-end](#week-end)
7. [Contacts](#contacts)
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

### Capacités récentes à connaître

- suggestions IA pour les activités et le weekend
- suggestions d'achats famille assistées par IA
- rappels famille intégrés aux jobs planifiés
- résumé hebdomadaire et intégrations calendrier / Garmin

---

## Jules — Suivi développement enfant

### Fonctionnalités

- Suivi des **jalons de développement** (motricité, langage, social) par rapport aux normes OMS
- **Courbes de croissance** (poids, taille, périmètre crânien) avec visualisation graphique
- **Carnet de santé** : vaccinations, consultations, ordonnances
- **Diversification alimentaire** : suivi des aliments introduits et réactions
- Suggestions IA personnalisées sur le développement
- Alertes sur les jalons en retard
- intégration avec les suggestions d'activités via invalidation de cache et notifications

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
- **Phase O — Suggestions IA avec pré-remplissage** : `POST /famille/activites/suggestions-ia-auto` retourne `suggestions_struct` (liste d'objets pré-remplissables) pour injecter directement dans le formulaire de création
- contribution au résumé hebdomadaire et au dashboard

### Usage

```
/famille/activites
```

### Pré-remplissage rapide (Phase O)

Le bouton **"Suggestions IA"** dans l'en-tête ouvre un dialogue :
1. L'API détecte la météo locale automatiquement
2. Retourne `suggestions_struct` : liste d'objets `{titre, description, type, duree_minutes, lieu}`
3. Cards de pré-remplissage rapide — clic sur "Utiliser cette suggestion" injecte les données dans le formulaire

```
POST /api/v1/famille/activites/suggestions-ia-auto
Body: { type_prefere?: "mixte"|"interieur"|"exterieur", nb_suggestions?: 4 }
Réponse: { suggestions: string, suggestions_struct: [{titre, description, type, duree_minutes, lieu}], meteo_detectee?: string, age_jules_mois?: number }
```

---

## Achats famille — Phase P

### Fonctionnalités

- Liste des achats prévus (cadeaux, vêtements, jouets, équipements) distincts des courses alimentaires
- Groupés par catégorie (cadeau, vêtement, jouet, livre, équipement, autre)
- Marquer un achat comme effectué avec prix réel
- **Suggestions IA proactives** : `POST /famille/achats/suggestions` infère les achats pertinents (anniversaires proches, jalons, saison)

### Usage

```
/famille/achats
```

### Suggestions IA proactives (Phase P)

Le bouton **"Générer des suggestions proactives"** appelle l'API qui :
1. Détecte les anniversaires dans les 30 prochains jours
2. Identifie les jalons récents de Jules
3. Tient compte de la saison courante
4. Retourne une liste de suggestions avec source + fourchette de prix

```
POST /api/v1/famille/achats/suggestions
Body: {}
Réponse: { suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }
```

---

## Budget familial

### Fonctionnalités

- Saisie des revenus et dépenses par catégorie
- Graphiques de répartition du budget (diagramme camembert)
- Suivi mensuel avec comparaison aux mois précédents
- Alertes quand les dépenses dépassent un budget défini
- Export CSV des transactions
- base de travail pour l'agrégation future avec maison et jeux

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
- interaction cible identifiée avec le planning central

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
- score weekend alimenté par job planifié dédié

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
- **Phase R — Résumés IA sauvegardés** : les entrées avec tag `resume-ia` sont affichées dans une section dédiée "Résumés IA récents" en haut de la timeline

### Usage

```
/famille/journal
```

### Résumés IA (Phase R)

Le bouton "Résumé IA semaine" appelle `POST /famille/journal/ia-semaine` (ou l'alias `resumer-semaine`). Le résumé est **automatiquement sauvegardé** comme entrée journal avec tag `resume-ia` + humeur `bien`. Il apparaît dans la section "Résumés IA récents" (max 3 derniers affichés).

```
POST /api/v1/famille/journal/resumer-semaine
Body: { date_debut?: "YYYY-MM-DD", style?: "narratif"|"bullet" }
Réponse: { resume: string, date_debut: string, date_fin: string }
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
