-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration 022: Table Action History
-- ═══════════════════════════════════════════════════════════════════════════════
-- Description: Table d'audit pour tracer toutes les actions utilisateur
--              (CRUD recettes, inventaire, planning, etc.)
--
-- Tables créées:
--   - action_history : Historique des actions utilisateur
--
-- Utilisé par: src/services/core/utilisateur/historique.py
-- ═══════════════════════════════════════════════════════════════════════════════
-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: action_history                                          │
-- │ Description: Audit trail des actions utilisateur               │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS action_history (
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
-- ┌─────────────────────────────────────────────────────────────────┐
-- │ INDEX                                                          │
-- └─────────────────────────────────────────────────────────────────┘
-- Index principal sur user_id pour requêtes par utilisateur
CREATE INDEX IF NOT EXISTS idx_action_history_user_id ON action_history(user_id);
-- Index sur action_type pour filtrage par type d'action
CREATE INDEX IF NOT EXISTS idx_action_history_action_type ON action_history(action_type);
-- Index sur created_at pour requêtes temporelles (DESC pour les plus récentes)
CREATE INDEX IF NOT EXISTS idx_action_history_created_at ON action_history(created_at DESC);
-- Index composite pour recherche par entité
CREATE INDEX IF NOT EXISTS idx_action_history_entity ON action_history(entity_type, entity_id);
-- ┌─────────────────────────────────────────────────────────────────┐
-- │ COMMENTAIRES                                                   │
-- └─────────────────────────────────────────────────────────────────┘
COMMENT ON TABLE action_history IS 'Audit trail des actions utilisateur pour traçabilité et fonctionnalité undo';
COMMENT ON COLUMN action_history.user_id IS 'Identifiant unique de l''utilisateur';
COMMENT ON COLUMN action_history.action_type IS 'Type d''action (ex: recette.created, inventaire.updated)';
COMMENT ON COLUMN action_history.entity_type IS 'Type d''entité concernée (recette, inventaire, etc.)';
COMMENT ON COLUMN action_history.entity_id IS 'ID de l''entité concernée';
COMMENT ON COLUMN action_history.details IS 'Métadonnées additionnelles en JSON';
COMMENT ON COLUMN action_history.old_value IS 'Valeur avant modification (pour restauration)';
COMMENT ON COLUMN action_history.new_value IS 'Valeur après modification';
-- ┌─────────────────────────────────────────────────────────────────┐
-- │ RLS (Row Level Security)                                       │
-- └─────────────────────────────────────────────────────────────────┘
-- Activer RLS
ALTER TABLE action_history ENABLE ROW LEVEL SECURITY;
-- Politique: les utilisateurs peuvent voir leur propre historique
CREATE POLICY action_history_select_own ON action_history FOR
SELECT USING (true);
-- Lecture publique pour l'admin/dashboard
-- Politique: insertion autorisée pour tous (l'app gère l'authentification)
CREATE POLICY action_history_insert ON action_history FOR
INSERT WITH CHECK (true);
-- ═══════════════════════════════════════════════════════════════════════════════
-- FIN Migration 022
-- ═══════════════════════════════════════════════════════════════════════════════
