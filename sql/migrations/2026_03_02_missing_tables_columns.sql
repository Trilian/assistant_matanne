-- Migration: tables et colonnes manquantes détectées en production
-- Generated: 2026-03-02

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. TABLE etats_persistants (PersistentState)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etats_persistants (
    id          SERIAL PRIMARY KEY,
    namespace   VARCHAR(100) NOT NULL,
    user_id     VARCHAR(100) NOT NULL DEFAULT 'default',
    data        JSONB NOT NULL DEFAULT '{}',
    cree_le     TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le  TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pstate_namespace_user UNIQUE (namespace, user_id)
);

CREATE INDEX IF NOT EXISTS idx_etats_persistants_namespace ON etats_persistants (namespace);
CREATE INDEX IF NOT EXISTS idx_etats_persistants_user_id   ON etats_persistants (user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. COLONNES MANQUANTES : zones_jardin
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE zones_jardin
    ADD COLUMN IF NOT EXISTS etat_note         INTEGER     DEFAULT 3,
    ADD COLUMN IF NOT EXISTS etat_description  TEXT,
    ADD COLUMN IF NOT EXISTS objectif          TEXT,
    ADD COLUMN IF NOT EXISTS budget_estime     NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS prochaine_action  TEXT,
    ADD COLUMN IF NOT EXISTS date_prochaine_action DATE,
    ADD COLUMN IF NOT EXISTS photos_url        JSONB       DEFAULT '[]';

-- Contrainte CHECK sur etat_note (1=catastrophe, 5=parfait)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_zones_jardin_etat_note'
    ) THEN
        ALTER TABLE zones_jardin
            ADD CONSTRAINT ck_zones_jardin_etat_note
            CHECK (etat_note BETWEEN 1 AND 5);
    END IF;
END
$$;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Activer RLS sur etats_persistants (cohérence avec les autres tables)
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE etats_persistants ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "etats_persistants_all"
    ON etats_persistants FOR ALL
    USING (true) WITH CHECK (true);

COMMIT;
