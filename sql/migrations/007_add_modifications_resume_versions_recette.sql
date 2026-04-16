-- Migration 007 : Ajout de la colonne modifications_resume sur versions_recette
-- Permet de persister le résumé des adaptations (Jules et robots) directement en DB
-- au lieu de le recalculer à chaque appel IA.

ALTER TABLE versions_recette
    ADD COLUMN IF NOT EXISTS modifications_resume JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN versions_recette.modifications_resume
    IS 'Résumé des modifications apportées (liste de chaînes), ex: ["sans sel", "champignons mixés"]';
