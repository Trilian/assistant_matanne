-- ============================================================================
-- ASSISTANT MATANNE — SCRIPT D'INITIALISATION COMPLET
-- ============================================================================
-- Version : 2.0
-- Date    : 2025-01-27
-- Cible   : Supabase PostgreSQL
-- Tables  : 94 (83 modèles ORM + 11 tables maison hub)
-- ============================================================================
--
-- Ce script crée l'intégralité du schéma de la base de données.
-- Il remplace tous les anciens fichiers de migration (017-024).
--
-- Usage:
--   1. Exécuter dans Supabase SQL Editor ou psql
--   2. Les données de référence sont insérées automatiquement
--   3. RLS est activé sur toutes les tables
--
-- ============================================================================

BEGIN;

-- ============================================================================
-- PARTIE 0 : SUPPRESSION DE TOUTES LES TABLES (CASCADE)
-- ============================================================================

-- Vues d'abord
DROP VIEW IF EXISTS v_objets_a_remplacer CASCADE;
DROP VIEW IF EXISTS v_temps_par_activite_30j CASCADE;
DROP VIEW IF EXISTS v_budget_travaux_par_piece CASCADE;
DROP VIEW IF EXISTS v_taches_jour CASCADE;
DROP VIEW IF EXISTS v_charge_semaine CASCADE;
DROP VIEW IF EXISTS v_stats_domaine_mois CASCADE;
DROP VIEW IF EXISTS v_autonomie CASCADE;
DROP VIEW IF EXISTS v_factures_alertes CASCADE;
DROP VIEW IF EXISTS v_budgets_status CASCADE;

-- Fonctions
DROP FUNCTION IF EXISTS fn_temps_entretien_par_mois CASCADE;

-- Tables dépendantes (enfants) en premier
DROP TABLE IF EXISTS actions_plantes CASCADE;
DROP TABLE IF EXISTS plantes_jardin CASCADE;
DROP TABLE IF EXISTS zones_jardin CASCADE;
DROP TABLE IF EXISTS plans_jardin CASCADE;
DROP TABLE IF EXISTS logs_statut_objets CASCADE;
DROP TABLE IF EXISTS couts_travaux CASCADE;
DROP TABLE IF EXISTS versions_pieces CASCADE;
DROP TABLE IF EXISTS sessions_travail CASCADE;
DROP TABLE IF EXISTS objets_maison CASCADE;
DROP TABLE IF EXISTS pieces_maison CASCADE;
DROP TABLE IF EXISTS etapes_batch_cooking CASCADE;
DROP TABLE IF EXISTS preparations_batch CASCADE;
DROP TABLE IF EXISTS sessions_batch_cooking CASCADE;
DROP TABLE IF EXISTS jeux_paris_sportifs CASCADE;
DROP TABLE IF EXISTS jeux_matchs CASCADE;
DROP TABLE IF EXISTS jeux_grilles_loto CASCADE;
DROP TABLE IF EXISTS jeux_alertes CASCADE;
DROP TABLE IF EXISTS repas CASCADE;
DROP TABLE IF EXISTS elements_templates CASCADE;
DROP TABLE IF EXISTS liste_courses CASCADE;
DROP TABLE IF EXISTS articles_modeles CASCADE;
DROP TABLE IF EXISTS recette_ingredients CASCADE;
DROP TABLE IF EXISTS etapes_recette CASCADE;
DROP TABLE IF EXISTS versions_recette CASCADE;
DROP TABLE IF EXISTS historique_recettes CASCADE;
DROP TABLE IF EXISTS repas_batch CASCADE;
DROP TABLE IF EXISTS retours_recettes CASCADE;
DROP TABLE IF EXISTS historique_inventaire CASCADE;
DROP TABLE IF EXISTS inventaire CASCADE;
DROP TABLE IF EXISTS entrees_bien_etre CASCADE;
DROP TABLE IF EXISTS jalons CASCADE;
DROP TABLE IF EXISTS entrees_sante CASCADE;
DROP TABLE IF EXISTS taches_projets CASCADE;
DROP TABLE IF EXISTS taches_routines CASCADE;
DROP TABLE IF EXISTS journaux_jardin CASCADE;
DROP TABLE IF EXISTS garmin_tokens CASCADE;
DROP TABLE IF EXISTS activites_garmin CASCADE;
DROP TABLE IF EXISTS resumes_quotidiens_garmin CASCADE;
DROP TABLE IF EXISTS journaux_alimentaires CASCADE;
DROP TABLE IF EXISTS evenements_calendrier CASCADE;
DROP TABLE IF EXISTS depenses_home CASCADE;
DROP TABLE IF EXISTS comparatifs CASCADE;
DROP TABLE IF EXISTS factures CASCADE;
DROP TABLE IF EXISTS recoltes CASCADE;
DROP TABLE IF EXISTS taches_home CASCADE;

-- Tables autonomes
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS recettes CASCADE;
DROP TABLE IF EXISTS profils_utilisateurs CASCADE;
DROP TABLE IF EXISTS plannings CASCADE;
DROP TABLE IF EXISTS profils_enfants CASCADE;
DROP TABLE IF EXISTS routines_sante CASCADE;
DROP TABLE IF EXISTS objectifs_sante CASCADE;
DROP TABLE IF EXISTS projets CASCADE;
DROP TABLE IF EXISTS routines CASCADE;
DROP TABLE IF EXISTS elements_jardin CASCADE;
DROP TABLE IF EXISTS listes_courses CASCADE;
DROP TABLE IF EXISTS modeles_courses CASCADE;
DROP TABLE IF EXISTS templates_semaine CASCADE;
DROP TABLE IF EXISTS config_batch_cooking CASCADE;
DROP TABLE IF EXISTS jeux_equipes CASCADE;
DROP TABLE IF EXISTS jeux_tirages_loto CASCADE;
DROP TABLE IF EXISTS jeux_stats_loto CASCADE;
DROP TABLE IF EXISTS jeux_historique CASCADE;
DROP TABLE IF EXISTS jeux_series CASCADE;
DROP TABLE IF EXISTS jeux_configuration CASCADE;
DROP TABLE IF EXISTS activites_weekend CASCADE;
DROP TABLE IF EXISTS achats_famille CASCADE;
DROP TABLE IF EXISTS activites_famille CASCADE;
DROP TABLE IF EXISTS budgets_famille CASCADE;
DROP TABLE IF EXISTS articles_achats_famille CASCADE;
DROP TABLE IF EXISTS evenements_planning CASCADE;
DROP TABLE IF EXISTS meubles CASCADE;
DROP TABLE IF EXISTS depenses_maison CASCADE;
DROP TABLE IF EXISTS actions_ecologiques CASCADE;
DROP TABLE IF EXISTS taches_entretien CASCADE;
DROP TABLE IF EXISTS stocks_maison CASCADE;
DROP TABLE IF EXISTS preferences_utilisateurs CASCADE;
DROP TABLE IF EXISTS openfoodfacts_cache CASCADE;
DROP TABLE IF EXISTS depenses CASCADE;
DROP TABLE IF EXISTS budgets_mensuels CASCADE;
DROP TABLE IF EXISTS alertes_meteo CASCADE;
DROP TABLE IF EXISTS config_meteo CASCADE;
DROP TABLE IF EXISTS sauvegardes CASCADE;
DROP TABLE IF EXISTS historique_actions CASCADE;
DROP TABLE IF EXISTS calendriers_externes CASCADE;
DROP TABLE IF EXISTS abonnements_push CASCADE;
DROP TABLE IF EXISTS preferences_notifications CASCADE;
DROP TABLE IF EXISTS configs_calendriers_externes CASCADE;

-- Tables migration 020 (maison hub)
DROP TABLE IF EXISTS preferences_home CASCADE;
DROP TABLE IF EXISTS stats_home CASCADE;
DROP TABLE IF EXISTS plantes_catalogue CASCADE;
DROP TABLE IF EXISTS objectifs_autonomie CASCADE;
DROP TABLE IF EXISTS contrats CASCADE;
DROP TABLE IF EXISTS budgets_home CASCADE;

