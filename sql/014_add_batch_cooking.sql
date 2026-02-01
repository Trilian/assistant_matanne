-- ═══════════════════════════════════════════════════════════
-- MIGRATION: Add Batch Cooking Tables
-- Version: 013
-- Date: 2026-02-01
-- 
-- Exécuter ce SQL dans Supabase SQL Editor si la migration
-- Alembic n'est pas disponible
-- ═══════════════════════════════════════════════════════════

-- TABLE: config_batch_cooking
-- Configuration singleton pour le batch cooking
CREATE TABLE IF NOT EXISTS config_batch_cooking (
    id SERIAL PRIMARY KEY,
    jours_batch JSONB DEFAULT '[6]'::jsonb,
    heure_debut_preferee TIME DEFAULT '10:00:00',
    duree_max_session INTEGER DEFAULT 180,
    avec_jules_par_defaut BOOLEAN DEFAULT true,
    robots_disponibles JSONB DEFAULT '["four", "plaques"]'::jsonb,
    preferences_stockage JSONB,
    objectif_portions_semaine INTEGER DEFAULT 20,
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW()
);

-- TABLE: sessions_batch_cooking
-- Sessions de batch cooking planifiées/en cours/terminées
CREATE TABLE IF NOT EXISTS sessions_batch_cooking (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    date_session DATE NOT NULL,
    heure_debut TIME,
    heure_fin TIME,
    duree_estimee INTEGER DEFAULT 120,
    duree_reelle INTEGER,
    statut VARCHAR(20) DEFAULT 'planifiee',
    avec_jules BOOLEAN DEFAULT false,
    planning_id INTEGER REFERENCES plannings(id) ON DELETE SET NULL,
    recettes_selectionnees JSONB,
    robots_utilises JSONB,
    notes_avant TEXT,
    notes_apres TEXT,
    genere_par_ia BOOLEAN DEFAULT false,
    nb_portions_preparees INTEGER DEFAULT 0,
    nb_recettes_completees INTEGER DEFAULT 0,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW()
);

-- Index pour sessions
CREATE INDEX IF NOT EXISTS ix_sessions_batch_date ON sessions_batch_cooking(date_session);
CREATE INDEX IF NOT EXISTS ix_sessions_batch_statut ON sessions_batch_cooking(statut);
CREATE INDEX IF NOT EXISTS idx_session_date_statut ON sessions_batch_cooking(date_session, statut);

-- TABLE: etapes_batch_cooking
-- Étapes d'une session avec gestion de parallélisation
CREATE TABLE IF NOT EXISTS etapes_batch_cooking (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions_batch_cooking(id) ON DELETE CASCADE,
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    ordre INTEGER NOT NULL,
    groupe_parallele INTEGER DEFAULT 0,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_minutes INTEGER DEFAULT 10,
    duree_reelle INTEGER,
    robots_requis JSONB,
    est_supervision BOOLEAN DEFAULT false,
    alerte_bruit BOOLEAN DEFAULT false,
    temperature INTEGER,
    statut VARCHAR(20) DEFAULT 'a_faire',
    heure_debut TIMESTAMP,
    heure_fin TIMESTAMP,
    notes TEXT,
    timer_actif BOOLEAN DEFAULT false
);

-- Index pour étapes
CREATE INDEX IF NOT EXISTS ix_etapes_batch_session ON etapes_batch_cooking(session_id);
CREATE INDEX IF NOT EXISTS ix_etapes_batch_recette ON etapes_batch_cooking(recette_id);
CREATE INDEX IF NOT EXISTS idx_etape_session_ordre ON etapes_batch_cooking(session_id, ordre);

-- TABLE: preparations_batch
-- Préparations stockées issues du batch cooking
CREATE TABLE IF NOT EXISTS preparations_batch (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions_batch_cooking(id) ON DELETE SET NULL,
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    portions_initiales INTEGER NOT NULL DEFAULT 4,
    portions_restantes INTEGER NOT NULL DEFAULT 4,
    date_preparation DATE NOT NULL,
    date_peremption DATE NOT NULL,
    localisation VARCHAR(50) DEFAULT 'frigo',
    container VARCHAR(100),
    etagere VARCHAR(50),
    repas_attribues JSONB,
    notes TEXT,
    photo_url VARCHAR(500),
    consomme BOOLEAN DEFAULT false,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW()
);

-- Index pour préparations
CREATE INDEX IF NOT EXISTS ix_prep_date ON preparations_batch(date_preparation);
CREATE INDEX IF NOT EXISTS ix_prep_peremption ON preparations_batch(date_peremption);
CREATE INDEX IF NOT EXISTS ix_prep_localisation ON preparations_batch(localisation);
CREATE INDEX IF NOT EXISTS ix_prep_consomme ON preparations_batch(consomme);
CREATE INDEX IF NOT EXISTS idx_prep_localisation_peremption ON preparations_batch(localisation, date_peremption);
CREATE INDEX IF NOT EXISTS idx_prep_consomme_peremption ON preparations_batch(consomme, date_peremption);

-- Trigger pour mise à jour automatique de modifie_le
CREATE OR REPLACE FUNCTION update_modifie_le()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modifie_le = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Appliquer le trigger aux tables batch cooking
DROP TRIGGER IF EXISTS tr_config_batch_modifie ON config_batch_cooking;
CREATE TRIGGER tr_config_batch_modifie
    BEFORE UPDATE ON config_batch_cooking
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

DROP TRIGGER IF EXISTS tr_sessions_batch_modifie ON sessions_batch_cooking;
CREATE TRIGGER tr_sessions_batch_modifie
    BEFORE UPDATE ON sessions_batch_cooking
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

DROP TRIGGER IF EXISTS tr_prep_batch_modifie ON preparations_batch;
CREATE TRIGGER tr_prep_batch_modifie
    BEFORE UPDATE ON preparations_batch
    FOR EACH ROW EXECUTE FUNCTION update_modifie_le();

-- ═══════════════════════════════════════════════════════════
-- DONNÉES INITIALES (optionnel)
-- ═══════════════════════════════════════════════════════════

-- Configuration par défaut (si pas déjà existante)
INSERT INTO config_batch_cooking (
    jours_batch,
    heure_debut_preferee,
    duree_max_session,
    avec_jules_par_defaut,
    robots_disponibles,
    objectif_portions_semaine
)
SELECT 
    '[6]'::jsonb,
    '10:00:00'::time,
    180,
    true,
    '["four", "plaques", "cookeo"]'::jsonb,
    20
WHERE NOT EXISTS (SELECT 1 FROM config_batch_cooking);

-- ═══════════════════════════════════════════════════════════
-- VÉRIFICATION
-- ═══════════════════════════════════════════════════════════
-- Après exécution, vérifier avec:
-- SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%batch%';
