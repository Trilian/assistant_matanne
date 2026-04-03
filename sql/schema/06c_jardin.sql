-- ============================================================================
-- ASSISTANT MATANNE — Maison : Jardin & Autonomie
-- ============================================================================
-- Contient : jardin, plans, zones, plantes, récoltes, autonomie alimentaire
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE elements_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_plante VARCHAR(100) NOT NULL,
    emplacement VARCHAR(200),
    date_plantation DATE,
    frequence_arrosage VARCHAR(50),
    derniere_action DATE,
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_garden_items_type ON elements_jardin(type_plante);
CREATE INDEX IF NOT EXISTS ix_garden_items_statut ON elements_jardin(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plans_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    largeur NUMERIC(6, 2) NOT NULL,
    hauteur NUMERIC(6, 2) NOT NULL,
    description TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_plans_jardin_nom ON plans_jardin(nom);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE journaux_jardin (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garden_logs_item FOREIGN KEY (garden_item_id) REFERENCES elements_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_garden_logs_item ON journaux_jardin(garden_item_id);
CREATE INDEX IF NOT EXISTS ix_garden_logs_date ON journaux_jardin(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER,
    nom VARCHAR(100) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    superficie_m2 NUMERIC(8, 2),
    exposition VARCHAR(10),
    type_sol VARCHAR(50),
    arrosage_auto BOOLEAN DEFAULT FALSE,
    description TEXT,
    -- Positions 2D (canvas)
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    couleur VARCHAR(20) DEFAULT '#4CAF50',
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_zones_jardin_plan_id FOREIGN KEY (plan_id) REFERENCES plans_jardin(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_type ON zones_jardin(type_zone);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_plan_id ON zones_jardin(plan_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plantes_jardin (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    variete VARCHAR(100),
    etat VARCHAR(20) DEFAULT 'bon',
    date_plantation DATE,
    mois_semis VARCHAR(100),
    mois_recolte VARCHAR(100),
    arrosage VARCHAR(50),
    notes TEXT,
    position_x NUMERIC(8, 2),
    position_y NUMERIC(8, 2),
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_plantes_jardin_zone FOREIGN KEY (zone_id) REFERENCES zones_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plantes_jardin_zone ON plantes_jardin(zone_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE actions_plantes (
    id SERIAL PRIMARY KEY,
    plante_id INTEGER NOT NULL,
    type_action VARCHAR(50) NOT NULL,
    date_action DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite NUMERIC(8, 2),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_actions_plantes_plante_id FOREIGN KEY (plante_id) REFERENCES plantes_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_plante_id ON actions_plantes(plante_id);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_type_action ON actions_plantes(type_action);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_date_action ON actions_plantes(date_action);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plantes_catalogue (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    nom_latin VARCHAR(150),
    famille VARCHAR(50),
    varietes JSONB DEFAULT '[]',
    mois_semis_interieur JSONB DEFAULT '[]',
    mois_semis_exterieur JSONB DEFAULT '[]',
    mois_plantation JSONB DEFAULT '[]',
    mois_recolte JSONB DEFAULT '[]',
    compagnons_positifs JSONB DEFAULT '[]',
    compagnons_negatifs JSONB DEFAULT '[]',
    espacement_cm INTEGER DEFAULT 30,
    profondeur_semis_cm INTEGER DEFAULT 2,
    jours_germination INTEGER DEFAULT 10,
    jours_jusqu_recolte INTEGER DEFAULT 60,
    arrosage VARCHAR(20) DEFAULT 'regulier' CHECK (
        arrosage IN ('quotidien', 'regulier', 'modere', 'faible')
    ),
    exposition VARCHAR(20) DEFAULT 'soleil' CHECK (
        exposition IN ('soleil', 'mi_ombre', 'ombre')
    ),
    rendement_kg_m2 DECIMAL(4, 2) DEFAULT 2.0,
    besoin_famille_4_kg_an DECIMAL(6, 2),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plantes_catalogue_famille ON plantes_catalogue(famille);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE recoltes (
    id SERIAL PRIMARY KEY,
    plante_jardin_id INTEGER REFERENCES plantes_jardin(id) ON DELETE CASCADE,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE CASCADE,
    legume VARCHAR(100) NOT NULL,
    date_recolte DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite_kg DECIMAL(6, 2) NOT NULL,
    qualite VARCHAR(20) DEFAULT 'bonne' CHECK (
        qualite IN ('excellente', 'bonne', 'moyenne', 'passable')
    ),
    destination VARCHAR(20) DEFAULT 'frais' CHECK (
        destination IN ('frais', 'conserve', 'congele', 'donne', 'perdu')
    ),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_recoltes_date ON recoltes(date_recolte);
CREATE INDEX IF NOT EXISTS idx_recoltes_legume ON recoltes(legume);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE objectifs_autonomie (
    id SERIAL PRIMARY KEY,
    legume VARCHAR(100) NOT NULL UNIQUE,
    besoin_kg_an DECIMAL(6, 2) NOT NULL,
    surface_ideale_m2 DECIMAL(6, 2),
    production_kg_an DECIMAL(6, 2) DEFAULT 0,
    surface_actuelle_m2 DECIMAL(6, 2) DEFAULT 0,
    pourcentage_atteint INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN besoin_kg_an > 0 THEN LEAST(
                100,
                ROUND((production_kg_an / besoin_kg_an) * 100)
            )
            ELSE 0
        END
    ) STORED,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


