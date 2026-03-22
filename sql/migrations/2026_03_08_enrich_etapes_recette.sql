-- Migration: Enrichir la table etapes_recette avec robots, température, supervision, parallélisation
-- Aligne EtapeRecette avec EtapeBatchCooking pour permettre robot/température par étape

ALTER TABLE etapes_recette
    ADD COLUMN IF NOT EXISTS titre VARCHAR(200),
    ADD COLUMN IF NOT EXISTS robots_optionnels JSONB,
    ADD COLUMN IF NOT EXISTS temperature INTEGER,
    ADD COLUMN IF NOT EXISTS est_supervision BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS groupe_parallele INTEGER DEFAULT 0;

COMMENT ON COLUMN etapes_recette.titre IS 'Titre court optionnel de l étape';
COMMENT ON COLUMN etapes_recette.robots_optionnels IS 'Liste des robots utilisables (JSON array de strings)';
COMMENT ON COLUMN etapes_recette.temperature IS 'Température requise en degrés Celsius';
COMMENT ON COLUMN etapes_recette.est_supervision IS 'Étape de surveillance passive (ex: cuisson four)';
COMMENT ON COLUMN etapes_recette.groupe_parallele IS 'Groupe pour parallélisation (même groupe = simultané, 0 = séquentiel)';
