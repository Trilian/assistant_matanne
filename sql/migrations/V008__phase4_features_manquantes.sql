-- V008 — Phase 4 : Features manquantes (stubs → implémentation)
-- Date : 31 mars 2026
-- Actions :
--   1. Table minuteur_sessions (persistance minuteur)
--   2. Aucune action pour batch_cooking_congelation et ia_suggestions_historique
--      (déjà créées dans INIT_COMPLET via Phase 3)

BEGIN;

-- ═══════════════════════════════════════════════════════════
-- 1. TABLE MINUTEUR_SESSIONS
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS minuteur_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    label VARCHAR(200) NOT NULL,
    duree_secondes INTEGER NOT NULL CHECK (duree_secondes > 0),
    recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL,
    date_debut TIMESTAMP,
    date_fin TIMESTAMP,
    terminee BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT FALSE,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_minuteur_user_id ON minuteur_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_minuteur_active ON minuteur_sessions(active);
CREATE INDEX IF NOT EXISTS idx_minuteur_cree_le ON minuteur_sessions(cree_le DESC);

-- Trigger modifie_le
CREATE TRIGGER trg_minuteur_sessions_modifie_le
    BEFORE UPDATE ON minuteur_sessions
    FOR EACH ROW
    EXECUTE FUNCTION mettre_a_jour_modifie_le();

-- RLS
ALTER TABLE minuteur_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "minuteur_sessions_user_policy" ON minuteur_sessions
    FOR ALL
    USING (user_id = current_setting('app.current_user_id', true))
    WITH CHECK (user_id = current_setting('app.current_user_id', true));

-- ═══════════════════════════════════════════════════════════
-- 2. ENREGISTREMENT MIGRATION
-- ═══════════════════════════════════════════════════════════

INSERT INTO schema_migrations (version, description, applied_at)
VALUES ('V008', 'Phase 4 : features manquantes (minuteur, congelation DB, IA historique)', NOW())
ON CONFLICT (version) DO NOTHING;

COMMIT;
