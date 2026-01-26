-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- ASSISTANT MATANNE - SCRIPT SQL COMPLET POUR SUPABASE
-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- Version: 3.0.0
-- Date: 2026-01-26
-- Description: Script complet pour créer toutes les tables de l'application
-- Usage: Copier-coller dans Supabase SQL Editor et exécuter
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

BEGIN;

-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 1: TABLES DE BASE (CUISINE)
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Ingrédients
CREATE TABLE IF NOT EXISTS ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL UNIQUE,
    categorie VARCHAR(100),
    unite VARCHAR(50) NOT NULL DEFAULT 'pcs',
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_ingredients_nom ON ingredients(nom);
CREATE INDEX IF NOT EXISTS idx_ingredients_categorie ON ingredients(categorie);

-- Recettes
CREATE TABLE IF NOT EXISTS recettes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    temps_preparation INTEGER NOT NULL DEFAULT 0,
    temps_cuisson INTEGER NOT NULL DEFAULT 0,
    portions INTEGER NOT NULL DEFAULT 4,
    difficulte VARCHAR(50) NOT NULL DEFAULT 'moyen',
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    saison VARCHAR(50) NOT NULL DEFAULT 'toute_année',
    categorie VARCHAR(100),
    -- Flags
    est_rapide BOOLEAN DEFAULT FALSE,
    est_equilibre BOOLEAN DEFAULT FALSE,
    compatible_bebe BOOLEAN DEFAULT FALSE,
    compatible_batch BOOLEAN DEFAULT FALSE,
    congelable BOOLEAN DEFAULT FALSE,
    -- Bio & Local
    est_bio BOOLEAN DEFAULT FALSE,
    est_local BOOLEAN DEFAULT FALSE,
    score_bio INTEGER DEFAULT 0,
    score_local INTEGER DEFAULT 0,
    -- Robots
    compatible_cookeo BOOLEAN DEFAULT FALSE,
    compatible_monsieur_cuisine BOOLEAN DEFAULT FALSE,
    compatible_airfryer BOOLEAN DEFAULT FALSE,
    compatible_multicooker BOOLEAN DEFAULT FALSE,
    -- Nutrition
    calories INTEGER,
    proteines FLOAT,
    lipides FLOAT,
    glucides FLOAT,
    -- IA & Media
    genere_par_ia BOOLEAN DEFAULT FALSE,
    score_ia FLOAT,
    url_image VARCHAR(500),
    -- Import (pour recipe_import service)
    source_url TEXT,
    source_site VARCHAR(100),
    imported_at TIMESTAMPTZ,
    -- Timestamps
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_temps_prep_positif CHECK (temps_preparation >= 0),
    CONSTRAINT ck_temps_cuisson_positif CHECK (temps_cuisson >= 0),
    CONSTRAINT ck_portions_valides CHECK (portions > 0 AND portions <= 20),
    CONSTRAINT ck_score_bio CHECK (score_bio >= 0 AND score_bio <= 100),
    CONSTRAINT ck_score_local CHECK (score_local >= 0 AND score_local <= 100)
);
CREATE INDEX IF NOT EXISTS idx_recettes_nom ON recettes(nom);
CREATE INDEX IF NOT EXISTS idx_recettes_type ON recettes(type_repas);
CREATE INDEX IF NOT EXISTS idx_recettes_saison ON recettes(saison);

-- Association Recettes-Ingrédients
CREATE TABLE IF NOT EXISTS recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantite FLOAT NOT NULL DEFAULT 1,
    unite VARCHAR(50) NOT NULL DEFAULT 'pcs',
    optionnel BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT ck_quantite_positive CHECK (quantite > 0)
);

-- Étapes de recettes
CREATE TABLE IF NOT EXISTS etapes_recette (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    ordre INTEGER NOT NULL,
    description TEXT NOT NULL,
    duree INTEGER,
    
    CONSTRAINT ck_ordre_positif CHECK (ordre > 0)
);

