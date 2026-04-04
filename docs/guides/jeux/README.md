# 🎮 Guide Module Jeux

> Guide complet du module Jeux : paris sportifs intelligents, Loto/Euromillions avec IA et backtest.

**Statut** : ✅ **100% COMPLET** — Phases S/T/U/V/W finalisées (27 mars 2026)

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Dashboard Jeux](#dashboard-jeux)
3. [Paris sportifs intelligents](#paris-sportifs-intelligents)
4. [Loto & IA](#loto--ia)
5. [Euromillions](#euromillions)
6. [Performance & Analytics](#performance--analytics)
7. [API Reference](#api-reference)

---

## Vue d'ensemble

Le module **Jeux** est un système complet de suivi et d'analyse des paris sportifs et jeux de loterie avec **intelligence artificielle** (Mistral AI), détection d'opportunités et backtest.

**URL principale** : `/jeux`  
**Backend** : `src/services/jeux/` (13 modèles, 5 services IA, 20+ endpoints)  
**Frontend** : `frontend/src/app/(app)/jeux/` (6 pages, 15+ composants)

### 🎯 Fonctionnalités clés

- **Dashboard contextuel** : Budget, value bets, séries détectées, KPIs temps réel
- **Prédictions IA** : Analyse de matchs avec probabilités, confiance, conseils
- **Générateur de grilles IA** : Loto optimisé (modes chauds/froids/équilibre) + critique personnalisée
- **Heatmaps** : Évolution des cotes bookmaker, fréquences numéros loto
- **Backtest** : Simulation ROI sur historique, validation stratégies
- **Notifications push** : Résultats paris/loto en temps réel (Web Push)
- **Services planifiés** : cron jeux et alertes périodiques côté backend

### Points d'attention actuels

- l'agrégation pertes/gains -> budget global reste une interaction planifiée mais pas encore finalisée

> ⚠️ **Avertissement** : Ce module est conçu pour un usage personnel de suivi analytique. MaTanne ne réalise pas de paris réels — il s'agit uniquement d'un outil de gestion, d'apprentissage et de contrôle budgétaire.

---

## Dashboard Jeux

**URL** : `/jeux`

Hub central avec vision temps réel de votre activité de jeu.

### Sections

1. **Bandeau budget** : Progression vers limite mensuelle (barre + alerte si >80%)
2. **Opportunités** : Value bets détectés automatiquement (Expected Value >5%)
3. **Analyse IA** : Résumé Mistral de votre activité récente (tendances, recommandations)
4. **KPIs** : ROI global, taux de réussite, bénéfice net, paris actifs

### Widgets personnalisables

- Drag & drop pour réorganiser les grilles
- Sauvegarde automatique dans `localStorage`
- Support mobile avec navigation fluide

---

## Paris sportifs intelligents

**URL** : `/jeux/paris`

### Fonctionnalités de base

- ✅ CRUD paris (créer, modifier, supprimer)
- ✅ Filtres par statut (en cours, gagné, perdu, annulé)
- ✅ Calcul automatique gains/pertes
- ✅ Statistiques : ROI, taux de réussite, mise moyenne

### 🤖 Intelligence artificielle

#### Prédictions de matchs

Lors de la création d'un pari, cliquez sur un match pour ouvrir le **drawer de détail** :

- *API Reference

### Dashboard & Séries

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/dashboard` | Dashboard complet (budget, value bets, KPIs, analyse IA) |
| GET | `/api/v1/jeux/series` | Séries actives détectées (seuil configurable) |
| GET | `/api/v1/jeux/alertes` | Alertes séries dangereuses |

### Paris sportifs

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/paris` | Lister paris (filtres statut/championnat) |
| POST | `/api/v1/jeux/paris` | Créer pari (bloqué si limite atteinte) |
| PATCH | `/api/v1/jeux/paris/{id}` | Modifier pari (résultat, statut) |
| DELETE | `/api/v1/jeux/paris/{id}` | Supprimer pari |
| GET | `/api/v1/jeux/paris/stats` | Statistiques globales paris |
| GET | `/api/v1/jeux/paris/predictions/{match_id}` | Prédiction IA pour un match |
| GET | `/api/v1/jeux/paris/value-bets` | Value bets détectés (EV >5%) |
| GET | `/api/v1/jeux/paris/cotes-historique/{match_id}` | Évolution cotes bookmaker (heatmap) |

### Loto

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/loto/tirages` | Historique tirages officiels |
| GET | `/api/v1/jeux/loto/grilles` | Mes grilles jouées |
| POST | `/api/v1/jeux/loto/grilles` | Ajouter grille |
| GET | `/api/v1/jeux/loto/stats` | Stats globales (fréquences, total gains) |
| GET | `/api/v1/jeux/loto/numeros-retard` | Numéros en retard (seuil 2σ) |
| POST | `/api/v1/jeux/loto/generer-grille` | Générateur classique (statistique/aléatoire) |
| POST | `/api/v1/jeux/loto/generer-grille-ia-ponderee` | Générateur IA (modes chauds/froids/équilibre) |
| POST | `/api/v1/jeux/loto/analyser-grille` | Analyse critique IA d'une grille |

### Euromillions

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/euromillions/tirages` | Historique tirages |
| GET | `/api/v1/jeux/euromillions/grilles` | Mes grilles |
| POST | `/api/v1/jeux/euromillions/grilles` | Ajouter grille |
| GET | `/api/v1/jeux/euromillions/stats` | Statistiques |
| POST | `/api/v1/jeux/euromillions/generer-grille` | Générateur classique |

### Performance & Analytics

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| GET | `/api/v1/jeux/performance` | Métriques globales (ROI, taux réussite, bénéfice) |
| GET | `/api/v1/jeux/performance/confiance` | Breakdown par tranches confiance IA |
| GET | `/api/v1/jeux/resume-mensuel` | Résumé IA du mois (Mistral) |
| GET | `/api/v1/jeux/backtest` | Simulation rétrospective stratégies |

### Utilitaires

| Méthode | URL | Description |
| --------- | ----- | ------------- |
| POST | `/api/v1/jeux/analyse-ia` | Analyse IA générique (paris/loto) |
| GET | `/api/v1/jeux/notifications` | Notifications jeux non lues |
| POST | `/api/v1/jeux/notifications/{id}/lue` | Marquer notification comme lue |

---

## Schémas de données

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
  numeros: number[]; // 5 numéros entre 1-49
  numero_chance: number; // 1-10
  mise: number;
  date_tirage: string;
  gains?: number;
  est_virtuelle: boolean; // true si générée pour simulation
  strategie?: "statistique" | "aleatoire" | "ia";
  mode_ia?: "chauds" | "froids" | "equilibre";
}
```

### AnalyseGrilleIA

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
  appreciation: string; // "Excellent" | "Bon" | "Moyen" | "À revoir"
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

## Guide développeur

### Services backend

- **`JeuxAIService`** : Moteur IA Mistral (prédictions, suggestions, analyses)
- **`SeriesService`** : Détection loi des séries (n-grammes, patterns)
- **`PredictionServiceJeux`** : Modèle prédictif local (forme, H2H, cotes)
- **`BacktestService`** : Simulateur ROI rétrospectif

### Composants frontend clés

- `GrilleIAPonderee` : Générateur + analyseur IA loto
- `HeatmapCotes` : Graphique évolution cotes (Recharts LineChart)
- `HeatmapNumeros` : Visualisation fréquences numéros (grid colorée)
- `DrawerMatchDetail` : Sheet latéral prédictions match
- `BacktestResultatCard` : Affichage résultats simulation

### Hooks personnalisés

- `useNotificationsJeux()` : Écoute service worker, affiche toasts résultats
- `demanderPermissionNotificationsJeux()` : Demande permission navigateur

### Tests

```bash
# Backend — Tests unitaires du module jeux
pytest tests/services/test_jeux_phases_tuw.py -v

# Frontend — Tests composants jeux
cd frontend && npm test -- jeux
```

---

## Ressources complémentaires

- [API_REFERENCE.md](../../API_REFERENCE.md) : Documentation OpenAPI complète
- [MODULES.md](../../MODULES.md) : Architecture générale modules
- [CHANGELOG.md](../../CHANGELOG.md) : Historique des évolutions du module

---

**Dernière mise à jour** : Avril 2026 — Module Jeux complet (backend + frontend + UI + docs)iers tirages)
2. **Mode Froids** : Mise sur les numéros en retard (loi des séries)
3. **Mode Équilibré** : Mix 60% chauds + 40% froids (recommandé)

**Powered by** : Mistral AI analyse l'historique complet, calcule pondérations, génère grille optimisée

#### Analyse IA de votre grille

Après génération (ou saisie manuelle d'une grille existante), cliquez **"Analyser cette grille"** :

- **Note globale** : 0-10 selon qualité statistique
- **Points forts** : Ex. "Bon mix numéros pairs/impairs", "Spread déciles équilibré"
- **Points faibles** : Ex. "Trop de numéros consécutifs", "Tous dans tranche 1-20"
- **Recommandations** : Suggestions concrètes d'amélioration
- **Appréciation** : Texte synthétique (Excellent/Bon/Moyen/À revoir)

**Algorithme IA** : Vérifie 8 critères (distribution pairs/impairs, déciles, consécutifs, somme, écart min/max, modulo 10, primes, patterns)

### 📈 Numéros en retard

Section dédiée affichant les 10 numéros les plus en retard avec :

- **Valeur de retard** : Score absolu (nombre de tirages sans sortir)
- **Badge 🔥** : Si retard >2× écart-type (statistiquement significatif)

### 🎲 Backtest loto

Bouton "📊 Backtest" sur la page :

- Simule stratégie sur 100 derniers tirages
- Calcule ROI, taux de rentabilité, variance
- Compare performances mode statistique vs aléatoire vs IA

---

## Euromillions

**URL** : `/jeux/euromillions`

Même logique que Loto avec spécificités :

- **Grille** : 5 numéros (1-50) + 2 étoiles (1-12)
- **Générateur classique** : Stratégies statistique/aléatoire
- **Heatmap** : Séparé numéros principaux + étoiles
- **Stats** : Fréquences, retards, tirages récents

> 💡 **Note** : Le générateur IA pondéré n'est pas disponible pour Euromillions. Il reste limité au Loto.

---

## Performance & Analytics

**URL** : `/jeux/performance`

### Vue d'ensemble

- **ROI global** : (Total gains - Total mises) / Total mises × 100
- **Taux de réussite** : % paris gagnés
- **Bénéfice net** : Somme algébrique gains - mises
- **Paris actifs** : Nombre de paris en cours

### Graphiques

1. **Évolution bankroll** : LineChart cumulatif (gains - pertes)
2. **Breakdown par championnat** : BarChart horizontal (ROI par compétition)
3. **Breakdown par confiance IA** : BarChart tranches de confiance (0-50%, 50-70%, etc.)

### 📝 Résumé mensuel IA

Bouton "Générer résumé mensuel" :

- **Powered by** : Mistral AI analyse toutes les données du mois
- **Contenu** : 
  - Synthèse performances (meilleurs/pires paris)
  - Tendances identifiées (sports rentables, erreurs récurrentes)
  - Recommandations stratégiques personnalisées
  - Objectifs suggérés pour le mois suivant

### 🔙 Backtest

Simulation rétrospective pour valider stratégies :

- **Paramètres** : Type jeu (paris/loto), seuil value bet, nb tirages/matchs
- **Résultats** : ROI simulé, variance, ratio Sharpe, drawdown max
- **Graphique** : Courbe equity hypothétique

---

### 🔔 Notifications push résultats

**Activation** : Paramètres > Notifications > "Activer les notifications jeux"

Types de notifications Web Push :

1. **Pari gagné** 🎉 : Affiche montant gain + action "Voir détails"
2. **Pari perdu** 😞 : Affiche perte + encouragement
3. **Résultat loto** 🎱 : Affiche numéros gagnants + votre résultat

**Implémentation** :

- Service Worker écoute messages backend
- Hook `useNotificationsJeux()` activé dans layout racine
- Toasts Sonner avec actions contextuelles
- Permission navigateur requise (demandée via bouton paramètres)

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
| ------------- | -------------- | ---------------------------------- |
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
| ----------- | ------------ | ------------------------------------- |
| `numeros`  | int[5]     | 5 numéros entre 1 et 50             |
| `etoiles`  | int[2]     | 2 étoiles entre 1 et 12             |
| `mise`     | decimal    | Montant joué                        |
| `date_tirage` | date   | Date du tirage                      |
| `gains`    | decimal    | Gains obtenus                       |

---

## API Reference

### Endpoints principaux

| Méthode | URL                           | Description                       |
| -------- | ------------------------------- | ----------------------------------- |
| GET    | `/api/v1/jeux/paris`          | Lister les paris                  |
| POST   | `/api/v1/jeux/paris`          | Ajouter un pari                   |
| PUT    | `/api/v1/jeux/paris/{id}`     | Modifier un pari (résultat)       |
| GET    | `/api/v1/jeux/paris/stats`    | Statistiques paris                |
| GET    | `/api/v1/jeux/loto`           | Lister les grilles loto           |
| POST   | `/api/v1/jeux/loto`           | Ajouter une grille                |
| GET    | `/api/v1/jeux/euromillions`   | Lister les grilles euromillions   |
| POST   | `/api/v1/jeux/euromillions`   | Ajouter une grille                |

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
