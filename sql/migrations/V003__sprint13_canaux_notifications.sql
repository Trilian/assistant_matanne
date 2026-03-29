-- ─────────────────────────────────────────────────────────────────────────────
-- Migration V003 — Sprint 13 : ajout canaux_par_categorie dans preferences_notifications
-- Date : 2026-03-29
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE preferences_notifications
    ADD COLUMN IF NOT EXISTS canaux_par_categorie JSONB
        DEFAULT '{"rappels":["push","ntfy"],"alertes":["push","ntfy","email"],"resumes":["email"]}'::jsonb;

-- Mettre à jour les lignes existantes sans valeur
UPDATE preferences_notifications
SET canaux_par_categorie = '{"rappels":["push","ntfy"],"alertes":["push","ntfy","email"],"resumes":["email"]}'::jsonb
WHERE canaux_par_categorie IS NULL;
