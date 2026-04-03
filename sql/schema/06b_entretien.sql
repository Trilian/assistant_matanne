-- ============================================================================
-- ASSISTANT MATANNE — Maison : Entretien & Organisation
-- ============================================================================
-- Contient : entretien, préférences home, tâches home, stats, checklists
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_entretien (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    piece VARCHAR(50),
    frequence_jours INTEGER,
    derniere_fois DATE,
    prochaine_fois DATE,
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    responsable VARCHAR(50),
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    fait BOOLEAN NOT NULL DEFAULT FALSE,
    integrer_planning BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_categorie ON taches_entretien(categorie);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_prochaine ON taches_entretien(prochaine_fois);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_fait ON taches_entretien(fait);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE preferences_home (
    id SERIAL PRIMARY KEY,
    max_taches_jour INTEGER DEFAULT 3,
    max_heures_jour DECIMAL(4, 2) DEFAULT 2.0,
    heures_jardin JSONB DEFAULT '[7, 8, 18, 19]',
    heures_menage JSONB DEFAULT '[9, 10, 14, 15]',
    heures_admin JSONB DEFAULT '[20, 21]',
    jours_jardin JSONB DEFAULT '[6, 7]',
    jours_menage JSONB DEFAULT '[6]',
    notification_matin BOOLEAN DEFAULT TRUE,
    heure_briefing INTEGER DEFAULT 7,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_home (
    id SERIAL PRIMARY KEY,
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN ('jardin', 'entretien', 'charges', 'depenses')
    ),
    type_tache VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_min INTEGER DEFAULT 15,
    priorite VARCHAR(20) DEFAULT 'normale' CHECK (
        priorite IN (
            'urgente',
            'haute',
            'normale',
            'basse',
            'optionnelle'
        )
    ),
    date_due DATE,
    date_faite DATE,
    statut VARCHAR(20) DEFAULT 'a_faire' CHECK (
        statut IN (
            'a_faire',
            'en_cours',
            'fait',
            'reporte',
            'annule'
        )
    ),
    generee_auto BOOLEAN DEFAULT FALSE,
    source VARCHAR(50),
    source_id INTEGER,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE
    SET NULL,
        piece_id INTEGER REFERENCES pieces_maison(id) ON DELETE
    SET NULL,
        cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_taches_home_domaine ON taches_home(domaine);
CREATE INDEX IF NOT EXISTS idx_taches_home_statut ON taches_home(statut);
CREATE INDEX IF NOT EXISTS idx_taches_home_date_due ON taches_home(date_due);
CREATE INDEX IF NOT EXISTS idx_taches_home_source ON taches_home(source, source_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE stats_home (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN (
            'jardin',
            'entretien',
            'charges',
            'depenses',
            'total'
        )
    ),
    temps_prevu_min INTEGER DEFAULT 0,
    temps_reel_min INTEGER DEFAULT 0,
    taches_prevues INTEGER DEFAULT 0,
    taches_completees INTEGER DEFAULT 0,
    taches_reportees INTEGER DEFAULT 0,
    score_jour INTEGER DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, domaine)
);
CREATE INDEX IF NOT EXISTS idx_stats_home_date ON stats_home(date);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE checklists_vacances (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_voyage VARCHAR(50) NOT NULL,
    destination VARCHAR(200),
    duree_jours INTEGER,
    date_depart DATE,
    date_retour DATE,
    terminee BOOLEAN DEFAULT FALSE,
    archivee BOOLEAN DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_checklists_type_voyage ON checklists_vacances(type_voyage);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE items_checklist (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES checklists_vacances(id) ON DELETE CASCADE,
    libelle VARCHAR(300) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    ordre INTEGER DEFAULT 0,
    fait BOOLEAN DEFAULT FALSE,
    responsable VARCHAR(50),
    quand VARCHAR(20),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_items_checklist_checklist ON items_checklist(checklist_id);


