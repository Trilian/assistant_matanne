-- ============================================================
-- MIGRATION SUPABASE - Module Famille (Jules, Santé, Activités, Shopping)
-- ============================================================
-- Exécute ce script dans Supabase SQL Editor pour ajouter les tables
-- Date: 2026-01-24
-- Version: 1.0
-- ============================================================


-- ============================================================
-- 0. TABLE CHILD_PROFILES (Profils Enfants - Dépendance)
-- ============================================================

CREATE TABLE IF NOT EXISTS child_profiles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    notes TEXT,
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_child_profiles_actif ON child_profiles(actif);
CREATE INDEX IF NOT EXISTS idx_child_profiles_name ON child_profiles(name);


-- ============================================================
-- 1. TABLE MILESTONES (Jalons Jules)
-- ============================================================

CREATE TABLE IF NOT EXISTS milestones (
    id BIGSERIAL PRIMARY KEY,
    child_id BIGINT NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_milestone_categorie CHECK (categorie IN ('langage', 'motricité', 'social', 'cognitif', 'alimentation', 'sommeil', 'autre'))
);

CREATE INDEX idx_milestones_child_id ON milestones(child_id);
CREATE INDEX idx_milestones_date_atteint ON milestones(date_atteint);
CREATE INDEX idx_milestones_categorie ON milestones(categorie);


-- ============================================================
-- 2. TABLE FAMILY_ACTIVITIES (Activités Familiales)
-- ============================================================

CREATE TABLE IF NOT EXISTS family_activities (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    duree_heures FLOAT,
    lieu VARCHAR(200),
    qui_participe JSONB,
    age_minimal_recommande INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_activite_duree_positive CHECK (duree_heures > 0 OR duree_heures IS NULL),
    CONSTRAINT ck_activite_age_positif CHECK (age_minimal_recommande >= 0 OR age_minimal_recommande IS NULL),
    CONSTRAINT ck_activite_statut CHECK (statut IN ('planifié', 'terminé', 'annulé'))
);

CREATE INDEX idx_family_activities_date_prevue ON family_activities(date_prevue);
CREATE INDEX idx_family_activities_statut ON family_activities(statut);
CREATE INDEX idx_family_activities_type_activite ON family_activities(type_activite);


-- ============================================================
-- 3. TABLE HEALTH_ROUTINES (Routines Sport)
-- ============================================================

CREATE TABLE IF NOT EXISTS health_routines (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    frequence VARCHAR(50) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50) NOT NULL DEFAULT 'modérée',
    jours_semaine JSONB,
    calories_brulees_estimees INTEGER,
    actif BOOLEAN DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_routine_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_routine_intensite CHECK (intensite IN ('basse', 'modérée', 'haute'))
);

CREATE INDEX idx_health_routines_actif ON health_routines(actif);
CREATE INDEX idx_health_routines_type_routine ON health_routines(type_routine);


-- ============================================================
-- 4. TABLE HEALTH_OBJECTIVES (Objectifs Santé)
-- ============================================================

CREATE TABLE IF NOT EXISTS health_objectives (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    valeur_cible FLOAT NOT NULL,
    unite VARCHAR(50),
    valeur_actuelle FLOAT,
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    date_cible DATE NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_objective_valeur_positive CHECK (valeur_cible > 0),
    CONSTRAINT ck_objective_dates CHECK (date_debut <= date_cible),
    CONSTRAINT ck_objective_priorite CHECK (priorite IN ('basse', 'moyenne', 'haute')),
    CONSTRAINT ck_objective_statut CHECK (statut IN ('en_cours', 'atteint', 'abandonné'))
);

CREATE INDEX idx_health_objectives_statut ON health_objectives(statut);
CREATE INDEX idx_health_objectives_date_cible ON health_objectives(date_cible);
CREATE INDEX idx_health_objectives_priorite ON health_objectives(priorite);


-- ============================================================
-- 5. TABLE HEALTH_ENTRIES (Suivi Santé Quotidien)
-- ============================================================

CREATE TABLE IF NOT EXISTS health_entries (
    id BIGSERIAL PRIMARY KEY,
    routine_id BIGINT REFERENCES health_routines(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type_activite VARCHAR(100) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50),
    calories_brulees INTEGER,
    note_energie INTEGER,
    note_moral INTEGER,
    ressenti TEXT,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (note_energie >= 1 AND note_energie <= 10 OR note_energie IS NULL),
    CONSTRAINT ck_entry_moral CHECK (note_moral >= 1 AND note_moral <= 10 OR note_moral IS NULL),
    CONSTRAINT ck_entry_intensite CHECK (intensite IN ('basse', 'modérée', 'haute') OR intensite IS NULL)
);

