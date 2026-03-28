# 📁 Migrations SQL — Archivé (Sprint 1)

> ⚠️ **Sprint 1 — 28 mars 2026** : Ce répertoire est archivé.
>
> Les 3 fichiers de migration (`001_routine_moment_journee.sql`, `002_standardize_user_id_uuid.sql`, `003_add_cotes_historique.sql`) ont été absorbés dans `sql/INIT_COMPLET.sql`.
>
> **Workflow actif** : `sql/INIT_COMPLET.sql` est la seule source de vérité pour le schéma DB.
> Voir `docs/MIGRATION_GUIDE.md` pour les instructions.


## Suivi

Les migrations appliquées sont trackées dans la table `schema_migrations` :

```sql
SELECT numero, description, applied_at FROM schema_migrations;
```
