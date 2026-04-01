# Scripts — Guide d'utilisation

Scripts utilitaires pour le développement, le déploiement et la maintenance d'Assistant Matanne.

> **Prérequis** : Être à la racine du projet. Variables d'environnement chargées depuis `.env.local`.

---

## _archive/ *(scripts legacy, non exécutés en routine)*

Scripts historiques conservés pour audit/référence. Voir `scripts/_archive/README.md`.

---

## analysis/ *(outils ad-hoc, exécution manuelle)*

### `analyze_api.py`
Analyse les routes FastAPI dans `src/api/`, détecte les patterns, et suggère des améliorations (endpoints manquants, conventions non respectées).

```bash
python scripts/analysis/analyze_api.py
```

### `audit_metrics.py`
Audit rapide des métriques du codebase : nombre de fichiers Python et lignes de code par répertoire (`src/api/`, `src/core/`, `src/services/`) + tests.

```bash
python scripts/analysis/audit_metrics.py
```

---

## db/ *(intégrés à `manage.py`)*

### `check_db.py`
Vérifie la connexion à la base de données en lançant un `SELECT 1`. Affiche les détails d'erreur si la connexion échoue.

```bash
python manage.py check-db
# ou directement :
python scripts/db/check_db.py
```

### `deploy_supabase.py`
Déploie le schéma SQL vers Supabase via `psycopg2`. Supporte plusieurs modes :

```bash
python manage.py deploy-schema
# ou directement :
python scripts/db/deploy_supabase.py --check      # Vérifie les migrations en attente
python scripts/db/deploy_supabase.py --deploy     # Applique les migrations
python scripts/db/deploy_supabase.py --status     # Affiche l'état des migrations
python scripts/db/deploy_supabase.py --rollback   # Annule la dernière migration
```

### `import_recettes.py`
Importe les recettes standard depuis `data/seed/recettes_standard.json` dans la base de données (modèles `Recette`, `Ingredient`, `Etape`).

```bash
python manage.py seed-recipes
# ou directement :
python scripts/db/import_recettes.py
```

### `reset_supabase.py`
**⚠️ DESTRUCTIF** — Supprime et recrée le schéma complet Supabase. Toutes les données sont perdues.

```bash
python manage.py reset-supabase
# ou directement :
python scripts/db/reset_supabase.py
```

### `seed_data.py`
Génère des données de démonstration réalistes : jardin, bien-être, planning, ingrédients, inventaire.

```bash
python manage.py seed-demo
# ou directement :
python scripts/db/seed_data.py
```

---

## setup/ *(configuration initiale, exécution ponctuelle)*

### `convert_to_utf8.py` *(utilisé en CI/CD)*
Détecte et supprime les BOM UTF-8 (`\xef\xbb\xbf`) des fichiers Python.

```bash
python scripts/setup/convert_to_utf8.py --check    # Vérifie sans modifier
python scripts/setup/convert_to_utf8.py --fix      # Corrige les fichiers
python scripts/setup/convert_to_utf8.py --verbose  # Mode verbeux
```

### `generate_vapid.py`
Génère une paire de clés VAPID (EC P-256, base64) pour les notifications push. Affiche les valeurs à copier dans `.env.local`.

```bash
python scripts/setup/generate_vapid.py
```

### `setup_api_key.py`
Configuration interactive de la clé API Football-Data.org (statistiques sportives, 10 req/min en tier gratuit). Écrit la clé dans `.env.local`.

```bash
python scripts/setup/setup_api_key.py
```

---

## test/ *(intégrés à `manage.py`)*

### `audit_tests_fast.py`
Audit rapide des tests : mapping source → fichier de test, détection des patterns inefficaces (hasattr-only, import-only, mocking excessif), score qualité 0-100. Génère un rapport CSV.

```bash
python manage.py audit-tests
# ou directement :
python scripts/test/audit_tests_fast.py
```

### `test_manager.py`
Orchestrateur principal des tests avec interface CLI. Génère des rapports HTML.

```bash
python manage.py test-quick                      # Tests rapides
python manage.py test-core                       # Tests core
# ou directement :
python scripts/test/test_manager.py all          # Tous les tests
python scripts/test/test_manager.py coverage     # Avec couverture
python scripts/test/test_manager.py core         # Tests core uniquement
python scripts/test/test_manager.py services     # Tests services uniquement
python scripts/test/test_manager.py integration  # Tests d'intégration
python scripts/test/test_manager.py quick        # Tests rapides (sans benchmarks)
```

> Voir aussi : `python manage.py test_coverage` qui lance `pytest --cov` directement.
