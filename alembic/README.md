# Alembic migrations — Assistant Matanne

Ce dossier contient les migrations de base de données gérées par **Alembic**.

## Contexte

Le schéma initial de l'application est défini dans `sql/INIT_COMPLET.sql` et
appliqué directement sur Supabase. Le système de migrations SQL-file maison
(`GestionnaireMigrations`) gère les migrations `sql/migrations/V00x_***.sql`.

Alembic prend le relais pour les **migrations incrémentales** à partir de la
baseline `0001_initial_baseline`, offrant :
- Autogénération depuis les modèles SQLAlchemy (`--autogenerate`)
- Historique versionné et traçable
- Rollback fiable
- Génération SQL offline pour Supabase

## Démarrage sur une DB existante

Si la DB a déjà le schéma `sql/INIT_COMPLET.sql` appliqué :

```bash
# Marquer la DB comme étant à la baseline sans ré-exécuter de migration
alembic stamp head

# Vérifier l'état
alembic current
```

## Commandes courantes

```bash
# Générer une migration depuis les changements de modèles
alembic revision --autogenerate -m "ajout_table_taches"

# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer une migration spécifique
alembic upgrade +1

# Revenir en arrière d'une version
alembic downgrade -1

# Voir l'historique
alembic history --verbose

# Voir la version courante
alembic current
```

## Mode offline (Supabase)

Pour générer du SQL à appliquer manuellement via le SQL Editor Supabase :

```bash
alembic upgrade head --sql > migration_output.sql
```

## Convention de nommage

`YYYYMMDD_<révision>_<description_courte>.py`

Exemple : `20260401_a1b2c3d4_ajout_table_rappels.py`
