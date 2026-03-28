# Alembic migrations — Assistant Matanne (ARCHIVÉ)

> **⚠️ Sprint 1 — 2026-03-28** : Alembic est **désactivé**. Les versions Alembic ont été absorbées
> dans `sql/INIT_COMPLET.sql` (source de vérité unique). `alembic.ini` a été renommé en
> `alembic.ini.bak`. Le workflow actif est `INIT_COMPLET.sql` + `GestionnaireMigrations`.



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
