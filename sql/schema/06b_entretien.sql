-- ============================================================================
-- ASSISTANT MATANNE — Maison : Entretien & Organisation
-- ============================================================================
-- Contient : entretien, checklists vacances
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS taches_entretien (
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
-- La table legacy `preferences_home` a été retirée : les préférences passent
-- désormais par `preferences_utilisateurs` et la configuration applicative.


-- ─────────────────────────────────────────────────────────────────────────────
-- Les anciennes tables `taches_home` et `stats_home` ont été retirées du schéma
-- actif : les besoins courants passent désormais par `taches_entretien` et les
-- vues SQL de planning maison.


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_vacances (
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
CREATE TABLE IF NOT EXISTS items_checklist (
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


