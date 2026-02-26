# Archive des migrations SQL

Ces fichiers de migration ont été **consolidés** dans `sql/INIT_COMPLET.sql` (v3.0).

Ils sont conservés ici à titre d'historique uniquement. Pour une installation fraîche,
exécutez uniquement `INIT_COMPLET.sql`.

## Fichiers archivés

| Fichier | Contenu | Intégré dans |
|---------|---------|--------------|
| `add_jeux_euromillions_tables.sql` | 5 tables jeux (euromillions, cotes, etc.) | PARTIE 5B |
| `037_maison_extensions.sql` | 15 tables extensions maison | PARTIE 5C |
| `utilitaires_schema.sql` | 7 tables utilitaires (notes, journal, etc.) | PARTIE 5D |
| `migration_profils_parametres.sql` | Seed data (profils, budgets, objectifs) | PARTIE 10 |
| `migration_timestamps_fr.sql` | Renommage colonnes timestamps | Non nécessaire (schéma créé directement en français) |

> **Date d'archivage** : Février 2026
