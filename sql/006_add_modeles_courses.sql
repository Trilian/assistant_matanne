-- Phase 2: Modèles de courses persistants (Tables pour Supabase PostgreSQL)
-- À exécuter dans l'onglet SQL de Supabase

-- ═══════════════════════════════════════════════════════════
-- TABLE: modeles_courses
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS modeles_courses (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Phase 2: Support multi-user
    utilisateur_id VARCHAR(100),
    
    -- Métadonnées
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW(),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Données articles (JSONB pour flexibilité)
    articles_data JSONB
);

-- Créer les indexes
CREATE INDEX IF NOT EXISTS ix_modeles_courses_nom ON modeles_courses(nom);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_utilisateur_id ON modeles_courses(utilisateur_id);
CREATE INDEX IF NOT EXISTS ix_modeles_courses_actif ON modeles_courses(actif);


-- ═══════════════════════════════════════════════════════════
-- TABLE: articles_modeles
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS articles_modeles (
    id SERIAL PRIMARY KEY,
    modele_id INTEGER NOT NULL,
    ingredient_id INTEGER,
    
    -- Propriétés de l'article
    nom_article VARCHAR(100) NOT NULL,
    quantite FLOAT NOT NULL DEFAULT 1.0,
    unite VARCHAR(20) NOT NULL DEFAULT 'pièce',
    rayon_magasin VARCHAR(100) NOT NULL DEFAULT 'Autre',
    priorite VARCHAR(20) NOT NULL DEFAULT 'moyenne',
    notes TEXT,
    
    -- Tri/Ordre
    ordre INTEGER NOT NULL DEFAULT 0,
    
    -- Métadonnées
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Contraintes
    CONSTRAINT fk_articles_modeles_modele_id 
        FOREIGN KEY (modele_id) 
        REFERENCES modeles_courses(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_articles_modeles_ingredient_id 
        FOREIGN KEY (ingredient_id) 
        REFERENCES ingredients(id) 
        ON DELETE SET NULL,
    
    CONSTRAINT ck_article_modele_quantite_positive 
        CHECK (quantite > 0),
    
    CONSTRAINT ck_article_modele_priorite_valide 
        CHECK (priorite IN ('haute', 'moyenne', 'basse'))
);

-- Créer les indexes
CREATE INDEX IF NOT EXISTS ix_articles_modeles_modele_id ON articles_modeles(modele_id);
CREATE INDEX IF NOT EXISTS ix_articles_modeles_ingredient_id ON articles_modeles(ingredient_id);


-- ═══════════════════════════════════════════════════════════
-- DONNÉES DE DÉMO (optionnel)
-- ═══════════════════════════════════════════════════════════

-- Insérer un modèle de démo si la table est vide
INSERT INTO modeles_courses (nom, description, utilisateur_id, actif)
VALUES (
    '🏠 Courses semaine',
    'Template standard pour les courses hebdomadaires',
    NULL,
    TRUE
)
ON CONFLICT DO NOTHING;

-- Récupérer l'ID du modèle (si inséré)
DO $$
DECLARE
    v_modele_id INT;
BEGIN
    SELECT id INTO v_modele_id 
    FROM modeles_courses 
    WHERE nom = '🏠 Courses semaine' 
    LIMIT 1;
    
    -- Insérer articles de démo si le modèle existe et n'a pas d'articles
    IF v_modele_id IS NOT NULL THEN
        INSERT INTO articles_modeles (
            modele_id, nom_article, quantite, unite, 
            rayon_magasin, priorite, ordre
        )
        SELECT 
            v_modele_id, nom_article, quantite, unite,
            rayon_magasin, priorite, ordre
        FROM (
            VALUES
                ('Tomates', 2.0, 'kg', 'Fruits & Légumes', 'haute', 0),
                ('Fromage blanc', 1.0, 'pot', 'Laiterie', 'haute', 1),
                ('Pain complet', 1.0, 'pièce', 'Boulangerie', 'haute', 2),
                ('Huile d''olive', 1.0, 'litre', 'Épicerie', 'moyenne', 3)
        ) AS items(nom_article, quantite, unite, rayon_magasin, priorite, ordre)
        WHERE NOT EXISTS (
            SELECT 1 FROM articles_modeles WHERE modele_id = v_modele_id
        );
    END IF;
END $$;


-- ═══════════════════════════════════════════════════════════
-- VÉRIFICATION
-- ═══════════════════════════════════════════════════════════

-- Vérifier que les tables ont bien été créées
SELECT 
    table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('modeles_courses', 'articles_modeles')
ORDER BY table_name;

-- Vérifier les données de démo
SELECT m.nom, COUNT(a.id) as nb_articles
FROM modeles_courses m
LEFT JOIN articles_modeles a ON m.id = a.modele_id
GROUP BY m.id, m.nom;
