-- ============================================================================
-- SCRIPT MIGRATION COMPLET - ASSISTANT MATANNE
-- Compatible Supabase PostgreSQL
-- Généré le 2026-02-10
-- À exécuter dans l'éditeur SQL de Supabase
-- ============================================================================
-- ============================================================================
-- PARTIE 0: SUPPRESSION DE TOUTES LES TABLES (ordre inverse des FK)
-- ============================================================================
-- Désactiver temporairement les vérifications de FK pour le drop
SET session_replication_role = 'replica';
-- Tables avec FK (enfants) - supprimer en premier
DROP TABLE IF EXISTS evenements_calendrier CASCADE;
DROP TABLE IF EXISTS recipe_feedbacks CASCADE;
DROP TABLE IF EXISTS preparations_batch CASCADE;
DROP TABLE IF EXISTS etapes_batch_cooking CASCADE;
DROP TABLE IF EXISTS sessions_batch_cooking CASCADE;
DROP TABLE IF EXISTS jeux_grilles_loto CASCADE;
DROP TABLE IF EXISTS jeux_paris_sportifs CASCADE;
DROP TABLE IF EXISTS jeux_matchs CASCADE;
DROP TABLE IF EXISTS garden_logs CASCADE;
DROP TABLE IF EXISTS routine_tasks CASCADE;
DROP TABLE IF EXISTS project_tasks CASCADE;
DROP TABLE IF EXISTS health_entries CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS wellbeing_entries CASCADE;
DROP TABLE IF EXISTS repas CASCADE;
DROP TABLE IF EXISTS articles_modeles CASCADE;
DROP TABLE IF EXISTS liste_courses CASCADE;
DROP TABLE IF EXISTS historique_inventaire CASCADE;
DROP TABLE IF EXISTS inventaire CASCADE;
DROP TABLE IF EXISTS batch_meals CASCADE;
DROP TABLE IF EXISTS historique_recettes CASCADE;
DROP TABLE IF EXISTS versions_recette CASCADE;
DROP TABLE IF EXISTS etapes_recette CASCADE;
DROP TABLE IF EXISTS recette_ingredients CASCADE;
DROP TABLE IF EXISTS food_logs CASCADE;
DROP TABLE IF EXISTS garmin_daily_summaries CASCADE;
DROP TABLE IF EXISTS garmin_activities CASCADE;
DROP TABLE IF EXISTS garmin_tokens CASCADE;
-- Tables parentes
DROP TABLE IF EXISTS external_calendar_configs CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;
DROP TABLE IF EXISTS push_subscriptions CASCADE;
DROP TABLE IF EXISTS calendriers_externes CASCADE;
DROP TABLE IF EXISTS backups CASCADE;
DROP TABLE IF EXISTS config_meteo CASCADE;
DROP TABLE IF EXISTS alertes_meteo CASCADE;
DROP TABLE IF EXISTS budgets_mensuels CASCADE;
DROP TABLE IF EXISTS depenses CASCADE;
DROP TABLE IF EXISTS openfoodfacts_cache CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS house_stocks CASCADE;
DROP TABLE IF EXISTS maintenance_tasks CASCADE;
DROP TABLE IF EXISTS garden_zones CASCADE;
DROP TABLE IF EXISTS eco_actions CASCADE;
DROP TABLE IF EXISTS house_expenses CASCADE;
DROP TABLE IF EXISTS furniture CASCADE;
DROP TABLE IF EXISTS calendar_events CASCADE;
DROP TABLE IF EXISTS health_objectives CASCADE;
DROP TABLE IF EXISTS shopping_items_famille CASCADE;
DROP TABLE IF EXISTS family_budgets CASCADE;
DROP TABLE IF EXISTS family_activities CASCADE;
DROP TABLE IF EXISTS family_purchases CASCADE;
DROP TABLE IF EXISTS weekend_activities CASCADE;
DROP TABLE IF EXISTS config_batch_cooking CASCADE;
DROP TABLE IF EXISTS jeux_historique CASCADE;
DROP TABLE IF EXISTS jeux_stats_loto CASCADE;
DROP TABLE IF EXISTS jeux_tirages_loto CASCADE;
DROP TABLE IF EXISTS jeux_equipes CASCADE;
DROP TABLE IF EXISTS modeles_courses CASCADE;
DROP TABLE IF EXISTS garden_items CASCADE;
DROP TABLE IF EXISTS routines CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS health_routines CASCADE;
DROP TABLE IF EXISTS child_profiles CASCADE;
DROP TABLE IF EXISTS plannings CASCADE;
DROP TABLE IF EXISTS listes_courses CASCADE;
DROP TABLE IF EXISTS recettes CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
-- Réactiver les vérifications de FK
SET session_replication_role = 'origin';
-- Supprimer les fonctions de trigger si elles existent
DROP FUNCTION IF EXISTS update_modifie_le_column() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
-- ============================================================================
-- PARTIE 1: TABLES DE BASE (sans dépendances FK)
-- ============================================================================
-- -----------------------------------------------------------------------------
-- 1.1 INGREDIENTS (table de base pour recettes, inventaire, courses)
-- -----------------------------------------------------------------------------
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100),
    unite VARCHAR(50) NOT NULL DEFAULT 'pcs',
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_ingredients_nom ON ingredients(nom);
CREATE INDEX ix_ingredients_nom ON ingredients(nom);
CREATE INDEX ix_ingredients_categorie ON ingredients(categorie);
-- -----------------------------------------------------------------------------
-- 1.2 USER PROFILES (Garmin & santé)
-- -----------------------------------------------------------------------------
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(200),
    avatar_emoji VARCHAR(10) NOT NULL DEFAULT '👤',
    date_naissance DATE,
    taille_cm INTEGER,
    poids_kg FLOAT,
    objectif_poids_kg FLOAT,
    objectif_pas_quotidien INTEGER NOT NULL DEFAULT 10000,
    objectif_calories_brulees INTEGER NOT NULL DEFAULT 500,
    objectif_minutes_actives INTEGER NOT NULL DEFAULT 30,
    garmin_connected BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_user_profiles_username ON user_profiles(username);
