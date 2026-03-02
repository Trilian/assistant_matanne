-- Migration: ensure utilitaires tables (journal, contacts, liens) have expected columns/indexes/triggers
-- Idempotent: safe to run multiple times
BEGIN;
-- Create tables if missing (safe no-op if exist)
CREATE TABLE IF NOT EXISTS journal_bord (
    id BIGSERIAL PRIMARY KEY,
    date_entree DATE NOT NULL UNIQUE,
    contenu TEXT,
    humeur VARCHAR(20),
    energie INTEGER,
    gratitudes JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal_bord(date_entree DESC);
CREATE TABLE IF NOT EXISTS contacts_utiles (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    telephone VARCHAR(30),
    email VARCHAR(200),
    adresse TEXT,
    specialite VARCHAR(200),
    favori BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'contacts_utiles'
        AND column_name = 'categorie'
) THEN CREATE INDEX IF NOT EXISTS idx_contacts_utiles_categorie ON contacts_utiles(categorie);
END IF;
IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'contacts_utiles'
        AND column_name = 'nom'
) THEN CREATE INDEX IF NOT EXISTS idx_contacts_utiles_nom ON contacts_utiles(nom);
END IF;
IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'contacts_utiles'
        AND column_name = 'favori'
) THEN CREATE INDEX IF NOT EXISTS idx_contacts_utiles_favori ON contacts_utiles(favori);
END IF;
END $$;
CREATE TABLE IF NOT EXISTS liens_favoris (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    description TEXT,
    favori BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'liens_favoris'
        AND column_name = 'categorie'
) THEN CREATE INDEX IF NOT EXISTS idx_liens_categorie ON liens_favoris(categorie);
END IF;
IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'liens_favoris'
        AND column_name = 'favori'
) THEN CREATE INDEX IF NOT EXISTS idx_liens_favori ON liens_favoris(favori);
END IF;
END $$;
-- Ensure expected columns exist (for older DBs missing individual columns)
ALTER TABLE IF EXISTS journal_bord
ADD COLUMN IF NOT EXISTS contenu TEXT,
    ADD COLUMN IF NOT EXISTS humeur VARCHAR(20),
    ADD COLUMN IF NOT EXISTS energie INTEGER,
    ADD COLUMN IF NOT EXISTS gratitudes JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS cree_le TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modifie_le TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE IF EXISTS contacts_utiles
ADD COLUMN IF NOT EXISTS categorie VARCHAR(50) DEFAULT 'autre',
    ADD COLUMN IF NOT EXISTS telephone VARCHAR(30),
    ADD COLUMN IF NOT EXISTS email VARCHAR(200),
    ADD COLUMN IF NOT EXISTS adresse TEXT,
    ADD COLUMN IF NOT EXISTS specialite VARCHAR(200),
    ADD COLUMN IF NOT EXISTS favori BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS cree_le TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modifie_le TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE IF EXISTS liens_favoris
ADD COLUMN IF NOT EXISTS url TEXT,
    ADD COLUMN IF NOT EXISTS categorie VARCHAR(50) DEFAULT 'autre',
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS favori BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS cree_le TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modifie_le TIMESTAMPTZ DEFAULT NOW();
-- Create triggers to update modifie_le if function is available
DO $$ BEGIN IF EXISTS (
    SELECT 1
    FROM pg_proc
    WHERE proname = 'update_modifie_le'
) THEN IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_journal_bord_modifie'
) THEN CREATE TRIGGER trg_journal_bord_modifie BEFORE
UPDATE ON journal_bord FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_contacts_utiles_modifie'
) THEN CREATE TRIGGER trg_contacts_utiles_modifie BEFORE
UPDATE ON contacts_utiles FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM pg_trigger
    WHERE tgname = 'trg_liens_favoris_modifie'
) THEN CREATE TRIGGER trg_liens_favoris_modifie BEFORE
UPDATE ON liens_favoris FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
END IF;
END IF;
END $$;
COMMIT;
