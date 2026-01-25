-- ════════════════════════════════════════════════════════════════════════════
-- MODULE MAISON - Scripts SQL pour Supabase
-- Tables pour Projets, Jardin, et Entretien
-- 
-- Date: 25 Janvier 2026
-- Status: Production-ready
-- ════════════════════════════════════════════════════════════════════════════

-- ════════════════════════════════════════════════════════════════════════════
-- 1. TABLE PROJETS (Maison)
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin_prevue DATE,
    date_fin_reelle DATE,
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indices pour performance
    CONSTRAINT ck_statut CHECK (statut IN ('à_faire', 'en_cours', 'terminé', 'annulé')),
    CONSTRAINT ck_priorite CHECK (priorite IN ('basse', 'moyenne', 'haute', 'urgente'))
);

CREATE INDEX IF NOT EXISTS idx_projects_statut ON projects(statut);
CREATE INDEX IF NOT EXISTS idx_projects_priorite ON projects(priorite);

-- ════════════════════════════════════════════════════════════════════════════
-- 2. TABLE TÂCHES PROJETS
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'à_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echéance DATE,
    assigné_à VARCHAR(200),
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_task_statut CHECK (statut IN ('à_faire', 'en_cours', 'terminé', 'annulé')),
    CONSTRAINT ck_task_priorite CHECK (priorite IN ('basse', 'moyenne', 'haute', 'urgente'))
);

CREATE INDEX IF NOT EXISTS idx_project_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_statut ON project_tasks(statut);

-- ════════════════════════════════════════════════════════════════════════════
-- 3. TABLE JARDIN - PLANTES
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS garden_items (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    date_plantation DATE,
    date_recolte_prevue DATE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_garden_statut CHECK (statut IN ('actif', 'inactif', 'mort'))
);

CREATE INDEX IF NOT EXISTS idx_garden_items_type ON garden_items(type);
CREATE INDEX IF NOT EXISTS idx_garden_items_statut ON garden_items(statut);

-- ════════════════════════════════════════════════════════════════════════════
-- 4. TABLE JARDIN - JOURNAL D'ENTRETIEN
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS garden_logs (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER REFERENCES garden_items(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_garden_logs_garden_item_id ON garden_logs(garden_item_id);
CREATE INDEX IF NOT EXISTS idx_garden_logs_date ON garden_logs(date);

-- ════════════════════════════════════════════════════════════════════════════
-- 5. TABLE ENTRETIEN - ROUTINES
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    frequence VARCHAR(50) NOT NULL DEFAULT 'quotidien',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ck_frequence CHECK (frequence IN ('quotidien', 'hebdomadaire', 'bi-hebdomadaire', 'mensuel'))
);

CREATE INDEX IF NOT EXISTS idx_routines_categorie ON routines(categorie);
CREATE INDEX IF NOT EXISTS idx_routines_actif ON routines(actif);

-- ════════════════════════════════════════════════════════════════════════════
-- 6. TABLE ENTRETIEN - TÂCHES DE ROUTINES
-- ════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS routine_tasks (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routine_tasks_routine_id ON routine_tasks(routine_id);

-- ════════════════════════════════════════════════════════════════════════════
-- VÉRIFICATION DES TABLES
-- ════════════════════════════════════════════════════════════════════════════

-- Afficher les tables créées
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
