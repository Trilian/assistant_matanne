-- ============================================================================
-- MIGRATIONS SUPABASE - Inventaire Module
-- ============================================================================
-- Lancer ces migrations dans l'ordre sur votre base Supabase
-- SQL Editor -> Créer une nouvelle requête -> Copier/coller -> Run
-- 
-- ⚠️ IMPORTANT: Faire un backup AVANT de lancer!
-- ============================================================================


-- ============================================================================
-- MIGRATION 004: Créer la table historique_inventaire
-- ============================================================================
-- Description: Ajoute le tracking des modifications d'articles
-- Status: À lancer en PREMIER

CREATE TABLE IF NOT EXISTS historique_inventaire (
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
    date_modification TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilisateur VARCHAR(100),
    notes TEXT,
    CONSTRAINT fk_historique_article FOREIGN KEY (article_id) 
        REFERENCES inventaire(id) ON DELETE CASCADE,
    CONSTRAINT fk_historique_ingredient FOREIGN KEY (ingredient_id) 
        REFERENCES ingredients(id) ON DELETE CASCADE
);

-- Créer les indexes pour les performances
CREATE INDEX IF NOT EXISTS idx_historique_article_id 
    ON historique_inventaire(article_id);

CREATE INDEX IF NOT EXISTS idx_historique_ingredient_id 
    ON historique_inventaire(ingredient_id);

CREATE INDEX IF NOT EXISTS idx_historique_type_modification 
    ON historique_inventaire(type_modification);

CREATE INDEX IF NOT EXISTS idx_historique_date_modification 
    ON historique_inventaire(date_modification);

-- Rendre la table accessible via RLS si nécessaire (optionnel)
ALTER TABLE historique_inventaire ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- MIGRATION 005: Ajouter les champs photos à la table inventaire
-- ============================================================================
-- Description: Support des photos pour les articles
-- Status: À lancer en DEUXIÈME (après migration 004)

ALTER TABLE inventaire
ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS photo_filename VARCHAR(200),
ADD COLUMN IF NOT EXISTS photo_uploaded_at TIMESTAMP;

-- Créer un index sur les photos (optionnel, pour les requêtes)
CREATE INDEX IF NOT EXISTS idx_inventaire_photo_url 
    ON inventaire(photo_url) WHERE photo_url IS NOT NULL;

-- ============================================================================
-- VÉRIFICATION - Exécuter après les migrations
-- ============================================================================
-- Vérifier que les tables sont bien créées:

-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' AND table_name IN ('historique_inventaire', 'inventaire');

-- ============================================================================
-- NOTES:
-- ============================================================================
-- ✅ Si vous avez déjà historique_inventaire: Pas de problème, les IF NOT EXISTS empêchent les erreurs
-- ✅ Les indexes améliorent les requêtes de filtrage et de recherche
-- ✅ ON DELETE CASCADE supprime les historiques si un article est supprimé
-- ✅ RLS peut être configuré selon votre politique de sécurité

-- Pour ANNULER (si besoin):
-- DROP TABLE IF EXISTS historique_inventaire CASCADE;
-- ALTER TABLE inventaire 
--     DROP COLUMN IF EXISTS photo_url,
--     DROP COLUMN IF EXISTS photo_filename, 
--     DROP COLUMN IF EXISTS photo_uploaded_at;
