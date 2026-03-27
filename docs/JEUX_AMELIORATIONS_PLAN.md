# 🎮 Module Jeux - Améliorations Complètes (3 semaines)

## Vue d'ensemble

Implémentation complète du système expert pour Paris Sportifs, Loto et Euromillions avec IA, cron jobs et statistiques personnelles.

---

## 📦 Backend Services

### 1. **BankrollManager** (`src/services/jeux/bankroll_manager.py`)

**Objectif**: Gestion de bankroll avec critère de Kelly fractionnaire

**Méthodes clés**:
- `calculer_mise_kelly(bankroll, edge, cote)`: Calcule la mise optimale
  - Formule: `kelly = (edge × (cote - 1)) / (cote - 1)`
  - Multiplier fractionnaire: **25%** (conservateur)
  - Retourne: Mise suggérée en euros

- `valider_mise(mise, bankroll, seuil=0.05)`: Valide la mise
  - Seuil d'alerte: **3%** de la bankroll (warning)
  - Hard cap: **5%** de la bankroll (bloquant)
  - Retourne: `{"autorise": bool, "alerte": bool, "raison": str}`

- `obtenir_historique(user_id, jours=30)`: Historique bankroll
  - Query: Table `BankrollHistorique`
  - Format: `[{"date": "2024-01-15", "montant": 1000.0, "variation": 50.0}]`

**Utilisation**:
```python
from src.services.jeux.bankroll_manager import BankrollManager

manager = BankrollManager()
mise = manager.calculer_mise_kelly(bankroll=1000, edge=0.05, cote=2.5)
validation = manager.valider_mise(mise, 1000)
# mise = 20.0€, validation = {"autorise": True, "alerte": False}
```

---

### 2. **SeriesStatistiquesService** (`src/services/jeux/series_statistiques.py`)

**Objectif**: Détection de biais cognitifs dans les séries de paris

**Tests statistiques**:
1. **Runs Test** (scipy.stats): Détecte alternances non-aléatoires
2. **Chi-Square Test**: Identifie surreprésentation d'outcomes
3. **Z-Score**: Analyse écarts-types pour détecter patterns

**Patterns détectés**:
- **Hot Hand Fallacy**: Croire qu'une série gagnante continue
- **Gambler's Fallacy**: Penser qu'après pertes, victoire "due"
- **Régression à la moyenne**: Ignorer retour à performance moyenne

**Méthode principale**:
```python
def analyser_patterns_utilisateur(user_id: int) -> dict:
    """
    Retourne:
    {
        "regression_moyenne": {
            "alerte": bool,
            "severite": "faible" | "moyenne" | "elevee",
            "message": str,
            "details": dict,
            "type_pattern": str
        },
        "hot_hand": {...},
        "gamblers_fallacy": {...}
    }
    """
```

---

### 3. **EuromillionsIAService** (`src/services/jeux/euromillions_ia.py`)

**Objectif**: Génération IA de grilles Euromillions avec 4 stratégies

**Stratégies disponibles**:

1. **Équilibrée** (`generer_equilibree`):
   - 60% fréquences + 40% retards
   - Pool fusionné, sélection aléatoire pondérée
   - Target: Distribution équilibrée pairs/hauts

2. **Fréquences** (`generer_frequences`):
   - Top 10 numéros les plus tirés (historique)
   - Pondération par fréquence
   - Étoiles: Mêmes critères

3. **Retards** (`generer_retards`):
   - Top 10 numéros avec retard maximal
   - "Compensatoire" (assume rattrapage)
   - Pondération inverse du retard

4. **IA Creative** (`generer_ia_creative`):
   - Appel LLM Mistral-7B via OpenRouter
   - Prompt: Stats + consignes créatives
   - Parsing JSON: `{"numeros": [1-50], "etoiles": [1-12]}`

**Quality Scoring**:
```python
def calculer_qualite_grille(numeros, etoiles) -> float:
    """
    Base score: 50
    + 15 si 45-55% pairs
    + 15 si 50-60% hauts (26-50)
    + 20 si somme 130-200
    Max: 100
    """
```

**Exemple**:
```python
from src.services.jeux.euromillions_ia import EuromillionsIAService

svc = EuromillionsIAService()
grille = svc.generer_equilibree()
# {"numeros": [7, 14, 23, 38, 49], "etoiles": [3, 9], "qualite": 85}
```

---

### 4. **StatsPersonnellesService** (`src/services/jeux/stats_personnelles.py`)

