-- Migration manuelle pour les tables du domaine Jeux
-- À exécuter manuellement dans Supabase SQL Editor si Alembic échoue

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_equipes
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_equipes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    nom_court VARCHAR(50),
    championnat VARCHAR(50) NOT NULL,
    pays VARCHAR(50),
    logo_url VARCHAR(255),
    -- Stats agrégées
    matchs_joues INTEGER DEFAULT 0,
    victoires INTEGER DEFAULT 0,
    nuls INTEGER DEFAULT 0,
    defaites INTEGER DEFAULT 0,
    buts_marques INTEGER DEFAULT 0,
    buts_encaisses INTEGER DEFAULT 0,
    -- Méta
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_jeux_equipes_championnat ON jeux_equipes(championnat);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_matchs
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_matchs (
    id SERIAL PRIMARY KEY,
    equipe_domicile_id INTEGER NOT NULL REFERENCES jeux_equipes(id),
    equipe_exterieur_id INTEGER NOT NULL REFERENCES jeux_equipes(id),
    championnat VARCHAR(50) NOT NULL,
    journee INTEGER,
    date_match DATE NOT NULL,
    heure VARCHAR(5),
    -- Résultat
    score_domicile INTEGER,
    score_exterieur INTEGER,
    resultat VARCHAR(10),
    joue BOOLEAN DEFAULT FALSE,
    -- Cotes
    cote_domicile FLOAT,
    cote_nul FLOAT,
    cote_exterieur FLOAT,
    -- Prédiction IA
    prediction_resultat VARCHAR(10),
    prediction_proba_dom FLOAT,
    prediction_proba_nul FLOAT,
    prediction_proba_ext FLOAT,
    prediction_confiance FLOAT,
    prediction_raison TEXT,
    -- Méta
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_jeux_matchs_date ON jeux_matchs(date_match);
CREATE INDEX IF NOT EXISTS ix_jeux_matchs_championnat ON jeux_matchs(championnat);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_paris_sportifs
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_paris_sportifs (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES jeux_matchs(id),
    type_pari VARCHAR(30) DEFAULT '1N2',
    prediction VARCHAR(20) NOT NULL,
    cote FLOAT NOT NULL,
    mise NUMERIC(10, 2) DEFAULT 0,
    -- Résultat
    statut VARCHAR(20) DEFAULT 'en_attente',
    gain NUMERIC(10, 2),
    -- Tracking
    est_virtuel BOOLEAN DEFAULT TRUE,
    confiance_prediction FLOAT,
    notes TEXT,
    -- Méta
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_jeux_paris_statut ON jeux_paris_sportifs(statut);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_tirages_loto
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_tirages_loto (
    id SERIAL PRIMARY KEY,
    date_tirage DATE NOT NULL UNIQUE,
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    jackpot_euros INTEGER,
    gagnants_rang1 INTEGER,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_jeux_tirages_date ON jeux_tirages_loto(date_tirage);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_grilles_loto
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_grilles_loto (
    id SERIAL PRIMARY KEY,
    tirage_id INTEGER REFERENCES jeux_tirages_loto(id),
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    est_virtuelle BOOLEAN DEFAULT TRUE,
    source_prediction VARCHAR(50) DEFAULT 'manuel',
    mise NUMERIC(10, 2) DEFAULT 2.20,
    numeros_trouves INTEGER,
    chance_trouvee BOOLEAN,
    gain NUMERIC(10, 2),
    rang INTEGER,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_stats_loto
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_stats_loto (
    id SERIAL PRIMARY KEY,
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    frequences_numeros JSONB,
    frequences_chance JSONB,
    numeros_chauds JSONB,
    numeros_froids JSONB,
    numeros_retard JSONB,
    somme_moyenne FLOAT,
    paires_frequentes JSONB,
    nb_tirages_analyses INTEGER DEFAULT 0
);

-- ═══════════════════════════════════════════════════════════════════
-- TABLE: jeux_historique
-- ═══════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS jeux_historique (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    nb_paris INTEGER DEFAULT 0,
    mises_totales NUMERIC(10, 2) DEFAULT 0,
    gains_totaux NUMERIC(10, 2) DEFAULT 0,
    paris_gagnes INTEGER DEFAULT 0,
    paris_perdus INTEGER DEFAULT 0,
    predictions_correctes INTEGER DEFAULT 0,
    predictions_totales INTEGER DEFAULT 0,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_jeux_historique_date_type ON jeux_historique(date, type_jeu);
