-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbees (SQL-first)
-- ============================================================================
-- Objectif: conserver un script idempotent pour aligner les schemas existants
-- avec les conventions actuelles quand les colonnes ont evolue.
-- ============================================================================

-- Phase 5: workflow validation v2 (planning + courses)

-- Plannings: ajoute `etat` si absent, puis migre depuis `actif` si present.
ALTER TABLE plannings
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'plannings' AND column_name = 'actif'
    ) THEN
        UPDATE plannings
        SET etat = CASE
            WHEN actif IS TRUE THEN 'valide'
            ELSE 'archive'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_plannings_etat ON plannings(etat);

-- Listes de courses: ajoute `etat` et `archivee`, puis migre depuis `statut` si present.
ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS etat VARCHAR(20) NOT NULL DEFAULT 'brouillon';

ALTER TABLE listes_courses
    ADD COLUMN IF NOT EXISTS archivee BOOLEAN NOT NULL DEFAULT FALSE;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'listes_courses' AND column_name = 'statut'
    ) THEN
        UPDATE listes_courses
        SET etat = CASE
            WHEN statut IN ('active', 'en_cours') THEN 'active'
            WHEN statut IN ('completee', 'archivee') THEN 'terminee'
            ELSE 'brouillon'
        END
        WHERE etat = 'brouillon';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_listes_courses_etat ON listes_courses(etat);
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses(archivee);
