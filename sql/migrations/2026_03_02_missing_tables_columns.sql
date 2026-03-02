-- Migration: tables et colonnes manquantes détectées en production
-- Generated: 2026-03-02
BEGIN;
-- ─────────────────────────────────────────────────────────────────────────────
-- 1. TABLE etats_persistants (PersistentState)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS etats_persistants (
    id SERIAL PRIMARY KEY,
    namespace VARCHAR(100) NOT NULL,
    user_id VARCHAR(100) NOT NULL DEFAULT 'default',
    data JSONB NOT NULL DEFAULT '{}',
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_pstate_namespace_user UNIQUE (namespace, user_id)
);
CREATE INDEX IF NOT EXISTS idx_etats_persistants_namespace ON etats_persistants (namespace);
CREATE INDEX IF NOT EXISTS idx_etats_persistants_user_id ON etats_persistants (user_id);
-- ─────────────────────────────────────────────────────────────────────────────
-- 2. COLONNES MANQUANTES : zones_jardin
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE zones_jardin
ADD COLUMN IF NOT EXISTS etat_note INTEGER DEFAULT 3,
    ADD COLUMN IF NOT EXISTS etat_description TEXT,
    ADD COLUMN IF NOT EXISTS objectif TEXT,
    ADD COLUMN IF NOT EXISTS budget_estime NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS prochaine_action TEXT,
    ADD COLUMN IF NOT EXISTS date_prochaine_action DATE,
    ADD COLUMN IF NOT EXISTS photos_url JSONB DEFAULT '[]';
-- Contrainte CHECK sur etat_note (1=catastrophe, 5=parfait)
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'ck_zones_jardin_etat_note'
) THEN
ALTER TABLE zones_jardin
ADD CONSTRAINT ck_zones_jardin_etat_note CHECK (
        etat_note BETWEEN 1 AND 5
    );
END IF;
END $$;
-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Activer RLS sur etats_persistants (cohérence avec les autres tables)
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE etats_persistants ENABLE ROW LEVEL SECURITY;
DO $do$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_policy
    WHERE polname = 'etats_persistants_all'
        AND polrelid = 'etats_persistants'::regclass
) THEN EXECUTE 'CREATE POLICY "etats_persistants_all" ON etats_persistants FOR ALL USING (true) WITH CHECK (true)';
END IF;
END $do$;
-- ─────────────────────────────────────────────────────────────────────────────
-- 4. COLONNES MANQUANTES : evenements_planning (récurrence)
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE evenements_planning
ADD COLUMN IF NOT EXISTS recurrence_type VARCHAR(20),
    ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS recurrence_jours VARCHAR(20),
    ADD COLUMN IF NOT EXISTS recurrence_fin DATE,
    ADD COLUMN IF NOT EXISTS parent_event_id INTEGER REFERENCES evenements_planning(id) ON DELETE
SET NULL;
CREATE INDEX IF NOT EXISTS idx_evenements_planning_parent_event_id ON evenements_planning (parent_event_id);
-- ─────────────────────────────────────────────────────────────────────────────
-- 5. COLONNES MANQUANTES : recettes (flags, nutrition, robots, IA)
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE recettes
ADD COLUMN IF NOT EXISTS est_rapide BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_equilibre BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_vegetarien BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_batch BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS congelable BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS type_proteines VARCHAR(100),
    ADD COLUMN IF NOT EXISTS est_bio BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS est_local BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS score_bio INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS score_local INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS compatible_cookeo BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_monsieur_cuisine BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_airfryer BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS compatible_multicooker BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS calories INTEGER,
    ADD COLUMN IF NOT EXISTS proteines FLOAT,
    ADD COLUMN IF NOT EXISTS lipides FLOAT,
    ADD COLUMN IF NOT EXISTS glucides FLOAT,
    ADD COLUMN IF NOT EXISTS genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS score_ia FLOAT,
    ADD COLUMN IF NOT EXISTS url_image VARCHAR(500);
CREATE INDEX IF NOT EXISTS idx_recettes_est_rapide ON recettes (est_rapide);
CREATE INDEX IF NOT EXISTS idx_recettes_est_vegetarien ON recettes (est_vegetarien);
CREATE INDEX IF NOT EXISTS idx_recettes_compatible_bebe ON recettes (compatible_bebe);
CREATE INDEX IF NOT EXISTS idx_recettes_compatible_batch ON recettes (compatible_batch);
CREATE INDEX IF NOT EXISTS idx_recettes_est_bio ON recettes (est_bio);
CREATE INDEX IF NOT EXISTS idx_recettes_est_local ON recettes (est_local);
CREATE INDEX IF NOT EXISTS idx_recettes_compatible_cookeo ON recettes (compatible_cookeo);
CREATE INDEX IF NOT EXISTS idx_recettes_compatible_monsieur_cuisine ON recettes (compatible_monsieur_cuisine);
CREATE INDEX IF NOT EXISTS idx_recettes_compatible_airfryer ON recettes (compatible_airfryer);
-- ─────────────────────────────────────────────────────────────────────────────
-- 6. TABLE contacts_utiles (Annuaire familial)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contacts_utiles (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    specialite VARCHAR(200),
    telephone VARCHAR(20),
    email VARCHAR(200),
    adresse TEXT,
    horaires VARCHAR(200),
    notes TEXT,
    favori BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_categorie ON contacts_utiles (categorie);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_nom ON contacts_utiles (nom);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_favori ON contacts_utiles (favori)
WHERE favori = TRUE;
-- RLS contacts_utiles
ALTER TABLE contacts_utiles ENABLE ROW LEVEL SECURITY;
DO $do$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_policy
    WHERE polname = 'contacts_utiles_all'
        AND polrelid = 'contacts_utiles'::regclass
) THEN EXECUTE 'CREATE POLICY "contacts_utiles_all" ON contacts_utiles FOR ALL USING (true) WITH CHECK (true)';
END IF;
END $do$;
-- Trigger modifie_le
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_contacts_utiles_modifie'
) THEN CREATE TRIGGER trg_contacts_utiles_modifie BEFORE
UPDATE ON contacts_utiles FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
END IF;
END $$;
COMMIT;
