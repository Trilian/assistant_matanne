-- ═══════════════════════════════════════════════════════════════
-- Schema utilitaires — Tables pour les modules utilitaires étendus
-- ═══════════════════════════════════════════════════════════════
-- Notes et Mémos
CREATE TABLE IF NOT EXISTS notes_memos (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT,
    categorie VARCHAR(50) DEFAULT 'general',
    couleur VARCHAR(7) DEFAULT '#FFFFFF',
    epingle BOOLEAN DEFAULT false,
    est_checklist BOOLEAN DEFAULT false,
    items_checklist JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    rappel_date TIMESTAMPTZ,
    archive BOOLEAN DEFAULT false,
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
    contenu TEXT NOT NULL,
    humeur VARCHAR(20),
    gratitudes JSONB DEFAULT '[]'::jsonb,
    energie INTEGER CHECK (
        energie IS NULL
        OR energie BETWEEN 1 AND 10
    ),
    tags JSONB DEFAULT '[]'::jsonb,
    meteo JSONB,
    photos JSONB DEFAULT '[]'::jsonb,
    evenements_lies JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal_bord(date_entree DESC);
-- Contacts utiles
CREATE TABLE IF NOT EXISTS contacts_utiles (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'autre',
    specialite VARCHAR(200),
    telephone VARCHAR(20),
    email VARCHAR(200),
    adresse TEXT,
    horaires VARCHAR(200),
    notes TEXT,
    favori BOOLEAN DEFAULT false,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contacts_categorie ON contacts_utiles(categorie);
CREATE INDEX IF NOT EXISTS idx_contacts_nom ON contacts_utiles(nom);
CREATE INDEX IF NOT EXISTS idx_contacts_favori ON contacts_utiles(favori)
WHERE favori = true;
-- Liens favoris
CREATE TABLE IF NOT EXISTS liens_favoris (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    url TEXT NOT NULL,
    categorie VARCHAR(100),
    description TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    favori BOOLEAN DEFAULT false,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_liens_categorie ON liens_favoris(categorie);
CREATE INDEX IF NOT EXISTS idx_liens_favori ON liens_favoris(favori)
WHERE favori = true;
-- Mots de passe maison
CREATE TABLE IF NOT EXISTS mots_de_passe_maison (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) DEFAULT 'wifi',
    identifiant VARCHAR(200),
    valeur_chiffree TEXT NOT NULL,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_mdp_categorie ON mots_de_passe_maison(categorie);
-- Presse-papiers partagé
CREATE TABLE IF NOT EXISTS presse_papiers (
    id BIGSERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    auteur VARCHAR(100),
    expire_le TIMESTAMPTZ,
    epingle BOOLEAN DEFAULT false,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pp_cree_le ON presse_papiers(cree_le DESC);
-- Relevés énergie
CREATE TABLE IF NOT EXISTS releves_energie (
    id BIGSERIAL PRIMARY KEY,
    type_energie VARCHAR(50) NOT NULL,
    mois INTEGER NOT NULL CHECK (
        mois >= 1
        AND mois <= 12
    ),
    annee INTEGER NOT NULL,
    valeur_compteur NUMERIC(12, 2),
    consommation NUMERIC(10, 2) CHECK (
        consommation IS NULL
        OR consommation >= 0
    ),
    unite VARCHAR(10) NOT NULL DEFAULT 'kWh',
    montant NUMERIC(10, 2) CHECK (
        montant IS NULL
        OR montant >= 0
    ),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_energie_type ON releves_energie(type_energie);
CREATE INDEX IF NOT EXISTS idx_energie_annee ON releves_energie(annee DESC);
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
DO $$ BEGIN CREATE TRIGGER trg_presse_papiers_modifie BEFORE
UPDATE ON presse_papiers FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN CREATE TRIGGER trg_releves_energie_modifie BEFORE
UPDATE ON releves_energie FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
