# ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦ Guide Module Famille

> Ce guide couvre le suivi familial dans MaTanne : dÃ©veloppement de Jules, activitÃ©s, budget, routines, contacts, journal, anniversaires, documents.

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Jules â€” Suivi dÃ©veloppement enfant](#jules--suivi-dÃ©veloppement-enfant)
3. [ActivitÃ©s familiales](#activitÃ©s-familiales)
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

Le module **Famille** centralise le suivi du dÃ©veloppement de l'enfant et la vie familiale.

**URL** : `/famille`
**Service backend** : `src/services/famille/`
**Route API** : `src/api/routes/famille.py` (`/api/v1/famille`)

### CapacitÃ©s rÃ©centes Ã  connaÃ®tre

- suggestions IA pour les activitÃ©s et le weekend
- suggestions d'achats famille assistÃ©es par IA
- rappels famille intÃ©grÃ©s aux jobs planifiÃ©s
- rÃ©sumÃ© hebdomadaire et intÃ©grations calendrier / Garmin

---

## Jules â€” Suivi dÃ©veloppement enfant

### FonctionnalitÃ©s

- Suivi des **jalons de dÃ©veloppement** (motricitÃ©, langage, social) par rapport aux normes OMS
- **Courbes de croissance** (poids, taille, pÃ©rimÃ¨tre crÃ¢nien) avec visualisation graphique
- **Carnet de santÃ©** : vaccinations, consultations, ordonnances
- **Diversification alimentaire** : suivi des aliments introduits et rÃ©actions
- Suggestions IA personnalisÃ©es sur le dÃ©veloppement
- Alertes sur les jalons en retard
- intÃ©gration avec les suggestions d'activitÃ©s via invalidation de cache et notifications

### Usage

```
/famille/jules
```

### DonnÃ©es de rÃ©fÃ©rence

- `data/reference/normes_oms.json` â€” normes de croissance OMS (0-5 ans)
- `data/reference/calendrier_vaccinal_fr.json` â€” calendrier vaccinal France 2026

### Services IA

```python
from src.services.famille.jules_ai import JulesAIService
service = JulesAIService()
# Analyse dÃ©veloppement et suggestions personnalisÃ©es
analyse = service.analyser_developpement(age_mois=18, jalons_atteints=[...])
```

---

## ActivitÃ©s familiales

### FonctionnalitÃ©s

- Planification et suivi des activitÃ©s (sorties, sports, loisirs)
- CatÃ©gorisation (sport, culture, plein-air, crÃ©atifâ€¦)
- Association Ã  des membres de la famille
- Vue calendrier des activitÃ©s planifiÃ©es
- **Phase O â€” Suggestions IA avec prÃ©-remplissage** : `POST /famille/activites/suggestions-ia-auto` retourne `suggestions_struct` (liste d'objets prÃ©-remplissables) pour injecter directement dans le formulaire de crÃ©ation
- contribution au rÃ©sumÃ© hebdomadaire et au dashboard

### Usage

```
/famille/activites
```

### PrÃ©-remplissage rapide (Phase O)

Le bouton **"Suggestions IA"** dans l'en-tÃªte ouvre un dialogue :
1. L'API dÃ©tecte la mÃ©tÃ©o locale automatiquement
2. Retourne `suggestions_struct` : liste d'objets `{titre, description, type, duree_minutes, lieu}`
3. Cards de prÃ©-remplissage rapide â€” clic sur "Utiliser cette suggestion" injecte les donnÃ©es dans le formulaire

```
POST /api/v1/famille/activites/suggestions-ia-auto
Body: { type_prefere?: "mixte"|"interieur"|"exterieur", nb_suggestions?: 4 }
RÃ©ponse: { suggestions: string, suggestions_struct: [{titre, description, type, duree_minutes, lieu}], meteo_detectee?: string, age_jules_mois?: number }
```

---

## Achats famille â€” Phase P

### FonctionnalitÃ©s

- Liste des achats prÃ©vus (cadeaux, vÃªtements, jouets, Ã©quipements) distincts des courses alimentaires
- GroupÃ©s par catÃ©gorie (cadeau, vÃªtement, jouet, livre, Ã©quipement, autre)
- Marquer un achat comme effectuÃ© avec prix rÃ©el
- **Suggestions IA proactives** : `POST /famille/achats/suggestions` infÃ¨re les achats pertinents (anniversaires proches, jalons, saison)

### Usage

```
/famille/achats
```

### Suggestions IA proactives (Phase P)

Le bouton **"GÃ©nÃ©rer des suggestions proactives"** appelle l'API qui :
1. DÃ©tecte les anniversaires dans les 30 prochains jours
2. Identifie les jalons rÃ©cents de Jules
3. Tient compte de la saison courante
4. Retourne une liste de suggestions avec source + fourchette de prix

```
POST /api/v1/famille/achats/suggestions
Body: {}
RÃ©ponse: { suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }
```

---

## Budget familial

### FonctionnalitÃ©s

- Saisie des revenus et dÃ©penses par catÃ©gorie
- Graphiques de rÃ©partition du budget (diagramme camembert)
- Suivi mensuel avec comparaison aux mois prÃ©cÃ©dents
- Alertes quand les dÃ©penses dÃ©passent un budget dÃ©fini
- Export CSV des transactions
- base de travail pour l'agrÃ©gation future avec maison et jeux

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

### FonctionnalitÃ©s

- DÃ©finition des routines quotidiennes (matin, soir, semaine)
- Cases Ã  cocher interactives pour valider chaque Ã©tape
- Suivi de la rÃ©gularitÃ© (score de cohÃ©rence sur 30 jours)
- Routines dÃ©diÃ©es enfant (bain, lecture, coucher) et adulte
- interaction cible identifiÃ©e avec le planning central

### Usage

```
/famille/routines
```

---

## Week-end

### FonctionnalitÃ©s

- Suggestions d'activitÃ©s pour le week-end gÃ©nÃ©rÃ©es par IA
- BasÃ© sur la mÃ©tÃ©o locale, la saison, l'Ã¢ge de Jules
- Filtrage par rayon gÃ©ographique et budget
- Sauvegarde des activitÃ©s favorites
- score weekend alimentÃ© par job planifiÃ© dÃ©diÃ©

### Usage

```
/famille/weekend
```

### Service IA

```python
from src.services.famille.weekend_ai import WeekendAIService
service = WeekendAIService()
suggestions = service.suggerer_activites_weekend(
    mÃ©tÃ©o="ensoleillÃ©", rayon_km=30, budget=50
)
```

---

## Contacts

### FonctionnalitÃ©s

- Carnet de contacts familial (famille Ã©largie, amis, professionnels de santÃ©)
- CatÃ©gorisation (mÃ©decin, Ã©cole, garderie, famille, amis)
- Recherche rapide
- Notes personnalisÃ©es par contact

### Usage

```
/famille/contacts
```

---

## Journal

### FonctionnalitÃ©s

- Journal de bord familial (texte libre, anecdotes, moments forts)
- EntrÃ©es associÃ©es Ã  une date et un auteur
- Recherche dans les entrÃ©es passÃ©es
- SynthÃ¨se hebdomadaire gÃ©nÃ©rÃ©e par IA
- **Phase R â€” RÃ©sumÃ©s IA sauvegardÃ©s** : les entrÃ©es avec tag `resume-ia` sont affichÃ©es dans une section dÃ©diÃ©e "RÃ©sumÃ©s IA rÃ©cents" en haut de la timeline

### Usage

```
/famille/journal
```

### RÃ©sumÃ©s IA (Phase R)

Le bouton "RÃ©sumÃ© IA semaine" appelle `POST /famille/journal/ia-semaine` (ou l'alias `resumer-semaine`). Le rÃ©sumÃ© est **automatiquement sauvegardÃ©** comme entrÃ©e journal avec tag `resume-ia` + humeur `bien`. Il apparaÃ®t dans la section "RÃ©sumÃ©s IA rÃ©cents" (max 3 derniers affichÃ©s).

```
POST /api/v1/famille/journal/resumer-semaine
Body: { date_debut?: "YYYY-MM-DD", style?: "narratif"|"bullet" }
RÃ©ponse: { resume: string, date_debut: string, date_fin: string }
```

---

## Anniversaires

### FonctionnalitÃ©s

- Calendrier des anniversaires avec alertes J-7 et J-1
- IdÃ©es de cadeaux (suggestions IA)
- Historique des fÃªtes passÃ©es

### Usage

```
/famille/anniversaires
```

---

## Documents

### FonctionnalitÃ©s

- Archivage des documents administratifs familiaux (actes de naissance, passeports, CAFâ€¦)
- CatÃ©gorisation par type et membre de la famille
- AperÃ§u en ligne (PDF, images)
- Alertes d'expiration pour les documents temporaires

### Usage

```
/famille/documents
```

---

## API Reference

### Endpoints principaux

| MÃ©thode | URL                              | Description                         |
| -------- | ---------------------------------- | ------------------------------------- |
| GET    | `/api/v1/famille/jules/profil`   | Profil et donnÃ©es de Jules          |
| POST   | `/api/v1/famille/jules/jalons`   | Enregistrer un jalon                |
| GET    | `/api/v1/famille/activites`      | Lister les activitÃ©s                |
| POST   | `/api/v1/famille/budget`         | Ajouter une dÃ©pense/revenu          |
| GET    | `/api/v1/famille/budget/resume`  | RÃ©sumÃ© budgÃ©taire mensuel           |
| GET    | `/api/v1/famille/routines`       | Lister les routines                 |
| GET    | `/api/v1/famille/contacts`       | Lister les contacts                 |
| POST   | `/api/v1/famille/journal`        | Nouvelle entrÃ©e journal             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
