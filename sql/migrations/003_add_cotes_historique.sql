-- Migration V003: Ajout table cotes historique pour heatmap (Phase T)
-- Date: 27 mars 2026
-- Description: Ajoute table jeux_cotes_historique pour tracker l'évolution des cotes bookmaker

-- ════════════════════════════════════════════════════════════════
-- TABLE: jeux_cotes_historique
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS jeux_cotes_historique (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES jeux_matchs(id) ON DELETE CASCADE,
    
    -- Timestamp de capture
    date_capture TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Cotes principales (1N2)
    cote_domicile FLOAT,
    cote_nul FLOAT,
    cote_exterieur FLOAT,
    
    -- Cotes over/under (optionnel)
    cote_over_25 FLOAT,
    cote_under_25 FLOAT,
    
    -- Bookmaker source
    bookmaker VARCHAR(50) NOT NULL DEFAULT 'betclic',
    
    -- Timestamps auto
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index pour requêtes par match
CREATE INDEX idx_cotes_historique_match ON jeux_cotes_historique(match_id);

-- Index pour requêtes temporelles
CREATE INDEX idx_cotes_historique_date ON jeux_cotes_historique(date_capture);

-- Index composite match + date pour heatmap
CREATE INDEX idx_cotes_historique_match_date ON jeux_cotes_historique(match_id, date_capture);

-- ════════════════════════════════════════════════════════════════
-- RLS (Row Level Security)
-- ════════════════════════════════════════════════════════════════

ALTER TABLE jeux_cotes_historique ENABLE ROW LEVEL SECURITY;

-- Lecture publique (tous les utilisateurs authentifiés)
CREATE POLICY "Lecture cotes historique pour tous"
ON jeux_cotes_historique FOR SELECT
TO authenticated
USING (true);

-- Insertion réservée service backend
CREATE POLICY "Insertion cotes historique service uniquement"
ON jeux_cotes_historique FOR INSERT
TO authenticated
WITH CHECK (false); -- Bloque INSERT côté client, autorise via service_role

-- ════════════════════════════════════════════════════════════════
-- TRIGGER AUTO-UPDATE
-- ════════════════════════════════════════════════════════════════

CREATE TRIGGER auto_update_cotes_historique
    BEFORE UPDATE ON jeux_cotes_historique
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- ════════════════════════════════════════════════════════════════
-- COMMENTAIRES
-- ════════════════════════════════════════════════════════════════

COMMENT ON TABLE jeux_cotes_historique IS 'Historique captures cotes bookmaker pour heatmap évolution (Phase T)';
COMMENT ON COLUMN jeux_cotes_historique.date_capture IS 'Timestamp de capture des cotes';
COMMENT ON COLUMN jeux_cotes_historique.bookmaker IS 'Source bookmaker (betclic, winamax, etc.)';
