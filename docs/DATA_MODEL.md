# Data Model

Vue fonctionnelle du modele de donnees.

## Chiffres cle

- Tables ORM detectees: 143 (`__tablename__` hors `mixins.py`).
- Source de verite schema: `sql/schema/*.sql`.
- Script de regeneration: `scripts/db/regenerate_init.py`.

## Domaines

- Cuisine: recettes, ingredients, planning repas, courses, batch cooking.
- Famille: profils enfants, activites, routines, anniversaires, achats.
- Maison/Habitat: projets, entretien, depenses, artisans, garanties, plans habitat.
- Jeux: paris, loto, euromillions, stats et historiques.
- Utilitaires/Systeme: notes, journal, contacts, energie, logs, sauvegardes.
- Integrations: calendriers externes, tokens Garmin, notifications.

## Relations majeures

- Recettes <-> Ingredients (`recette_ingredients`).
- Planning -> Repas -> Recettes.
- Courses -> Articles courses (+ modeles).
- Profils enfants -> Jalons / activites / bien-etre.
- Projets maison -> taches projets.
- Contrats/artisans/garanties/interventions lies entre eux.

## Tables notables recentes

- `batch_cooking_congelation`
- `ia_suggestions_historique`
- `minuteur_sessions`
- Tables habitat (scenarios/criteres/annonces/plans/deco)

## Alignement ORM/SQL

Procedure recommandee:

1. Modifier `sql/schema/*.sql` (fichier thématique).
2. Regenerer `sql/INIT_COMPLET.sql`.
3. Aligner `src/core/models/`.
4. Aligner schemas API (`src/api/schemas/`).

## References

- ERD detaille: `docs/ERD_SCHEMA.md`
- Migrations SQL-first: `docs/MIGRATION_GUIDE.md`
- Index DB: `docs/guides/DATABASE_INDEXES.md`
