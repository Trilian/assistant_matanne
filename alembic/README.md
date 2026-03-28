# Alembic migrations — Assistant Matanne (ARCHIVÉ)

> **⚠️ Sprint 7 — 2026-03-28** : Alembic est **désactivé**.
>
> - Les migrations Alembic ont été absorbées dans `sql/INIT_COMPLET.sql`.
> - `alembic.ini` a été archivé en `alembic.ini.bak`.
> - Les artefacts techniques Alembic (`env.py`, `script.py.mako`, `versions/`) ont été retirés.

## Workflow actif

- Source de vérité schéma DB : `sql/INIT_COMPLET.sql`
- Application des changements : SQL direct + `GestionnaireMigrations`

Voir `docs/MIGRATION_GUIDE.md` pour les instructions à jour.

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