-- Versions de recettes (bébé, batch)
CREATE TABLE IF NOT EXISTS versions_recette (
    id SERIAL PRIMARY KEY,
    recette_base_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    type_version VARCHAR(50) NOT NULL,
    instructions_modifiees TEXT,
    ingredients_modifies JSONB,
    notes_bebe TEXT,
    etapes_paralleles_batch JSONB,
    temps_optimise_batch INTEGER,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Historique des recettes cuisinées
CREATE TABLE IF NOT EXISTS historique_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL REFERENCES recettes(id) ON DELETE CASCADE,
    date_cuisson DATE NOT NULL,
    portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    note INTEGER,
    avis TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_note_valide CHECK (note IS NULL OR (note >= 0 AND note <= 5)),
    CONSTRAINT ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0)
);

-- Batch meals (portions préparées)
CREATE TABLE IF NOT EXISTS batch_meals (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_creees INTEGER NOT NULL DEFAULT 1,
    portions_restantes INTEGER NOT NULL DEFAULT 1,
    date_preparation DATE NOT NULL DEFAULT CURRENT_DATE,
    date_peremption DATE NOT NULL,
    container_type VARCHAR(100),
    localisation VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 2: INVENTAIRE ET COURSES
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Inventaire
CREATE TABLE IF NOT EXISTS inventaire (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantite FLOAT NOT NULL DEFAULT 0,
    quantite_min FLOAT NOT NULL DEFAULT 0,
    emplacement VARCHAR(100),
    date_peremption DATE,
    derniere_maj TIMESTAMPTZ DEFAULT NOW(),
    photo_url VARCHAR(500),
    photo_filename VARCHAR(200),
    photo_uploaded_at TIMESTAMPTZ,
    code_barres VARCHAR(50),
    prix_unitaire FLOAT,
    
    CONSTRAINT ck_quantite_inventaire_positive CHECK (quantite >= 0),
    CONSTRAINT ck_seuil_positif CHECK (quantite_min >= 0)
);

-- Historique inventaire
CREATE TABLE IF NOT EXISTS historique_inventaire (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES inventaire(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    type_modification VARCHAR(50) NOT NULL,
    quantite_avant FLOAT,
    quantite_apres FLOAT,
    quantite_min_avant FLOAT,
    quantite_min_apres FLOAT,
    date_peremption_avant DATE,
    date_peremption_apres DATE,
    emplacement_avant VARCHAR(100),
    emplacement_apres VARCHAR(100),
    date_modification TIMESTAMPTZ DEFAULT NOW(),
    utilisateur VARCHAR(100),
    notes TEXT
);

-- Liste de courses
CREATE TABLE IF NOT EXISTS liste_courses (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantite_necessaire FLOAT NOT NULL DEFAULT 1,
    priorite VARCHAR(50) NOT NULL DEFAULT 'normale',
    achete BOOLEAN DEFAULT FALSE,
    suggere_par_ia BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    achete_le TIMESTAMPTZ,
    rayon_magasin VARCHAR(100),
    magasin_cible VARCHAR(50),
    notes TEXT,
    
    CONSTRAINT ck_quantite_courses_positive CHECK (quantite_necessaire > 0)
);

-- Modèles de courses
CREATE TABLE IF NOT EXISTS modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    utilisateur_id VARCHAR(100),
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    modifie_le TIMESTAMPTZ DEFAULT NOW(),
    actif BOOLEAN DEFAULT TRUE,
    articles_data JSONB DEFAULT '[]'
);

-- Articles des modèles
CREATE TABLE IF NOT EXISTS articles_modeles (
    id SERIAL PRIMARY KEY,
    modele_id INTEGER NOT NULL REFERENCES modeles_courses(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE SET NULL,
    nom_article VARCHAR(100) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1,
    unite VARCHAR(20) NOT NULL DEFAULT 'pcs',
    rayon_magasin VARCHAR(100) NOT NULL DEFAULT 'autre',
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    notes TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_article_modele_quantite_positive CHECK (quantite > 0),
    CONSTRAINT ck_article_modele_priorite_valide CHECK (priorite IN ('haute', 'moyenne', 'basse', 'normale'))
);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 3: PLANNING
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Plannings hebdomadaires
CREATE TABLE IF NOT EXISTS plannings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    semaine_debut DATE NOT NULL,
    semaine_fin DATE NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    genere_par_ia BOOLEAN DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Repas dans les plannings
CREATE TABLE IF NOT EXISTS repas (
    id SERIAL PRIMARY KEY,
    planning_id INTEGER NOT NULL REFERENCES plannings(id) ON DELETE CASCADE,
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50) NOT NULL,
    portion_ajustee INTEGER,
    prepare BOOLEAN DEFAULT FALSE,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_repas_date ON repas(date_repas);
CREATE INDEX IF NOT EXISTS idx_repas_type ON repas(type_repas);

-- Événements calendrier
CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMPTZ NOT NULL,
    date_fin TIMESTAMPTZ,
    lieu VARCHAR(200),
    type_event VARCHAR(50) NOT NULL,
    couleur VARCHAR(20),
    rappel_avant_minutes INTEGER,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_calendar_events_date ON calendar_events(date_debut);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 4: FAMILLE
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Profils enfants
CREATE TABLE IF NOT EXISTS child_profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    notes TEXT,
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Entrées bien-être
CREATE TABLE IF NOT EXISTS wellbeing_entries (
    id SERIAL PRIMARY KEY,
    child_id INTEGER REFERENCES child_profiles(id) ON DELETE CASCADE,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_wellbeing_date ON wellbeing_entries(date);

-- Jalons de développement
CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL REFERENCES child_profiles(id) ON DELETE CASCADE,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_milestones_date ON milestones(date_atteint);
CREATE INDEX IF NOT EXISTS idx_milestones_categorie ON milestones(categorie);

-- Activités familiales
CREATE TABLE IF NOT EXISTS family_activities (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    duree_heures FLOAT,
    lieu VARCHAR(200),
    qui_participe JSONB DEFAULT '[]',
    age_minimal_recommande INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_activite_duree_positive CHECK (duree_heures > 0),
    CONSTRAINT ck_activite_age_positif CHECK (age_minimal_recommande >= 0)
);
CREATE INDEX IF NOT EXISTS idx_family_activities_date ON family_activities(date_prevue);
CREATE INDEX IF NOT EXISTS idx_family_activities_type ON family_activities(type_activite);

-- Budget familial (ancien système)
CREATE TABLE IF NOT EXISTS family_budgets (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    categorie VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    montant FLOAT NOT NULL,
    magasin VARCHAR(200),
    est_recurrent BOOLEAN DEFAULT FALSE,
    frequence_recurrence VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_budget_montant_positive CHECK (montant > 0)
);
CREATE INDEX IF NOT EXISTS idx_family_budgets_date ON family_budgets(date);
CREATE INDEX IF NOT EXISTS idx_family_budgets_categorie ON family_budgets(categorie);

-- Shopping familial
CREATE TABLE IF NOT EXISTS shopping_items_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1,
    prix_estime FLOAT DEFAULT 0,
    liste VARCHAR(50) NOT NULL DEFAULT 'Nous',
    actif BOOLEAN DEFAULT TRUE,
    date_ajout TIMESTAMPTZ DEFAULT NOW(),
    date_achat TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_shopping_items_liste ON shopping_items_famille(liste);
CREATE INDEX IF NOT EXISTS idx_shopping_items_actif ON shopping_items_famille(actif);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 5: SANTÉ
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Routines santé
CREATE TABLE IF NOT EXISTS health_routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    frequence VARCHAR(50) NOT NULL,
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    intensite VARCHAR(50) NOT NULL DEFAULT 'modérée',
    jours_semaine JSONB DEFAULT '[]',
    calories_brulees_estimees INTEGER,
    actif BOOLEAN DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_routine_duree_positive CHECK (duree_minutes > 0)
);

-- Objectifs santé
CREATE TABLE IF NOT EXISTS health_objectives (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    valeur_cible FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    valeur_actuelle FLOAT,
    date_debut DATE NOT NULL,
    date_cible DATE NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_objective_valeur_positive CHECK (valeur_cible > 0),
    CONSTRAINT ck_objective_dates CHECK (date_debut <= date_cible)
);

-- Entrées santé
CREATE TABLE IF NOT EXISTS health_entries (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER REFERENCES health_routines(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type_activite VARCHAR(100) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50) NOT NULL DEFAULT 'modérée',
    calories_brulees INTEGER,
    note_energie INTEGER,
    note_moral INTEGER,
    ressenti TEXT,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (note_energie >= 1 AND note_energie <= 10),
    CONSTRAINT ck_entry_moral CHECK (note_moral >= 1 AND note_moral <= 10)
);
CREATE INDEX IF NOT EXISTS idx_health_entries_date ON health_entries(date);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 6: MAISON
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Projets maison
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin_prevue DATE,
    date_fin_reelle DATE,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_projects_statut ON projects(statut);

-- Tâches projets
CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'a_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echeance DATE,
    assigne_a VARCHAR(200),
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Routines maison
CREATE TABLE IF NOT EXISTS routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    frequence VARCHAR(50) NOT NULL DEFAULT 'quotidien',
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Tâches routines
CREATE TABLE IF NOT EXISTS routine_tasks (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL REFERENCES routines(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Jardin
CREATE TABLE IF NOT EXISTS garden_items (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    date_plantation DATE,
    date_recolte_prevue DATE,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);

-- Journal jardin
CREATE TABLE IF NOT EXISTS garden_logs (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER REFERENCES garden_items(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 7: NOUVELLES FONCTIONNALITÉS (BUDGET, MÉTÉO, CALENDRIER, NOTIFICATIONS)
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Dépenses (nouveau système avec user_id)
CREATE TABLE IF NOT EXISTS depenses (
    id BIGSERIAL PRIMARY KEY,
    montant DECIMAL(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recurrence VARCHAR(20),
    tags JSONB DEFAULT '[]',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_depenses_date ON depenses(date);
CREATE INDEX IF NOT EXISTS idx_depenses_categorie ON depenses(categorie);
CREATE INDEX IF NOT EXISTS idx_depenses_user ON depenses(user_id);

ALTER TABLE depenses DROP CONSTRAINT IF EXISTS check_categorie_valide;
ALTER TABLE depenses ADD CONSTRAINT check_categorie_valide CHECK (
    categorie IN (
        'alimentation', 'transport', 'logement', 'sante', 
        'loisirs', 'vetements', 'education', 'cadeaux',
        'abonnements', 'restaurant', 'vacances', 'bebe', 'autre'
    )
);

-- Budgets mensuels
CREATE TABLE IF NOT EXISTS budgets_mensuels (
    id BIGSERIAL PRIMARY KEY,
    mois DATE NOT NULL,
    budget_total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    budgets_par_categorie JSONB DEFAULT '{}',
    notes TEXT,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(mois, user_id)
);
CREATE INDEX IF NOT EXISTS idx_budgets_mois ON budgets_mensuels(mois);
CREATE INDEX IF NOT EXISTS idx_budgets_user ON budgets_mensuels(user_id);

-- Alertes météo
CREATE TABLE IF NOT EXISTS alertes_meteo (
    id BIGSERIAL PRIMARY KEY,
    type_alerte VARCHAR(30) NOT NULL,
    niveau VARCHAR(20) NOT NULL DEFAULT 'info',
    titre VARCHAR(200) NOT NULL,
    message TEXT,
    conseil_jardin TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    temperature DECIMAL(5, 2),
    lu BOOLEAN DEFAULT FALSE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_alertes_meteo_date ON alertes_meteo(date_debut);
CREATE INDEX IF NOT EXISTS idx_alertes_meteo_type ON alertes_meteo(type_alerte);
CREATE INDEX IF NOT EXISTS idx_alertes_meteo_user ON alertes_meteo(user_id);

-- Configuration météo
CREATE TABLE IF NOT EXISTS config_meteo (
    id BIGSERIAL PRIMARY KEY,
    latitude DECIMAL(10, 7) DEFAULT 48.8566,
    longitude DECIMAL(10, 7) DEFAULT 2.3522,
    ville VARCHAR(100) DEFAULT 'Paris',
    surface_jardin_m2 DECIMAL(10, 2) DEFAULT 50,
    notifications_gel BOOLEAN DEFAULT TRUE,
    notifications_canicule BOOLEAN DEFAULT TRUE,
    notifications_pluie BOOLEAN DEFAULT TRUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Backups
CREATE TABLE IF NOT EXISTS backups (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    tables_included JSONB DEFAULT '[]',
    row_counts JSONB DEFAULT '{}',
    size_bytes BIGINT DEFAULT 0,
    compressed BOOLEAN DEFAULT TRUE,
    storage_path VARCHAR(500),
    version VARCHAR(20) DEFAULT '1.0.0',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_backups_date ON backups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backups_user ON backups(user_id);

-- Calendriers externes
CREATE TABLE IF NOT EXISTS calendriers_externes (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    url TEXT,
    credentials JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    sync_interval_minutes INT DEFAULT 60,
    last_sync TIMESTAMPTZ,
    sync_direction VARCHAR(20) DEFAULT 'bidirectional',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_calendriers_provider ON calendriers_externes(provider);
CREATE INDEX IF NOT EXISTS idx_calendriers_user ON calendriers_externes(user_id);

-- Événements calendrier synchronisés
CREATE TABLE IF NOT EXISTS evenements_calendrier (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMPTZ NOT NULL,
    date_fin TIMESTAMPTZ,
    lieu VARCHAR(300),
    all_day BOOLEAN DEFAULT FALSE,
    recurrence_rule TEXT,
    rappel_minutes INT,
    source_calendrier_id BIGINT REFERENCES calendriers_externes(id) ON DELETE SET NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(uid, user_id)
);
CREATE INDEX IF NOT EXISTS idx_evenements_date ON evenements_calendrier(date_debut);
CREATE INDEX IF NOT EXISTS idx_evenements_user ON evenements_calendrier(user_id);

-- Abonnements push
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh_key TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_push_user ON push_subscriptions(user_id);

-- Préférences notifications
CREATE TABLE IF NOT EXISTS notification_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    courses_rappel BOOLEAN DEFAULT TRUE,
    repas_suggestion BOOLEAN DEFAULT TRUE,
    stock_alerte BOOLEAN DEFAULT TRUE,
    meteo_alerte BOOLEAN DEFAULT TRUE,
    budget_alerte BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 8: FONCTIONS UTILITAIRES
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Fonction pour calculer le total des dépenses d'un mois
CREATE OR REPLACE FUNCTION get_depenses_mois(p_user_id UUID, p_mois DATE)
RETURNS TABLE(
    categorie VARCHAR,
    total DECIMAL,
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.categorie,
        SUM(d.montant) as total,
        COUNT(*) as count
    FROM depenses d
    WHERE d.user_id = p_user_id
      AND DATE_TRUNC('month', d.date) = DATE_TRUNC('month', p_mois)
    GROUP BY d.categorie
    ORDER BY total DESC;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir le résumé budgétaire
CREATE OR REPLACE FUNCTION get_resume_budget(p_user_id UUID, p_mois DATE)
RETURNS JSONB AS $$
DECLARE
    v_budget_total DECIMAL;
    v_depenses_total DECIMAL;
    v_result JSONB;
BEGIN
    SELECT budget_total INTO v_budget_total
    FROM budgets_mensuels
    WHERE user_id = p_user_id
      AND mois = DATE_TRUNC('month', p_mois);
    
    SELECT COALESCE(SUM(montant), 0) INTO v_depenses_total
    FROM depenses
    WHERE user_id = p_user_id
      AND DATE_TRUNC('month', date) = DATE_TRUNC('month', p_mois);
    
    v_result := jsonb_build_object(
        'mois', p_mois,
        'budget_total', COALESCE(v_budget_total, 0),
        'depenses_total', v_depenses_total,
        'reste', COALESCE(v_budget_total, 0) - v_depenses_total,
        'pourcentage_utilise', 
            CASE WHEN COALESCE(v_budget_total, 0) > 0 
                 THEN ROUND((v_depenses_total / v_budget_total * 100)::numeric, 1)
                 ELSE 0 
            END
    );
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Fonction générique pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 9: TRIGGERS
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Triggers updated_at pour les tables qui en ont besoin
DROP TRIGGER IF EXISTS update_recettes_updated_at ON recettes;
CREATE TRIGGER update_recettes_updated_at
    BEFORE UPDATE ON recettes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_modeles_courses_updated_at ON modeles_courses;
CREATE TRIGGER update_modeles_courses_updated_at
    BEFORE UPDATE ON modeles_courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_depenses_updated_at ON depenses;
CREATE TRIGGER update_depenses_updated_at
    BEFORE UPDATE ON depenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_budgets_updated_at ON budgets_mensuels;
CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON budgets_mensuels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_config_meteo_updated_at ON config_meteo;
CREATE TRIGGER update_config_meteo_updated_at
    BEFORE UPDATE ON config_meteo
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_calendriers_updated_at ON calendriers_externes;
CREATE TRIGGER update_calendriers_updated_at
    BEFORE UPDATE ON calendriers_externes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_evenements_updated_at ON evenements_calendrier;
CREATE TRIGGER update_evenements_updated_at
    BEFORE UPDATE ON evenements_calendrier
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_notif_prefs_updated_at ON notification_preferences;
CREATE TRIGGER update_notif_prefs_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- PARTIE 10: ROW LEVEL SECURITY (RLS)
-- ═══════════════════════════════════════════════════════════════════════════════════════════════

-- Activer RLS sur les tables avec user_id
ALTER TABLE depenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets_mensuels ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertes_meteo ENABLE ROW LEVEL SECURITY;
ALTER TABLE config_meteo ENABLE ROW LEVEL SECURITY;
ALTER TABLE backups ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendriers_externes ENABLE ROW LEVEL SECURITY;
ALTER TABLE evenements_calendrier ENABLE ROW LEVEL SECURITY;
ALTER TABLE push_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- Policies RLS (l'utilisateur ne voit que ses propres données)
DROP POLICY IF EXISTS depenses_user_policy ON depenses;
CREATE POLICY depenses_user_policy ON depenses
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS budgets_user_policy ON budgets_mensuels;
CREATE POLICY budgets_user_policy ON budgets_mensuels
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS alertes_user_policy ON alertes_meteo;
CREATE POLICY alertes_user_policy ON alertes_meteo
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS config_meteo_user_policy ON config_meteo;
CREATE POLICY config_meteo_user_policy ON config_meteo
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS backups_user_policy ON backups;
CREATE POLICY backups_user_policy ON backups
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS calendriers_user_policy ON calendriers_externes;
CREATE POLICY calendriers_user_policy ON calendriers_externes
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS evenements_user_policy ON evenements_calendrier;
CREATE POLICY evenements_user_policy ON evenements_calendrier
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS push_user_policy ON push_subscriptions;
CREATE POLICY push_user_policy ON push_subscriptions
    FOR ALL USING (user_id = auth.uid());

DROP POLICY IF EXISTS notif_prefs_user_policy ON notification_preferences;
CREATE POLICY notif_prefs_user_policy ON notification_preferences
    FOR ALL USING (user_id = auth.uid());


COMMIT;

-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- VÉRIFICATION
-- ═══════════════════════════════════════════════════════════════════════════════════════════════
-- Exécuter après la migration pour vérifier:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
-- ═══════════════════════════════════════════════════════════════════════════════════════════════