CREATE INDEX idx_health_entries_date ON health_entries(date);
CREATE INDEX idx_health_entries_routine_id ON health_entries(routine_id);
CREATE INDEX idx_health_entries_type_activite ON health_entries(type_activite);


-- ============================================================
-- 6. TABLE FAMILY_BUDGETS (Budget Famille)
-- ============================================================

CREATE TABLE IF NOT EXISTS family_budgets (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    categorie VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    montant FLOAT NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ck_budget_montant_positive CHECK (montant > 0),
    CONSTRAINT ck_budget_categorie CHECK (
        categorie IN (
            'Jules_jouets',
            'Jules_vetements',
            'Jules_couches',
            'Nous_sport',
            'Nous_nutrition',
            'Activités',
            'Autre'
        )
    )
);

CREATE INDEX idx_family_budgets_date ON family_budgets(date);
CREATE INDEX idx_family_budgets_categorie ON family_budgets(categorie);


-- ============================================================
-- 7. DONNÉES DE TEST (Optionnel - Commenter si pas nécessaire)
-- ============================================================

-- Insérer Jules s'il n'existe pas
INSERT INTO child_profiles (name, date_of_birth, gender, notes, actif, cree_le)
VALUES ('Jules', '2024-06-22', 'M', 'Notre petit Jules ❤️', TRUE, NOW())
ON CONFLICT DO NOTHING;

-- Insérer quelques jalons d'exemple
INSERT INTO milestones (child_id, titre, description, categorie, date_atteint, notes, cree_le)
SELECT 
    cp.id,
    'Premiers jalons de Jules',
    'Suivi de ses apprentissages',
    'langage',
    CURRENT_DATE,
    'Exemple de jalon',
    NOW()
FROM child_profiles cp
WHERE cp.name = 'Jules'
ON CONFLICT DO NOTHING;


-- ============================================================
-- 8. VIEWS UTILES (Optionnel)
-- ============================================================

-- Vue: Budget mensuel
CREATE OR REPLACE VIEW v_family_budget_monthly AS
SELECT 
    DATE_TRUNC('month', date)::DATE as mois,
    categorie,
    COUNT(*) as nb_entries,
    SUM(montant) as total_montant
FROM family_budgets
GROUP BY DATE_TRUNC('month', date), categorie
ORDER BY mois DESC, categorie;

-- Vue: Activités semaine
CREATE OR REPLACE VIEW v_family_activities_week AS
SELECT 
    *,
    (date_prevue - CURRENT_DATE) as jours_avant
FROM family_activities
WHERE date_prevue >= CURRENT_DATE 
  AND date_prevue < CURRENT_DATE + INTERVAL '7 days'
ORDER BY date_prevue;

-- Vue: Routines actives
CREATE OR REPLACE VIEW v_health_routines_active AS
SELECT *
FROM health_routines
WHERE actif = TRUE
ORDER BY cree_le DESC;

-- Vue: Objectifs en cours
CREATE OR REPLACE VIEW v_health_objectives_active AS
SELECT 
    *,
    CASE 
        WHEN valeur_cible > 0 AND valeur_actuelle > 0 
        THEN (valeur_actuelle / valeur_cible * 100)::INT
        ELSE 0
    END as progression_pct
FROM health_objectives
WHERE statut = 'en_cours'
ORDER BY priorite, date_cible;


-- ============================================================
-- 9. RÉSUMÉ DES CHANGEMENTS
-- ============================================================
/*
Tables créées:
✅ milestones - Jalons et apprentissages de Jules
✅ family_activities - Activités et sorties familiales
✅ health_routines - Routines de sport/santé
✅ health_objectives - Objectifs de santé/bien-être
✅ health_entries - Entrées de suivi quotidien
✅ family_budgets - Dépenses familiales

Views créées:
✅ v_family_budget_monthly - Budget mensuel par catégorie
✅ v_family_activities_week - Activités de la semaine
✅ v_health_routines_active - Routines actives
✅ v_health_objectives_active - Objectifs en cours

Total: 6 tables + 4 views
Indices: 14+ pour performance optimale

Compatible avec: SQLAlchemy ORM (src/core/models.py)
*/
