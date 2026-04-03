-- ============================================================================
-- ASSISTANT MATANNE — Tables Habitat
-- ============================================================================
-- Contient : habitat_scenarios, habitat_plans, habitat_pieces,
--            habitat_criteres_immo, habitat_annonces, habitat_projets_deco
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_scenarios (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    budget_estime DECIMAL(12,2),
    surface_finale_m2 DECIMAL(8,2),
    nb_chambres INTEGER,
    score_global DECIMAL(5,2),
    avantages JSONB DEFAULT '[]'::jsonb,
    inconvenients JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    statut VARCHAR(50) DEFAULT 'brouillon',
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_statut ON habitat_scenarios(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_scenarios_score ON habitat_scenarios(score_global);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_criteres (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES habitat_scenarios(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    poids DECIMAL(4,2) DEFAULT 1.00,
    note DECIMAL(3,1),
    commentaire TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_criteres_scenario ON habitat_criteres(scenario_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_criteres_immo (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) DEFAULT 'Recherche principale',
    departements JSONB DEFAULT '[]'::jsonb,
    villes JSONB DEFAULT '[]'::jsonb,
    rayon_km INTEGER DEFAULT 10,
    budget_min DECIMAL(12,2),
    budget_max DECIMAL(12,2),
    surface_min_m2 DECIMAL(8,2),
    surface_terrain_min_m2 DECIMAL(10,2),
    nb_pieces_min INTEGER,
    nb_chambres_min INTEGER,
    type_bien VARCHAR(50),
    criteres_supplementaires JSONB DEFAULT '{}'::jsonb,
    seuil_alerte DECIMAL(5,2) DEFAULT 0.70,
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_annonces (
    id SERIAL PRIMARY KEY,
    critere_id INTEGER REFERENCES habitat_criteres_immo(id) ON DELETE SET NULL,
    source VARCHAR(100) NOT NULL,
    url_source VARCHAR(500) NOT NULL,
    titre VARCHAR(500),
    prix DECIMAL(12,2),
    surface_m2 DECIMAL(8,2),
    surface_terrain_m2 DECIMAL(10,2),
    nb_pieces INTEGER,
    ville VARCHAR(200),
    code_postal VARCHAR(10),
    departement VARCHAR(3),
    photos JSONB DEFAULT '[]'::jsonb,
    description_brute TEXT,
    score_pertinence DECIMAL(5,2),
    statut VARCHAR(50) DEFAULT 'nouveau',
    prix_m2_secteur DECIMAL(8,2),
    ecart_prix_pct DECIMAL(5,2),
    hash_dedup VARCHAR(64),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_statut ON habitat_annonces(statut);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_source ON habitat_annonces(source);
CREATE INDEX IF NOT EXISTS idx_habitat_annonces_ville ON habitat_annonces(ville);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_plans (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES habitat_scenarios(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    type_plan VARCHAR(50) NOT NULL,
    image_importee_url VARCHAR(500),
    donnees_pieces JSONB NOT NULL DEFAULT '{}'::jsonb,
    contraintes JSONB DEFAULT '{}'::jsonb,
    surface_totale_m2 DECIMAL(8,2),
    budget_estime DECIMAL(12,2),
    notes TEXT,
    version INTEGER DEFAULT 1,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_plans_type ON habitat_plans(type_plan);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_pieces (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    type_piece VARCHAR(50),
    surface_m2 DECIMAL(6,2),
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    hauteur_plafond DECIMAL(4,2),
    couleur_mur VARCHAR(7),
    sol_type VARCHAR(50),
    meubles JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_pieces_plan ON habitat_pieces(plan_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_modifications_plan (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    prompt_utilisateur TEXT NOT NULL,
    analyse_ia JSONB NOT NULL DEFAULT '{}'::jsonb,
    image_generee_url VARCHAR(500),
    acceptee BOOLEAN,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_projets_deco (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER REFERENCES habitat_pieces(id) ON DELETE SET NULL,
    nom_piece VARCHAR(200) NOT NULL,
    style VARCHAR(100),
    palette_couleurs JSONB DEFAULT '[]'::jsonb,
    inspirations JSONB DEFAULT '[]'::jsonb,
    budget_prevu DECIMAL(10,2),
    budget_depense DECIMAL(10,2) DEFAULT 0,
    statut VARCHAR(50) DEFAULT 'idee',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habitat_zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES habitat_plans(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    type_zone VARCHAR(100),
    surface_m2 DECIMAL(8,2),
    altitude_relative DECIMAL(4,2),
    position_x DECIMAL(8,2),
    position_y DECIMAL(8,2),
    largeur DECIMAL(8,2),
    longueur DECIMAL(8,2),
    donnees_canvas JSONB DEFAULT '{}'::jsonb,
    plantes JSONB DEFAULT '[]'::jsonb,
    amenagements JSONB DEFAULT '[]'::jsonb,
    budget_estime DECIMAL(10,2),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_habitat_zones_jardin_plan ON habitat_zones_jardin(plan_id);


-- Source: 08_jeux.sql
-- ============================================================================
-- ASSISTANT MATANNE — Tables Jeux
-- ============================================================================
-- Contient : jeux_equipes, jeux_matchs, paris_sportifs, loto, euromillions,
--            séries, alertes, cotes_historique
-- ============================================================================

