# ðŸŽ® Guide Module Jeux

> Guide complet du module Jeux : paris sportifs intelligents, Loto/Euromillions avec IA et backtest.

**Statut** : âœ… **100% COMPLET** â€” Phases S/T/U/V/W finalisÃ©es (27 mars 2026)

## Table des matiÃ¨res

1. [Vue d'ensemble](#vue-densemble)
2. [Dashboard Jeux](#dashboard-jeux)
3. [Paris sportifs intelligents](#paris-sportifs-intelligents)
4. [Loto & IA](#loto--ia)
5. [Euromillions](#euromillions)
6. [Performance & Analytics](#performance--analytics)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Jeux** est un systÃ¨me complet de suivi et d'analyse des paris sportifs et jeux de loterie avec **intelligence artificielle** (Mistral AI), dÃ©tection d'opportunitÃ©s et backtest.

**URL principale** : `/jeux`  
**Backend** : `src/services/jeux/` (13 modÃ¨les, 5 services IA, 20+ endpoints)  
**Frontend** : `frontend/src/app/(app)/jeux/` (6 pages, 15+ composants)

### ðŸŽ¯ FonctionnalitÃ©s clÃ©s

- **Dashboard contextuel** : Budget, value bets, sÃ©ries dÃ©tectÃ©es, KPIs temps rÃ©el
- **PrÃ©dictions IA** : Analyse de matchs avec probabilitÃ©s, confiance, conseils
- **GÃ©nÃ©rateur de grilles IA** : Loto optimisÃ© (modes chauds/froids/Ã©quilibre) + critique personnalisÃ©e
- **Heatmaps** : Ã‰volution des cotes bookmaker, frÃ©quences numÃ©ros loto
- **Backtest** : Simulation ROI sur historique, validation stratÃ©gies
- **Notifications push** : RÃ©sultats paris/loto en temps rÃ©el (Web Push)
- **Services planifiÃ©s** : cron jeux et alertes pÃ©riodiques cÃ´tÃ© backend

### Points d'attention actuels

- l'agrÃ©gation pertes/gains -> budget global reste une interaction planifiÃ©e mais pas encore finalisÃ©e

> âš ï¸ **Avertissement** : Ce module est conÃ§u pour un usage personnel de suivi analytique. MaTanne ne rÃ©alise pas de paris rÃ©els â€” il s'agit uniquement d'un outil de gestion, d'apprentissage et de contrÃ´le budgÃ©taire.

---

## Dashboard Jeux

**URL** : `/jeux`

Hub central avec vision temps rÃ©el de votre activitÃ© de jeu.

### Sections

1. **Bandeau budget** : Progression vers limite mensuelle (barre + alerte si >80%)
2. **OpportunitÃ©s** : Value bets dÃ©tectÃ©s automatiquement (Expected Value >5%)
3. **Analyse IA** : RÃ©sumÃ© Mistral de votre activitÃ© rÃ©cente (tendances, recommandations)
4. **KPIs** : ROI global, taux de rÃ©ussite, bÃ©nÃ©fice net, paris actifs

### Widgets personnalisables

- Drag & drop pour rÃ©organiser les grilles
- Sauvegarde automatique dans `localStorage`
- Support mobile avec navigation fluide

---

## Paris sportifs intelligents

**URL** : `/jeux/paris`

### FonctionnalitÃ©s de base

- âœ… CRUD paris (crÃ©er, modifier, supprimer)
- âœ… Filtres par statut (en cours, gagnÃ©, perdu, annulÃ©)
- âœ… Calcul automatique gains/pertes
- âœ… Statistiques : ROI, taux de rÃ©ussite, mise moyenne

### ðŸ¤– Intelligence artificielle

#### PrÃ©dictions de matchs

Lors de la crÃ©ation d'un pari, cliquez sur un match pour ouvrir le **drawer de dÃ©tail** :

- *API Reference

### Dashboard & SÃ©ries

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/dashboard` | Dashboard complet (budget, value bets, KPIs, analyse IA) |
| GET | `/api/v1/jeux/series` | SÃ©ries actives dÃ©tectÃ©es (seuil configurable) |
| GET | `/api/v1/jeux/alertes` | Alertes sÃ©ries dangereuses |

### Paris sportifs

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/paris` | Lister paris (filtres statut/championnat) |
| POST | `/api/v1/jeux/paris` | CrÃ©er pari (bloquÃ© si limite atteinte) |
| PATCH | `/api/v1/jeux/paris/{id}` | Modifier pari (rÃ©sultat, statut) |
| DELETE | `/api/v1/jeux/paris/{id}` | Supprimer pari |
| GET | `/api/v1/jeux/paris/stats` | Statistiques globales paris |
| GET | `/api/v1/jeux/paris/predictions/{match_id}` | PrÃ©diction IA pour un match |
| GET | `/api/v1/jeux/paris/value-bets` | Value bets dÃ©tectÃ©s (EV >5%) |
| GET | `/api/v1/jeux/paris/cotes-historique/{match_id}` | Ã‰volution cotes bookmaker (heatmap) |

### Loto

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/loto/tirages` | Historique tirages officiels |
| GET | `/api/v1/jeux/loto/grilles` | Mes grilles jouÃ©es |
| POST | `/api/v1/jeux/loto/grilles` | Ajouter grille |
| GET | `/api/v1/jeux/loto/stats` | Stats globales (frÃ©quences, total gains) |
| GET | `/api/v1/jeux/loto/numeros-retard` | NumÃ©ros en retard (seuil 2Ïƒ) |
| POST | `/api/v1/jeux/loto/generer-grille` | GÃ©nÃ©rateur classique (statistique/alÃ©atoire) |
| POST | `/api/v1/jeux/loto/generer-grille-ia-ponderee` | **[Phase U]** GÃ©nÃ©rateur IA (modes chauds/froids/Ã©quilibre) |
| POST | `/api/v1/jeux/loto/analyser-grille` | **[Phase U]** Analyse critique IA d'une grille |

### Euromillions

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/euromillions/tirages` | Historique tirages |
| GET | `/api/v1/jeux/euromillions/grilles` | Mes grilles |
| POST | `/api/v1/jeux/euromillions/grilles` | Ajouter grille |
| GET | `/api/v1/jeux/euromillions/stats` | Statistiques |
| POST | `/api/v1/jeux/euromillions/generer-grille` | GÃ©nÃ©rateur classique |

### Performance & Analytics

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/performance` | MÃ©triques globales (ROI, taux rÃ©ussite, bÃ©nÃ©fice) |
| GET | `/api/v1/jeux/performance/confiance` | Breakdown par tranches confiance IA |
| GET | `/api/v1/jeux/resume-mensuel` | RÃ©sumÃ© IA du mois (Mistral) |
| GET | `/api/v1/jeux/backtest` | Simulation rÃ©trospective stratÃ©gies |

### Utilitaires

| MÃ©thode | URL | Description |
| --------- | ----- | ------------- |
| POST | `/api/v1/jeux/analyse-ia` | Analyse IA gÃ©nÃ©rique (paris/loto) |
| GET | `/api/v1/jeux/notifications` | Notifications jeux non lues |
| POST | `/api/v1/jeux/notifications/{id}/lue` | Marquer notification comme lue |
| POST | `/api/v1/jeux/ocr-ticket` | OCR ticket papier (Pixtral) |

---

## SchÃ©mas de donnÃ©es

### PariSportif

```typescript
{
  id: number;
  match_id: number;
  type_pari: "1X2" | "over_under" | "handicap" | "buteur" | "exact_score";
  selection: string;
  cote: number;
  mise: number;
  gain?: number;
  statut: "en_cours" | "gagne" | "perdu" | "annule";
  date_pari: string;
  date_match: string;
  championnat?: string;
  notes?: string;
  confiance_ia?: number; // 0-1
}
```

### GrilleLoto

```typescript
{
  id: number;
  numeros: number[]; // 5 numÃ©ros entre 1-49
  numero_chance: number; // 1-10
  mise: number;
  date_tirage: string;
  gains?: number;
  est_virtuelle: boolean; // true si gÃ©nÃ©rÃ©e pour simulation
  strategie?: "statistique" | "aleatoire" | "ia";
  mode_ia?: "chauds" | "froids" | "equilibre"; // Phase U
}
```

### AnalyseGrilleIA (Phase U)

```typescript
{
  grille: {
    numeros: number[];
    numero_chance: number;
  };
  note: number; // 0-10
  points_forts: string[];
  points_faibles: string[];
  recommandations: string[];
  appreciation: string; // "Excellent" | "Bon" | "Moyen" | "Ã€ revoir"
}
```

### ValueBet

```typescript
{
  match_id: number;
  equipe_domicile: string;
  equipe_exterieur: string;
  type_pari: string;
  cote: number;
  proba_estimee: number; // 0-1
  expected_value: number; // %
  raison: string;
}
```

---

## Guide dÃ©veloppeur

### Services backend

- **`JeuxAIService`** : Moteur IA Mistral (prÃ©dictions, suggestions, analyses)
- **`SeriesService`** : DÃ©tection loi des sÃ©ries (n-grammes, patterns)
- **`PredictionServiceJeux`** : ModÃ¨le prÃ©dictif local (forme, H2H, cotes)
- **`BacktestService`** : Simulateur ROI rÃ©trospectif

### Composants frontend clÃ©s

- `GrilleIAPonderee` : GÃ©nÃ©rateur + analyseur IA loto
- `HeatmapCotes` : Graphique Ã©volution cotes (Recharts LineChart)
- `HeatmapNumeros` : Visualisation frÃ©quences numÃ©ros (grid colorÃ©e)
- `DrawerMatchDetail` : Sheet latÃ©ral prÃ©dictions match
- `BacktestResultatCard` : Affichage rÃ©sultats simulation

### Hooks personnalisÃ©s

- `useNotificationsJeux()` : Ã‰coute service worker, affiche toasts rÃ©sultats
- `demanderPermissionNotificationsJeux()` : Demande permission navigateur

### Tests

```bash
# Backend â€” 10 tests unitaires Phases T/U/W
pytest tests/services/test_jeux_phases_tuw.py -v

# Frontend â€” Tests composants jeux
cd frontend && npm test -- jeux
```

---

## Ressources complÃ©mentaires

- [FINALISATION_PHASES_TUW.md](FINALISATION_PHASES_TUW.md) : Guide technique implÃ©mentation Phases T/U/W
- [API_REFERENCE.md](../../API_REFERENCE.md) : Documentation OpenAPI complÃ¨te
- [MODULES.md](../../MODULES.md) : Architecture gÃ©nÃ©rale modules
- [STATUS_PHASES.md](../../STATUS_PHASES.md) : Ã‰tat d'avancement projet (Phases S-W âœ…)

---

**DerniÃ¨re mise Ã  jour** : 27 mars 2026 â€” Module Jeux 100% complet (backend + frontend + UI + docs)iers tirages)
2. **Mode Froids** : Mise sur les numÃ©ros en retard (loi des sÃ©ries)
3. **Mode Ã‰quilibrÃ©** : Mix 60% chauds + 40% froids (recommandÃ©)

**Powered by** : Mistral AI analyse l'historique complet, calcule pondÃ©rations, gÃ©nÃ¨re grille optimisÃ©e

#### Analyse IA de votre grille

AprÃ¨s gÃ©nÃ©ration (ou saisie manuelle d'une grille existante), cliquez **"Analyser cette grille"** :

- **Note globale** : 0-10 selon qualitÃ© statistique
- **Points forts** : Ex. "Bon mix numÃ©ros pairs/impairs", "Spread dÃ©ciles Ã©quilibrÃ©"
- **Points faibles** : Ex. "Trop de numÃ©ros consÃ©cutifs", "Tous dans tranche 1-20"
- **Recommandations** : Suggestions concrÃ¨tes d'amÃ©lioration
- **ApprÃ©ciation** : Texte synthÃ©tique (Excellent/Bon/Moyen/Ã€ revoir)

**Algorithme IA** : VÃ©rifie 8 critÃ¨res (distribution pairs/impairs, dÃ©ciles, consÃ©cutifs, somme, Ã©cart min/max, modulo 10, primes, patterns)

### ðŸ“ˆ NumÃ©ros en retard

Section dÃ©diÃ©e affichant les 10 numÃ©ros les plus en retard avec :

- **Valeur de retard** : Score absolu (nombre de tirages sans sortir)
- **Badge ðŸ”¥** : Si retard >2Ã— Ã©cart-type (statistiquement significatif)

### ðŸŽ² Backtest loto

Bouton "ðŸ“Š Backtest" sur la page :

- Simule stratÃ©gie sur 100 derniers tirages
- Calcule ROI, taux de rentabilitÃ©, variance
- Compare performances mode statistique vs alÃ©atoire vs IA

---

## Euromillions

**URL** : `/jeux/euromillions`

MÃªme logique que Loto avec spÃ©cificitÃ©s :

- **Grille** : 5 numÃ©ros (1-50) + 2 Ã©toiles (1-12)
- **GÃ©nÃ©rateur classique** : StratÃ©gies statistique/alÃ©atoire
- **Heatmap** : SÃ©parÃ© numÃ©ros principaux + Ã©toiles
- **Stats** : FrÃ©quences, retards, tirages rÃ©cents

> ðŸ’¡ **Note** : Le gÃ©nÃ©rateur IA pondÃ©rÃ© n'est pas encore implÃ©mentÃ© pour Euromillions (prÃ©vu Phase future). Actuellement disponible uniquement pour le Loto.

---

## Performance & Analytics

**URL** : `/jeux/performance`

### Vue d'ensemble

- **ROI global** : (Total gains - Total mises) / Total mises Ã— 100
- **Taux de rÃ©ussite** : % paris gagnÃ©s
- **BÃ©nÃ©fice net** : Somme algÃ©brique gains - mises
- **Paris actifs** : Nombre de paris en cours

### Graphiques

1. **Ã‰volution bankroll** : LineChart cumulatif (gains - pertes)
2. **Breakdown par championnat** : BarChart horizontal (ROI par compÃ©tition)
3. **Breakdown par confiance IA** : BarChart tranches de confiance (0-50%, 50-70%, etc.)

### ðŸ“ RÃ©sumÃ© mensuel IA

Bouton "GÃ©nÃ©rer rÃ©sumÃ© mensuel" :

- **Powered by** : Mistral AI analyse toutes les donnÃ©es du mois
- **Contenu** : 
  - SynthÃ¨se performances (meilleurs/pires paris)
  - Tendances identifiÃ©es (sports rentables, erreurs rÃ©currentes)
  - Recommandations stratÃ©giques personnalisÃ©es
  - Objectifs suggÃ©rÃ©s pour le mois suivant

### ðŸ”™ Backtest

Simulation rÃ©trospective pour valider stratÃ©gies :

- **ParamÃ¨tres** : Type jeu (paris/loto), seuil value bet, nb tirages/matchs
- **RÃ©sultats** : ROI simulÃ©, variance, ratio Sharpe, drawdown max
- **Graphique** : Courbe equity hypothÃ©tique

---

### ðŸ”” Notifications push rÃ©sultats

**Activation** : ParamÃ¨tres > Notifications > "Activer les notifications jeux"

Types de notifications Web Push :

1. **Pari gagnÃ©** ðŸŽ‰ : Affiche montant gain + action "Voir dÃ©tails"
2. **Pari perdu** ðŸ˜ž : Affiche perte + encouragement
3. **RÃ©sultat loto** ðŸŽ± : Affiche numÃ©ros gagnants + votre rÃ©sultat

**ImplÃ©mentation** :

- Service Worker Ã©coute messages backend
- Hook `useNotificationsJeux()` activÃ© dans layout racine
- Toasts Sonner avec actions contextuelles
- Permission navigateur requise (demandÃ©e via bouton paramÃ¨tres)

---

## Loto

### FonctionnalitÃ©s

- Saisie des grilles jouÃ©es (6 numÃ©ros + numÃ©ro chance)
- Comparaison automatique avec les rÃ©sultats officiels
- Historique des participations et gains
- Statistiques des numÃ©ros les plus jouÃ©s

### Usage

```
/jeux/loto
```

### Structure d'une grille Loto

| Champ        | Type         | Description                      |
| ------------- | -------------- | ---------------------------------- |
| `numeros`    | int[5]       | 5 numÃ©ros entre 1 et 49          |
| `numero_chance` | int       | NumÃ©ro chance entre 1 et 10      |
| `mise`       | decimal      | Montant jouÃ©                     |
| `date_tirage` | date        | Date du tirage                   |
| `gains`      | decimal      | Gains obtenus (0 si perdant)     |

---

## Euromillions

### FonctionnalitÃ©s

- Saisie des grilles Euromillions (5 numÃ©ros + 2 Ã©toiles)
- Suivi des participations et rÃ©sultats
- Statistiques de frÃ©quence des numÃ©ros tirÃ©s
- Historique avec calcul du solde global

### Usage

```
/jeux/euromillions
```

### Structure d'une grille Euromillions

| Champ      | Type       | Description                         |
| ----------- | ------------ | ------------------------------------- |
| `numeros`  | int[5]     | 5 numÃ©ros entre 1 et 50             |
| `etoiles`  | int[2]     | 2 Ã©toiles entre 1 et 12             |
| `mise`     | decimal    | Montant jouÃ©                        |
| `date_tirage` | date   | Date du tirage                      |
| `gains`    | decimal    | Gains obtenus                       |

---

## API Reference

### Endpoints principaux

| MÃ©thode | URL                           | Description                       |
| -------- | ------------------------------- | ----------------------------------- |
| GET    | `/api/v1/jeux/paris`          | Lister les paris                  |
| POST   | `/api/v1/jeux/paris`          | Ajouter un pari                   |
| PUT    | `/api/v1/jeux/paris/{id}`     | Modifier un pari (rÃ©sultat)       |
| GET    | `/api/v1/jeux/paris/stats`    | Statistiques paris                |
| GET    | `/api/v1/jeux/loto`           | Lister les grilles loto           |
| POST   | `/api/v1/jeux/loto`           | Ajouter une grille                |
| GET    | `/api/v1/jeux/euromillions`   | Lister les grilles euromillions   |
| POST   | `/api/v1/jeux/euromillions`   | Ajouter une grille                |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complÃ¨te.
