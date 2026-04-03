-- ============================================================================
-- ASSISTANT MATANNE — Maison : Projets & Routines
-- ============================================================================
-- Contient : projets, routines, tâches projet, tâches routine
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE projets (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin DATE,
    budget_estime FLOAT,
    budget_reel FLOAT,
    categorie VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_projects_statut ON projets(statut);
CREATE INDEX IF NOT EXISTS ix_projects_categorie ON projets(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]',
    heure_debut VARCHAR(10),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    moment_journee VARCHAR(20) NOT NULL DEFAULT 'flexible',
    jour_semaine INTEGER,
    derniere_completion DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_routines_type ON routines(type_routine);
CREATE INDEX IF NOT EXISTS ix_routines_actif ON routines(actif);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_projets (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'à_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echeance DATE,
    assigne_a VARCHAR(200),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_project_tasks_project FOREIGN KEY (project_id) REFERENCES projets(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_project_tasks_project ON taches_projets(project_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_statut ON taches_projets(statut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_routines (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_routine_tasks_routine FOREIGN KEY (routine_id) REFERENCES routines(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_routine_tasks_routine ON taches_routines(routine_id);


