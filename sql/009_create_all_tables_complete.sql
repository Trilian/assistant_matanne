-- ════════════════════════════════════════════════════════════════════════════
-- CRÉATION DE TOUTES LES TABLES - Assistant MaTanne v2.0
-- Date: 25 Janvier 2026
-- Exécuter ce script sur Supabase SQL Editor
-- ════════════════════════════════════════════════════════════════════════════

-- ═════════════════════════════════════════════════════════════════════════════
-- 🍽️  MODULE RECETTES (5 tables)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL UNIQUE,
    categorie VARCHAR(100),
    unite VARCHAR(50) NOT NULL DEFAULT 'pcs',
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recettes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    temps_preparation INTEGER NOT NULL,
    temps_cuisson INTEGER NOT NULL DEFAULT 0,
    portions INTEGER NOT NULL DEFAULT 4,
    difficulte VARCHAR(50) NOT NULL DEFAULT 'moyen',
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    saison VARCHAR(50) NOT NULL DEFAULT 'toute_année',
    categorie VARCHAR(100),
    est_rapide BOOLEAN DEFAULT FALSE,
    est_equilibre BOOLEAN DEFAULT FALSE,
    compatible_bebe BOOLEAN DEFAULT FALSE,
    compatible_batch BOOLEAN DEFAULT FALSE,
    congelable BOOLEAN DEFAULT FALSE,
    est_bio BOOLEAN DEFAULT FALSE,
    est_local BOOLEAN DEFAULT FALSE,
    score_bio INTEGER DEFAULT 0,
    score_local INTEGER DEFAULT 0,
    compatible_cookeo BOOLEAN DEFAULT FALSE,
    compatible_monsieur_cuisine BOOLEAN DEFAULT FALSE,
    compatible_airfryer BOOLEAN DEFAULT FALSE,
    compatible_multicooker BOOLEAN DEFAULT FALSE,
    calories INTEGER,
    proteines FLOAT,
    lipides FLOAT,
    glucides FLOAT,
    genere_par_ia BOOLEAN DEFAULT FALSE,
    score_ia FLOAT,
    url_image VARCHAR(500),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantite FLOAT,
    unite VARCHAR(20),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS etapes_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    numero_etape INTEGER,
    description TEXT,
    temps_minutes INTEGER,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS versions_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    nom_version VARCHAR(200),
    description TEXT,
    modifications TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 🛍️  MODULE COURSES (2 tables)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS articles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),
    quantite FLOAT,
    unite VARCHAR(20),
    prix FLOAT,
    statut VARCHAR(50) DEFAULT 'à_acheter',
    date_achat DATE,
    code_barre VARCHAR(20),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles_inventaire (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),
    quantite FLOAT,
    unite VARCHAR(20),
    date_expiration DATE,
    localisation VARCHAR(200),
    prix_unit FLOAT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 👨‍👩‍👧‍👦 MODULE FAMILLE (6 tables)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS child_profiles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    prenom VARCHAR(200) NOT NULL,
    date_naissance DATE,
    photos_url TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wellbeing_entries (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES child_profiles(id) ON DELETE CASCADE,
    date_entree DATE,
    sante TEXT,
    sommeil INTEGER,
    humeur VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES child_profiles(id) ON DELETE CASCADE,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    date_atteint DATE,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS family_activities (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100),
    date_prevue DATE,
    cout_estime FLOAT,
    duree_heures INTEGER,
    lieu VARCHAR(200),
    participants TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    frequence VARCHAR(50),
    type_routine VARCHAR(100),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_objectives (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    objectif_type VARCHAR(100),
    date_debut DATE,
    date_fin_prevue DATE,
    progression FLOAT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 🏠 MODULE MAISON (6 tables)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) DEFAULT 'en_cours',
    priorite VARCHAR(50) DEFAULT 'moyenne',
    date_debut DATE,
    date_fin_prevue DATE,
    date_fin_reelle DATE,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_project_statut CHECK (statut IN ('à_faire', 'en_cours', 'terminé', 'annulé')),
    CONSTRAINT ck_project_priorite CHECK (priorite IN ('basse', 'moyenne', 'haute', 'urgente'))
);

CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) DEFAULT 'à_faire',
    priorite VARCHAR(50) DEFAULT 'moyenne',
    date_echéance DATE,
    assigné_à VARCHAR(200),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_task_statut CHECK (statut IN ('à_faire', 'en_cours', 'terminé', 'annulé')),
    CONSTRAINT ck_task_priorite CHECK (priorite IN ('basse', 'moyenne', 'haute', 'urgente'))
);

CREATE TABLE IF NOT EXISTS garden_items (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    statut VARCHAR(50) DEFAULT 'actif',
    date_plantation DATE,
    date_recolte_prevue DATE,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_garden_statut CHECK (statut IN ('actif', 'inactif', 'mort'))
);