**Objectif**: Analyse de performances personnelles multi-jeux

**Méthodes**:

- `calculer_roi_global(user_id, jours=30)`:
  - ROI = (Gains - Mises) / Mises × 100
  - Agrège Paris + Loto + Euromillions
  - Retourne: `{"roi": float, "benefice_net": float, "nb_paris": int}`

- `calculer_win_rate(user_id, jours=30)`:
  - % paris gagnants par type
  - Retourne: `{"win_rate_global": float, "win_rate_paris": float, ...}`

- `analyser_patterns_gagnants(user_id, jours=90)`:
  - Identifie meilleurs types paris/stratégies
  - ROI par type de pari
  - Recommandations personnalisées

- `obtenir_evolution_mensuelle(user_id, mois=6)`:
  - ROI + Bénéfice par mois (6 derniers)
  - Format: `[{"mois": "2024-01", "roi": 5.2, "benefice": 120.0}]`

---

### 5. **Cron Jobs Paris** (`src/services/jeux/cron_jobs.py`)

**4 jobs automatisés**:

| Job | Fréquence | API | Description |
|-----|-----------|-----|-------------|
| `scraper_cotes_sportives` | 2h | The Odds API | Récupère cotes matchs Ligue 1 |
| `scraper_resultats_matchs` | 23h | API-Football | Met à jour scores finaux |
| `detecter_opportunites` | 30min | — | Calcule EV, détecte value bets |
| `analyser_series` | 9h | — | Lance tests statistiques patterns |

**Configuration**:
```python
from apscheduler.triggers.cron import CronTrigger

scheduler.add_job(
    scraper_cotes_sportives,
    trigger=CronTrigger(hour="*/2"),  # Toutes les 2h
    id="scraper_cotes",
    max_instances=1
)
```

**Limites API**:
- The Odds API: 360 requêtes/mois (500 limite)
- API-Football: 30 requêtes/mois (100 limite)

---

### 6. **Cron Jobs Loteries** (`src/services/jeux/cron_jobs_loteries.py`)

**2 jobs automatisés**:

| Job | Fréquence | Description |
|-----|-----------|-------------|
| `scraper_resultats_fdj` | 21h30 | Scrape résultats Loto + Euromillions |
| `backtest_grilles` | 22h | Compare grilles vs tirages, calcul gains |

**Backtest Logic**:
- Loto: 8 rangs (5N+C → 2N)
- Euromillions: 10 rangs (5N+2E → 2N)
- Met à jour: `GrilleLoto.backtest`, `statut` (gagnant/perdant)

**Barème gains** (estimés):
```python
# Loto
Rang 1: 5N + C → 1M€
Rang 2: 5N → 20k€
...
Rang 8: 2N → 2€

# Euromillions
Rang 1: 5N + 2E → 10M€
Rang 2: 5N + 1E → 100k€
...
Rang 10: 2N → 2€
```

---

### 7. **Scheduler Global** (`src/services/core/cron.py`)

**Lifecycle management**:
```python
from src.services.core.cron import demarrer_scheduler, arreter_scheduler

# Au startup FastAPI (main.py lifespan)
demarrer_scheduler()
# Enregistre 6 jobs (4 paris + 2 loteries)

# Au shutdown
arreter_scheduler()
```

**Configuration**:
- Timezone: `Europe/Paris`
- `coalesce=True`: Fusionne exécutions manquées
- `max_instances=1`: 1 seule instance par job
- `misfire_grace_time=300`: 5min tolérance retard

---

## 🎨 Frontend Components

### 1. **BankrollWidget** (`frontend/src/composants/jeux/bankroll-widget.tsx`)

**Fonctionnalités**:
- Graphique Chart.js: Évolution bankroll 30 derniers jours
- Calculateur Kelly temps réel (inputs: bankroll, cote, edge)
- Affichage validation: Couleur (vert <3%, jaune 3-5%, rouge >5%)

**Props**:
```typescript
interface BankrollWidgetProps {
  userId: number
}
```

**State**:
```typescript
const [bankroll, setBankroll] = useState<string>("")
const [mise, setMise] = useState<string>("")
const [cote, setCote] = useState<string>("")
const [edge, setEdge] = useState<string>("")
```

**Chart Config**:
- Type: Line chart
- Dataset: Montant bankroll par jour
- Tension: 0.1 (légère courbe)
- Fill: true (aire sous courbe)

---

