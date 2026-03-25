-- Migration: Ajout colonnes moment_journee et jour_semaine à la table routines
-- Date: 2025-01
-- Description: Permet de filtrer les routines par moment de la journée et jour de la semaine

ALTER TABLE routines
  ADD COLUMN IF NOT EXISTS moment_journee VARCHAR(20) NOT NULL DEFAULT 'flexible';

ALTER TABLE routines
  ADD COLUMN IF NOT EXISTS jour_semaine INTEGER;

COMMENT ON COLUMN routines.moment_journee IS 'Moment de la journée: matin, apres_midi, soir, flexible';
COMMENT ON COLUMN routines.jour_semaine IS 'Jour de la semaine (0=lundi, 6=dimanche) pour les routines hebdomadaires';
