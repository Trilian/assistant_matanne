-- ═══════════════════════════════════════════════════════════════
-- Schema utilitaires — Tables pour les modules utilitaires étendus
-- ═══════════════════════════════════════════════════════════════
-- Notes et Mémos
CREATE TABLE IF NOT EXISTS notes_memos (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT,
    categorie VARCHAR(50) DEFAULT 'general',
    couleur VARCHAR(20) DEFAULT '#ffffff',
    epingle BOOLEAN DEFAULT false,
    archive BOOLEAN DEFAULT false,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notes_memos_categorie ON notes_memos(categorie);
CREATE INDEX IF NOT EXISTS idx_notes_memos_epingle ON notes_memos(epingle)
WHERE epingle = true;
CREATE INDEX IF NOT EXISTS idx_notes_memos_archive ON notes_memos(archive);
-- Journal de bord
CREATE TABLE IF NOT EXISTS journal_bord (
    id BIGSERIAL PRIMARY KEY,
    date_entree DATE NOT NULL UNIQUE,
    contenu TEXT,
    humeur VARCHAR(20),
    energie INTEGER CHECK (
        energie BETWEEN 1 AND 10
    ),
    gratitudes JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal_bord(date_entree DESC);
-- Contacts utiles
CREATE TABLE IF NOT EXISTS contacts_utiles (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    telephone VARCHAR(30),
    email VARCHAR(200),
    adresse TEXT,
    specialite VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contacts_categorie ON contacts_utiles(categorie);
CREATE INDEX IF NOT EXISTS idx_contacts_nom ON contacts_utiles(nom);
-- Liens favoris
CREATE TABLE IF NOT EXISTS liens_favoris (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_liens_categorie ON liens_favoris(categorie);
-- Mots de passe maison
CREATE TABLE IF NOT EXISTS mots_de_passe_maison (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    identifiant VARCHAR(200),
    mot_de_passe_chiffre TEXT NOT NULL,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mdp_categorie ON mots_de_passe_maison(categorie);
-- Presse-papiers partagé
CREATE TABLE IF NOT EXISTS presse_papier_entrees (
    id BIGSERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    auteur VARCHAR(100),
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pp_cree_le ON presse_papier_entrees(cree_le DESC);
-- Relevés énergie
CREATE TABLE IF NOT EXISTS releves_energie (
    id BIGSERIAL PRIMARY KEY,
    categorie VARCHAR(30) NOT NULL CHECK (categorie IN ('electricite', 'gaz', 'eau')),
    date_releve DATE NOT NULL,
    valeur NUMERIC(12, 2) NOT NULL CHECK (valeur > 0),
    cout_reel NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_energie_categorie ON releves_energie(categorie);
CREATE INDEX IF NOT EXISTS idx_energie_date ON releves_energie(date_releve DESC);
-- ═══════════════════════════════════════════════════════════════
-- Triggers auto-update modifie_le
-- ═══════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_modifie_le() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DO $$ BEGIN CREATE TRIGGER trg_notes_memos_modifie BEFORE
UPDATE ON notes_memos FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_journal_bord_modifie BEFORE
UPDATE ON journal_bord FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_contacts_utiles_modifie BEFORE
UPDATE ON contacts_utiles FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_liens_favoris_modifie BEFORE
UPDATE ON liens_favoris FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_mdp_maison_modifie BEFORE
UPDATE ON mots_de_passe_maison FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_releves_energie_modifie BEFORE
UPDATE ON releves_energie FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
