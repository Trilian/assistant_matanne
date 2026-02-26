-- ═══════════════════════════════════════════════════════════
-- Migration: Ajout tables Euromillions, Cotes Historique, Mise Responsable
-- Date: 2026-02-26
-- ═══════════════════════════════════════════════════════════
-- ─────────────────────────────────────────────────────────
-- Table: jeux_tirages_euromillions
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_tirages_euromillions (
    id SERIAL PRIMARY KEY,
    date_tirage DATE NOT NULL,
    numero_1 INTEGER NOT NULL CHECK (
        numero_1 BETWEEN 1 AND 50
    ),
    numero_2 INTEGER NOT NULL CHECK (
        numero_2 BETWEEN 1 AND 50
    ),
    numero_3 INTEGER NOT NULL CHECK (
        numero_3 BETWEEN 1 AND 50
    ),
    numero_4 INTEGER NOT NULL CHECK (
        numero_4 BETWEEN 1 AND 50
    ),
    numero_5 INTEGER NOT NULL CHECK (
        numero_5 BETWEEN 1 AND 50
    ),
    etoile_1 INTEGER NOT NULL CHECK (
        etoile_1 BETWEEN 1 AND 12
    ),
    etoile_2 INTEGER NOT NULL CHECK (
        etoile_2 BETWEEN 1 AND 12
    ),
    jackpot NUMERIC(15, 2),
    nb_gagnants_rang1 INTEGER DEFAULT 0,
    rapport_rang1 NUMERIC(15, 2),
    code_my_million VARCHAR(10),
    donnees_json JSONB,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (date_tirage)
);
CREATE INDEX IF NOT EXISTS idx_tirages_euromillions_date ON jeux_tirages_euromillions(date_tirage DESC);
COMMENT ON TABLE jeux_tirages_euromillions IS 'Tirages Euromillions avec 5 numéros (1-50) + 2 étoiles (1-12)';
-- ─────────────────────────────────────────────────────────
-- Table: jeux_grilles_euromillions
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_grilles_euromillions (
    id SERIAL PRIMARY KEY,
    tirage_id INTEGER REFERENCES jeux_tirages_euromillions(id) ON DELETE
    SET NULL,
        numeros INTEGER [] NOT NULL,
        etoiles INTEGER [] NOT NULL,
        strategie VARCHAR(50),
        mise NUMERIC(10, 2) DEFAULT 2.50,
        gain NUMERIC(15, 2) DEFAULT 0,
        rang INTEGER,
        est_virtuelle BOOLEAN DEFAULT TRUE,
        cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_grilles_euromillions_tirage ON jeux_grilles_euromillions(tirage_id);
CREATE INDEX IF NOT EXISTS idx_grilles_euromillions_date ON jeux_grilles_euromillions(cree_le DESC);
COMMENT ON TABLE jeux_grilles_euromillions IS 'Grilles Euromillions jouées ou virtuelles (pour simulation)';
-- ─────────────────────────────────────────────────────────
-- Table: jeux_stats_euromillions
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_stats_euromillions (
    id SERIAL PRIMARY KEY,
    date_calcul DATE NOT NULL,
    frequences_numeros JSONB NOT NULL DEFAULT '{}',
    frequences_etoiles JSONB NOT NULL DEFAULT '{}',
    numeros_chauds JSONB DEFAULT '[]',
    numeros_froids JSONB DEFAULT '[]',
    etoiles_chaudes JSONB DEFAULT '[]',
    etoiles_froides JSONB DEFAULT '[]',
    patterns JSONB DEFAULT '{}',
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (date_calcul)
);
COMMENT ON TABLE jeux_stats_euromillions IS 'Statistiques calculées des fréquences Euromillions';
-- ─────────────────────────────────────────────────────────
-- Table: jeux_cotes_historique
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_cotes_historique (
    id SERIAL PRIMARY KEY,
    match_id INTEGER REFERENCES jeux_matchs(id) ON DELETE CASCADE,
    bookmaker VARCHAR(100) NOT NULL,
    marche VARCHAR(50) NOT NULL DEFAULT '1x2',
    cote_domicile NUMERIC(8, 3),
    cote_nul NUMERIC(8, 3),
    cote_exterieur NUMERIC(8, 3),
    donnees_json JSONB,
    timestamp_cote TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_match ON jeux_cotes_historique(match_id);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_timestamp ON jeux_cotes_historique(timestamp_cote DESC);
CREATE INDEX IF NOT EXISTS idx_cotes_hist_bookmaker ON jeux_cotes_historique(bookmaker);
COMMENT ON TABLE jeux_cotes_historique IS 'Historique des cotes par bookmaker pour détecter les mouvements';
-- ─────────────────────────────────────────────────────────
-- Table: jeux_mise_responsable
-- ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_mise_responsable (
    id SERIAL PRIMARY KEY,
    mois DATE NOT NULL,
    limite_mensuelle NUMERIC(10, 2) NOT NULL DEFAULT 50.00,
    mises_cumulees NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    nb_mises INTEGER NOT NULL DEFAULT 0,
    alerte_50 BOOLEAN DEFAULT FALSE,
    alerte_75 BOOLEAN DEFAULT FALSE,
    alerte_90 BOOLEAN DEFAULT FALSE,
    alerte_100 BOOLEAN DEFAULT FALSE,
    cooldown_actif BOOLEAN DEFAULT FALSE,
    cooldown_fin TIMESTAMP WITH TIME ZONE,
    auto_exclusion BOOLEAN DEFAULT FALSE,
    auto_exclusion_fin DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (mois)
);
CREATE INDEX IF NOT EXISTS idx_mise_responsable_mois ON jeux_mise_responsable(mois DESC);
COMMENT ON TABLE jeux_mise_responsable IS 'Suivi mensuel des mises avec limites, alertes et auto-exclusion';
-- ─────────────────────────────────────────────────────────
-- Seed: configuration initiale mise responsable (mois courant)
-- ─────────────────────────────────────────────────────────
INSERT INTO jeux_mise_responsable (mois, limite_mensuelle)
VALUES (DATE_TRUNC('month', CURRENT_DATE)::DATE, 50.00) ON CONFLICT (mois) DO NOTHING;
-- ─────────────────────────────────────────────────────────
-- Trigger: mise à jour automatique modifie_le
-- ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION trigger_set_modifie_le() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_mise_responsable_modifie_le ON jeux_mise_responsable;
CREATE TRIGGER trg_mise_responsable_modifie_le BEFORE
UPDATE ON jeux_mise_responsable FOR EACH ROW EXECUTE FUNCTION trigger_set_modifie_le();