-- Legacy (nettoyage)
DROP TABLE IF EXISTS garden_zones CASCADE;
DROP TABLE IF EXISTS schema_migrations CASCADE;


-- ============================================================================
-- PARTIE 1 : FONCTIONS TRIGGER
-- ============================================================================

CREATE OR REPLACE FUNCTION update_modifie_le_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modifie_le = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- PARTIE 2 : TABLE DE SUIVI DES MIGRATIONS
-- ============================================================================

CREATE TABLE schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    checksum VARCHAR(64),
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


-- ============================================================================
-- PARTIE 3 : TABLES AUTONOMES (sans dépendances FK)
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.01 INGREDIENTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL DEFAULT 'Autre',
    unite_mesure VARCHAR(50) NOT NULL DEFAULT 'pièce',
    calories_pour_100g FLOAT,
    saison VARCHAR(50),
    allergene BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_ingredients_nom ON ingredients(nom);
CREATE INDEX ix_ingredients_categorie ON ingredients(categorie);
CREATE INDEX ix_ingredients_saison ON ingredients(saison);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.02 USER_PROFILES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE profils_utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    taille_cm INTEGER,
    poids_kg FLOAT,
    age INTEGER,
    sexe VARCHAR(10),
    objectif_pas_quotidien INTEGER NOT NULL DEFAULT 10000,
    objectif_calories INTEGER NOT NULL DEFAULT 2000,
    objectif_sommeil_heures FLOAT NOT NULL DEFAULT 8.0,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.03 RECETTES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE recettes (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    instructions TEXT,
    temps_preparation INTEGER NOT NULL DEFAULT 0,
    temps_cuisson INTEGER NOT NULL DEFAULT 0,
    portions INTEGER NOT NULL DEFAULT 4,
    difficulte VARCHAR(50) NOT NULL DEFAULT 'Facile',
    categorie VARCHAR(100) NOT NULL DEFAULT 'Plat',
    saison VARCHAR(50),
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    tags JSONB DEFAULT '[]',
    image_url VARCHAR(500),
    source_url VARCHAR(500),
    note_moyenne FLOAT,
    nb_preparations INTEGER NOT NULL DEFAULT 0,
    cout_estime FLOAT,
    adaptee_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    batch_cooking BOOLEAN NOT NULL DEFAULT FALSE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_temps_preparation_positif CHECK (temps_preparation >= 0),
    CONSTRAINT ck_temps_cuisson_positif CHECK (temps_cuisson >= 0),
    CONSTRAINT ck_portions_positive CHECK (portions > 0)
);
CREATE INDEX ix_recettes_categorie ON recettes(categorie);
CREATE INDEX ix_recettes_type_repas ON recettes(type_repas);
CREATE INDEX ix_recettes_saison ON recettes(saison);
CREATE INDEX ix_recettes_batch_cooking ON recettes(batch_cooking);
CREATE INDEX ix_recettes_adaptee_bebe ON recettes(adaptee_bebe);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.04 PLANNINGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plannings (
    id SERIAL PRIMARY KEY,
    semaine_du DATE NOT NULL,
    semaine_au DATE NOT NULL,
    statut VARCHAR(50) NOT NULL DEFAULT 'brouillon',
    genere_par_ia BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_ia TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_plannings_semaine ON plannings(semaine_du);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.05 LISTES_COURSES (en-tête)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE listes_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    semaine_du DATE,
    statut VARCHAR(50) NOT NULL DEFAULT 'active',
    budget_estime FLOAT,
    budget_reel FLOAT,
    magasin_principal VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_listes_courses_semaine ON listes_courses(semaine_du);
CREATE INDEX ix_listes_courses_statut ON listes_courses(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.06 MODELES_COURSES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    utilisateur_id VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    articles_data JSONB
);
CREATE INDEX ix_modeles_courses_nom ON modeles_courses(nom);
CREATE INDEX ix_modeles_courses_utilisateur_id ON modeles_courses(utilisateur_id);
CREATE INDEX ix_modeles_courses_actif ON modeles_courses(actif);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.07 CHILD_PROFILES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE profils_enfants (
    id SERIAL PRIMARY KEY,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.08 HEALTH_ROUTINES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE routines_sante (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]',
    heure_preferee VARCHAR(10),
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    rappel BOOLEAN NOT NULL DEFAULT TRUE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_health_routines_type ON routines_sante(type_routine);
CREATE INDEX ix_health_routines_actif ON routines_sante(actif);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.09 HEALTH_OBJECTIVES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE objectifs_sante (
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
CREATE INDEX ix_health_objectives_categorie ON objectifs_sante(categorie);
CREATE INDEX ix_health_objectives_statut ON objectifs_sante(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.10 PROJECTS
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
CREATE INDEX ix_projects_statut ON projets(statut);
CREATE INDEX ix_projects_categorie ON projets(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.11 ROUTINES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]',
    heure_debut VARCHAR(10),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_routines_type ON routines(type_routine);
CREATE INDEX ix_routines_actif ON routines(actif);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.12 GARDEN_ITEMS
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
CREATE INDEX ix_garden_items_type ON elements_jardin(type_plante);
CREATE INDEX ix_garden_items_statut ON elements_jardin(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.13 TEMPLATES_SEMAINE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE templates_semaine (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.14 CONFIG_BATCH_COOKING
-- ─────────────────────────────────────────────────────────────────────────────
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
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_config_batch_duree_positive CHECK (duree_max_session > 0),
    CONSTRAINT ck_config_batch_objectif_positif CHECK (objectif_portions_semaine > 0)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.15 JEUX_EQUIPES
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.16 JEUX_TIRAGES_LOTO
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.17 JEUX_STATS_LOTO
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.18 JEUX_HISTORIQUE
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.19 JEUX_SERIES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE jeux_series (
    id SERIAL PRIMARY KEY,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    serie_actuelle INTEGER NOT NULL DEFAULT 0,
    frequence FLOAT NOT NULL DEFAULT 0.0,
    nb_occurrences INTEGER NOT NULL DEFAULT 0,
    nb_total INTEGER NOT NULL DEFAULT 0,
    derniere_occurrence DATE,
    derniere_mise_a_jour TIMESTAMP,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_jeux_series_type_jeu_championnat ON jeux_series(type_jeu, championnat);
CREATE INDEX ix_jeux_series_type_jeu_marche ON jeux_series(type_jeu, marche);
CREATE INDEX ix_jeux_series_value ON jeux_series((frequence * serie_actuelle) DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.20 JEUX_CONFIGURATION
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE jeux_configuration (
    id SERIAL PRIMARY KEY,
    cle VARCHAR(50) NOT NULL UNIQUE,
    valeur TEXT NOT NULL,
    description TEXT,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.21 WEEKEND_ACTIVITIES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE activites_weekend (
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
        note_lieu IS NULL OR (note_lieu >= 1 AND note_lieu <= 5)
    )
);
CREATE INDEX ix_weekend_activities_type ON activites_weekend(type_activite);
CREATE INDEX ix_weekend_activities_date ON activites_weekend(date_prevue);
CREATE INDEX ix_weekend_activities_statut ON activites_weekend(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.22 FAMILY_PURCHASES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE achats_famille (
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
CREATE INDEX ix_family_purchases_categorie ON achats_famille(categorie);
CREATE INDEX ix_family_purchases_priorite ON achats_famille(priorite);
CREATE INDEX ix_family_purchases_achete ON achats_famille(achete);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.23 FAMILY_ACTIVITIES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE activites_famille (
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
    CONSTRAINT ck_activite_duree_positive CHECK (duree_heures IS NULL OR duree_heures > 0),
    CONSTRAINT ck_activite_age_positif CHECK (age_minimal_recommande IS NULL OR age_minimal_recommande >= 0)
);
CREATE INDEX ix_family_activities_type ON activites_famille(type_activite);
CREATE INDEX ix_family_activities_date ON activites_famille(date_prevue);
CREATE INDEX ix_family_activities_statut ON activites_famille(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.24 FAMILY_BUDGETS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE budgets_famille (
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
CREATE INDEX ix_family_budgets_date ON budgets_famille(date);
CREATE INDEX ix_family_budgets_categorie ON budgets_famille(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.25 SHOPPING_ITEMS_FAMILLE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE articles_achats_famille (
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
CREATE INDEX ix_shopping_items_titre ON articles_achats_famille(titre);
CREATE INDEX ix_shopping_items_categorie ON articles_achats_famille(categorie);
CREATE INDEX ix_shopping_items_liste ON articles_achats_famille(liste);
CREATE INDEX ix_shopping_items_actif ON articles_achats_famille(actif);
CREATE INDEX ix_shopping_items_date ON articles_achats_famille(date_ajout);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.26 CALENDAR_EVENTS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE evenements_planning (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    date_fin TIMESTAMP WITH TIME ZONE,
    lieu VARCHAR(200),
    type_event VARCHAR(50) NOT NULL DEFAULT 'autre',
    couleur VARCHAR(20),
    rappel_avant_minutes INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_event_rappel_positif CHECK (rappel_avant_minutes IS NULL OR rappel_avant_minutes >= 0)
);
CREATE INDEX ix_calendar_events_date_debut ON evenements_planning(date_debut);
CREATE INDEX ix_calendar_events_type ON evenements_planning(type_event);
CREATE INDEX idx_date_type ON evenements_planning(date_debut, type_event);
CREATE INDEX idx_date_range ON evenements_planning(date_debut, date_fin);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.27 FURNITURE
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE meubles (
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
CREATE INDEX ix_furniture_piece ON meubles(piece);
CREATE INDEX ix_furniture_statut ON meubles(statut);
CREATE INDEX ix_furniture_priorite ON meubles(priorite);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.28 HOUSE_EXPENSES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE depenses_maison (
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_house_mois_valide CHECK (mois >= 1 AND mois <= 12),
    CONSTRAINT ck_house_montant_positif CHECK (montant >= 0),
    CONSTRAINT ck_house_consommation_positive CHECK (consommation IS NULL OR consommation >= 0)
);
CREATE INDEX ix_house_expenses_categorie ON depenses_maison(categorie);
CREATE INDEX ix_house_expenses_annee ON depenses_maison(annee);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.29 ECO_ACTIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE actions_ecologiques (
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
CREATE INDEX ix_eco_actions_type ON actions_ecologiques(type_action);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.30 MAINTENANCE_TASKS
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_maintenance_tasks_categorie ON taches_entretien(categorie);
CREATE INDEX ix_maintenance_tasks_prochaine ON taches_entretien(prochaine_fois);
CREATE INDEX ix_maintenance_tasks_fait ON taches_entretien(fait);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.31 HOUSE_STOCKS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE stocks_maison (
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
CREATE INDEX ix_house_stocks_categorie ON stocks_maison(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.32 USER_PREFERENCES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE preferences_utilisateurs (
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
CREATE UNIQUE INDEX uq_user_preferences_user_id ON preferences_utilisateurs(user_id);
CREATE INDEX ix_user_preferences_user_id ON preferences_utilisateurs(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.33 OPENFOODFACTS_CACHE
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.34 DEPENSES
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT ck_depense_montant_positif CHECK (montant > 0),
    CONSTRAINT check_categorie_valide CHECK (
        categorie IN (
            'alimentation', 'transport', 'logement', 'sante', 'loisirs',
            'vetements', 'education', 'cadeaux', 'abonnements', 'restaurant',
            'vacances', 'bebe', 'autre'
        )
    )
);
CREATE INDEX ix_depenses_categorie ON depenses(categorie);
CREATE INDEX ix_depenses_date ON depenses(date);
CREATE INDEX ix_depenses_user_id ON depenses(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.35 BUDGETS_MENSUELS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE budgets_mensuels (
    id BIGSERIAL PRIMARY KEY,
    mois DATE NOT NULL,
    budget_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    budgets_par_categorie JSONB DEFAULT '{}',
    notes TEXT,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_budget_total_positif CHECK (budget_total >= 0)
);
CREATE INDEX ix_budgets_mensuels_mois ON budgets_mensuels(mois);
CREATE INDEX ix_budgets_mensuels_user ON budgets_mensuels(user_id);
CREATE UNIQUE INDEX uq_budget_mois_user ON budgets_mensuels(mois, user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.36 ALERTES_METEO
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.37 CONFIG_METEO
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.38 BACKUPS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE sauvegardes (
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
CREATE INDEX ix_backups_user ON sauvegardes(user_id);
CREATE INDEX ix_backups_created ON sauvegardes(created_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.39 ACTION_HISTORY
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE historique_actions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT,
    entity_name VARCHAR(255),
    description TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_action_history_user_id ON historique_actions(user_id);
CREATE INDEX idx_action_history_action_type ON historique_actions(action_type);
CREATE INDEX idx_action_history_created_at ON historique_actions(created_at DESC);
CREATE INDEX idx_action_history_entity ON historique_actions(entity_type, entity_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.40 CALENDRIERS_EXTERNES
-- ─────────────────────────────────────────────────────────────────────────────
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.41 PUSH_SUBSCRIPTIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE abonnements_push (
    id BIGSERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,
    p256dh_key TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    device_info JSONB DEFAULT '{}',
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX uq_push_subscriptions_endpoint ON abonnements_push(endpoint);
CREATE INDEX ix_push_subscriptions_user ON abonnements_push(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.42 NOTIFICATION_PREFERENCES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE preferences_notifications (
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
CREATE UNIQUE INDEX uq_notification_prefs_user ON preferences_notifications(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.43 EXTERNAL_CALENDAR_CONFIGS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE configs_calendriers_externes (
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
CREATE INDEX ix_external_cal_user ON configs_calendriers_externes(user_id);
CREATE UNIQUE INDEX uq_user_calendar ON configs_calendriers_externes(user_id, provider, name);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.44 PLANS_JARDIN
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plans_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    largeur NUMERIC(6, 2) NOT NULL,
    hauteur NUMERIC(6, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_plans_jardin_nom ON plans_jardin(nom);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.45 PIECES_MAISON
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE pieces_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etage INTEGER DEFAULT 0,
    superficie_m2 NUMERIC(6, 2),
    type_piece VARCHAR(50),
    description TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_pieces_maison_type ON pieces_maison(type_piece);


-- ============================================================================
-- PARTIE 4 : TABLES AVEC DÉPENDANCES FK
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.01 GARMIN_TOKENS (→ profils_utilisateurs)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_garmin_tokens_user FOREIGN KEY (user_id)
        REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_garmin_tokens_user_id ON garmin_tokens(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.02 GARMIN_ACTIVITIES (→ profils_utilisateurs)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE activites_garmin (
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
    CONSTRAINT fk_garmin_activities_user FOREIGN KEY (user_id)
        REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_garmin_duree_positive CHECK (duree_secondes > 0)
);
CREATE UNIQUE INDEX uq_garmin_activity_id ON activites_garmin(garmin_activity_id);
CREATE INDEX ix_garmin_activities_user ON activites_garmin(user_id);
CREATE INDEX ix_garmin_activities_type ON activites_garmin(type_activite);
CREATE INDEX ix_garmin_activities_date ON activites_garmin(date_debut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.03 GARMIN_DAILY_SUMMARIES (→ profils_utilisateurs)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE resumes_quotidiens_garmin (
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
    CONSTRAINT fk_garmin_daily_user FOREIGN KEY (user_id)
        REFERENCES profils_utilisateurs(id) ON DELETE CASCADE
);
CREATE INDEX ix_garmin_daily_user ON resumes_quotidiens_garmin(user_id);
CREATE INDEX ix_garmin_daily_date ON resumes_quotidiens_garmin(date);
CREATE UNIQUE INDEX uq_garmin_daily_user_date ON resumes_quotidiens_garmin(user_id, date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.04 FOOD_LOGS (→ profils_utilisateurs)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE journaux_alimentaires (
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
    CONSTRAINT fk_food_logs_user FOREIGN KEY (user_id)
        REFERENCES profils_utilisateurs(id) ON DELETE CASCADE,
    CONSTRAINT ck_food_qualite_range CHECK (
        qualite IS NULL OR (qualite >= 1 AND qualite <= 5)
    )
);
CREATE INDEX ix_food_logs_user ON journaux_alimentaires(user_id);
CREATE INDEX ix_food_logs_date ON journaux_alimentaires(date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.05 RECETTE_INGREDIENTS (→ recettes, ingredients)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE recette_ingredients (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantite FLOAT NOT NULL,
    unite VARCHAR(50) NOT NULL,
    optionnel BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_recette_ing_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT fk_recette_ing_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_positive CHECK (quantite > 0)
);
CREATE INDEX ix_recette_ingredients_recette ON recette_ingredients(recette_id);
CREATE INDEX ix_recette_ingredients_ingredient ON recette_ingredients(ingredient_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.06 ETAPES_RECETTE (→ recettes)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE etapes_recette (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    ordre INTEGER NOT NULL,
    description TEXT NOT NULL,
    duree INTEGER,
    CONSTRAINT fk_etapes_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_ordre_positif CHECK (ordre > 0)
);
CREATE INDEX ix_etapes_recette_recette ON etapes_recette(recette_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.07 VERSIONS_RECETTE (→ recettes)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_versions_recette FOREIGN KEY (recette_base_id)
        REFERENCES recettes(id) ON DELETE CASCADE
);
CREATE INDEX ix_versions_recette_base ON versions_recette(recette_base_id);
CREATE INDEX ix_versions_recette_type ON versions_recette(type_version);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.08 HISTORIQUE_RECETTES (→ recettes)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE historique_recettes (
    id SERIAL PRIMARY KEY,
    recette_id INTEGER NOT NULL,
    date_cuisson DATE NOT NULL,
    portions_cuisinees INTEGER NOT NULL DEFAULT 1,
    note INTEGER,
    avis TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_historique_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_note_valide CHECK (note IS NULL OR (note >= 0 AND note <= 5)),
    CONSTRAINT ck_portions_cuisinees_positive CHECK (portions_cuisinees > 0)
);
CREATE INDEX ix_historique_recettes_recette ON historique_recettes(recette_id);
CREATE INDEX ix_historique_recettes_date ON historique_recettes(date_cuisson);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.09 BATCH_MEALS (→ recettes)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE repas_batch (
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
    CONSTRAINT fk_batch_meals_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE SET NULL
);
CREATE INDEX ix_batch_meals_recette ON repas_batch(recette_id);
CREATE INDEX ix_batch_meals_date_prep ON repas_batch(date_preparation);
CREATE INDEX ix_batch_meals_date_peremption ON repas_batch(date_peremption);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.10 RECIPE_FEEDBACKS (→ recettes)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE retours_recettes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    recette_id INTEGER NOT NULL,
    feedback VARCHAR(20) NOT NULL DEFAULT 'neutral',
    contexte VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_recipe_feedbacks_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE CASCADE,
    CONSTRAINT ck_feedback_type CHECK (feedback IN ('like', 'dislike', 'neutral'))
);
CREATE INDEX ix_recipe_feedbacks_user ON retours_recettes(user_id);
CREATE INDEX ix_recipe_feedbacks_recette ON retours_recettes(recette_id);
CREATE UNIQUE INDEX uq_user_recipe_feedback ON retours_recettes(user_id, recette_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.11 INVENTAIRE (→ ingredients)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_inventaire_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE CASCADE,
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

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.12 HISTORIQUE_INVENTAIRE (→ inventaire, ingredients)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_hist_inv_article FOREIGN KEY (article_id)
        REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_hist_inv_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE CASCADE
);
CREATE INDEX ix_historique_inventaire_article ON historique_inventaire(article_id);
CREATE INDEX ix_historique_inventaire_ingredient ON historique_inventaire(ingredient_id);
CREATE INDEX ix_historique_inventaire_type ON historique_inventaire(type_modification);
CREATE INDEX ix_historique_inventaire_date ON historique_inventaire(date_modification);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.13 LISTE_COURSES (articles) (→ listes_courses, ingredients)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_liste_courses_liste FOREIGN KEY (liste_id)
        REFERENCES listes_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_liste_courses_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE CASCADE,
    CONSTRAINT ck_quantite_courses_positive CHECK (quantite_necessaire > 0)
);
CREATE INDEX ix_liste_courses_liste ON liste_courses(liste_id);
CREATE INDEX ix_liste_courses_ingredient ON liste_courses(ingredient_id);
CREATE INDEX ix_liste_courses_priorite ON liste_courses(priorite);
CREATE INDEX ix_liste_courses_achete ON liste_courses(achete);
CREATE INDEX ix_liste_courses_cree_le ON liste_courses(cree_le);
CREATE INDEX ix_liste_courses_rayon ON liste_courses(rayon_magasin);
CREATE INDEX ix_liste_courses_magasin ON liste_courses(magasin_cible);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.14 ARTICLES_MODELES (→ modeles_courses, ingredients)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_articles_modeles_modele FOREIGN KEY (modele_id)
        REFERENCES modeles_courses(id) ON DELETE CASCADE,
    CONSTRAINT fk_articles_modeles_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredients(id) ON DELETE SET NULL,
    CONSTRAINT ck_article_modele_quantite_positive CHECK (quantite > 0),
    CONSTRAINT ck_article_modele_priorite_valide CHECK (
        priorite IN ('haute', 'moyenne', 'basse')
    )
);
CREATE INDEX ix_articles_modeles_modele ON articles_modeles(modele_id);
CREATE INDEX ix_articles_modeles_ingredient ON articles_modeles(ingredient_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.15 REPAS (→ plannings, recettes)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE repas (
    id SERIAL PRIMARY KEY,
    planning_id INTEGER NOT NULL,
    recette_id INTEGER,
    date_repas DATE NOT NULL,
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    portion_ajustee INTEGER,
    prepare BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    CONSTRAINT fk_repas_planning FOREIGN KEY (planning_id)
        REFERENCES plannings(id) ON DELETE CASCADE,
    CONSTRAINT fk_repas_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT ck_repas_portions_valides CHECK (
        portion_ajustee IS NULL OR (portion_ajustee > 0 AND portion_ajustee <= 20)
    )
);
CREATE INDEX ix_repas_planning ON repas(planning_id);
CREATE INDEX ix_repas_recette ON repas(recette_id);
CREATE INDEX ix_repas_date ON repas(date_repas);
CREATE INDEX ix_repas_type ON repas(type_repas);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.16 TEMPLATE_ITEMS (→ templates_semaine)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE elements_templates (
    id SERIAL PRIMARY KEY,
    template_id INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,
    heure_debut VARCHAR(5) NOT NULL,
    heure_fin VARCHAR(5),
    titre VARCHAR(200) NOT NULL,
    type_event VARCHAR(50) DEFAULT 'autre',
    lieu VARCHAR(200),
    couleur VARCHAR(20),
    CONSTRAINT fk_template_items_template FOREIGN KEY (template_id)
        REFERENCES templates_semaine(id) ON DELETE CASCADE,
    CONSTRAINT ck_template_jour_valide CHECK (jour_semaine >= 0 AND jour_semaine <= 6)
);
CREATE INDEX idx_template_jour ON elements_templates(template_id, jour_semaine);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.17 WELLBEING_ENTRIES (→ profils_enfants)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE entrees_bien_etre (
    id SERIAL PRIMARY KEY,
    child_id INTEGER,
    username VARCHAR(200),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    mood VARCHAR(100),
    sleep_hours FLOAT,
    activity VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_wellbeing_child FOREIGN KEY (child_id)
        REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX ix_wellbeing_child ON entrees_bien_etre(child_id);
CREATE INDEX ix_wellbeing_username ON entrees_bien_etre(username);
CREATE INDEX ix_wellbeing_date ON entrees_bien_etre(date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.18 MILESTONES (→ profils_enfants)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE jalons (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(100) NOT NULL,
    date_atteint DATE NOT NULL,
    photo_url VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_milestones_child FOREIGN KEY (child_id)
        REFERENCES profils_enfants(id) ON DELETE CASCADE
);
CREATE INDEX ix_milestones_child ON jalons(child_id);
CREATE INDEX ix_milestones_categorie ON jalons(categorie);
CREATE INDEX ix_milestones_date ON jalons(date_atteint);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.19 HEALTH_ENTRIES (→ routines_sante)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE entrees_sante (
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
    CONSTRAINT fk_health_entries_routine FOREIGN KEY (routine_id)
        REFERENCES routines_sante(id) ON DELETE CASCADE,
    CONSTRAINT ck_entry_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_entry_energie CHECK (
        note_energie IS NULL OR (note_energie >= 1 AND note_energie <= 10)
    ),
    CONSTRAINT ck_entry_moral CHECK (
        note_moral IS NULL OR (note_moral >= 1 AND note_moral <= 10)
    )
);
CREATE INDEX ix_health_entries_routine ON entrees_sante(routine_id);
CREATE INDEX ix_health_entries_date ON entrees_sante(date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.20 PROJECT_TASKS (→ projets)
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
    CONSTRAINT fk_project_tasks_project FOREIGN KEY (project_id)
        REFERENCES projets(id) ON DELETE CASCADE
);
CREATE INDEX ix_project_tasks_project ON taches_projets(project_id);
CREATE INDEX ix_project_tasks_statut ON taches_projets(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.21 ROUTINE_TASKS (→ routines)
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
    CONSTRAINT fk_routine_tasks_routine FOREIGN KEY (routine_id)
        REFERENCES routines(id) ON DELETE CASCADE
);
CREATE INDEX ix_routine_tasks_routine ON taches_routines(routine_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.22 GARDEN_LOGS (→ elements_jardin)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE journaux_jardin (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garden_logs_item FOREIGN KEY (garden_item_id)
        REFERENCES elements_jardin(id) ON DELETE CASCADE
);
CREATE INDEX ix_garden_logs_item ON journaux_jardin(garden_item_id);
CREATE INDEX ix_garden_logs_date ON journaux_jardin(date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.23 JEUX_MATCHS (→ jeux_equipes)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_jeux_matchs_dom FOREIGN KEY (equipe_domicile_id)
        REFERENCES jeux_equipes(id),
    CONSTRAINT fk_jeux_matchs_ext FOREIGN KEY (equipe_exterieur_id)
        REFERENCES jeux_equipes(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.24 JEUX_PARIS_SPORTIFS (→ jeux_matchs)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_jeux_paris_match FOREIGN KEY (match_id)
        REFERENCES jeux_matchs(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.25 JEUX_GRILLES_LOTO (→ jeux_tirages_loto)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_jeux_grilles_tirage FOREIGN KEY (tirage_id)
        REFERENCES jeux_tirages_loto(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.26 JEUX_ALERTES (→ jeux_series)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE jeux_alertes (
    id SERIAL PRIMARY KEY,
    serie_id INTEGER NOT NULL,
    type_jeu VARCHAR(20) NOT NULL,
    championnat VARCHAR(50),
    marche VARCHAR(50) NOT NULL,
    value_alerte FLOAT NOT NULL,
    serie_alerte INTEGER NOT NULL,
    frequence_alerte FLOAT NOT NULL,
    seuil_utilise FLOAT NOT NULL DEFAULT 2.0,
    notifie BOOLEAN NOT NULL DEFAULT FALSE,
    date_notification TIMESTAMP,
    resultat_verifie BOOLEAN NOT NULL DEFAULT FALSE,
    resultat_correct BOOLEAN,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jeux_alertes_serie FOREIGN KEY (serie_id)
        REFERENCES jeux_series(id) ON DELETE CASCADE
);
CREATE INDEX ix_jeux_alertes_notifie ON jeux_alertes(notifie) WHERE notifie = FALSE;
CREATE INDEX ix_jeux_alertes_resultat ON jeux_alertes(resultat_verifie, resultat_correct);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.27 SESSIONS_BATCH_COOKING (→ plannings)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_sessions_batch_planning FOREIGN KEY (planning_id)
        REFERENCES plannings(id) ON DELETE SET NULL,
    CONSTRAINT ck_session_duree_estimee_positive CHECK (duree_estimee > 0),
    CONSTRAINT ck_session_duree_reelle_positive CHECK (duree_reelle IS NULL OR duree_reelle > 0),
    CONSTRAINT ck_session_portions_positive CHECK (nb_portions_preparees >= 0),
    CONSTRAINT ck_session_recettes_positive CHECK (nb_recettes_completees >= 0)
);
CREATE INDEX ix_sessions_batch_date ON sessions_batch_cooking(date_session);
CREATE INDEX ix_sessions_batch_statut ON sessions_batch_cooking(statut);
CREATE INDEX ix_sessions_batch_planning ON sessions_batch_cooking(planning_id);
CREATE INDEX idx_session_date_statut ON sessions_batch_cooking(date_session, statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.28 ETAPES_BATCH_COOKING (→ sessions_batch_cooking, recettes)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_etapes_batch_session FOREIGN KEY (session_id)
        REFERENCES sessions_batch_cooking(id) ON DELETE CASCADE,
    CONSTRAINT fk_etapes_batch_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT ck_etape_batch_ordre_positif CHECK (ordre > 0),
    CONSTRAINT ck_etape_batch_duree_positive CHECK (duree_minutes > 0),
    CONSTRAINT ck_etape_batch_duree_reelle_positive CHECK (duree_reelle IS NULL OR duree_reelle > 0)
);
CREATE INDEX ix_etapes_batch_session ON etapes_batch_cooking(session_id);
CREATE INDEX ix_etapes_batch_recette ON etapes_batch_cooking(recette_id);
CREATE INDEX idx_etape_session_ordre ON etapes_batch_cooking(session_id, ordre);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.29 PREPARATIONS_BATCH (→ sessions_batch_cooking, recettes)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_prep_batch_session FOREIGN KEY (session_id)
        REFERENCES sessions_batch_cooking(id) ON DELETE SET NULL,
    CONSTRAINT fk_prep_batch_recette FOREIGN KEY (recette_id)
        REFERENCES recettes(id) ON DELETE SET NULL,
    CONSTRAINT ck_prep_portions_initiales_positive CHECK (portions_initiales > 0),
    CONSTRAINT ck_prep_portions_restantes_positive CHECK (portions_restantes >= 0)
);
CREATE INDEX ix_prep_batch_session ON preparations_batch(session_id);
CREATE INDEX ix_prep_batch_recette ON preparations_batch(recette_id);
CREATE INDEX ix_prep_batch_date ON preparations_batch(date_preparation);
CREATE INDEX ix_prep_batch_peremption ON preparations_batch(date_peremption);
CREATE INDEX ix_prep_batch_localisation ON preparations_batch(localisation);
CREATE INDEX ix_prep_batch_consomme ON preparations_batch(consomme);
CREATE INDEX idx_prep_localisation_peremption ON preparations_batch(localisation, date_peremption);
CREATE INDEX idx_prep_consomme_peremption ON preparations_batch(consomme, date_peremption);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.30 EVENEMENTS_CALENDRIER (→ calendriers_externes)
-- ─────────────────────────────────────────────────────────────────────────────
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
    CONSTRAINT fk_evenements_calendrier_source FOREIGN KEY (source_calendrier_id)
        REFERENCES calendriers_externes(id) ON DELETE SET NULL
);
CREATE INDEX ix_evenements_calendrier_date ON evenements_calendrier(date_debut);
CREATE INDEX ix_evenements_calendrier_user ON evenements_calendrier(user_id);
CREATE UNIQUE INDEX uq_event_uid_user ON evenements_calendrier(uid, user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.31 ZONES_JARDIN (→ plans_jardin)
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_zones_jardin_plan_id FOREIGN KEY (plan_id)
        REFERENCES plans_jardin(id) ON DELETE SET NULL
);
CREATE INDEX idx_zones_jardin_type ON zones_jardin(type_zone);
CREATE INDEX idx_zones_jardin_plan_id ON zones_jardin(plan_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.32 PLANTES_JARDIN (→ zones_jardin)
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
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_plantes_jardin_zone FOREIGN KEY (zone_id)
        REFERENCES zones_jardin(id) ON DELETE CASCADE
);
CREATE INDEX idx_plantes_jardin_zone ON plantes_jardin(zone_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.33 ACTIONS_PLANTES (→ plantes_jardin)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE actions_plantes (
    id SERIAL PRIMARY KEY,
    plante_id INTEGER NOT NULL,
    type_action VARCHAR(50) NOT NULL,
    date_action DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite NUMERIC(8, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_actions_plantes_plante_id FOREIGN KEY (plante_id)
        REFERENCES plantes_jardin(id) ON DELETE CASCADE
);
CREATE INDEX idx_actions_plantes_plante_id ON actions_plantes(plante_id);
CREATE INDEX idx_actions_plantes_type_action ON actions_plantes(type_action);
CREATE INDEX idx_actions_plantes_date_action ON actions_plantes(date_action);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.34 OBJETS_MAISON (→ pieces_maison)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE objets_maison (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'fonctionne',
    priorite_remplacement VARCHAR(20),
    date_achat DATE,
    prix_achat NUMERIC(10, 2),
    prix_remplacement_estime NUMERIC(10, 2),
    marque VARCHAR(100),
    modele VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_objets_maison_piece FOREIGN KEY (piece_id)
        REFERENCES pieces_maison(id) ON DELETE CASCADE
);
CREATE INDEX idx_objets_maison_piece ON objets_maison(piece_id);
CREATE INDEX idx_objets_maison_categorie ON objets_maison(categorie);
CREATE INDEX idx_objets_maison_statut ON objets_maison(statut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.35 SESSIONS_TRAVAIL
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE sessions_travail (
    id SERIAL PRIMARY KEY,
    type_activite VARCHAR(50) NOT NULL,
    zone_jardin_id INTEGER,
    piece_id INTEGER,
    description TEXT,
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP,
    duree_minutes INTEGER,
    notes TEXT,
    difficulte INTEGER,
    satisfaction INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ck_sessions_duree_positive CHECK (duree_minutes IS NULL OR duree_minutes >= 0),
    CONSTRAINT ck_difficulte_range CHECK (difficulte IS NULL OR (difficulte >= 1 AND difficulte <= 5)),
    CONSTRAINT ck_satisfaction_range CHECK (satisfaction IS NULL OR (satisfaction >= 1 AND satisfaction <= 5))
);
CREATE INDEX idx_sessions_travail_type ON sessions_travail(type_activite);
CREATE INDEX idx_sessions_travail_zone ON sessions_travail(zone_jardin_id);
CREATE INDEX idx_sessions_travail_piece ON sessions_travail(piece_id);
CREATE INDEX idx_sessions_travail_type_debut ON sessions_travail(type_activite, debut);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.36 VERSIONS_PIECES
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE versions_pieces (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_modification DATE NOT NULL,
    cout_total NUMERIC(10, 2),
    photo_avant_url VARCHAR(500),
    photo_apres_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    cree_par VARCHAR(100)
);
CREATE INDEX idx_versions_pieces_piece ON versions_pieces(piece_id);
CREATE INDEX idx_versions_pieces_piece_version ON versions_pieces(piece_id, version);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.37 COUTS_TRAVAUX (→ versions_pieces)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE couts_travaux (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    fournisseur VARCHAR(200),
    facture_ref VARCHAR(100),
    date_paiement DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_couts_travaux_version FOREIGN KEY (version_id)
        REFERENCES versions_pieces(id) ON DELETE CASCADE,
    CONSTRAINT ck_cout_montant_positif CHECK (montant >= 0)
);
CREATE INDEX idx_couts_travaux_version ON couts_travaux(version_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.38 LOGS_STATUT_OBJETS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE logs_statut_objets (
    id SERIAL PRIMARY KEY,
    objet_id INTEGER NOT NULL,
    ancien_statut VARCHAR(50),
    nouveau_statut VARCHAR(50) NOT NULL,
    raison TEXT,
    prix_estime NUMERIC(10, 2),
    priorite VARCHAR(20),
    ajoute_courses BOOLEAN DEFAULT FALSE,
    ajoute_budget BOOLEAN DEFAULT FALSE,
    date_changement TIMESTAMP DEFAULT NOW(),
    change_par VARCHAR(100)
);
CREATE INDEX idx_logs_statut_objet ON logs_statut_objets(objet_id);


-- ============================================================================
-- PARTIE 5 : TABLES HUB MAISON (sans modèles ORM — migration 020)
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.01 PREFERENCES_HOME
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.02 TACHES_HOME (→ zones_jardin, pieces_maison)
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
        priorite IN ('urgente', 'haute', 'normale', 'basse', 'optionnelle')
    ),
    date_due DATE,
    date_faite DATE,
    statut VARCHAR(20) DEFAULT 'a_faire' CHECK (
        statut IN ('a_faire', 'en_cours', 'fait', 'reporte', 'annule')
    ),
    generee_auto BOOLEAN DEFAULT FALSE,
    source VARCHAR(50),
    source_id INTEGER,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE SET NULL,
    piece_id INTEGER REFERENCES pieces_maison(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_taches_home_domaine ON taches_home(domaine);
CREATE INDEX idx_taches_home_statut ON taches_home(statut);
CREATE INDEX idx_taches_home_date_due ON taches_home(date_due);
CREATE INDEX idx_taches_home_source ON taches_home(source, source_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.03 STATS_HOME
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE stats_home (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN ('jardin', 'entretien', 'charges', 'depenses', 'total')
    ),
    temps_prevu_min INTEGER DEFAULT 0,
    temps_reel_min INTEGER DEFAULT 0,
    taches_prevues INTEGER DEFAULT 0,
    taches_completees INTEGER DEFAULT 0,
    taches_reportees INTEGER DEFAULT 0,
    score_jour INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, domaine)
);
CREATE INDEX idx_stats_home_date ON stats_home(date);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.04 PLANTES_CATALOGUE
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_plantes_catalogue_famille ON plantes_catalogue(famille);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.05 RECOLTES (→ plantes_jardin, zones_jardin)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_recoltes_date ON recoltes(date_recolte);
CREATE INDEX idx_recoltes_legume ON recoltes(legume);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.06 OBJECTIFS_AUTONOMIE
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
            WHEN besoin_kg_an > 0 THEN LEAST(100, ROUND((production_kg_an / besoin_kg_an) * 100))
            ELSE 0
        END
    ) STORED,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.07 CONTRATS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE contrats (
    id SERIAL PRIMARY KEY,
    type_contrat VARCHAR(30) NOT NULL CHECK (
        type_contrat IN (
            'electricite', 'gaz', 'eau', 'internet', 'telephone', 'mobile',
            'assurance_habitation', 'assurance_auto', 'assurance_sante',
            'abonnement', 'autre'
        )
    ),
    fournisseur VARCHAR(100) NOT NULL,
    reference_contrat VARCHAR(100),
    date_debut DATE,
    date_fin DATE,
    date_renouvellement DATE,
    montant_mensuel DECIMAL(10, 2),
    montant_annuel DECIMAL(10, 2),
    actif BOOLEAN DEFAULT TRUE,
    tacite_reconduction BOOLEAN DEFAULT TRUE,
    fichier_url TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_contrats_type ON contrats(type_contrat);
CREATE INDEX idx_contrats_actif ON contrats(actif);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.08 FACTURES (→ contrats)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE factures (
    id SERIAL PRIMARY KEY,
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE CASCADE,
    date_facture DATE NOT NULL,
    date_echeance DATE,
    periode_debut DATE,
    periode_fin DATE,
    montant_ht DECIMAL(10, 2),
    montant_ttc DECIMAL(10, 2) NOT NULL,
    conso_kwh DECIMAL(10, 2),
    conso_m3 DECIMAL(10, 2),
    payee BOOLEAN DEFAULT FALSE,
    date_paiement DATE,
    fichier_url TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_factures_contrat ON factures(contrat_id);
CREATE INDEX idx_factures_date ON factures(date_facture);
CREATE INDEX idx_factures_payee ON factures(payee);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.09 COMPARATIFS (→ contrats)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE comparatifs (
    id SERIAL PRIMARY KEY,
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE CASCADE,
    date_analyse DATE DEFAULT CURRENT_DATE,
    fournisseur_suggere VARCHAR(100),
    offre_nom VARCHAR(200),
    economie_mensuelle DECIMAL(10, 2),
    economie_annuelle DECIMAL(10, 2),
    avantages TEXT,
    inconvenients TEXT,
    lien_offre TEXT,
    applique BOOLEAN DEFAULT FALSE,
    date_application DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.10 DEPENSES_HOME (→ contrats, factures)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE depenses_home (
    id SERIAL PRIMARY KEY,
    date_depense DATE NOT NULL DEFAULT CURRENT_DATE,
    montant DECIMAL(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL CHECK (
        categorie IN (
            'jardin', 'entretien', 'energie', 'travaux',
            'equipement', 'decoration', 'assurance', 'autre'
        )
    ),
    sous_categorie VARCHAR(50),
    description TEXT,
    magasin VARCHAR(100),
    recurrent BOOLEAN DEFAULT FALSE,
    frequence_mois INTEGER,
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE SET NULL,
    facture_id INTEGER REFERENCES factures(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_depenses_home_date ON depenses_home(date_depense);
CREATE INDEX idx_depenses_home_categorie ON depenses_home(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.11 BUDGETS_HOME
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE budgets_home (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL UNIQUE,
    montant_mensuel DECIMAL(10, 2) NOT NULL,
    alerte_pourcent INTEGER DEFAULT 80,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================================
-- PARTIE 6 : TRIGGERS (modifie_le / updated_at)
-- ============================================================================

-- Tables avec colonne modifie_le
DO $$
DECLARE t TEXT;
    tables_modifie_le TEXT[] := ARRAY[
        'profils_utilisateurs', 'garmin_tokens', 'recettes', 'activites_weekend',
        'achats_famille', 'jeux_equipes', 'jeux_matchs', 'config_batch_cooking',
        'sessions_batch_cooking', 'preparations_batch', 'plannings',
        'modeles_courses', 'templates_semaine'
    ];
BEGIN
    FOREACH t IN ARRAY tables_modifie_le LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trigger_update_modifie_le ON %I', t);
        EXECUTE format('
            CREATE TRIGGER trigger_update_modifie_le
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modifie_le_column()
        ', t);
    END LOOP;
END $$;

-- Tables avec colonne updated_at
DO $$
DECLARE t TEXT;
    tables_updated_at TEXT[] := ARRAY[
        'listes_courses', 'meubles', 'taches_entretien', 'stocks_maison',
        'preferences_utilisateurs', 'depenses', 'budgets_mensuels', 'config_meteo',
        'calendriers_externes', 'preferences_notifications',
        'configs_calendriers_externes', 'evenements_calendrier',
        'plans_jardin', 'zones_jardin', 'plantes_jardin',
        'pieces_maison', 'objets_maison',
        'preferences_home', 'taches_home', 'objectifs_autonomie',
        'contrats', 'budgets_home'
    ];
BEGIN
    FOREACH t IN ARRAY tables_updated_at LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trigger_update_updated_at ON %I', t);
        EXECUTE format('
            CREATE TRIGGER trigger_update_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column()
        ', t);
    END LOOP;
END $$;


-- ============================================================================
-- PARTIE 7 : VUES UTILES
-- ============================================================================

-- Vue: Objets à remplacer avec priorité
CREATE OR REPLACE VIEW v_objets_a_remplacer AS
SELECT
    o.id, o.nom, o.categorie, o.statut, o.priorite_remplacement,
    o.prix_remplacement_estime, p.nom AS piece, p.etage
FROM objets_maison o
JOIN pieces_maison p ON o.piece_id = p.id
WHERE o.statut IN ('a_changer', 'a_acheter', 'a_reparer')
ORDER BY
    CASE o.priorite_remplacement
        WHEN 'urgente' THEN 1 WHEN 'haute' THEN 2
        WHEN 'normale' THEN 3 WHEN 'basse' THEN 4 ELSE 5
    END,
    o.prix_remplacement_estime DESC NULLS LAST;

-- Vue: Temps par activité (30 derniers jours)
CREATE OR REPLACE VIEW v_temps_par_activite_30j AS
SELECT
    type_activite,
    COUNT(*) AS nb_sessions,
    COALESCE(SUM(duree_minutes), 0) AS duree_totale_minutes,
    ROUND(AVG(duree_minutes)::numeric, 1) AS duree_moyenne_minutes,
    ROUND(AVG(difficulte)::numeric, 1) AS difficulte_moyenne,
    ROUND(AVG(satisfaction)::numeric, 1) AS satisfaction_moyenne
FROM sessions_travail
WHERE debut >= NOW() - INTERVAL '30 days' AND fin IS NOT NULL
GROUP BY type_activite
ORDER BY duree_totale_minutes DESC;

-- Vue: Budget travaux par pièce
CREATE OR REPLACE VIEW v_budget_travaux_par_piece AS
SELECT
    p.id AS piece_id, p.nom AS piece,
    COUNT(DISTINCT v.id) AS nb_versions,
    COALESCE(SUM(c.montant), 0) AS cout_total,
    COUNT(DISTINCT c.id) AS nb_lignes_cout,
    MAX(v.date_modification) AS derniere_modif
FROM pieces_maison p
LEFT JOIN versions_pieces v ON v.piece_id = p.id
LEFT JOIN couts_travaux c ON c.version_id = v.id
GROUP BY p.id, p.nom
ORDER BY cout_total DESC;

-- Vue: Tâches du jour
CREATE OR REPLACE VIEW v_taches_jour AS
SELECT t.*,
    z.nom AS zone_nom, p.nom AS piece_nom,
    CASE
        WHEN t.priorite = 'urgente' THEN 1 WHEN t.priorite = 'haute' THEN 2
        WHEN t.priorite = 'normale' THEN 3 WHEN t.priorite = 'basse' THEN 4
        ELSE 5
    END AS priorite_ordre
FROM taches_home t
LEFT JOIN zones_jardin z ON t.zone_jardin_id = z.id
LEFT JOIN pieces_maison p ON t.piece_id = p.id
WHERE t.statut IN ('a_faire', 'en_cours')
    AND (t.date_due IS NULL OR t.date_due <= CURRENT_DATE + INTERVAL '1 day')
ORDER BY priorite_ordre, t.date_due NULLS LAST;

-- Vue: Charge semaine
CREATE OR REPLACE VIEW v_charge_semaine AS
SELECT d.jour,
    COALESCE(SUM(t.duree_min), 0) AS temps_prevu_min,
    COUNT(t.id) AS nb_taches,
    CASE
        WHEN COALESCE(SUM(t.duree_min), 0) > 120 THEN 'surcharge'
        WHEN COALESCE(SUM(t.duree_min), 0) > 90 THEN 'charge'
        WHEN COALESCE(SUM(t.duree_min), 0) > 60 THEN 'normal'
        ELSE 'leger'
    END AS niveau_charge
FROM (SELECT generate_series(CURRENT_DATE, CURRENT_DATE + INTERVAL '6 days', INTERVAL '1 day')::DATE AS jour) d
LEFT JOIN taches_home t ON t.date_due = d.jour AND t.statut IN ('a_faire', 'en_cours')
GROUP BY d.jour ORDER BY d.jour;

-- Vue: Pourcentage autonomie alimentaire
CREATE OR REPLACE VIEW v_autonomie AS
SELECT
    COALESCE(SUM(production_kg_an), 0) AS production_totale_kg,
    COALESCE(SUM(besoin_kg_an), 0) AS besoin_total_kg,
    CASE WHEN COALESCE(SUM(besoin_kg_an), 0) > 0
        THEN ROUND((SUM(production_kg_an) / SUM(besoin_kg_an)) * 100) ELSE 0
    END AS pourcentage_global,
    COUNT(*) AS nb_legumes_suivis,
    COUNT(*) FILTER (WHERE pourcentage_atteint >= 100) AS nb_objectifs_atteints
FROM objectifs_autonomie;


-- ============================================================================
-- PARTIE 8 : FONCTIONS HELPER
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_temps_entretien_par_mois(
    p_annee INTEGER DEFAULT EXTRACT(YEAR FROM NOW())::INTEGER,
    p_mois INTEGER DEFAULT NULL
)
RETURNS TABLE (
    mois INTEGER, annee INTEGER, type_activite VARCHAR,
    nb_sessions BIGINT, duree_totale_minutes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        EXTRACT(MONTH FROM s.debut)::INTEGER AS mois,
        EXTRACT(YEAR FROM s.debut)::INTEGER AS annee,
        s.type_activite,
        COUNT(*)::BIGINT AS nb_sessions,
        COALESCE(SUM(s.duree_minutes), 0)::BIGINT AS duree_totale_minutes
    FROM sessions_travail s
    WHERE EXTRACT(YEAR FROM s.debut)::INTEGER = p_annee
        AND (p_mois IS NULL OR EXTRACT(MONTH FROM s.debut)::INTEGER = p_mois)
        AND s.fin IS NOT NULL
    GROUP BY EXTRACT(MONTH FROM s.debut), EXTRACT(YEAR FROM s.debut), s.type_activite
    ORDER BY mois, type_activite;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- PARTIE 9 : ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Activer RLS sur TOUTES les tables
DO $$
DECLARE t TEXT;
    all_tables TEXT[] := ARRAY[
        -- Système
        'schema_migrations', 'historique_actions', 'sauvegardes',
        'abonnements_push', 'preferences_notifications',
        -- Cuisine
        'ingredients', 'recettes', 'recette_ingredients', 'etapes_recette',
        'versions_recette', 'historique_recettes', 'retours_recettes',
        -- Batch Cooking
        'repas_batch', 'config_batch_cooking', 'sessions_batch_cooking',
        'etapes_batch_cooking', 'preparations_batch',
        -- Inventaire & Courses
        'inventaire', 'historique_inventaire', 'listes_courses', 'liste_courses',
        'modeles_courses', 'articles_modeles', 'articles_achats_famille',
        -- Planning & Calendrier
        'plannings', 'repas', 'evenements_planning', 'templates_semaine', 'elements_templates',
        'calendriers_externes', 'evenements_calendrier', 'configs_calendriers_externes',
        -- Famille
        'profils_enfants', 'entrees_bien_etre', 'jalons',
        'activites_famille', 'budgets_famille', 'achats_famille',
        'activites_weekend',
        -- Santé & Fitness
        'profils_utilisateurs', 'routines_sante', 'objectifs_sante', 'entrees_sante',
        'journaux_alimentaires', 'garmin_tokens', 'activites_garmin', 'resumes_quotidiens_garmin',
        -- Finances
        'depenses', 'budgets_mensuels', 'depenses_maison',
        -- Habitat
        'meubles', 'stocks_maison', 'taches_entretien', 'actions_ecologiques',
        -- Maison
        'projets', 'taches_projets', 'routines', 'taches_routines',
        'elements_jardin', 'journaux_jardin',
        -- Jeux
        'jeux_equipes', 'jeux_matchs', 'jeux_paris_sportifs',
        'jeux_tirages_loto', 'jeux_grilles_loto', 'jeux_stats_loto',
        'jeux_historique', 'jeux_series', 'jeux_alertes', 'jeux_configuration',
        -- Jardin & Météo
        'alertes_meteo', 'config_meteo',
        -- Temps Entretien
        'plans_jardin', 'zones_jardin', 'plantes_jardin', 'actions_plantes',
        'pieces_maison', 'objets_maison', 'sessions_travail',
        'versions_pieces', 'couts_travaux', 'logs_statut_objets',
        -- Préférences
        'preferences_utilisateurs', 'openfoodfacts_cache',
        -- Hub Maison (migration 020)
        'preferences_home', 'taches_home', 'stats_home',
        'plantes_catalogue', 'recoltes', 'objectifs_autonomie',
        'contrats', 'factures', 'comparatifs', 'depenses_home', 'budgets_home'
    ];
BEGIN
    FOREACH t IN ARRAY all_tables LOOP
        EXECUTE format('ALTER TABLE IF EXISTS public.%I ENABLE ROW LEVEL SECURITY', t);

        -- Politique authenticated
        EXECUTE format('DROP POLICY IF EXISTS "authenticated_access_%s" ON public.%I', t, t);
        EXECUTE format(
            'CREATE POLICY "authenticated_access_%s" ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
            t, t
        );

        -- Politique service_role
        EXECUTE format('DROP POLICY IF EXISTS "service_role_access_%s" ON public.%I', t, t);
        EXECUTE format(
            'CREATE POLICY "service_role_access_%s" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
            t, t
        );
    END LOOP;
END $$;


-- ============================================================================
-- PARTIE 10 : DONNÉES DE RÉFÉRENCE
-- ============================================================================

-- Configuration jeux par défaut
INSERT INTO jeux_configuration (cle, valeur, description) VALUES
    ('seuil_value_alerte', '2.0', 'Seuil de value minimum pour créer une alerte'),
    ('seuil_value_haute', '2.5', 'Seuil de value pour opportunité haute'),
    ('seuil_series_minimum', '3', 'Série minimum significative'),
    ('sync_paris_interval_hours', '6', 'Intervalle sync paris en heures'),
    ('sync_loto_days', 'mon,wed,sat', 'Jours de sync loto'),
    ('sync_loto_hour', '21:30', 'Heure de sync loto')
ON CONFLICT (cle) DO NOTHING;

-- Préférences maison par défaut
INSERT INTO preferences_home (id, max_taches_jour, max_heures_jour)
VALUES (1, 3, 2.0)
ON CONFLICT (id) DO NOTHING;

-- Budgets maison par défaut
INSERT INTO budgets_home (categorie, montant_mensuel, alerte_pourcent) VALUES
    ('jardin', 100.00, 80), ('entretien', 50.00, 80),
    ('energie', 200.00, 90), ('travaux', 150.00, 80),
    ('equipement', 100.00, 80), ('decoration', 50.00, 80),
    ('assurance', 150.00, 95), ('autre', 50.00, 80)
ON CONFLICT (categorie) DO NOTHING;

-- Objectifs autonomie alimentaire
INSERT INTO objectifs_autonomie (legume, besoin_kg_an, surface_ideale_m2) VALUES
    ('Tomate', 40.00, 8.00), ('Courgette', 25.00, 6.00),
    ('Haricot vert', 15.00, 5.00), ('Pomme de terre', 80.00, 20.00),
    ('Carotte', 20.00, 4.00), ('Salade', 30.00, 3.00),
    ('Poireau', 15.00, 3.00), ('Oignon', 10.00, 2.00),
    ('Ail', 3.00, 1.00), ('Fraise', 10.00, 4.00)
ON CONFLICT (legume) DO NOTHING;

-- Grants Supabase
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;


-- ============================================================================
-- PARTIE 11 : VÉRIFICATION FINALE
-- ============================================================================

SELECT
    tablename,
    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.tablename) AS nb_colonnes
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;

COMMIT;

-- ============================================================================
-- FIN DU SCRIPT — 94 tables créées
-- ============================================================================
--
-- Stratégie RLS:
--   service_role : Accès complet (Streamlit backend via DATABASE_URL)
--   authenticated: Accès complet (future auth Supabase)
--   anon         : Pas d'accès (PostgREST avec clé anonyme bloqué)
--
-- ============================================================================