CREATE INDEX ix_user_profiles_username ON user_profiles(username);
-- -----------------------------------------------------------------------------
-- 1.3 RECETTES
-- -----------------------------------------------------------------------------
CREATE TABLE recettes (
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
    est_rapide BOOLEAN NOT NULL DEFAULT FALSE,
    est_equilibre BOOLEAN NOT NULL DEFAULT FALSE,
    est_vegetarien BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_batch BOOLEAN NOT NULL DEFAULT FALSE,
    congelable BOOLEAN NOT NULL DEFAULT FALSE,
    type_proteines VARCHAR(100),
    est_bio BOOLEAN NOT NULL DEFAULT FALSE,
    est_local BOOLEAN NOT NULL DEFAULT FALSE,
    score_bio INTEGER NOT NULL DEFAULT 0,
    score_local INTEGER NOT NULL DEFAULT 0,
    compatible_cookeo BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_monsieur_cuisine BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_airfryer BOOLEAN NOT NULL DEFAULT FALSE,
    compatible_multicooker BOOLEAN NOT NULL DEFAULT FALSE,
    calories INTEGER,
    proteines FLOAT,
    lipides FLOAT,
    glucides FLOAT,
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    score_ia FLOAT,
    url_image VARCHAR(500),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT ck_temps_prep_positif CHECK (temps_preparation >= 0),
    CONSTRAINT ck_temps_cuisson_positif CHECK (temps_cuisson >= 0),
    CONSTRAINT ck_portions_valides CHECK (
        portions > 0
        AND portions <= 20
    ),
    CONSTRAINT ck_score_bio CHECK (
        score_bio >= 0
        AND score_bio <= 100
    ),
    CONSTRAINT ck_score_local CHECK (
        score_local >= 0
        AND score_local <= 100
    )
);
CREATE INDEX ix_recettes_nom ON recettes(nom);
CREATE INDEX ix_recettes_type_repas ON recettes(type_repas);
CREATE INDEX ix_recettes_saison ON recettes(saison);
CREATE INDEX ix_recettes_est_rapide ON recettes(est_rapide);
CREATE INDEX ix_recettes_est_vegetarien ON recettes(est_vegetarien);
CREATE INDEX ix_recettes_compatible_bebe ON recettes(compatible_bebe);
CREATE INDEX ix_recettes_compatible_batch ON recettes(compatible_batch);
CREATE INDEX ix_recettes_est_bio ON recettes(est_bio);
CREATE INDEX ix_recettes_est_local ON recettes(est_local);
CREATE INDEX ix_recettes_compatible_cookeo ON recettes(compatible_cookeo);
CREATE INDEX ix_recettes_compatible_monsieur_cuisine ON recettes(compatible_monsieur_cuisine);
CREATE INDEX ix_recettes_compatible_airfryer ON recettes(compatible_airfryer);
CREATE INDEX ix_recettes_cree_le ON recettes(cree_le);
-- -----------------------------------------------------------------------------
-- 1.4 LISTES COURSES
-- -----------------------------------------------------------------------------
CREATE TABLE listes_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    archivee BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_listes_courses_nom ON listes_courses(nom);
CREATE INDEX ix_listes_courses_archivee ON listes_courses(archivee);
CREATE INDEX ix_listes_courses_created_at ON listes_courses(created_at);
-- -----------------------------------------------------------------------------
-- 1.5 PLANNINGS
-- -----------------------------------------------------------------------------
CREATE TABLE plannings (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    semaine_debut DATE NOT NULL,
    semaine_fin DATE NOT NULL,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_plannings_semaine_debut ON plannings(semaine_debut);
CREATE INDEX ix_plannings_actif ON plannings(actif);
-- -----------------------------------------------------------------------------
-- 1.6 CHILD PROFILES (Jules & enfants)
-- -----------------------------------------------------------------------------
CREATE TABLE child_profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    notes TEXT,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_child_profiles_actif ON child_profiles(actif);
-- -----------------------------------------------------------------------------
-- 1.7 HEALTH ROUTINES
-- -----------------------------------------------------------------------------
CREATE TABLE health_routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    frequence VARCHAR(50) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50) NOT NULL DEFAULT 'modérée',
    jours_semaine JSONB,
    calories_brulees_estimees INTEGER,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_routine_duree_positive CHECK (duree_minutes > 0)
);
CREATE INDEX ix_health_routines_type_routine ON health_routines(type_routine);
CREATE INDEX ix_health_routines_actif ON health_routines(actif);
-- -----------------------------------------------------------------------------
-- 1.8 PROJECTS (Maison)
-- -----------------------------------------------------------------------------
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin_prevue DATE,
    date_fin_reelle DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_projects_statut ON projects(statut);
CREATE INDEX ix_projects_priorite ON projects(priorite);
-- -----------------------------------------------------------------------------
-- 1.9 ROUTINES (Maison)
-- -----------------------------------------------------------------------------
CREATE TABLE routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100),
    frequence VARCHAR(50) NOT NULL DEFAULT 'quotidien',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_routines_categorie ON routines(categorie);