### 2. **DetectionPatternModal** (`frontend/src/composants/jeux/detection-pattern-modal.tsx`)

**Tabs**:
1. 🔥 **Hot Hand**: Messages éducatifs sur illusion "série chaude"
2. 🎲 **Gambler's Fallacy**: Explications "loi des grands nombres"
3. 📉 **Régression à la moyenne**: Conseils retour performance moyenne

**Persistence**:
```typescript
localStorage.setItem(`jeux_patterns_cache_dismissed_${pattern}`, "true")
// Cache dismiss pendant 7 jours
```

**Props**:
```typescript
interface Props {
  patterns: ResultatTest[]  // Filtré: seulement patterns avec alerte=true
  open: boolean
  onClose: () => void
}
```

---

### 3. **TableauLotoExpert** (`frontend/src/composants/jeux/tableau-loto-expert.tsx`)

**6 Filtres**:
- `qualite_min`: Slider 0-100
- `nb_pairs`: Select (tous, 2, 3, 4)
- `somme_min/max`: Input number
- `search`: Input text (filtre numéros)

**Colonnes**:
| Colonne | Type | Description |
|---------|------|-------------|
| Numéros | Badges | 5 numéros + chance |
| Stratégie | Badge | equilibree/frequences/retards/ia |
| Qualité | % coloré | Vert ≥70, Jaune 50-69, Rouge <50 |
| Pairs/Impairs | Text | "3P-2I" |
| Hauts/Bas | Text | "2H-3B" |
| Somme | Number | Somme des 5 numéros |
| Date | Date | Date tirage |
| Gains | €/— | Montant ou tiret si non joué |

**Export CSV**:
- react-csv library
- 9 colonnes complètes
- Filename: `loto_expert_YYYYMMDD.csv`

---

### 4. **TableauEuromillionsExpert** (`frontend/src/composants/jeux/tableau-euromillions-expert.tsx`)

**Similaire Loto** avec adaptations:
- 5 numéros + 2 étoiles (colonnes séparées)
- Filtre stratégie: 4 options (equilibree, frequences, retards, ia_creative)
- Analyse: Distribution numeros + étoiles

---

### 5. **StatsPersonnelles** (`frontend/src/composants/jeux/stats-personnelles.tsx`)

**4 Cartes métriques**:
1. **ROI Global**: % avec icône TrendingUp/Down
2. **Win Rate**: % avec icône Target
3. **Bénéfice Net**: € avec icône Trophy
4. **Activité**: Nombre paris + grilles

**3 Tabs**:
1. **Évolution**: Chart.js dual-axis (Bénéfice €, ROI %)
2. **Patterns**: Recommandations + ROI par type + Meilleures stratégies
3. **Détails**: Win rate par jeu + Résumé financier

**Sélecteur période**:
- 7 jours, 30 jours, 90 jours, 6 mois, 1 an

---

## 🔌 API Endpoints

### Paris Sportifs

```http
GET /api/v1/jeux/bankroll/{user_id}
# Retourne: {"historique": [...], "bankroll_actuel": 1000.0}

POST /api/v1/jeux/bankroll/suggestion-mise
# Body: {"bankroll": 1000, "edge": 0.05, "cote": 2.5}
# Retourne: {"mise_suggeree": 20.0, "validation": {...}}

GET /api/v1/jeux/paris/analyse-patterns/{user_id}
# Retourne: {"regression_moyenne": {...}, "hot_hand": {...}, ...}
```

### Euromillions

```http
GET /api/v1/jeux/euromillions/grilles-expert?qualite_min=50&strategie=ia_creative
# Retourne: {"items": [{"id", "numeros", "etoiles", "qualite", ...}]}
```

### Loto

```http
GET /api/v1/jeux/loto/grilles-expert?qualite_min=60
# Retourne: {"items": [...]}
```

### Stats Personnelles

```http
GET /api/v1/jeux/stats/personnelles/{user_id}?periode=30
# Retourne: {
#   "roi": {...},
#   "win_rate": {...},
#   "patterns": {...},
#   "evolution": [...]
# }
```

---

## 📊 Modèles de données

### Nouveaux champs backtest

**GrilleLoto**:
```python
backtest = Column(JSON)
# Structure:
{
    "rang": int,        # 1-8 (0 si perdant)
    "nb_bons": int,     # Nombre bons numéros
    "chance_ok": bool,  # Numéro chance correct
    "gain": float       # Montant gagné (0 si perdant)
}
```

