-- Migration: add missing recette flag columns expected by SQLAlchemy models
-- Generated: 2026-03-01
BEGIN;
ALTER TABLE IF EXISTS recettes
ADD COLUMN IF NOT EXISTS est_rapide BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_equilibre BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_vegetarien BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_bebe BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_batch BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS congelable BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS type_proteines VARCHAR(50),
    ADD COLUMN IF NOT EXISTS est_bio BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_local BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS score_bio NUMERIC DEFAULT 0,
    ADD COLUMN IF NOT EXISTS score_local NUMERIC DEFAULT 0,
    ADD COLUMN IF NOT EXISTS compatible_cookeo BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_monsieur_cuisine BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_airfryer BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_multicooker BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS calories INTEGER,
    ADD COLUMN IF NOT EXISTS proteines NUMERIC,
    ADD COLUMN IF NOT EXISTS lipides NUMERIC,
    ADD COLUMN IF NOT EXISTS glucides NUMERIC,
    ADD COLUMN IF NOT EXISTS genere_par_ia BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS score_ia NUMERIC DEFAULT 0,
    ADD COLUMN IF NOT EXISTS url_image VARCHAR(500);
-- Backfill from existing columns where names differ
UPDATE recettes
SET compatible_bebe = adaptee_bebe
WHERE (
        compatible_bebe IS NULL
        OR compatible_bebe = FALSE
    )
    AND (adaptee_bebe IS NOT NULL);
UPDATE recettes
SET compatible_batch = batch_cooking
WHERE (
        compatible_batch IS NULL
        OR compatible_batch = FALSE
    )
    AND (batch_cooking IS NOT NULL);
UPDATE recettes
SET url_image = image_url
WHERE (
        url_image IS NULL
        OR url_image = ''
    )
    AND (
        image_url IS NOT NULL
        AND image_url <> ''
    );
-- Indexes used by models
CREATE INDEX IF NOT EXISTS ix_recettes_est_rapide ON recettes (est_rapide);
CREATE INDEX IF NOT EXISTS ix_recettes_est_equilibre ON recettes (est_equilibre);
COMMIT;
