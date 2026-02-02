-- Migration 017: Colonnes manquantes pour maison refonte
-- 1. photos_url pour garden_zones
-- 2. integrer_planning + autres pour maintenance_tasks

-- ═══════════════════════════════════════════════════════════
-- GARDEN_ZONES: Ajout colonne photos
-- ═══════════════════════════════════════════════════════════

ALTER TABLE garden_zones
ADD COLUMN IF NOT EXISTS photos_url TEXT[];

COMMENT ON COLUMN garden_zones.photos_url IS 'URLs photos avant/après au format ["avant:url1", "apres:url2"]';


-- ═══════════════════════════════════════════════════════════
-- MAINTENANCE_TASKS: Ajout colonnes manquantes
-- ═══════════════════════════════════════════════════════════

-- Colonne intégration planning (pour afficher dans calendrier unifié)
ALTER TABLE maintenance_tasks
ADD COLUMN IF NOT EXISTS integrer_planning BOOLEAN DEFAULT FALSE;

-- Colonne durée estimée en minutes
ALTER TABLE maintenance_tasks
ADD COLUMN IF NOT EXISTS duree_minutes INTEGER DEFAULT 30;

-- Colonne responsable (anne, mathieu, tous)
ALTER TABLE maintenance_tasks
ADD COLUMN IF NOT EXISTS responsable VARCHAR(50);

-- Colonne pièce concernée
ALTER TABLE maintenance_tasks
ADD COLUMN IF NOT EXISTS piece VARCHAR(50);

-- Colonne notes
ALTER TABLE maintenance_tasks
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Index sur prochaine_fois pour requêtes alertes
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_prochaine_fois 
ON maintenance_tasks(prochaine_fois);

-- Index sur fait pour filtrage rapide
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_fait 
ON maintenance_tasks(fait);

COMMENT ON COLUMN maintenance_tasks.integrer_planning IS 'Si true, apparaît dans le calendrier unifié';
COMMENT ON COLUMN maintenance_tasks.duree_minutes IS 'Durée estimée pour planification';
COMMENT ON COLUMN maintenance_tasks.responsable IS 'anne, mathieu, ou tous';
