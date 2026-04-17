-- Migration: Remplacement de poisson_par_semaine par nb_poisson_blanc + nb_poisson_gras
-- Date: 2026-04-17

ALTER TABLE preferences_utilisateurs
    ADD COLUMN IF NOT EXISTS nb_poisson_blanc INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS nb_poisson_gras INTEGER NOT NULL DEFAULT 1;

-- Migrer les données existantes depuis poisson_par_semaine
UPDATE preferences_utilisateurs
SET
    nb_poisson_blanc = CASE WHEN poisson_par_semaine >= 1 THEN 1 ELSE 0 END,
    nb_poisson_gras  = CASE WHEN poisson_par_semaine >= 2 THEN 1 ELSE 0 END
WHERE nb_poisson_blanc = 1 AND nb_poisson_gras = 1;
