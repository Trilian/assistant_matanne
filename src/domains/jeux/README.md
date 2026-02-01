# 🎲 Module Jeux - Guide Complet

## Vue d'ensemble

Le module **Jeux** propose deux fonctionnalités principales:

1. **⚽ Paris Sportifs** - Suivre et prédire les matchs européens
2. **🎰 Loto** - Analyser les probabilités et tester des stratégies

> ⚠️ **Important**: Ces outils sont à **titre éducatif**. Les prédictions ne sont pas garanties et le jeu comporte des risques.

---

## 📋 Table des matières

1. [Configuration initiale](#configuration-initiale)
2. [Paris Sportifs](#paris-sportifs)
3. [Loto](#loto)
4. [Architecture](#architecture)
5. [APIs utilisées](#apis-utilisées)
6. [Troubleshooting](#troubleshooting)

---

## Configuration initiale

### Étape 1: Obtenir une clé API Football-Data.org

1. Aller sur [https://www.football-data.org](https://www.football-data.org)
2. Cliquer sur **Register** (gratuit)
3. Confirmer votre email
4. Copier votre token dans `.env.local`:

```env
FOOTBALL_DATA_API_KEY=votre_token_ici
```

### Étape 2: Exécuter le setup de la BD

```bash
# Créer les tables (si pas encore fait)
python manage.py migrate

# Ou manuellement:
# - Copier le contenu de sql/013_add_jeux_tables_manual.sql
# - Exécuter dans Supabase SQL Editor
```

### Étape 3: Tester les APIs

```bash
python tests/test_jeux_apis.py
```

Vous devriez voir:

```
✅ PASS - Football-Data API
✅ PASS - FDJ Loto Scraper
✅ PASS - UI Helpers
```

---

## ⚽ Paris Sportifs

### Accès

Menu principal → 🎲 Jeux → ⚽ Paris Sportifs

### Fonctionnalités

#### 📊 Tab 1: Prédictions

Affiche les matchs à venir avec:

- **Probabilités**: % victoire domicile/nul/extérieur
- **Confiance**: Entre 40% et 100% selon la fiabilité
- **Cotes recommandées**: Basées sur le modèle prédictif
- **Forme des équipes**: Derniers 5 matchs avec scoring
- **H2H**: Historique face-à-face

**Modèle de prédiction** (sophistiqué):

```
Probabilité = 40% × Forme + 12% × Avantage domicile
             + 20% × H2H + 10% × Cotes bookmakers
             + 10% × Contexte (blessures, etc)
```

#### 💰 Tab 2: Dashboard Performance

Suivi de vos paris:

- Profit/Perte total en unités
- ROI % (Return on Investment)
- Taux de réussite
- Graphique des gains cumulés
- Comparaison: théorique vs réel

#### 📈 Tab 3: Statistiques Championnats

Analyse par championnat:

- Classement à jour
- Statistiques équipes (buts, points)
- Tendances de marquage
- % d'over/under

#### ⚙️ Tab 4: Gestion des données

- Ajouter équipes manuellement
- Saisir les résultats de matchs
- Synchroniser avec l'API
- Voir l'historique

### Workflow recommandé

1. **Lundi matin**: Actualiser les matchs de la semaine

   ```
   Cliquer "🔄 Actualiser depuis API"
   ```

2. **Analyser les prédictions**
   - Lire les probabilités
   - Vérifier la confiance du modèle
   - Comparer avec vos propres analyses

3. **Saisir les paris**
   - Cliquer "➕ Enregistrer un pari"
   - Entrer mise, cote
   - Cocher "Virtual" pour tester sans argent

4. **Mettre à jour les résultats**
   - Après le match, synchroniser les scores
   - Système calcule le gain automatiquement

5. **Analyser le Dashboard**
   - Voir l'évolution de votre ROI
   - Identifier les points forts/faibles

### Stratégie suggérée

```
✅ À faire:
- Miser quand confiance > 70%
- Suivre le modèle strictement (discipline)
- Tester en "Virtual" d'abord
- Analyser les récits échoués
- Miser petit (1-5% du bankroll par pari)

❌ À éviter:
- Miser sur faible confiance
- Suivre ses intuitions vs le modèle
- Effet de recency (dernier match)
- Surestimer les chances
- Miser grosse (risque de ruine)
```

---

## 🎰 Loto

### Accès

Menu principal → 🎲 Jeux → 🎰 Loto

### Fonctionnalités

#### 📊 Tab 1: Statistiques

Affiche l'analyse des derniers 50 tirages:

- **Fréquence de chaque numéro** (1-49)
- **Numéros chauds**: Sortis plus souvent
- **Numéros froids**: Sortis moins souvent
- **Paires fréquentes**: Souvent sorties ensemble
- **Heatmap visuelle**: Couleurs = fréquence

#### 🎫 Tab 2: Générateur de grilles

**6 stratégies** pour générer vos tickets:

1. **Aléatoire** 🎲
   - Tirage complètement aléatoire
   - Référence pour comparer

2. **Équilibrée** ⚖️
   - Mix de numéros pairs/impairs
   - Mix de petits/grands
   - Idéal pour couvrir l'espace

3. **Chauds** 🔥
   - Utilise les numéros sortis souvent
   - Logique: pattern peut continuer

4. **Froids** ❄️
   - Utilise les numéros peu sortis
   - Logique: due pour correction statistique

5. **Débordement** 📈
   - Utilise les tendances fortes
   - Ajuste selon paires fréquentes

6. **Contre-Intuitif** 🤔
   - Évite les numéros trop populaires
   - Logique: moins de gagnants si vous trouvez

**Comment utiliser**:

```python
1. Sélectionner la stratégie
2. Cliquer "Générer grille"
3. Affichage: 5 numéros + 1 numéro chance
4. Cliquer "Copier" pour noter/jouer
5. Cliquer "Sauvegarder" pour tracker
```

#### 🧪 Tab 3: Simulation (Backtesting)

Teste une stratégie sur l'historique:

```
Sélectionner stratégie → Cliquer "Simuler"
↓
Résultat pour les 50 derniers tirages:
- Nombre de matchs (tickets qui gagnent)
- Répartition des gains
- ROI réel vs inversions théoriques
```

**Interprétation**:

- ROI > 0% → Stratégie légèrement profitable
- ROI < 0% → Attendu (jeu déficitaire par design)
- Comparaison stratégies → Identifier la moins mauvaise

#### 📐 Tab 4: Espérance mathématique

**Vérité sur la Loto FDJ**:

```
Espérance = -51%

= Vous jouez 100€ en moyenne
  → Gain attendu = 49€
  → Perte = 51€

Raison: La FDJ prend 50% et rend les 50% en gains
```

C'est voulu et légal! Le jeu n'est **jamais rentable** sur le long terme.

### ⚠️ Important: Réclamation d'équité

> Cette page utilise des **analyses statistiques pures**. Aucun pattern réel ne peut prédire la loto. Les numéros "chauds" et "froids" n'affectent pas les tirages futurs (probabilité indépendante). Cet outil est **éducatif** pour démontrer les concepts statistiques.

---

## 🏗️ Architecture

### Fichiers clés

```
src/domains/jeux/
├── __init__.py                      # Entrypoint module
├── logic/
│   ├── __init__.py
│   ├── paris_logic.py              # ~600 lignes: ML predictions
│   ├── loto_logic.py               # ~750 lignes: Statistical analysis
│   ├── api_football.py             # Football-Data.org client
│   ├── scraper_loto.py             # FDJ web scraper
│   ├── api_service.py              # Service layer (sync BD<->API)
│   └── ui_helpers.py               # UI utilities with fallback
└── ui/
    ├── __init__.py
    ├── paris.py                    # Streamlit UI pour paris
    └── loto.py                     # Streamlit UI pour loto

src/core/models/
└── jeux.py                         # SQLAlchemy models (7 tables)

tests/
└── test_jeux_apis.py              # Test suite
```

### Stack technologique

| Composant      | Technologie                     |
| -------------- | ------------------------------- |
| Framework      | Streamlit 1.52+                 |
| Prédictions    | ML Ensemble (5 factors)         |
| Visualisations | Plotly 5.24+                    |
| Données        | PostgreSQL via SQLAlchemy 2.0   |
| APIs           | Football-Data.org + Web scraper |
| Cache          | Streamlit @st.cache_data        |

### Flux de données

```
┌─────────────────────────────────────────────────────┐
│                    UTILISATEUR                      │
│              (Streamlit UI)                         │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼─────┐              ┌───────▼────┐
   │ Paris.py │              │  Loto.py   │
   └────┬─────┘              └───────┬────┘
        │                             │
   ┌────▼───────────────────────────┬┘
   │  ui_helpers.py (fallback)      │
   │  ┌────────────────────────────┘│
   │  │                             │
┌──▼──▼──────────┐         ┌────────▼──────┐
│  API Football  │         │  Scraper Loto │
│  (live data)   │         │  (FDJ web)    │
└──┬────────────┘         └────────┬───────┘
   │                               │
   └───────────────┬───────────────┘
                   │
          ┌────────▼────────┐
          │  PostgreSQL BD  │
          │ (cache/history) │
          └─────────────────┘
```

### Modèles de prédiction

**Paris Sportifs** (ML Ensemble):

```python
proba_victoire_domicile = (
    0.40 * forme_domicile +
    0.12 * BONUS_DOMICILE +
    0.20 * h2h_domicile +
    0.10 * (1 / cote_domicile) +  # Inverse bookmakers
    0.18 * facteurs_contexte
)
```

**Loto** (Statistical):

```python
# Fréquence + Patterns + Hot/Cold
# PAS de prédiction (jeu d'aléa pur)
# Juste analyse pour trouver la "moins mauvaise" stratégie
```

---

## 🌐 APIs utilisées

### Football-Data.org

**Documentation**: [https://www.football-data.org/client/register](https://www.football-data.org/client/register)

**Endpoints utilisés**:

```
GET /competitions/{id}/matches       # Matchs à venir/passés
GET /competitions/{id}/standings     # Classement
GET /teams/{id}/matches              # Historique équipe
GET /teams                           # Recherche équipe
```

**Limitations gratuit**:

- ✅ 10 req/min
- ✅ 10 ans d'historique
- ✅ Tous les championnats majeurs
- ❌ Cotes de paris (premium)
- ❌ Données en temps réel (2h delay)

### FDJ Web Scraper

**URL**: https://www.fdj.fr/jeux/loto

**Limitations**:

- ~50 tirages historiques accessibles
- Peut être lent (1-5 sec)
- Pas d'API officielle (scraping fragile)

**Fallback**: Données en cache BD après 1ère sync

---

## 🔧 Troubleshooting

### ❓ Q: "Clé API non trouvée"

**A**: Vérifier `.env.local`:

```bash
# Afficher les variables
python -c "from src.core.config import obtenir_parametres; print(obtenir_parametres())"
```

Si manquante, ajouter:

```env
FOOTBALL_DATA_API_KEY=votre_token_ici
```

---

### ❓ Q: "Aucun match n'apparaît"

**A**: Les options:

1. Vérifier que matches existent (pas en été)
2. Vérifier connexion API: `python tests/test_jeux_apis.py`
3. Vérifier que les tables BD existent: `SELECT * FROM jeux_matchs;` (Supabase)
4. Fallback BD fonctionne toujours (même sans API)

---

### ❓ Q: "Les prédictions sont incorrectes"

**A**: C'est normal! Le modèle:

- ✅ Meilleur que hasard (~35-45% vs 33% random)
- ❌ Pas aussi bon qu'on aimerait (~70%+ requis pour rentable)
- Dépend de: Form, H2H, injuries, motivation, etc

**C'est un jeu difficile!**

---

### ❓ Q: "Scraper Loto échoue"

**A**: Options:

1. FDJ bloque les scrapers (temporaire) → Attendre 5 min
2. Format FDJ changé → Fallback BD automatique
3. Internet down → Utiliser cache local

```bash
# Tester:
python -c "
from src.domains.jeux.logic.scraper_loto import charger_tirages_loto
tirages = charger_tirages_loto(10)
print(len(tirages))
"
```

---

### ❓ Q: "Performance lente"

**A**: Cache manquant! Streamlit l'ajoute:

```python
# Première fois: 3-5 sec
# Fois suivantes (30 min): <100ms
```

Forcer rafraîchir:

```
Cliquer "C" en haut à droite du navigateur
Puis "🔄 Actualiser depuis API"
```

---

## 📚 Ressources

- [Copilot Instructions Complètes](../copilot-instructions.md)
- [Configuration APIs Détaillée](../APIS_CONFIGURATION.md)
- [Architecture Générale](docs/ARCHITECTURE.md)
- [Guide SQLAlchemy](docs/SQLALCHEMY_SESSION_GUIDE.md)

---

## 💡 Conseils finaux

✅ **À faire**:

- Utiliser les modèles comme **guide** pas loi absolue
- Combiner avec votre analyse personnelle
- Tester en virtual d'abord
- Gérer le bankroll (Kelly criterion)
- Apprendre des échecs

❌ **À ÉVITER**:

- Croire le modèle à 100%
- Miser grosse (risque de ruine)
- Jeu émotionnel (après perte)
- Dépendance au jeu

**Bonne chance! 🍀**