CREATE TABLE IF NOT EXISTS garden_logs (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER REFERENCES garden_items(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    frequence VARCHAR(50) DEFAULT 'quotidien',
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_frequence CHECK (frequence IN ('quotidien', 'hebdomadaire', 'bi-hebdomadaire', 'mensuel'))
);

CREATE TABLE IF NOT EXISTS routine_tasks (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 📅 MODULE PLANNING (3 tables)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP,
    lieu VARCHAR(200),
    type_event VARCHAR(50) DEFAULT 'autre',
    couleur VARCHAR(20),
    rappel_avant_minutes INTEGER,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plannings (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    type_planning VARCHAR(100),
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repas (
    id SERIAL PRIMARY KEY,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50),
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    portions INTEGER,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 👨‍🍳 MODULE BATCH COOKING (1 table)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS batch_meals (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions INTEGER,
    date_preparation DATE,
    jours_conservation INTEGER,
    conteneurs_utilises INTEGER,
    cout_total FLOAT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 💰 MODULE BUDGET (1 table)
-- ═════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS family_budgets (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    montant_budget FLOAT NOT NULL,
    montant_utilise FLOAT DEFAULT 0,
    categorie VARCHAR(100) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE,
    couleur VARCHAR(20),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═════════════════════════════════════════════════════════════════════════════
-- 📑 CRÉATION DES INDEX POUR PERFORMANCE
-- ═════════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_recettes_categorie ON recettes(categorie);
CREATE INDEX IF NOT EXISTS idx_recettes_difficulte ON recettes(difficulte);
CREATE INDEX IF NOT EXISTS idx_articles_courses_statut ON articles_courses(statut);
CREATE INDEX IF NOT EXISTS idx_articles_courses_date_achat ON articles_courses(date_achat);
CREATE INDEX IF NOT EXISTS idx_articles_inventaire_categorie ON articles_inventaire(categorie);
CREATE INDEX IF NOT EXISTS idx_child_profiles_nom ON child_profiles(nom);
CREATE INDEX IF NOT EXISTS idx_wellbeing_entries_child_id ON wellbeing_entries(child_id);
CREATE INDEX IF NOT EXISTS idx_milestones_child_id ON milestones(child_id);
CREATE INDEX IF NOT EXISTS idx_milestones_categorie ON milestones(categorie);
CREATE INDEX IF NOT EXISTS idx_family_activities_type_activite ON family_activities(type_activite);
CREATE INDEX IF NOT EXISTS idx_family_activities_date_prevue ON family_activities(date_prevue);
CREATE INDEX IF NOT EXISTS idx_health_routines_type_routine ON health_routines(type_routine);
CREATE INDEX IF NOT EXISTS idx_health_objectives_objectif_type ON health_objectives(objectif_type);
CREATE INDEX IF NOT EXISTS idx_projects_statut ON projects(statut);
CREATE INDEX IF NOT EXISTS idx_projects_priorite ON projects(priorite);
CREATE INDEX IF NOT EXISTS idx_project_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_statut ON project_tasks(statut);
CREATE INDEX IF NOT EXISTS idx_garden_items_type ON garden_items(type);
CREATE INDEX IF NOT EXISTS idx_garden_items_statut ON garden_items(statut);
CREATE INDEX IF NOT EXISTS idx_garden_logs_garden_item_id ON garden_logs(garden_item_id);
CREATE INDEX IF NOT EXISTS idx_garden_logs_date ON garden_logs(date);
CREATE INDEX IF NOT EXISTS idx_routines_categorie ON routines(categorie);
CREATE INDEX IF NOT EXISTS idx_routines_actif ON routines(actif);
CREATE INDEX IF NOT EXISTS idx_routine_tasks_routine_id ON routine_tasks(routine_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_date_debut ON calendar_events(date_debut);
CREATE INDEX IF NOT EXISTS idx_calendar_events_type_event ON calendar_events(type_event);
CREATE INDEX IF NOT EXISTS idx_plannings_date_debut ON plannings(date_debut);
CREATE INDEX IF NOT EXISTS idx_plannings_type_planning ON plannings(type_planning);
CREATE INDEX IF NOT EXISTS idx_repas_date_repas ON repas(date_repas);
CREATE INDEX IF NOT EXISTS idx_batch_meals_date_preparation ON batch_meals(date_preparation);
CREATE INDEX IF NOT EXISTS idx_family_budgets_categorie ON family_budgets(categorie);
CREATE INDEX IF NOT EXISTS idx_family_budgets_date_debut ON family_budgets(date_debut);

-- ═════════════════════════════════════════════════════════════════════════════
-- ✅ SCRIPT COMPLET - ASSISTANT MATANNE v2.0
-- ═════════════════════════════════════════════════════════════════════════════
-- Crée 24 tables avec indices pour performance
-- Date: 25 Janvier 2026
-- ═════════════════════════════════════════════════════════════════════════════
