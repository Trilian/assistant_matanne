-- Migration: add missing columns detected in production
-- Generated: 2026-03-03
BEGIN;
-- Anniversaires: idées_cadeaux (TEXT) et historique_cadeaux (JSONB)
ALTER TABLE IF EXISTS anniversaires_famille
ADD COLUMN IF NOT EXISTS idees_cadeaux TEXT,
    ADD COLUMN IF NOT EXISTS historique_cadeaux JSONB DEFAULT '[]';
-- Documents famille: catégorie
ALTER TABLE IF EXISTS documents_famille
ADD COLUMN IF NOT EXISTS categorie VARCHAR(50) NOT NULL DEFAULT 'autre';
CREATE INDEX IF NOT EXISTS idx_documents_famille_categorie ON documents_famille (categorie);
-- Voyages: participants (JSONB)
ALTER TABLE IF EXISTS voyages
ADD COLUMN IF NOT EXISTS participants JSONB DEFAULT '[]';
-- Souvenirs: video_url
ALTER TABLE IF EXISTS souvenirs_famille
ADD COLUMN IF NOT EXISTS video_url VARCHAR(500);
-- Albums: couverture_url
ALTER TABLE IF EXISTS albums_famille
ADD COLUMN IF NOT EXISTS couverture_url VARCHAR(500);
-- Contacts: telephone_2
ALTER TABLE IF EXISTS contacts_famille
ADD COLUMN IF NOT EXISTS telephone_2 VARCHAR(20);
COMMIT;