CREATE INDEX ix_routines_actif ON routines(actif);
-- -----------------------------------------------------------------------------
-- 1.10 GARDEN ITEMS
-- -----------------------------------------------------------------------------
CREATE TABLE garden_items (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    date_plantation DATE,
    date_recolte_prevue DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_garden_items_type ON garden_items(type);
CREATE INDEX ix_garden_items_statut ON garden_items(statut);
-- -----------------------------------------------------------------------------
-- 1.11 MODELES COURSES
-- -----------------------------------------------------------------------------
CREATE TABLE modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    utilisateur_id VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    articles_data JSONB
);
CREATE INDEX ix_modeles_courses_nom ON modeles_courses(nom);
CREATE INDEX ix_modeles_courses_utilisateur_id ON modeles_courses(utilisateur_id);
CREATE INDEX ix_modeles_courses_actif ON modeles_courses(actif);
-- -----------------------------------------------------------------------------
-- 1.12 JEUX - ÉQUIPES
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_equipes (
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
-- -----------------------------------------------------------------------------
-- 1.13 JEUX - TIRAGES LOTO
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_tirages_loto (
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
CREATE UNIQUE INDEX uq_tirages_loto_date ON jeux_tirages_loto(date_tirage);
-- -----------------------------------------------------------------------------
-- 1.14 JEUX - STATS LOTO
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_stats_loto (
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
-- -----------------------------------------------------------------------------
-- 1.15 JEUX - HISTORIQUE
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_historique (
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
-- -----------------------------------------------------------------------------
-- 1.16 CONFIG BATCH COOKING
-- -----------------------------------------------------------------------------
CREATE TABLE config_batch_cooking (
    id SERIAL PRIMARY KEY,
    jours_batch JSONB NOT NULL DEFAULT '[6]',
    heure_debut_preferee TIME DEFAULT '10:00',
    duree_max_session INTEGER NOT NULL DEFAULT 180,
    avec_jules_par_defaut BOOLEAN NOT NULL DEFAULT TRUE,
    robots_disponibles JSONB NOT NULL DEFAULT '["four", "plaques"]',
    preferences_stockage JSONB,
    objectif_portions_semaine INTEGER NOT NULL DEFAULT 20,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
-- -----------------------------------------------------------------------------
-- 1.17 TABLES STANDALONE (sans FK)
-- -----------------------------------------------------------------------------
-- Weekend Activities
CREATE TABLE weekend_activities (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    type_activite VARCHAR(100) NOT NULL,
    date_prevue DATE NOT NULL,
    heure_debut VARCHAR(10),
    duree_estimee_h FLOAT,
    lieu VARCHAR(200),
    adresse TEXT,
    latitude FLOAT,
    longitude FLOAT,
    adapte_jules BOOLEAN NOT NULL DEFAULT TRUE,
    age_min_mois INTEGER,
    cout_estime FLOAT,
    cout_reel FLOAT,
    meteo_requise VARCHAR(50),
    statut VARCHAR(50) NOT NULL DEFAULT 'planifié',
    note_lieu INTEGER,
    commentaire TEXT,
    a_refaire BOOLEAN,
    participants JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_weekend_note_range CHECK (
        note_lieu IS NULL
        OR (
            note_lieu >= 1
            AND note_lieu <= 5
        )
    )
);
CREATE INDEX ix_weekend_activities_type ON weekend_activities(type_activite);
CREATE INDEX ix_weekend_activities_date ON weekend_activities(date_prevue);
CREATE INDEX ix_weekend_activities_statut ON weekend_activities(statut);
-- Family Purchases
CREATE TABLE family_purchases (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    prix_estime FLOAT,
    prix_reel FLOAT,
    url VARCHAR(500),
    image_url VARCHAR(500),
    magasin VARCHAR(200),
    taille VARCHAR(50),
    age_recommande_mois INTEGER,
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    date_achat DATE,
    suggere_par VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_family_purchases_categorie ON family_purchases(categorie);
CREATE INDEX ix_family_purchases_priorite ON family_purchases(priorite);
CREATE INDEX ix_family_purchases_achete ON family_purchases(achete);
-- Family Activities
CREATE TABLE family_activities (
    id SERIAL PRIMARY KEY,
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
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_activite_duree_positive CHECK (
        duree_heures IS NULL
        OR duree_heures > 0
    ),
    CONSTRAINT ck_activite_age_positif CHECK (
        age_minimal_recommande IS NULL
        OR age_minimal_recommande >= 0
    )
);
CREATE INDEX ix_family_activities_type ON family_activities(type_activite);
CREATE INDEX ix_family_activities_date ON family_activities(date_prevue);
CREATE INDEX ix_family_activities_statut ON family_activities(statut);
-- Family Budgets
CREATE TABLE family_budgets (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    categorie VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    montant FLOAT NOT NULL,
    magasin VARCHAR(200),
    est_recurrent BOOLEAN NOT NULL DEFAULT FALSE,
    frequence_recurrence VARCHAR(50),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_budget_montant_positive CHECK (montant > 0)
);
CREATE INDEX ix_family_budgets_date ON family_budgets(date);
CREATE INDEX ix_family_budgets_categorie ON family_budgets(categorie);
-- Shopping Items Famille
CREATE TABLE shopping_items_famille (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    prix_estime FLOAT NOT NULL DEFAULT 0.0,
    liste VARCHAR(50) NOT NULL DEFAULT 'Nous',
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_ajout TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    date_achat TIMESTAMP WITH TIME ZONE
);
CREATE INDEX ix_shopping_items_titre ON shopping_items_famille(titre);
CREATE INDEX ix_shopping_items_categorie ON shopping_items_famille(categorie);
CREATE INDEX ix_shopping_items_liste ON shopping_items_famille(liste);
CREATE INDEX ix_shopping_items_actif ON shopping_items_famille(actif);
CREATE INDEX ix_shopping_items_date ON shopping_items_famille(date_ajout);
-- Health Objectives
CREATE TABLE health_objectives (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    valeur_cible FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    valeur_actuelle FLOAT,
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    date_cible DATE NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_objective_valeur_positive CHECK (valeur_cible > 0),
    CONSTRAINT ck_objective_dates CHECK (date_debut <= date_cible)
);
CREATE INDEX ix_health_objectives_categorie ON health_objectives(categorie);
CREATE INDEX ix_health_objectives_statut ON health_objectives(statut);
-- Calendar Events
CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(200),
    type_event VARCHAR(50) NOT NULL DEFAULT 'autre',
    couleur VARCHAR(20),
    rappel_avant_minutes INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_calendar_events_date_debut ON calendar_events(date_debut);
CREATE INDEX ix_calendar_events_type ON calendar_events(type_event);
CREATE INDEX idx_date_type ON calendar_events(date_debut, type_event);
CREATE INDEX idx_date_range ON calendar_events(date_debut, date_fin);
-- Furniture (Maison Extended)
CREATE TABLE furniture (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    piece VARCHAR(50) NOT NULL,
    categorie VARCHAR(100),
    prix_estime NUMERIC(10, 2),
    prix_max NUMERIC(10, 2),
    prix_reel NUMERIC(10, 2),
    statut VARCHAR(20) NOT NULL DEFAULT 'souhaite',
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    magasin VARCHAR(200),
    url VARCHAR(500),
    reference VARCHAR(100),
    largeur_cm INTEGER,
    hauteur_cm INTEGER,
    profondeur_cm INTEGER,
    date_souhait DATE NOT NULL DEFAULT CURRENT_DATE,
    date_achat DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_furniture_piece ON furniture(piece);
CREATE INDEX ix_furniture_statut ON furniture(statut);
CREATE INDEX ix_furniture_priorite ON furniture(priorite);
-- House Expenses
CREATE TABLE house_expenses (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL,
    mois INTEGER NOT NULL,
    annee INTEGER NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    consommation FLOAT,
    unite_consommation VARCHAR(20),
    fournisseur VARCHAR(200),
    numero_contrat VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_house_expenses_categorie ON house_expenses(categorie);
CREATE INDEX ix_house_expenses_annee ON house_expenses(annee);
-- Eco Actions
CREATE TABLE eco_actions (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_action VARCHAR(50) NOT NULL,
    ancien_produit VARCHAR(200),
    nouveau_produit VARCHAR(200),
    cout_ancien_mensuel NUMERIC(10, 2),
    cout_nouveau_initial NUMERIC(10, 2),
    economie_mensuelle NUMERIC(10, 2),
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_eco_actions_type ON eco_actions(type_action);
-- Garden Zones
CREATE TABLE garden_zones (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    surface_m2 INTEGER,
    etat_note INTEGER NOT NULL DEFAULT 1,
    etat_description TEXT,
    objectif TEXT,
    budget_estime NUMERIC(10, 2),
    prochaine_action VARCHAR(200),
    date_prochaine_action DATE,
    photos_url JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_garden_zones_type ON garden_zones(type_zone);
-- Maintenance Tasks
CREATE TABLE maintenance_tasks (
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_maintenance_tasks_categorie ON maintenance_tasks(categorie);
CREATE INDEX ix_maintenance_tasks_prochaine ON maintenance_tasks(prochaine_fois);
CREATE INDEX ix_maintenance_tasks_fait ON maintenance_tasks(fait);
-- House Stocks
CREATE TABLE house_stocks (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 0,
    unite VARCHAR(20) NOT NULL DEFAULT 'unité',
    seuil_alerte INTEGER NOT NULL DEFAULT 1,
    emplacement VARCHAR(200),
    prix_unitaire NUMERIC(10, 2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_house_stocks_categorie ON house_stocks(categorie);
-- User Preferences
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    nb_adultes INTEGER NOT NULL DEFAULT 2,
    jules_present BOOLEAN NOT NULL DEFAULT TRUE,
    jules_age_mois INTEGER NOT NULL DEFAULT 19,
    temps_semaine VARCHAR(20) NOT NULL DEFAULT 'normal',
    temps_weekend VARCHAR(20) NOT NULL DEFAULT 'long',
    aliments_exclus JSONB NOT NULL DEFAULT '[]',
    aliments_favoris JSONB NOT NULL DEFAULT '[]',
    poisson_par_semaine INTEGER NOT NULL DEFAULT 2,
    vegetarien_par_semaine INTEGER NOT NULL DEFAULT 1,
    viande_rouge_max INTEGER NOT NULL DEFAULT 2,
    robots JSONB NOT NULL DEFAULT '[]',
    magasins_preferes JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX ix_user_preferences_user_id ON user_preferences(user_id);
-- OpenFoodFacts Cache
CREATE TABLE openfoodfacts_cache (
    id SERIAL PRIMARY KEY,
    code_barres VARCHAR(50) NOT NULL,
    nom VARCHAR(300),
    marque VARCHAR(200),
    categorie VARCHAR(200),
    nutriscore VARCHAR(1),
    nova_group INTEGER,
    ecoscore VARCHAR(1),
    nutrition_data JSONB,
    allergenes JSONB DEFAULT '[]',
    image_url VARCHAR(500),
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_openfoodfacts_code ON openfoodfacts_cache(code_barres);
CREATE INDEX ix_openfoodfacts_code ON openfoodfacts_cache(code_barres);
-- Depenses (Budget)
CREATE TABLE depenses (
    id BIGSERIAL PRIMARY KEY,
    montant NUMERIC(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL DEFAULT 'autre',
    description TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recurrence VARCHAR(20),
    tags JSONB DEFAULT '[]',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT check_categorie_valide CHECK (
        categorie IN (
            'alimentation',
            'transport',
            'logement',
            'sante',
            'loisirs',
            'vetements',
            'education',
            'cadeaux',
            'abonnements',
            'restaurant',
            'vacances',
            'bebe',
            'autre'
        )
    )
);
CREATE INDEX ix_depenses_categorie ON depenses(categorie);
CREATE INDEX ix_depenses_date ON depenses(date);
CREATE INDEX ix_depenses_user_id ON depenses(user_id);
-- Budgets Mensuels
CREATE TABLE budgets_mensuels (
    id BIGSERIAL PRIMARY KEY,
    mois DATE NOT NULL,
    budget_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    budgets_par_categorie JSONB DEFAULT '{}',
    notes TEXT,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_budgets_mensuels_mois ON budgets_mensuels(mois);
CREATE INDEX ix_budgets_mensuels_user ON budgets_mensuels(user_id);
CREATE UNIQUE INDEX uq_budget_mois_user ON budgets_mensuels(mois, user_id);
-- Alertes Meteo
CREATE TABLE alertes_meteo (
    id BIGSERIAL PRIMARY KEY,
    type_alerte VARCHAR(30) NOT NULL,
    niveau VARCHAR(20) NOT NULL DEFAULT 'info',
    titre VARCHAR(200) NOT NULL,
    message TEXT,
    conseil_jardin TEXT,
    date_debut DATE NOT NULL,
    date_fin DATE,
    temperature NUMERIC(5, 2),
    lu BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_alertes_meteo_type ON alertes_meteo(type_alerte);
CREATE INDEX ix_alertes_meteo_date ON alertes_meteo(date_debut);
CREATE INDEX ix_alertes_meteo_user ON alertes_meteo(user_id);
-- Config Meteo
CREATE TABLE config_meteo (
    id BIGSERIAL PRIMARY KEY,
    latitude NUMERIC(10, 7) NOT NULL DEFAULT 48.8566,
    longitude NUMERIC(10, 7) NOT NULL DEFAULT 2.3522,
    ville VARCHAR(100) NOT NULL DEFAULT 'Paris',
    surface_jardin_m2 NUMERIC(10, 2) NOT NULL DEFAULT 50,
    notifications_gel BOOLEAN NOT NULL DEFAULT TRUE,
    notifications_canicule BOOLEAN NOT NULL DEFAULT TRUE,
    notifications_pluie BOOLEAN NOT NULL DEFAULT TRUE,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_config_meteo_user ON config_meteo(user_id);
-- Backups
CREATE TABLE backups (
    id BIGSERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    tables_included JSONB DEFAULT '[]',
    row_counts JSONB DEFAULT '{}',
    size_bytes BIGINT NOT NULL DEFAULT 0,
    compressed BOOLEAN NOT NULL DEFAULT TRUE,
    storage_path VARCHAR(500),
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_backups_user ON backups(user_id);
CREATE INDEX ix_backups_created ON backups(created_at);
-- Calendriers Externes
CREATE TABLE calendriers_externes (
    id BIGSERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    url TEXT,
    credentials JSONB,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sync_interval_minutes INTEGER NOT NULL DEFAULT 60,
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_direction VARCHAR(20) NOT NULL DEFAULT 'bidirectional',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_calendriers_externes_provider ON calendriers_externes(provider);
CREATE INDEX ix_calendriers_externes_user ON calendriers_externes(user_id);
-- Push Subscriptions
CREATE TABLE push_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,
    p256dh_key TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_push_subscriptions_endpoint ON push_subscriptions(endpoint);
CREATE INDEX ix_push_subscriptions_user ON push_subscriptions(user_id);
-- Notification Preferences
CREATE TABLE notification_preferences (
    id BIGSERIAL PRIMARY KEY,
    courses_rappel BOOLEAN NOT NULL DEFAULT TRUE,
    repas_suggestion BOOLEAN NOT NULL DEFAULT TRUE,
    stock_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    meteo_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    budget_alerte BOOLEAN NOT NULL DEFAULT TRUE,
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '07:00',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_notification_prefs_user ON notification_preferences(user_id);
-- External Calendar Configs
CREATE TABLE external_calendar_configs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    provider VARCHAR(20) NOT NULL DEFAULT 'google',
    name VARCHAR(200) NOT NULL DEFAULT 'Mon Calendrier',
    calendar_url VARCHAR(500),
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP WITH TIME ZONE,
    sync_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sync_direction VARCHAR(20) NOT NULL DEFAULT 'import',
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_calendar_provider CHECK (
        provider IN ('google', 'apple', 'outlook', 'ical_url')
    )
);
CREATE INDEX ix_external_cal_user ON external_calendar_configs(user_id);
CREATE UNIQUE INDEX uq_user_calendar ON external_calendar_configs(user_id, provider, name);
-- ============================================================================
-- PARTIE 2: TABLES AVEC FOREIGN KEYS
-- ============================================================================
-- -----------------------------------------------------------------------------
-- 2.1 GARMIN TOKENS (dépend de user_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE garmin_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    oauth_token VARCHAR(500) NOT NULL,
    oauth_token_secret VARCHAR(500) NOT NULL,
    garmin_user_id VARCHAR(100),
    derniere_sync TIMESTAMP WITH TIME ZONE,
    sync_active BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_tokens_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_garmin_tokens_user_id ON garmin_tokens(user_id);
-- -----------------------------------------------------------------------------
-- 2.2 GARMIN ACTIVITIES (dépend de user_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE garmin_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    garmin_activity_id VARCHAR(100) NOT NULL,
    type_activite VARCHAR(50) NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    duree_secondes INTEGER NOT NULL,
    distance_metres FLOAT,
    calories INTEGER,
    fc_moyenne INTEGER,
    fc_max INTEGER,
    vitesse_moyenne FLOAT,
    allure_moyenne FLOAT,
    elevation_gain INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_activities_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
    CONSTRAINT ck_garmin_duree_positive CHECK (duree_secondes > 0)
);
CREATE UNIQUE INDEX uq_garmin_activity_id ON garmin_activities(garmin_activity_id);
CREATE INDEX ix_garmin_activities_user ON garmin_activities(user_id);
CREATE INDEX ix_garmin_activities_type ON garmin_activities(type_activite);
CREATE INDEX ix_garmin_activities_date ON garmin_activities(date_debut);
-- -----------------------------------------------------------------------------
-- 2.3 GARMIN DAILY SUMMARIES (dépend de user_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE garmin_daily_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    pas INTEGER NOT NULL DEFAULT 0,
    distance_metres INTEGER NOT NULL DEFAULT 0,
    calories_totales INTEGER NOT NULL DEFAULT 0,
    calories_actives INTEGER NOT NULL DEFAULT 0,
    minutes_actives INTEGER NOT NULL DEFAULT 0,
    minutes_tres_actives INTEGER NOT NULL DEFAULT 0,
    fc_repos INTEGER,
    fc_min INTEGER,
    fc_max INTEGER,
    sommeil_total_minutes INTEGER,
    sommeil_profond_minutes INTEGER,
    sommeil_leger_minutes INTEGER,
    sommeil_rem_minutes INTEGER,
    stress_moyen INTEGER,
    body_battery_max INTEGER,
    body_battery_min INTEGER,
    raw_data JSONB,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garmin_daily_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE
);
CREATE INDEX ix_garmin_daily_user ON garmin_daily_summaries(user_id);
CREATE INDEX ix_garmin_daily_date ON garmin_daily_summaries(date);
CREATE UNIQUE INDEX uq_garmin_daily_user_date ON garmin_daily_summaries(user_id, date);
-- -----------------------------------------------------------------------------
-- 2.4 FOOD LOGS (dépend de user_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE food_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    heure TIMESTAMP WITH TIME ZONE,
    repas VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    calories_estimees INTEGER,
    proteines_g FLOAT,
    glucides_g FLOAT,
    lipides_g FLOAT,
    qualite INTEGER,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_food_logs_user FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE,
    CONSTRAINT ck_food_qualite_range CHECK (
        qualite IS NULL
        OR (
            qualite >= 1
            AND qualite <= 5
        )
    )
);
CREATE INDEX ix_food_logs_user ON food_logs(user_id);
CREATE INDEX ix_food_logs_date ON food_logs(date);
-- -----------------------------------------------------------------------------
-- 2.5 RECETTE INGREDIENTS (dépend de recettes et ingredients)
-- -----------------------------------------------------------------------------
CREATE TABLE recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    optionnel BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_recette_ing_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recette_ing_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_positive CHECK (quantite > 0)
);
CREATE INDEX ix_recette_ingredients_recette ON recette_ingredients(recette_id);
CREATE INDEX ix_recette_ingredients_ingredient ON recette_ingredients(ingredient_id);
-- -----------------------------------------------------------------------------
-- 2.6 ETAPES RECETTE (dépend de recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE etapes_recette (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    description TEXT NOT NULL,
    duree INTEGER,
    CONSTRAINT fk_etapes_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_ordre_positif CHECK (ordre > 0)
);
CREATE INDEX ix_etapes_recette_recette ON etapes_recette(recette_id);
-- -----------------------------------------------------------------------------
-- 2.7 VERSIONS RECETTE (dépend de recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE versions_recette (
    id SERIAL PRIMARY KEY,
    recette_base_id INTEGER NOT NULL,
    type_version VARCHAR(50) NOT NULL,
    instructions_modifiees TEXT,
    ingredients_modifies JSONB,
    notes_bebe TEXT,
    etapes_paralleles_batch JSONB,
    temps_optimise_batch INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_versions_recette FOREIGN KEY (recette_base_id) REFERENCES recettes(id) ON DELETE CASCADE
);
CREATE INDEX ix_versions_recette_base ON versions_recette(recette_base_id);
CREATE INDEX ix_versions_recette_type ON versions_recette(type_version);
-- -----------------------------------------------------------------------------
-- 2.8 HISTORIQUE RECETTES (dépend de recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE historique_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    date_cuisson DATE NOT NULL,
    portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    note INTEGER,
    avis TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historique_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_note_valide CHECK (
        note IS NULL
        OR (
            note >= 0
            AND note <= 5
        )
    ),
    CONSTRAINT ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0)
);
CREATE INDEX ix_historique_recettes_recette ON historique_recettes(recette_id);
CREATE INDEX ix_historique_recettes_date ON historique_recettes(date_cuisson);
-- -----------------------------------------------------------------------------
-- 2.9 BATCH MEALS (dépend de recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE batch_meals (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_creees INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    container_type VARCHAR(100),
    localisation VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_batch_meals_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_batch_meals_recette ON batch_meals(recette_id);
CREATE INDEX ix_batch_meals_date_prep ON batch_meals(date_preparation);
CREATE INDEX ix_batch_meals_date_peremption ON batch_meals(date_peremption);
-- -----------------------------------------------------------------------------
-- 2.10 INVENTAIRE (dépend de ingredients)
-- -----------------------------------------------------------------------------
CREATE TABLE inventaire (
    id SERIAL PRIMARY KEY,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 0.0,
    quantite_min FLOAT NOT NULL DEFAULT 1.0,
    emplacement VARCHAR(100),
    date_peremption DATE,
    derniere_maj TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    photo_url VARCHAR(500),
    photo_filename VARCHAR(200),
    photo_uploaded_at TIMESTAMP WITH TIME ZONE,
    code_barres VARCHAR(50),
    prix_unitaire FLOAT,
    CONSTRAINT fk_inventaire_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_inventaire_positive CHECK (quantite >= 0),
    CONSTRAINT ck_seuil_positif CHECK (quantite_min >= 0)
);
CREATE UNIQUE INDEX uq_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX ix_inventaire_ingredient ON inventaire(ingredient_id);
CREATE INDEX ix_inventaire_emplacement ON inventaire(emplacement);
CREATE INDEX ix_inventaire_peremption ON inventaire(date_peremption);
CREATE INDEX ix_inventaire_derniere_maj ON inventaire(derniere_maj);
CREATE UNIQUE INDEX uq_code_barres ON inventaire(code_barres);
CREATE INDEX ix_inventaire_code_barres ON inventaire(code_barres);
-- -----------------------------------------------------------------------------
-- 2.11 HISTORIQUE INVENTAIRE (dépend de inventaire et ingredients)
-- -----------------------------------------------------------------------------
CREATE TABLE historique_inventaire (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    quantite_avant FLOAT,
    quantite_apres FLOAT,
    quantite_min_avant FLOAT,
    quantite_min_apres FLOAT,
    date_peremption_avant DATE,
    date_peremption_apres DATE,
    emplacement_avant VARCHAR(100),
    emplacement_apres VARCHAR(100),
    date_modification TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    utilisateur VARCHAR(100),
    notes TEXT,
    CONSTRAINT fk_hist_inv_article FOREIGN KEY (article_id) REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_hist_inv_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);
CREATE INDEX ix_historique_inventaire_article ON historique_inventaire(article_id);
CREATE INDEX ix_historique_inventaire_ingredient ON historique_inventaire(ingredient_id);
CREATE INDEX ix_historique_inventaire_type ON historique_inventaire(type_modification);
CREATE INDEX ix_historique_inventaire_date ON historique_inventaire(date_modification);
-- -----------------------------------------------------------------------------
-- 2.12 LISTE COURSES (articles) (dépend de listes_courses et ingredients)
-- -----------------------------------------------------------------------------
CREATE TABLE liste_courses (
    id SERIAL PRIMARY KEY,
    liste_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite_necessaire FLOAT NOT NULL,
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    achete BOOLEAN NOT NULL DEFAULT FALSE,
    suggere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    achete_le TIMESTAMP WITH TIME ZONE,
    rayon_magasin VARCHAR(100),
    magasin_cible VARCHAR(50),
    notes TEXT,
    CONSTRAINT fk_liste_courses_liste FOREIGN KEY (liste_id) REFERENCES listes_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_liste_courses_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_courses_positive CHECK (quantite_necessaire > 0)
);
CREATE INDEX ix_liste_courses_liste ON liste_courses(liste_id);
CREATE INDEX ix_liste_courses_ingredient ON liste_courses(ingredient_id);
CREATE INDEX ix_liste_courses_priorite ON liste_courses(priorite);
CREATE INDEX ix_liste_courses_achete ON liste_courses(achete);
CREATE INDEX ix_liste_courses_cree_le ON liste_courses(cree_le);
CREATE INDEX ix_liste_courses_rayon ON liste_courses(rayon_magasin);
CREATE INDEX ix_liste_courses_magasin ON liste_courses(magasin_cible);
-- -----------------------------------------------------------------------------
-- 2.13 ARTICLES MODELES (dépend de modeles_courses et ingredients)
-- -----------------------------------------------------------------------------
CREATE TABLE articles_modeles (
    id SERIAL PRIMARY KEY,
    modele_id INTEGER NOT NULL,
    ingredient_id INTEGER,
    nom_article VARCHAR(100) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    unite VARCHAR(20) NOT NULL DEFAULT 'pièce',
    rayon_magasin VARCHAR(100) NOT NULL DEFAULT 'Autre',
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    notes TEXT,
    ordre INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_articles_modeles_modele FOREIGN KEY (modele_id) REFERENCES modeles_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_modeles_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE
    SET NULL,
        CONSTRAINT ck_article_modele_quantite_positive CHECK (quantite > 0),
        CONSTRAINT ck_article_modele_priorite_valide CHECK (priorite IN ('haute', 'moyenne', 'basse'))
);
CREATE INDEX ix_articles_modeles_modele ON articles_modeles(modele_id);
CREATE INDEX ix_articles_modeles_ingredient ON articles_modeles(ingredient_id);
-- -----------------------------------------------------------------------------
-- 2.14 REPAS (dépend de plannings et recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE repas (
    id SERIAL PRIMARY KEY,
    planning_id INTEGER NOT NULL,
    recette_id INTEGER,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    portion_ajustee INTEGER,
    prepare BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    CONSTRAINT fk_repas_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE CASCADE,
    CONSTRAINT fk_repas_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_repas_planning ON repas(planning_id);
CREATE INDEX ix_repas_recette ON repas(recette_id);
CREATE INDEX ix_repas_date ON repas(date_repas);
CREATE INDEX ix_repas_type ON repas(type_repas);
-- -----------------------------------------------------------------------------
-- 2.15 WELLBEING ENTRIES (dépend de child_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE wellbeing_entries (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_wellbeing_child FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE
);
CREATE INDEX ix_wellbeing_child ON wellbeing_entries(child_id);
CREATE INDEX ix_wellbeing_username ON wellbeing_entries(username);
CREATE INDEX ix_wellbeing_date ON wellbeing_entries(date);
-- -----------------------------------------------------------------------------
-- 2.16 MILESTONES (dépend de child_profiles)
-- -----------------------------------------------------------------------------
CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_milestones_child FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE
);
CREATE INDEX ix_milestones_child ON milestones(child_id);
CREATE INDEX ix_milestones_categorie ON milestones(categorie);
CREATE INDEX ix_milestones_date ON milestones(date_atteint);
-- -----------------------------------------------------------------------------
-- 2.17 HEALTH ENTRIES (dépend de health_routines)
-- -----------------------------------------------------------------------------
CREATE TABLE health_entries (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type_activite VARCHAR(100) NOT NULL,
    duree_minutes INTEGER NOT NULL,
    intensite VARCHAR(50),
    calories_brulees INTEGER,
    note_energie INTEGER,
    note_moral INTEGER,
    ressenti TEXT,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_health_entries_routine FOREIGN KEY (routine_id) REFERENCES health_routines(id) ON DELETE CASCADE,
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (
        note_energie IS NULL
        OR (
            note_energie >= 1
            AND note_energie <= 10
        )
    ),
    CONSTRAINT ck_entry_moral CHECK (
        note_moral IS NULL
        OR (
            note_moral >= 1
            AND note_moral <= 10
        )
    )
);
CREATE INDEX ix_health_entries_routine ON health_entries(routine_id);
CREATE INDEX ix_health_entries_date ON health_entries(date);
-- -----------------------------------------------------------------------------
-- 2.18 PROJECT TASKS (dépend de projects)
-- -----------------------------------------------------------------------------
CREATE TABLE project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'à_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echeance DATE,
    assigne_a VARCHAR(200),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_project_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX ix_project_tasks_project ON project_tasks(project_id);
CREATE INDEX ix_project_tasks_statut ON project_tasks(statut);
-- -----------------------------------------------------------------------------
-- 2.19 ROUTINE TASKS (dépend de routines)
-- -----------------------------------------------------------------------------
CREATE TABLE routine_tasks (
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
CREATE INDEX ix_routine_tasks_routine ON routine_tasks(routine_id);
-- -----------------------------------------------------------------------------
-- 2.20 GARDEN LOGS (dépend de garden_items)
-- -----------------------------------------------------------------------------
CREATE TABLE garden_logs (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garden_logs_item FOREIGN KEY (garden_item_id) REFERENCES garden_items(id) ON DELETE CASCADE
);
CREATE INDEX ix_garden_logs_item ON garden_logs(garden_item_id);
CREATE INDEX ix_garden_logs_date ON garden_logs(date);
-- -----------------------------------------------------------------------------
-- 2.21 JEUX MATCHS (dépend de jeux_equipes)
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_matchs (
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
-- -----------------------------------------------------------------------------
-- 2.22 JEUX PARIS SPORTIFS (dépend de jeux_matchs)
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_paris_sportifs (
    id SERIAL PRIMARY KEY,
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
-- -----------------------------------------------------------------------------
-- 2.23 JEUX GRILLES LOTO (dépend de jeux_tirages_loto)
-- -----------------------------------------------------------------------------
CREATE TABLE jeux_grilles_loto (
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
-- -----------------------------------------------------------------------------
-- 2.24 SESSIONS BATCH COOKING (dépend de plannings)
-- -----------------------------------------------------------------------------
CREATE TABLE sessions_batch_cooking (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_session DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    duree_estimee INTEGER NOT NULL DEFAULT 120,
    duree_reelle INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'planifiee',
    avec_jules BOOLEAN NOT NULL DEFAULT FALSE,
    planning_id INTEGER,
    recettes_selectionnees JSONB,
    robots_utilises JSONB,
    notes_avant TEXT,
    notes_apres TEXT,
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    nb_portions_preparees INTEGER NOT NULL DEFAULT 0,
    nb_recettes_completees INTEGER NOT NULL DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sessions_batch_planning FOREIGN KEY (planning_id) REFERENCES plannings(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_sessions_batch_date ON sessions_batch_cooking(date_session);
CREATE INDEX ix_sessions_batch_statut ON sessions_batch_cooking(statut);
CREATE INDEX ix_sessions_batch_planning ON sessions_batch_cooking(planning_id);
CREATE INDEX idx_session_date_statut ON sessions_batch_cooking(date_session, statut);
-- -----------------------------------------------------------------------------
-- 2.25 ETAPES BATCH COOKING (dépend de sessions_batch_cooking et recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE etapes_batch_cooking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    recette_id INTEGER,
    ordre INTEGER NOT NULL,
    groupe_parallele INTEGER NOT NULL DEFAULT 0,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_minutes INTEGER NOT NULL DEFAULT 10,
    duree_reelle INTEGER,
    robots_requis JSONB,
    est_supervision BOOLEAN NOT NULL DEFAULT FALSE,
    alerte_bruit BOOLEAN NOT NULL DEFAULT FALSE,
    temperature INTEGER,
    statut VARCHAR(20) NOT NULL DEFAULT 'a_faire',
    heure_debut TIMESTAMP WITH TIME ZONE,
    heure_fin TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    timer_actif BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_etapes_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE CASCADE,
    CONSTRAINT fk_etapes_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_etapes_batch_session ON etapes_batch_cooking(session_id);
CREATE INDEX ix_etapes_batch_recette ON etapes_batch_cooking(recette_id);
CREATE INDEX idx_etape_session_ordre ON etapes_batch_cooking(session_id, ordre);
-- -----------------------------------------------------------------------------
-- 2.26 PREPARATIONS BATCH (dépend de sessions_batch_cooking et recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE preparations_batch (
    id SERIAL PRIMARY KEY,
    session_id INTEGER,
    recette_id INTEGER,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_initiales INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    localisation VARCHAR(50) NOT NULL DEFAULT 'frigo',
    container VARCHAR(100),
    etagere VARCHAR(50),
    repas_attribues JSONB,
    notes TEXT,
    photo_url VARCHAR(500),
    consomme BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_prep_batch_session FOREIGN KEY (session_id) REFERENCES sessions_batch_cooking(id) ON DELETE
    SET NULL,
        CONSTRAINT fk_prep_batch_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_prep_batch_session ON preparations_batch(session_id);
CREATE INDEX ix_prep_batch_recette ON preparations_batch(recette_id);
CREATE INDEX ix_prep_batch_date ON preparations_batch(date_preparation);
CREATE INDEX ix_prep_batch_peremption ON preparations_batch(date_peremption);
CREATE INDEX ix_prep_batch_localisation ON preparations_batch(localisation);
CREATE INDEX ix_prep_batch_consomme ON preparations_batch(consomme);
CREATE INDEX idx_prep_localisation_peremption ON preparations_batch(localisation, date_peremption);
CREATE INDEX idx_prep_consomme_peremption ON preparations_batch(consomme, date_peremption);
-- -----------------------------------------------------------------------------
-- 2.27 RECIPE FEEDBACKS (dépend de recettes)
-- -----------------------------------------------------------------------------
CREATE TABLE recipe_feedbacks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    recette_id INTEGER NOT NULL,
    feedback VARCHAR(20) NOT NULL DEFAULT 'neutral',
    contexte VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_recipe_feedbacks_recette FOREIGN KEY (recette_id) REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_feedback_type CHECK (feedback IN ('like', 'dislike', 'neutral'))
);
CREATE INDEX ix_recipe_feedbacks_user ON recipe_feedbacks(user_id);
CREATE INDEX ix_recipe_feedbacks_recette ON recipe_feedbacks(recette_id);
CREATE UNIQUE INDEX uq_user_recipe_feedback ON recipe_feedbacks(user_id, recette_id);
-- -----------------------------------------------------------------------------
-- 2.28 EVENEMENTS CALENDRIER (dépend de calendriers_externes)
-- -----------------------------------------------------------------------------
CREATE TABLE evenements_calendrier (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(255) NOT NULL,
    titre VARCHAR(300) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(300),
    all_day BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_rule TEXT,
    rappel_minutes INTEGER,
    source_calendrier_id BIGINT,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_evenements_calendrier_source FOREIGN KEY (source_calendrier_id) REFERENCES calendriers_externes(id) ON DELETE
    SET NULL
);
CREATE INDEX ix_evenements_calendrier_date ON evenements_calendrier(date_debut);
CREATE INDEX ix_evenements_calendrier_user ON evenements_calendrier(user_id);
CREATE UNIQUE INDEX uq_event_uid_user ON evenements_calendrier(uid, user_id);
-- ============================================================================
-- PARTIE 3: TRIGGERS pour modifie_le / updated_at automatique
-- ============================================================================
CREATE OR REPLACE FUNCTION update_modifie_le_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ language 'plpgsql';
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ language 'plpgsql';
-- Appliquer le trigger sur les tables avec modifie_le
DO $$
DECLARE t TEXT;
tables_modifie_le TEXT [] := ARRAY [
        'user_profiles', 'garmin_tokens', 'recettes', 'weekend_activities',
        'family_purchases', 'jeux_equipes', 'jeux_matchs', 'config_batch_cooking',
        'sessions_batch_cooking', 'preparations_batch'
    ];
BEGIN FOREACH t IN ARRAY tables_modifie_le LOOP EXECUTE format(
    'DROP TRIGGER IF EXISTS trigger_update_modifie_le ON %I',
    t
);
EXECUTE format(
    '
            CREATE TRIGGER trigger_update_modifie_le
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modifie_le_column()
        ',
    t
);
END LOOP;
END $$;
-- Appliquer le trigger sur les tables avec updated_at
DO $$
DECLARE t TEXT;
tables_updated_at TEXT [] := ARRAY [
        'listes_courses', 'modeles_courses', 'furniture', 'garden_zones',
        'maintenance_tasks', 'house_stocks', 'user_preferences',
        'depenses', 'budgets_mensuels', 'config_meteo', 'calendriers_externes',
        'notification_preferences', 'external_calendar_configs', 'evenements_calendrier'
    ];
BEGIN FOREACH t IN ARRAY tables_updated_at LOOP EXECUTE format(
    'DROP TRIGGER IF EXISTS trigger_update_updated_at ON %I',
    t
);
EXECUTE format(
    '
            CREATE TRIGGER trigger_update_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column()
        ',
    t
);
END LOOP;
END $$;
-- ============================================================================
-- PARTIE 4: VÉRIFICATION FINALE
-- ============================================================================
-- Afficher le résumé des tables créées
SELECT tablename,
    (
        SELECT COUNT(*)
        FROM information_schema.columns c
        WHERE c.table_name = t.tablename
    ) as nb_colonnes
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;
-- ============================================================================
-- FIN DU SCRIPT - 65 tables créées
-- ============================================================================
