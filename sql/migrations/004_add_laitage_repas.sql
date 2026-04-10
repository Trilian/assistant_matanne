-- Migration 004: Ajout colonne laitage sur la table repas
-- Laitage = texte seul (yaourt, fromage blanc, fromage...) lié à déjeuner/dîner
-- Distinct de notes (saisie manuelle libre) et dessert (dessert + recette optionnelle)

ALTER TABLE repas ADD COLUMN IF NOT EXISTS laitage VARCHAR(200);
