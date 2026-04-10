-- ============================================================================
-- ASSISTANT MATANNE — Tables Jeux
-- ============================================================================
-- Contient : jeux_equipes, jeux_matchs, paris_sportifs, loto, euromillions,
--            séries, alertes, cotes_historique
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_equipes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    nom_court VARCHAR(50),
    championnat VARCHAR(50) NOT NULL,
    pays VARCHAR(50),
    logo_url VARCHAR(255),
    matchs_joues INTEGER NOT NULL DEFAULT 0,
    victoires INTEGER NOT NULL DEFAULT 0,
    nuls INTEGER NOT NULL DEFAULT 0,
    defaites INTEGER NOT NULL DEFAULT 0,
    buts_marques INTEGER NOT NULL DEFAULT 0,
    buts_encaisses INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_tirages_loto (
    id SERIAL PRIMARY KEY,
    date_tirage DATE NOT NULL,
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    jackpot_euros INTEGER,
    gagnants_rang1 INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_tirages_loto_date ON jeux_tirages_loto(date_tirage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_stats_loto (
    id SERIAL PRIMARY KEY,
    date_calcul TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    frequences_numeros JSONB,
    frequences_chance JSONB,
    numeros_chauds JSONB,
    numeros_froids JSONB,
    numeros_retard JSONB,
    somme_moyenne FLOAT,
    paires_frequentes JSONB,
    nb_tirages_analyses INTEGER NOT NULL DEFAULT 0
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_historique (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    nb_paris INTEGER NOT NULL DEFAULT 0,
    mises_totales NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    gains_totaux NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    paris_gagnes INTEGER NOT NULL DEFAULT 0,
    paris_perdus INTEGER NOT NULL DEFAULT 0,
    predictions_correctes INTEGER NOT NULL DEFAULT 0,
    predictions_totales INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_series (
    id SERIAL PRIMARY KEY,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    serie_actuelle INTEGER NOT NULL DEFAULT 0,
    frequence FLOAT NOT NULL DEFAULT 0.0,
    nb_occurrences INTEGER NOT NULL DEFAULT 0,
    nb_total INTEGER NOT NULL DEFAULT 0,
    derniere_occurrence DATE,
    derniere_mise_a_jour TIMESTAMP,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_championnat ON jeux_series(type_jeu, championnat);
CREATE INDEX IF NOT EXISTS ix_jeux_series_type_jeu_marche ON jeux_series(type_jeu, marche);
CREATE INDEX IF NOT EXISTS ix_jeux_series_value ON jeux_series((frequence * serie_actuelle) DESC);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_configuration (
    id SERIAL PRIMARY KEY,
    cle VARCHAR(50) NOT NULL UNIQUE,
    valeur TEXT NOT NULL,
    description TEXT,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_matchs (
    id SERIAL PRIMARY KEY,
    equipe_domicile_id INTEGER NOT NULL,
    equipe_exterieur_id INTEGER NOT NULL,
    championnat VARCHAR(50) NOT NULL,
    journee INTEGER,
    date_match DATE NOT NULL,
    heure VARCHAR(5),
    score_domicile INTEGER,
    score_exterieur INTEGER,
    resultat VARCHAR(10),
    joue BOOLEAN NOT NULL DEFAULT FALSE,
    cote_domicile FLOAT,
    cote_nul FLOAT,
    cote_exterieur FLOAT,
    prediction_resultat VARCHAR(10),
    prediction_proba_dom FLOAT,
    prediction_proba_nul FLOAT,
    prediction_proba_ext FLOAT,
    prediction_confiance FLOAT,
    prediction_raison TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_jeux_matchs_dom FOREIGN KEY (equipe_domicile_id) REFERENCES jeux_equipes(id),
    CONSTRAINT fk_jeux_matchs_ext FOREIGN KEY (equipe_exterieur_id) REFERENCES jeux_equipes(id)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_paris_sportifs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    match_id INTEGER NOT NULL,
    type_pari VARCHAR(30) NOT NULL DEFAULT '1N2',
    prediction VARCHAR(20) NOT NULL,
    cote FLOAT NOT NULL,
    mise NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    gain NUMERIC(10, 2),
    est_virtuel BOOLEAN NOT NULL DEFAULT TRUE,
    confiance_prediction FLOAT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_jeux_paris_match FOREIGN KEY (match_id) REFERENCES jeux_matchs(id)
);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_match_id ON jeux_paris_sportifs(match_id);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_statut ON jeux_paris_sportifs(statut);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_cree_le ON jeux_paris_sportifs(cree_le);
CREATE INDEX IF NOT EXISTS idx_paris_match_date ON jeux_paris_sportifs(match_id, cree_le);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_grilles_loto (
    id SERIAL PRIMARY KEY,
    tirage_id INTEGER,
    numero_1 INTEGER NOT NULL,
    numero_2 INTEGER NOT NULL,
    numero_3 INTEGER NOT NULL,
    numero_4 INTEGER NOT NULL,
    numero_5 INTEGER NOT NULL,
    numero_chance INTEGER NOT NULL,
    est_virtuelle BOOLEAN NOT NULL DEFAULT TRUE,
    source_prediction VARCHAR(50) NOT NULL DEFAULT 'manuel',
    mise NUMERIC(10, 2) NOT NULL DEFAULT 2.20,
    numeros_trouves INTEGER,
    chance_trouvee BOOLEAN,
    gain NUMERIC(10, 2),
    rang INTEGER,
    date_creation TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    notes TEXT,
    CONSTRAINT fk_jeux_grilles_tirage FOREIGN KEY (tirage_id) REFERENCES jeux_tirages_loto(id)
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jeux_alertes (
    id SERIAL PRIMARY KEY,
    serie_id INTEGER NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    value_alerte FLOAT NOT NULL,
    serie_alerte INTEGER NOT NULL,
    frequence_alerte FLOAT NOT NULL,
    seuil_utilise FLOAT NOT NULL DEFAULT 2.0,
    notifie BOOLEAN NOT NULL DEFAULT FALSE,
    date_notification TIMESTAMP,
    resultat_verifie BOOLEAN NOT NULL DEFAULT FALSE,
    resultat_correct BOOLEAN,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jeux_alertes_serie FOREIGN KEY (serie_id) REFERENCES jeux_series(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_notifie ON jeux_alertes(notifie)
WHERE notifie = FALSE;
CREATE INDEX IF NOT EXISTS ix_jeux_alertes_resultat ON jeux_alertes(resultat_verifie, resultat_correct);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- Source: 09_notifications.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Notifications
-- ============================================================================
-- Contient : abonnements_push, preferences_notifications, webhooks_abonnements,
--            historique_notifications
-- ============================================================================

