# 🏠 Assistant Matanne

> Hub de gestion familiale intelligent propulsé par l'IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com)

## 🚀 Démarrage rapide

```bash
# 1. Cloner et installer
git clone <repo>
cd assistant_matanne
pip install -r requirements.txt

# 2. Configurer l'environnement
cp .env.example .env.local
# Éditer .env.local avec vos clés

# 3. Lancer
streamlit run src/app.py
```

## 📋 Fonctionnalités

| Module | Description |
|--------|-------------|
| 🍽️ **Cuisine** | Recettes, planning repas, suggestions IA, batch cooking |
| 🛒 **Courses** | Listes intelligentes, scan codes-barres, modèles |
| 📦 **Inventaire** | Stock, alertes péremption, seuils automatiques |
| 👶 **Famille** | Suivi Jules (développement), activités, bien-être |
| 💰 **Budget** | Suivi dépenses, budgets mensuels, alertes |
| 🏡 **Maison** | Projets, routines, jardin |
| 💪 **Santé** | Objectifs fitness, routines sport |
| 📅 **Planning** | Calendrier, synchronisation externe |

## 🏗️ Architecture

```
src/
├── app.py              # Point d'entrée Streamlit
├── core/               # Noyau applicatif
│   ├── config.py       # Configuration (Pydantic Settings)
│   ├── database.py     # Connexion PostgreSQL + migrations
│   ├── models/         # Modèles SQLAlchemy ORM
│   ├── decorators.py   # @with_db_session, @with_cache
│   └── ai/             # Client Mistral AI + cache sémantique
├── services/           # Logique métier
├── modules/            # Pages Streamlit (lazy loading)
└── ui/                 # Composants UI réutilisables
```

## ⚙️ Configuration

### Variables d'environnement (.env.local)

```env
# Base de données Supabase
DATABASE_URL=postgresql://user:password@host:5432/db

# IA Mistral
MISTRAL_API_KEY=your_key_here

# Optionnel
REDIS_URL=redis://localhost:6379
VAPID_PRIVATE_KEY=your_vapid_key
```

### Fichiers de configuration

| Fichier | Usage |
|---------|-------|
| `.env.local` | Variables d'environnement locales (prioritaire) |
| `.env` | Variables par défaut |
| `pyproject.toml` | Dépendances Poetry, config tests/lint |
| `alembic.ini` | Configuration migrations |

## 🗄️ Base de données

### Déployer sur Supabase

1. Ouvrir Supabase SQL Editor
2. Copier-coller le contenu de `sql/SUPABASE_COMPLET_V3.sql`
3. Exécuter

### Migrations locales (Alembic)

```bash
# Créer une migration
python manage.py create_migration "Description"

# Appliquer les migrations
python manage.py migrate

# Voir l'historique
alembic history
```

## 🧪 Tests

```bash
# Tous les tests avec couverture
python manage.py test_coverage

# Tests spécifiques
pytest tests/test_recettes.py -v

# Un seul test
pytest tests/test_budget.py::test_ajouter_depense -v
```

## 📝 Commandes utiles

```bash
# Lancer l'app
streamlit run src/app.py

# Formater le code
python manage.py format_code

# Linter
python manage.py lint

# Générer requirements.txt
python manage.py generate_requirements
```

## 📚 Documentation complémentaire

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture détaillée
- [ROADMAP.md](ROADMAP.md) - Roadmap et TODO
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Guide développeur Copilot

## 📄 Licence

Projet privé - Usage familial uniquement.
