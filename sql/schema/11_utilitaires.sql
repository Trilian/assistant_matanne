-- ============================================================================
-- ASSISTANT MATANNE — Tables Utilitaires
-- ============================================================================
-- Contient : notes_memos, journal_bord, contacts_utiles, liens_favoris,
--            mots_de_passe_maison, presse_papier_entrees, releves_energie,
--            voyages, checklists_voyage, templates_checklist
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS voyages (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(300) NOT NULL,
    destination VARCHAR(300) NOT NULL,
    date_depart DATE NOT NULL,
    date_retour DATE NOT NULL,
    type_voyage VARCHAR(50) DEFAULT 'vacances',
    budget_prevu NUMERIC(10, 2),
    budget_depense NUMERIC(10, 2) DEFAULT 0,
    statut VARCHAR(30) NOT NULL DEFAULT 'planifie',
    notes TEXT,
    reservations JSONB DEFAULT '[]',
    budget_reel FLOAT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_voyage_dates CHECK (date_retour >= date_depart),
    CONSTRAINT ck_voyage_statut CHECK (
        statut IN ('planifie', 'en_cours', 'termine', 'annule')
    )
);
CREATE INDEX IF NOT EXISTS ix_voyages_depart ON voyages(date_depart);
CREATE INDEX IF NOT EXISTS ix_voyages_statut ON voyages(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS templates_checklist (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_voyage VARCHAR(50),
    description TEXT,
    articles JSONB NOT NULL DEFAULT '[]',
    est_defaut BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_templates_type ON templates_checklist(type_voyage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_voyage (
    id SERIAL PRIMARY KEY,
    voyage_id INTEGER NOT NULL,
    template_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    articles JSONB NOT NULL DEFAULT '[]',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_checklist_voyage FOREIGN KEY (voyage_id) REFERENCES voyages(id) ON DELETE CASCADE,
    CONSTRAINT fk_checklist_template FOREIGN KEY (template_id) REFERENCES templates_checklist(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS ix_checklists_voyage ON checklists_voyage(voyage_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notes_memos (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    contenu TEXT,
    categorie VARCHAR(50) DEFAULT 'general',
    couleur VARCHAR(20) DEFAULT '#ffffff',
    epingle BOOLEAN DEFAULT FALSE,
    archive BOOLEAN DEFAULT FALSE,
    tags JSONB DEFAULT '[]'::jsonb,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_notes_memos_categorie ON notes_memos(categorie);
CREATE INDEX IF NOT EXISTS idx_notes_memos_epingle ON notes_memos(epingle)
WHERE epingle = TRUE;
CREATE INDEX IF NOT EXISTS idx_notes_memos_archive ON notes_memos(archive);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_categorie ON contacts_utiles(categorie);
CREATE INDEX IF NOT EXISTS idx_contacts_utiles_nom ON contacts_utiles(nom);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS presse_papier_entrees (
    id BIGSERIAL PRIMARY KEY,
    contenu TEXT NOT NULL,
    auteur VARCHAR(100),
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pp_cree_le ON presse_papier_entrees(cree_le DESC);


-- ─────────────────────────────────────────────────────────────────────────────
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


