-- Migration 021: Ajout PlanJardin, ActionPlante et colonnes de position
-- Date: 2026-02-19
-- Description:
--   - Nouvelle table plans_jardin pour les plans 2D du jardin
--   - Nouvelle table actions_plantes pour l'historique des actions sur les plantes
--   - Ajout colonne plan_id dans zones_jardin (FK vers plans_jardin)
--   - Ajout colonnes position_x, position_y dans plantes_jardin

-- ═══════════════════════════════════════════════════════════
-- TABLE: plans_jardin
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS plans_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    largeur NUMERIC(6, 2) NOT NULL,
    hauteur NUMERIC(6, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche par nom
CREATE INDEX IF NOT EXISTS idx_plans_jardin_nom ON plans_jardin(nom);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_plans_jardin_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_plans_jardin_updated_at ON plans_jardin;
CREATE TRIGGER trigger_plans_jardin_updated_at
    BEFORE UPDATE ON plans_jardin
    FOR EACH ROW
    EXECUTE FUNCTION update_plans_jardin_updated_at();

-- Commentaires
COMMENT ON TABLE plans_jardin IS 'Plans 2D du jardin avec dimensions';
COMMENT ON COLUMN plans_jardin.nom IS 'Nom du plan';
COMMENT ON COLUMN plans_jardin.largeur IS 'Largeur en mètres';
COMMENT ON COLUMN plans_jardin.hauteur IS 'Hauteur en mètres';


-- ═══════════════════════════════════════════════════════════
-- ALTER TABLE: zones_jardin - Ajout plan_id
-- ═══════════════════════════════════════════════════════════

-- Ajouter la colonne plan_id si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'zones_jardin' AND column_name = 'plan_id'
    ) THEN
        ALTER TABLE zones_jardin ADD COLUMN plan_id INTEGER;
    END IF;
END $$;

-- Ajouter la contrainte FK
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_zones_jardin_plan_id' AND table_name = 'zones_jardin'
    ) THEN
        ALTER TABLE zones_jardin
        ADD CONSTRAINT fk_zones_jardin_plan_id
        FOREIGN KEY (plan_id) REFERENCES plans_jardin(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Index sur plan_id
CREATE INDEX IF NOT EXISTS idx_zones_jardin_plan_id ON zones_jardin(plan_id);

COMMENT ON COLUMN zones_jardin.plan_id IS 'Référence au plan jardin parent (optionnel)';


-- ═══════════════════════════════════════════════════════════
-- ALTER TABLE: plantes_jardin - Ajout position_x, position_y
-- ═══════════════════════════════════════════════════════════

-- Ajouter position_x si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'plantes_jardin' AND column_name = 'position_x'
    ) THEN
        ALTER TABLE plantes_jardin ADD COLUMN position_x NUMERIC(8, 2);
    END IF;
END $$;

-- Ajouter position_y si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'plantes_jardin' AND column_name = 'position_y'
    ) THEN
        ALTER TABLE plantes_jardin ADD COLUMN position_y NUMERIC(8, 2);
    END IF;
END $$;

COMMENT ON COLUMN plantes_jardin.position_x IS 'Position X sur le plan 2D (en mètres)';
COMMENT ON COLUMN plantes_jardin.position_y IS 'Position Y sur le plan 2D (en mètres)';


-- ═══════════════════════════════════════════════════════════
-- TABLE: actions_plantes
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS actions_plantes (
    id SERIAL PRIMARY KEY,
    plante_id INTEGER NOT NULL,
    type_action VARCHAR(50) NOT NULL,
    date_action DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite NUMERIC(8, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_actions_plantes_plante_id
        FOREIGN KEY (plante_id) REFERENCES plantes_jardin(id) ON DELETE CASCADE
);

-- Index pour recherche
CREATE INDEX IF NOT EXISTS idx_actions_plantes_plante_id ON actions_plantes(plante_id);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_type_action ON actions_plantes(type_action);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_date_action ON actions_plantes(date_action);

-- Commentaires
COMMENT ON TABLE actions_plantes IS 'Historique des actions effectuées sur les plantes (arrosage, récolte, taille, traitement...)';
COMMENT ON COLUMN actions_plantes.plante_id IS 'Plante concernée';
COMMENT ON COLUMN actions_plantes.type_action IS 'Type d''action: arrosage, taille, recolte, traitement, semis, repiquage, etc.';
COMMENT ON COLUMN actions_plantes.date_action IS 'Date de l''action';
COMMENT ON COLUMN actions_plantes.quantite IS 'Quantité (kg pour récoltes, litres pour arrosage, etc.)';
COMMENT ON COLUMN actions_plantes.notes IS 'Notes supplémentaires';


-- ═══════════════════════════════════════════════════════════
-- RLS (Row Level Security) - Si activé sur Supabase
-- ═══════════════════════════════════════════════════════════

-- Activer RLS sur les nouvelles tables
ALTER TABLE plans_jardin ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions_plantes ENABLE ROW LEVEL SECURITY;

-- Politique permissive pour plans_jardin (accès complet pour utilisateurs authentifiés)
DROP POLICY IF EXISTS "plans_jardin_all_access" ON plans_jardin;
CREATE POLICY "plans_jardin_all_access" ON plans_jardin
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Politique permissive pour actions_plantes
DROP POLICY IF EXISTS "actions_plantes_all_access" ON actions_plantes;
CREATE POLICY "actions_plantes_all_access" ON actions_plantes
    FOR ALL
    USING (true)
    WITH CHECK (true);


-- ═══════════════════════════════════════════════════════════
-- VÉRIFICATION
-- ═══════════════════════════════════════════════════════════

-- Afficher les tables créées/modifiées
DO $$
BEGIN
    RAISE NOTICE 'Migration 021 terminée avec succès:';
    RAISE NOTICE '  - Table plans_jardin créée';
    RAISE NOTICE '  - Table actions_plantes créée';
    RAISE NOTICE '  - Colonne plan_id ajoutée à zones_jardin';
    RAISE NOTICE '  - Colonnes position_x, position_y ajoutées à plantes_jardin';
END $$;
