# ???????? Guide Module Famille

> Ce guide couvre le suivi familial dans MaTanne : d�veloppement de Jules, activit�s, budget, routines, contacts, journal, anniversaires, documents.

## Table des mati�res

1. [Vue d'ensemble](#vue-densemble)
2. [Jules � Suivi d�veloppement enfant](#jules--suivi-d�veloppement-enfant)
3. [Activit�s familiales](#activit�s-familiales)
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

Le module **Famille** centralise le suivi du d�veloppement de l'enfant et la vie familiale.

**URL** : `/famille`
**Service backend** : `src/services/famille/`
**Route API** : `src/api/routes/famille.py` (`/api/v1/famille`)

### Capacit�s r�centes � conna�tre

- suggestions IA pour les activit�s et le weekend
- suggestions d'achats famille assist�es par IA
- rappels famille int�gr�s aux jobs planifi�s
- r�sum� hebdomadaire et int�grations calendrier / Garmin

---

## Jules � Suivi d�veloppement enfant

### Fonctionnalit�s

- Suivi des **jalons de d�veloppement** (motricit�, langage, social) par rapport aux normes OMS
- **Courbes de croissance** (poids, taille, p�rim�tre cr�nien) avec visualisation graphique
- **Carnet de sant�** : vaccinations, consultations, ordonnances
- **Diversification alimentaire** : suivi des aliments introduits et r�actions
- Suggestions IA personnalis�es sur le d�veloppement
- Alertes sur les jalons en retard
- int�gration avec les suggestions d'activit�s via invalidation de cache et notifications

### Usage

```
/famille/jules
```

### Donn�es de r�f�rence

- `data/reference/normes_oms.json` � normes de croissance OMS (0-5 ans)
- `data/reference/calendrier_vaccinal_fr.json` � calendrier vaccinal France 2026

### Services IA

```python
from src.services.famille.jules_ai import JulesAIService
service = JulesAIService()
# Analyse d�veloppement et suggestions personnalis�es
analyse = service.analyser_developpement(age_mois=18, jalons_atteints=[...])
```

---

## Activit�s familiales

### Fonctionnalit�s

- Planification et suivi des activit�s (sorties, sports, loisirs)
- Cat�gorisation (sport, culture, plein-air, cr�atif�)
- Association � des membres de la famille
- Vue calendrier des activit�s planifi�es
- **Phase O � Suggestions IA avec pr�-remplissage** : `POST /famille/activites/suggestions-ia-auto` retourne `suggestions_struct` (liste d'objets pr�-remplissables) pour injecter directement dans le formulaire de cr�ation
- contribution au r�sum� hebdomadaire et au dashboard

### Usage

```
/famille/activites
```

### Pr�-remplissage rapide (Phase O)

Le bouton **"Suggestions IA"** dans l'en-t�te ouvre un dialogue :
1. L'API d�tecte la m�t�o locale automatiquement
2. Retourne `suggestions_struct` : liste d'objets `{titre, description, type, duree_minutes, lieu}`
3. Cards de pr�-remplissage rapide � clic sur "Utiliser cette suggestion" injecte les donn�es dans le formulaire

```
POST /api/v1/famille/activites/suggestions-ia-auto
Body: { type_prefere?: "mixte"|"interieur"|"exterieur", nb_suggestions?: 4 }
R�ponse: { suggestions: string, suggestions_struct: [{titre, description, type, duree_minutes, lieu}], meteo_detectee?: string, age_jules_mois?: number }
```

---

## Achats famille � Phase P

### Fonctionnalit�s

- Liste des achats pr�vus (cadeaux, v�tements, jouets, �quipements) distincts des courses alimentaires
- Group�s par cat�gorie (cadeau, v�tement, jouet, livre, �quipement, autre)
- Marquer un achat comme effectu� avec prix r�el
- **Suggestions IA proactives** : `POST /famille/achats/suggestions` inf�re les achats pertinents (anniversaires proches, jalons, saison)

### Usage

```
/famille/achats
```

### Suggestions IA proactives (Phase P)

Le bouton **"G�n�rer des suggestions proactives"** appelle l'API qui :
1. D�tecte les anniversaires dans les 30 prochains jours
2. Identifie les jalons r�cents de Jules
3. Tient compte de la saison courante
4. Retourne une liste de suggestions avec source + fourchette de prix

```
POST /api/v1/famille/achats/suggestions
Body: {}
R�ponse: { suggestions: [{titre, description, source, fourchette_prix?, ou_acheter?, pertinence?}], total }
```

---

## Budget familial

### Fonctionnalit�s

- Saisie des revenus et d�penses par cat�gorie
- Graphiques de r�partition du budget (diagramme camembert)
- Suivi mensuel avec comparaison aux mois pr�c�dents
- Alertes quand les d�penses d�passent un budget d�fini
- Export CSV des transactions
- base de travail pour l'agr�gation future avec maison et jeux

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

### Fonctionnalit�s

- D�finition des routines quotidiennes (matin, soir, semaine)
- Cases � cocher interactives pour valider chaque �tape
- Suivi de la r�gularit� (score de coh�rence sur 30 jours)
- Routines d�di�es enfant (bain, lecture, coucher) et adulte
- interaction cible identifi�e avec le planning central

### Usage

```
/famille/routines
```

---

## Week-end

### Fonctionnalit�s

- Suggestions d'activit�s pour le week-end g�n�r�es par IA
- Bas� sur la m�t�o locale, la saison, l'�ge de Jules
- Filtrage par rayon g�ographique et budget
- Sauvegarde des activit�s favorites
- score weekend aliment� par job planifi� d�di�

### Usage

```
/famille/weekend
```

### Service IA

```python
from src.services.famille.weekend_ai import WeekendAIService
service = WeekendAIService()
suggestions = service.suggerer_activites_weekend(
    m�t�o="ensoleill�", rayon_km=30, budget=50
)
```

---

## Contacts

### Fonctionnalit�s

- Carnet de contacts familial (famille �largie, amis, professionnels de sant�)
- Cat�gorisation (m�decin, �cole, garderie, famille, amis)
- Recherche rapide
- Notes personnalis�es par contact

### Usage

```
/famille/contacts
```

---

## Journal

### Fonctionnalit�s

- Journal de bord familial (texte libre, anecdotes, moments forts)
- Entr�es associ�es � une date et un auteur
- Recherche dans les entr�es pass�es
- Synth�se hebdomadaire g�n�r�e par IA
- **Phase R � R�sum�s IA sauvegard�s** : les entr�es avec tag `resume-ia` sont affich�es dans une section d�di�e "R�sum�s IA r�cents" en haut de la timeline

### Usage

```
/famille/journal
```

### R�sum�s IA (Phase R)

Le bouton "R�sum� IA semaine" appelle `POST /famille/journal/ia-semaine` (ou l'alias `resumer-semaine`). Le r�sum� est **automatiquement sauvegard�** comme entr�e journal avec tag `resume-ia` + humeur `bien`. Il appara�t dans la section "R�sum�s IA r�cents" (max 3 derniers affich�s).

```
POST /api/v1/famille/journal/resumer-semaine
Body: { date_debut?: "YYYY-MM-DD", style?: "narratif"|"bullet" }
R�ponse: { resume: string, date_debut: string, date_fin: string }
```

---

## Anniversaires

### Fonctionnalit�s

- Calendrier des anniversaires avec alertes J-7 et J-1
- Id�es de cadeaux (suggestions IA)
- Historique des f�tes pass�es

### Usage

```
/famille/anniversaires
```

---

## Documents

### Fonctionnalit�s

- Archivage des documents administratifs familiaux (actes de naissance, passeports, CAF�)
- Cat�gorisation par type et membre de la famille
- Aper�u en ligne (PDF, images)
- Alertes d'expiration pour les documents temporaires

### Usage

```
/famille/documents
```

---

## API Reference

### Endpoints principaux

| M�thode | URL                              | Description                         |
| -------- | ---------------------------------- | ------------------------------------- |
| GET    | `/api/v1/famille/jules/profil`   | Profil et donn�es de Jules          |
| POST   | `/api/v1/famille/jules/jalons`   | Enregistrer un jalon                |
| GET    | `/api/v1/famille/activites`      | Lister les activit�s                |
| POST   | `/api/v1/famille/budget`         | Ajouter une d�pense/revenu          |
| GET    | `/api/v1/famille/budget/resume`  | R�sum� budg�taire mensuel           |
| GET    | `/api/v1/famille/routines`       | Lister les routines                 |
| GET    | `/api/v1/famille/contacts`       | Lister les contacts                 |
| POST   | `/api/v1/famille/journal`        | Nouvelle entr�e journal             |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation compl�te.
