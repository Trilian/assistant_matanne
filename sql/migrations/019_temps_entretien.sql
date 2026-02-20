-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration 019: Tables Temps d'Entretien
-- ═══════════════════════════════════════════════════════════════════════════════
-- Description: Ajoute les tables pour le suivi du temps d'entretien
--              jardin/maison, le versioning des pièces, et le tracking
--              des statuts des objets.
--
-- Tables créées:
--   - pieces_maison        : Pièces de la maison
--   - objets_maison        : Objets/équipements par pièce
--   - zones_jardin         : Zones du jardin
--   - plantes_jardin       : Plantes dans les zones
--   - sessions_travail     : Sessions chronomètre entretien
--   - versions_pieces      : Historique modifications pièces
--   - couts_travaux        : Coûts détaillés des travaux
--   - logs_statut_objets   : Historique statuts objets
-- ═══════════════════════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: pieces_maison                                           │
-- │ Description: Pièces de la maison avec caractéristiques         │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS pieces_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etage INTEGER DEFAULT 0,
    superficie_m2 NUMERIC(6,2),
    type_piece VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index sur le type de pièce
CREATE INDEX IF NOT EXISTS idx_pieces_maison_type ON pieces_maison(type_piece);

-- Trigger pour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pieces_maison_updated_at
    BEFORE UPDATE ON pieces_maison
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE pieces_maison IS 'Pièces de la maison avec leurs caractéristiques';
COMMENT ON COLUMN pieces_maison.etage IS '0=RDC, 1=1er étage, -1=sous-sol, etc.';
COMMENT ON COLUMN pieces_maison.type_piece IS 'chambre, salon, cuisine, sdb, bureau, etc.';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: objets_maison                                           │
-- │ Description: Objets/équipements dans les pièces                │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS objets_maison (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL REFERENCES pieces_maison(id) ON DELETE CASCADE,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'fonctionne',
    priorite_remplacement VARCHAR(20),
    date_achat DATE,
    prix_achat NUMERIC(10,2),
    prix_remplacement_estime NUMERIC(10,2),
    marque VARCHAR(100),
    modele VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_objets_maison_piece ON objets_maison(piece_id);
CREATE INDEX IF NOT EXISTS idx_objets_maison_categorie ON objets_maison(categorie);
CREATE INDEX IF NOT EXISTS idx_objets_maison_statut ON objets_maison(statut);

-- Trigger pour updated_at
CREATE TRIGGER trg_objets_maison_updated_at
    BEFORE UPDATE ON objets_maison
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE objets_maison IS 'Objets et équipements dans les pièces de la maison';
COMMENT ON COLUMN objets_maison.statut IS 'fonctionne, a_reparer, a_changer, a_acheter, en_commande, hors_service, a_donner, archive';
COMMENT ON COLUMN objets_maison.priorite_remplacement IS 'urgente, haute, normale, basse, future';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: zones_jardin                                            │
-- │ Description: Zones du jardin (potager, pelouse, massif...)     │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS zones_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    superficie_m2 NUMERIC(8,2),
    exposition VARCHAR(10),
    type_sol VARCHAR(50),
    arrosage_auto BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_zones_jardin_type ON zones_jardin(type_zone);

-- Trigger pour updated_at
CREATE TRIGGER trg_zones_jardin_updated_at
    BEFORE UPDATE ON zones_jardin
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE zones_jardin IS 'Zones du jardin: potager, pelouse, massif, verger, etc.';
COMMENT ON COLUMN zones_jardin.exposition IS 'N, S, E, O, NE, NO, SE, SO';
COMMENT ON COLUMN zones_jardin.type_zone IS 'potager, pelouse, massif, verger, terrasse, haie, etc.';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: plantes_jardin                                          │
-- │ Description: Plantes dans les zones du jardin                  │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS plantes_jardin (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES zones_jardin(id) ON DELETE CASCADE,
    nom VARCHAR(100) NOT NULL,
    variete VARCHAR(100),
    etat VARCHAR(20) DEFAULT 'bon',
    date_plantation DATE,
    mois_semis VARCHAR(100),    -- JSON array: "[3,4,5]"
    mois_recolte VARCHAR(100),  -- JSON array: "[7,8,9]"
    arrosage VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_plantes_jardin_zone ON plantes_jardin(zone_id);

-- Trigger pour updated_at
CREATE TRIGGER trg_plantes_jardin_updated_at
    BEFORE UPDATE ON plantes_jardin
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE plantes_jardin IS 'Plantes cultivées dans les différentes zones du jardin';
COMMENT ON COLUMN plantes_jardin.etat IS 'excellent, bon, attention, probleme';
COMMENT ON COLUMN plantes_jardin.arrosage IS 'quotidien, hebdomadaire, bi-hebdo, mensuel, etc.';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: sessions_travail                                        │
-- │ Description: Sessions de travail avec chronomètre              │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS sessions_travail (
    id SERIAL PRIMARY KEY,
    -- Type et contexte
    type_activite VARCHAR(50) NOT NULL,
    zone_jardin_id INTEGER,
    piece_id INTEGER,
    description TEXT,
    -- Temps
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP,
    duree_minutes INTEGER,
    -- Feedback
    notes TEXT,
    difficulte INTEGER CHECK (difficulte IS NULL OR (difficulte >= 1 AND difficulte <= 5)),
    satisfaction INTEGER CHECK (satisfaction IS NULL OR (satisfaction >= 1 AND satisfaction <= 5)),
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    -- Contraintes
    CONSTRAINT ck_sessions_duree_positive CHECK (duree_minutes IS NULL OR duree_minutes >= 0)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type ON sessions_travail(type_activite);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_zone ON sessions_travail(zone_jardin_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_piece ON sessions_travail(piece_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type_debut ON sessions_travail(type_activite, debut);

COMMENT ON TABLE sessions_travail IS 'Sessions de travail d''entretien avec chronomètre';
COMMENT ON COLUMN sessions_travail.type_activite IS 'arrosage, tonte, menage_general, bricolage, etc.';
COMMENT ON COLUMN sessions_travail.difficulte IS 'Niveau de difficulté ressenti (1-5)';
COMMENT ON COLUMN sessions_travail.satisfaction IS 'Niveau de satisfaction (1-5)';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: versions_pieces                                         │
-- │ Description: Historique des versions/modifications de pièces   │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS versions_pieces (
    id SERIAL PRIMARY KEY,
    -- Pièce et version
    piece_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    -- Détails
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_modification DATE NOT NULL,
    -- Coûts
    cout_total NUMERIC(10,2),
    -- Photos
    photo_avant_url VARCHAR(500),
    photo_apres_url VARCHAR(500),
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    cree_par VARCHAR(100)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece ON versions_pieces(piece_id);
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece_version ON versions_pieces(piece_id, version);

COMMENT ON TABLE versions_pieces IS 'Historique des modifications de pièces avec versioning';
COMMENT ON COLUMN versions_pieces.type_modification IS 'ajout_meuble, retrait_meuble, renovation, peinture, amenagement, etc.';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: couts_travaux                                           │
-- │ Description: Détails des coûts de travaux par version          │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS couts_travaux (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL REFERENCES versions_pieces(id) ON DELETE CASCADE,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    montant NUMERIC(10,2) NOT NULL CHECK (montant >= 0),
    fournisseur VARCHAR(200),
    facture_ref VARCHAR(100),
    date_paiement DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_couts_travaux_version ON couts_travaux(version_id);

COMMENT ON TABLE couts_travaux IS 'Détails des coûts de travaux (main d''œuvre, matériaux)';
COMMENT ON COLUMN couts_travaux.categorie IS 'main_oeuvre, materiaux, location_materiel, divers';


-- ┌─────────────────────────────────────────────────────────────────┐
-- │ TABLE: logs_statut_objets                                      │
-- │ Description: Historique des changements de statut d'objets     │
-- └─────────────────────────────────────────────────────────────────┘
CREATE TABLE IF NOT EXISTS logs_statut_objets (
    id SERIAL PRIMARY KEY,
    objet_id INTEGER NOT NULL,
    ancien_statut VARCHAR(50),
    nouveau_statut VARCHAR(50) NOT NULL,
    raison TEXT,
    prix_estime NUMERIC(10,2),
    priorite VARCHAR(20),
    ajoute_courses BOOLEAN DEFAULT FALSE,
    ajoute_budget BOOLEAN DEFAULT FALSE,
    date_changement TIMESTAMP DEFAULT NOW(),
    change_par VARCHAR(100)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_logs_statut_objet ON logs_statut_objets(objet_id);

COMMENT ON TABLE logs_statut_objets IS 'Historique des changements de statut des objets';
COMMENT ON COLUMN logs_statut_objets.nouveau_statut IS 'fonctionne, a_reparer, a_changer, a_acheter, en_commande, etc.';
COMMENT ON COLUMN logs_statut_objets.ajoute_courses IS 'Si l''objet a été ajouté à la liste de courses';
COMMENT ON COLUMN logs_statut_objets.ajoute_budget IS 'Si l''objet a été ajouté au budget prévisionnel';


-- ═══════════════════════════════════════════════════════════════════════════════
-- VUES UTILES
-- ═══════════════════════════════════════════════════════════════════════════════

-- Vue: Objets à remplacer avec priorité
CREATE OR REPLACE VIEW v_objets_a_remplacer AS
SELECT
    o.id,
    o.nom,
    o.categorie,
    o.statut,
    o.priorite_remplacement,
    o.prix_remplacement_estime,
    p.nom AS piece,
    p.etage
FROM objets_maison o
JOIN pieces_maison p ON o.piece_id = p.id
WHERE o.statut IN ('a_changer', 'a_acheter', 'a_reparer')
ORDER BY
    CASE o.priorite_remplacement
        WHEN 'urgente' THEN 1
        WHEN 'haute' THEN 2
        WHEN 'normale' THEN 3
        WHEN 'basse' THEN 4
        ELSE 5
    END,
    o.prix_remplacement_estime DESC NULLS LAST;

COMMENT ON VIEW v_objets_a_remplacer IS 'Liste des objets à remplacer triés par priorité';


-- Vue: Temps passé par type d'activité (30 derniers jours)
CREATE OR REPLACE VIEW v_temps_par_activite_30j AS
SELECT
    type_activite,
    COUNT(*) AS nb_sessions,
    COALESCE(SUM(duree_minutes), 0) AS duree_totale_minutes,
    ROUND(AVG(duree_minutes)::numeric, 1) AS duree_moyenne_minutes,
    ROUND(AVG(difficulte)::numeric, 1) AS difficulte_moyenne,
    ROUND(AVG(satisfaction)::numeric, 1) AS satisfaction_moyenne
FROM sessions_travail
WHERE debut >= NOW() - INTERVAL '30 days'
  AND fin IS NOT NULL
GROUP BY type_activite
ORDER BY duree_totale_minutes DESC;

COMMENT ON VIEW v_temps_par_activite_30j IS 'Statistiques temps par activité sur les 30 derniers jours';


-- Vue: Budget travaux par pièce
CREATE OR REPLACE VIEW v_budget_travaux_par_piece AS
SELECT
    p.id AS piece_id,
    p.nom AS piece,
    COUNT(DISTINCT v.id) AS nb_versions,
    COALESCE(SUM(c.montant), 0) AS cout_total,
    COUNT(DISTINCT c.id) AS nb_lignes_cout,
    MAX(v.date_modification) AS derniere_modif
FROM pieces_maison p
LEFT JOIN versions_pieces v ON v.piece_id = p.id
LEFT JOIN couts_travaux c ON c.version_id = v.id
GROUP BY p.id, p.nom
ORDER BY cout_total DESC;

COMMENT ON VIEW v_budget_travaux_par_piece IS 'Budget total des travaux par pièce de la maison';


-- ═══════════════════════════════════════════════════════════════════════════════
-- FONCTIONS HELPER
-- ═══════════════════════════════════════════════════════════════════════════════

-- Fonction: Calculer le temps total par mois
CREATE OR REPLACE FUNCTION fn_temps_entretien_par_mois(
    p_annee INTEGER DEFAULT EXTRACT(YEAR FROM NOW())::INTEGER,
    p_mois INTEGER DEFAULT NULL
)
RETURNS TABLE (
    mois INTEGER,
    annee INTEGER,
    type_activite VARCHAR,
    nb_sessions BIGINT,
    duree_totale_minutes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        EXTRACT(MONTH FROM s.debut)::INTEGER AS mois,
        EXTRACT(YEAR FROM s.debut)::INTEGER AS annee,
        s.type_activite,
        COUNT(*)::BIGINT AS nb_sessions,
        COALESCE(SUM(s.duree_minutes), 0)::BIGINT AS duree_totale_minutes
    FROM sessions_travail s
    WHERE EXTRACT(YEAR FROM s.debut)::INTEGER = p_annee
      AND (p_mois IS NULL OR EXTRACT(MONTH FROM s.debut)::INTEGER = p_mois)
      AND s.fin IS NOT NULL
    GROUP BY
        EXTRACT(MONTH FROM s.debut),
        EXTRACT(YEAR FROM s.debut),
        s.type_activite
    ORDER BY mois, type_activite;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fn_temps_entretien_par_mois IS 'Retourne les statistiques de temps d''entretien par mois et type d''activité';


-- ═══════════════════════════════════════════════════════════════════════════════
-- RLS (Row Level Security) - À activer selon votre politique
-- ═══════════════════════════════════════════════════════════════════════════════

-- ALTER TABLE pieces_maison ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE objets_maison ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE zones_jardin ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE plantes_jardin ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sessions_travail ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE versions_pieces ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE couts_travaux ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE logs_statut_objets ENABLE ROW LEVEL SECURITY;

-- Politique exemple pour accès public (à adapter):
-- CREATE POLICY "Allow all" ON pieces_maison FOR ALL USING (true);


-- ═══════════════════════════════════════════════════════════════════════════════
-- DONNÉES DE TEST (optionnel - à commenter en production)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Pièces exemple
-- INSERT INTO pieces_maison (nom, etage, superficie_m2, type_piece) VALUES
--     ('Salon', 0, 35.5, 'salon'),
--     ('Cuisine', 0, 18.0, 'cuisine'),
--     ('Chambre parentale', 1, 22.0, 'chambre'),
--     ('Chambre Jules', 1, 14.0, 'chambre'),
--     ('Salle de bain', 1, 8.5, 'salle_de_bain'),
--     ('Bureau', 0, 12.0, 'bureau'),
--     ('Garage', 0, 25.0, 'garage');

-- Zones jardin exemple
-- INSERT INTO zones_jardin (nom, type_zone, superficie_m2, exposition) VALUES
--     ('Potager principal', 'potager', 30.0, 'S'),
--     ('Pelouse avant', 'pelouse', 100.0, 'E'),
--     ('Massif roses', 'massif', 15.0, 'S'),
--     ('Terrasse', 'terrasse', 40.0, 'SO'),
--     ('Haie séparative', 'haie', 25.0, 'N');
