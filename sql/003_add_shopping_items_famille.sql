-- Migration SQL: Ajout de la table shopping_items_famille pour le shopping familial

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE: shopping_items_famille
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS shopping_items_famille (
    id BIGSERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    quantite FLOAT DEFAULT 1.0,
    prix_estime FLOAT DEFAULT 0.0,
    liste VARCHAR(50) DEFAULT 'Nous',
    actif BOOLEAN DEFAULT TRUE,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_achat TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_shopping_items_famille_categorie 
    ON shopping_items_famille(categorie);

CREATE INDEX IF NOT EXISTS idx_shopping_items_famille_liste 
    ON shopping_items_famille(liste);

CREATE INDEX IF NOT EXISTS idx_shopping_items_famille_actif 
    ON shopping_items_famille(actif);

CREATE INDEX IF NOT EXISTS idx_shopping_items_famille_date_ajout 
    ON shopping_items_famille(date_ajout);

-- Vue: Articles à acheter (actifs)
DROP VIEW IF EXISTS v_shopping_items_actifs CASCADE;
CREATE VIEW v_shopping_items_actifs AS
SELECT 
    id,
    titre,
    categorie,
    quantite,
    prix_estime,
    liste,
    date_ajout
FROM shopping_items_famille
WHERE actif = TRUE
ORDER BY date_ajout DESC;

-- Vue: Statistiques par catégorie
DROP VIEW IF EXISTS v_shopping_stats_categorie CASCADE;
CREATE VIEW v_shopping_stats_categorie AS
SELECT 
    categorie,
    COUNT(*) as nb_articles,
    SUM(prix_estime) as prix_total_estime,
    COUNT(CASE WHEN actif = TRUE THEN 1 END) as articles_actifs
FROM shopping_items_famille
GROUP BY categorie;
