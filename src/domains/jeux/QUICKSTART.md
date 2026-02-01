# 🚀 Démarrage Rapide - Module Jeux

## ⏱️ 5 minutes pour démarrer

### 1. Obtenir la clé API (2 min)

```bash
# Aller sur https://www.football-data.org/client/register
# S'inscrire (gratuit)
# Confirmer email
# Copier le token
```

### 2. Configurer (.env.local)

```env
FOOTBALL_DATA_API_KEY=votre_token_ici
```

### 3. Créer les tables BD (optionnel)

```bash
# Si pas encore fait:
python manage.py migrate

# Ou manuellement:
# Copier sql/013_add_jeux_tables_manual.sql
# Exécuter dans Supabase SQL Editor
```

### 4. Lancer l'app

```bash
streamlit run src/app.py
```

### 5. Naviguer vers 🎲 Jeux

**Menu → 🎲 Jeux → Choisir:**

- ⚽ Paris Sportifs
- 🎰 Loto

---

## 🎯 Utilisation rapide

### ⚽ Paris Sportifs

```
1. "🔄 Actualiser" → Charge les matchs de la semaine
2. Analyser les prédictions (% de victoire)
3. Cliquer sur un match pour plus de détails
4. "➕ Enregistrer pari" → Tracker vos paris
5. Dashboard → Voir votre profit/ROI
```

### 🎰 Loto

```
1. "Statistiques" → Voir fréquences des numéros
2. "Générateur" → Choisir une stratégie
3. "Générer grille" → Créer vos tickets
4. "Simulation" → Tester une stratégie sur l'historique
5. "Espérance" → Comprendre pourquoi on perd (math!)
```

---

## 📦 Ce qui est inclus

✅ **Paris Sportifs**:

- ⚽ Matchs Ligue 1, Premier League, La Liga, Serie A, Bundesliga
- 🔮 Prédictions ML avec 5 facteurs (forme, H2H, domicile, odds, contexte)
- 📊 Dashboard de performance avec ROI tracking
- 💾 Historique complet des paris

✅ **Loto**:

- 🎰 Analyse statistique FDJ
- 🔥 Numéros chauds/froids
- 🎲 6 stratégies différentes de génération
- 🧪 Backtesting (tester sur 50 tirages)
- 📐 Espérance mathématique (pourquoi -51%)

✅ **APIs intégrées**:

- 🌐 Football-Data.org (live data)
- 🕷️ FDJ Web Scraper (historique Loto)
- 📦 Fallback BD automatique (fonctionne sans API)

---

## 🔧 Configuration avancée

### Variable d'env supplémentaires

```env
# Football-Data API key (requis pour live)
FOOTBALL_DATA_API_KEY=token_here

# Cache TTL (en secondes)
JEUX_CACHE_TTL=1800  # 30 min par défaut

# Limite de requêtes API (fallback si dépassée)
JEUX_API_TIMEOUT=10
```

### Synchronisation automatique (cron)

```python
# Dans votre cron job (ex: tous les jours à 9h)
from src.domains.jeux.logic.api_service import (
    synchroniser_matchs_api_vers_bd,
    synchroniser_resultats_matches_api
)

synchroniser_matchs_api_vers_bd("Ligue 1", jours=14)
synchroniser_resultats_matches_api("Ligue 1")
```

---

## 🐛 Troubleshooting rapide

| Problème                   | Solution                                               |
| -------------------------- | ------------------------------------------------------ |
| "Clé API non trouvée"      | Vérifier `.env.local` et relancer app                  |
| "Aucun match"              | Cliquer "🔄 Actualiser" ou vérifier internet           |
| "Scraper Loto échoue"      | Normal (FDJ bloque temps en temps), fallback BD existe |
| "Performance lente"        | 1ère fois = 3-5sec, puis cache <100ms                  |
| "Tables BD n'existent pas" | `python manage.py migrate` ou SQL manuel               |

---

## 📚 Docs complètes

- **Guide complet**: [README.md](README.md)
- **Config APIs**: [APIS_CONFIGURATION.md](../../APIS_CONFIGURATION.md)
- **Tests**: `python tests/test_jeux_apis.py`
- **Architecture générale**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 💡 Pro Tips

✨ **Pour une meilleure expérience**:

```python
# 1. Utiliser "Virtual" mode d'abord (pas d'argent réel)
# 2. Comparer vos prédictions vs le modèle
# 3. Tracker vos paris pour apprendre
# 4. Ne JAMAIS miser plus de 5% du bankroll
# 5. Combine modèle + analyse personnelle
```

---

## ✅ Vérifier que tout marche

```bash
# Test complet (2 minutes)
python tests/test_jeux_apis.py

# Résultat attendu:
# ✅ PASS - Football-Data API
# ✅ PASS - FDJ Loto Scraper
# ✅ PASS - UI Helpers
```

---

**Vous êtes prêt! Lancez l'app et explorez! 🚀**

Pour chaque question: Consultez [README.md](README.md) ou créez une issue.
