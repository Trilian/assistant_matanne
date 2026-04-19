-- Migration: Ajout tables simulation rénovation, plans maison, zones terrain
-- Date: 2026-04-19
-- Description: Phase 1 refonte module maison — simulateur multi-scénarios + éditeur 2D + terrain

-- ═══════════════════════════════════════════════════════════
-- PLANS MAISON (doit être créé avant simulations à cause des FK)
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS plans_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_plan VARCHAR(50) NOT NULL DEFAULT 'interieur',
    version INTEGER NOT NULL DEFAULT 1,
    est_actif BOOLEAN NOT NULL DEFAULT TRUE,
    donnees_canvas JSONB,
    echelle_px_par_m FLOAT NOT NULL DEFAULT 50.0,
    largeur_canvas INTEGER NOT NULL DEFAULT 1200,
    hauteur_canvas INTEGER NOT NULL DEFAULT 800,
    etage INTEGER NOT NULL DEFAULT 0,
    thumbnail_path VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plans_maison_type ON plans_maison(type_plan);
CREATE INDEX IF NOT EXISTS idx_plans_maison_actif ON plans_maison(est_actif);

-- ═══════════════════════════════════════════════════════════
-- SIMULATIONS RÉNOVATION
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS simulations_renovation (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_projet VARCHAR(100) NOT NULL,
    statut VARCHAR(30) NOT NULL DEFAULT 'brouillon',
    pieces_concernees TEXT,
    zones_terrain TEXT,
    projet_id INTEGER REFERENCES projets(id),
    plan_id INTEGER REFERENCES plans_maison(id),
    tags VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_simulations_type ON simulations_renovation(type_projet);
CREATE INDEX IF NOT EXISTS idx_simulations_statut ON simulations_renovation(statut);
CREATE INDEX IF NOT EXISTS idx_simulations_projet ON simulations_renovation(projet_id);
CREATE INDEX IF NOT EXISTS idx_simulations_plan ON simulations_renovation(plan_id);

-- ═══════════════════════════════════════════════════════════
-- SCÉNARIOS SIMULATION
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS scenarios_simulation (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES simulations_renovation(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    est_favori BOOLEAN NOT NULL DEFAULT FALSE,
    budget_estime_min NUMERIC(12,2),
    budget_estime_max NUMERIC(12,2),
    budget_materiaux NUMERIC(12,2),
    budget_main_oeuvre NUMERIC(12,2),
    duree_estimee_jours INTEGER,
    score_faisabilite INTEGER,
    analyse_faisabilite TEXT,
    contraintes_techniques TEXT,
    recommandations TEXT,
    impact_dpe VARCHAR(10),
    gain_energetique_pct FLOAT,
    plus_value_estimee NUMERIC(12,2),
    postes_travaux JSONB,
    artisans_necessaires TEXT,
    plan_avant_id INTEGER REFERENCES plans_maison(id),
    plan_apres_id INTEGER REFERENCES plans_maison(id),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scenarios_simulation ON scenarios_simulation(simulation_id);

-- ═══════════════════════════════════════════════════════════
-- ZONES TERRAIN
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS zones_terrain (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    description TEXT,
    surface_m2 FLOAT,
    altitude_min FLOAT,
    altitude_max FLOAT,
    pente_pct FLOAT,
    exposition VARCHAR(20),
    geometrie JSONB,
    lien_jardin BOOLEAN NOT NULL DEFAULT FALSE,
    etat VARCHAR(50) NOT NULL DEFAULT 'existant',
    date_amenagement DATE,
    cout_amenagement NUMERIC(12,2),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zones_terrain_type ON zones_terrain(type_zone);

-- ═══════════════════════════════════════════════════════════
-- RLS (Row Level Security)
-- ═══════════════════════════════════════════════════════════

ALTER TABLE plans_maison ENABLE ROW LEVEL SECURITY;
ALTER TABLE simulations_renovation ENABLE ROW LEVEL SECURITY;
ALTER TABLE scenarios_simulation ENABLE ROW LEVEL SECURITY;
ALTER TABLE zones_terrain ENABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════
-- TRIGGERS modifie_le
-- ═══════════════════════════════════════════════════════════

CREATE OR REPLACE TRIGGER trg_plans_maison_modifie_le
    BEFORE UPDATE ON plans_maison
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

CREATE OR REPLACE TRIGGER trg_simulations_renovation_modifie_le
    BEFORE UPDATE ON simulations_renovation
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

CREATE OR REPLACE TRIGGER trg_scenarios_simulation_modifie_le
    BEFORE UPDATE ON scenarios_simulation
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

CREATE OR REPLACE TRIGGER trg_zones_terrain_modifie_le
    BEFORE UPDATE ON zones_terrain
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();