**GrilleEuromillions**:
```python
backtest = Column(JSON)
# Structure:
{
    "rang": int,                # 1-10
    "nb_bons_numeros": int,     # 0-5
    "nb_bonnes_etoiles": int,   # 0-2
    "gain": float
}
```

---

## 🧪 Tests & Validation

### Tests unitaires recommandés

```python
# Backend - Kelly Criterion
def test_kelly_calculation():
    manager = BankrollManager()
    mise = manager.calculer_mise_kelly(1000, 0.05, 2.5)
    assert 15 < mise < 25  # Varie selon formule exacte

# Backend - Quality Score
def test_euromillions_quality():
    svc = EuromillionsIAService()
    qualite = svc.calculer_qualite_grille([10, 20, 30, 40, 50], [3, 9])
    assert 0 <= qualite <= 100
    # Test edge cases: tous pairs, somme extrême
```

```typescript
// Frontend - Bankroll calculation
describe('BankrollWidget', () => {
  it('calculates Kelly suggestion correctly', () => {
    const suggestion = useMemo(() => {
      const b = 1000, c = 2.5, e = 0.05
      const kelly = (e * (c - 1)) / (c - 1) * 0.25
      return b * kelly
    }, [])
    expect(suggestion).toBeGreaterThan(0)
    expect(suggestion).toBeLessThan(1000 * 0.05)  // Hard cap
  })
})
```

---

## 🚀 Déploiement

### Configuration requise

**Variables d'environnement** (`.env.local`):
```bash
# APIs externes
ODDS_API_KEY=your_odds_api_key
RAPIDAPI_KEY=your_rapidapi_key
OPENROUTER_API_KEY=your_openrouter_key

# Cron jobs
ENABLE_CRON_JOBS=true
CRON_TIMEZONE=Europe/Paris
```

**Dépendances Python** (pyproject.toml):
```toml
[tool.poetry.dependencies]
apscheduler = "^3.10.0"
scipy = "^1.11.0"
httpx = "^0.24.0"
```

**Dépendances Frontend** (package.json):
```json
{
  "dependencies": {
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "react-csv": "^2.2.2"
  }
}
```

### Checklist déploiement

- [ ] Migrations DB: Vérifier champs `backtest` dans GrilleLoto/GrilleEuromillions
- [ ] Clés API: Configurer The Odds API, API-Football, OpenRouter
- [ ] Cron: Vérifier `demarrer_scheduler()` appelé dans `main.py` lifespan
- [ ] Tests: Exécuter `pytest tests/services/jeux/` (minimum)
- [ ] Frontend: Build Next.js sans erreurs (`npm run build`)
- [ ] Monitoring: Activer logs APScheduler niveau INFO

---

## 📈 Améliorations futures

### Court terme (Sprint +1)
- Tests E2E Playwright pour workflow complet
- Export PDF stats personnelles
- Notifications push pour value bets détectés

### Moyen terme (Phase suivante)
- Multi-bookmakers (comparaison cotes Betclic/PMU/Unibet)
- Backtest historique 5 ans (optimisation stratégies)
- Cash-out simulator (calcul hedge bets)

### Long terme (Roadmap)
- Modèle ML prédictif (Random Forest sur features matchs)
- API publique (webhook value bets pour partenaires)
- Dashboard analytics avancé (Streamlit/Metabase)

---

## 🤝 Contribution

**Structure des commits**:
```
feat(jeux): Add EuromillionsIAService with 4 generation strategies
fix(jeux): Correct Kelly formula fractional multiplier (0.25)
docs(jeux): Update API reference for stats personnelles endpoint
```

**Convention nommage**:
- Backend: Français (variables, fonctions, docstrings)
- Frontend: Français (hooks `utiliser-`, composants descriptifs)
- Tests: `test_{feature}_{scenario}` (en anglais)

---

## 📚 Références

- **Critère de Kelly**: https://en.wikipedia.org/wiki/Kelly_criterion
- **Runs Test**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.runs_test.html
- **APScheduler**: https://apscheduler.readthedocs.io/
- **Chart.js**: https://www.chartjs.org/docs/
- **Barème FDJ Loto**: https://www.fdj.fr/jeux-de-tirage/loto
- **Barème FDJ Euromillions**: https://www.fdj.fr/jeux-de-tirage/euromillions

---

**Version**: 1.0.0  
**Date**: 2024-01  
**Auteurs**: Équipe dev assistant_matanne
