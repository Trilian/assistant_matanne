-- ═══════════════════════════════════════════════════════════
-- MIGRATION: Renommage colonnes created_at → cree_le, updated_at → modifie_le
-- Date: 2025
-- Description: Standardisation des timestamps en convention française
-- ═══════════════════════════════════════════════════════════

-- IMPORTANT: Exécuter cette migration sur la base Supabase AVANT de déployer
-- le code Python mis à jour. Les alias SQL permettent une transition progressive.

BEGIN;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 1: Tables avec created_at UNIQUEMENT (12 tables)
-- ═══════════════════════════════════════════════════════════

ALTER TABLE depenses_maison RENAME COLUMN created_at TO cree_le;
ALTER TABLE alertes_meteo RENAME COLUMN created_at TO cree_le;
ALTER TABLE abonnements_push RENAME COLUMN created_at TO cree_le;
ALTER TABLE sauvegardes RENAME COLUMN created_at TO cree_le;
ALTER TABLE historique_actions RENAME COLUMN created_at TO cree_le;
ALTER TABLE actions_ecologiques RENAME COLUMN created_at TO cree_le;
ALTER TABLE sessions_travail RENAME COLUMN created_at TO cree_le;
ALTER TABLE versions_pieces RENAME COLUMN created_at TO cree_le;
ALTER TABLE couts_travaux RENAME COLUMN created_at TO cree_le;
ALTER TABLE actions_plantes RENAME COLUMN created_at TO cree_le;
ALTER TABLE retours_recettes RENAME COLUMN created_at TO cree_le;
ALTER TABLE openfoodfacts_cache RENAME COLUMN created_at TO cree_le;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 2: Tables avec created_at + updated_at (16 tables)
-- ═══════════════════════════════════════════════════════════

ALTER TABLE depenses RENAME COLUMN created_at TO cree_le;
ALTER TABLE depenses RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE budgets_mensuels RENAME COLUMN created_at TO cree_le;
ALTER TABLE budgets_mensuels RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE config_meteo RENAME COLUMN created_at TO cree_le;
ALTER TABLE config_meteo RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE preferences_notifications RENAME COLUMN created_at TO cree_le;
ALTER TABLE preferences_notifications RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE meubles RENAME COLUMN created_at TO cree_le;
ALTER TABLE meubles RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE stocks_maison RENAME COLUMN created_at TO cree_le;
ALTER TABLE stocks_maison RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE taches_entretien RENAME COLUMN created_at TO cree_le;
ALTER TABLE taches_entretien RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE pieces_maison RENAME COLUMN created_at TO cree_le;
ALTER TABLE pieces_maison RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE objets_maison RENAME COLUMN created_at TO cree_le;
ALTER TABLE objets_maison RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE zones_jardin RENAME COLUMN created_at TO cree_le;
ALTER TABLE zones_jardin RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE plantes_jardin RENAME COLUMN created_at TO cree_le;
ALTER TABLE plantes_jardin RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE plans_jardin RENAME COLUMN created_at TO cree_le;
ALTER TABLE plans_jardin RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE preferences_utilisateurs RENAME COLUMN created_at TO cree_le;
ALTER TABLE preferences_utilisateurs RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE configs_calendriers_externes RENAME COLUMN created_at TO cree_le;
ALTER TABLE configs_calendriers_externes RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE calendriers_externes RENAME COLUMN created_at TO cree_le;
ALTER TABLE calendriers_externes RENAME COLUMN updated_at TO modifie_le;

ALTER TABLE evenements_calendrier RENAME COLUMN created_at TO cree_le;
ALTER TABLE evenements_calendrier RENAME COLUMN updated_at TO modifie_le;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 3: Renommer les index existants
-- ═══════════════════════════════════════════════════════════

ALTER INDEX IF EXISTS ix_backups_created RENAME TO ix_sauvegardes_cree_le;
ALTER INDEX IF EXISTS idx_action_history_created_at RENAME TO idx_historique_actions_cree_le;

-- ═══════════════════════════════════════════════════════════
-- PARTIE 4: Mettre à jour le trigger updated_at → modifie_le
-- ═══════════════════════════════════════════════════════════

-- Remplacer la fonction trigger
CREATE OR REPLACE FUNCTION update_modifie_le_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modifie_le = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Supprimer les anciens triggers et recréer avec la nouvelle fonction
DO $$
DECLARE
    tables_with_modifie_le TEXT[] := ARRAY[
        'depenses', 'budgets_mensuels', 'config_meteo',
        'preferences_notifications', 'meubles', 'stocks_maison',
        'taches_entretien', 'pieces_maison', 'objets_maison',
        'zones_jardin', 'plantes_jardin', 'plans_jardin',
        'preferences_utilisateurs', 'configs_calendriers_externes',
        'calendriers_externes', 'evenements_calendrier'
    ];
    t TEXT;
BEGIN
    FOREACH t IN ARRAY tables_with_modifie_le LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trigger_update_updated_at ON %I', t);
        EXECUTE format('
            CREATE TRIGGER trigger_update_modifie_le
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modifie_le_column()', t);
    END LOOP;
END $$;

COMMIT;
