-- ============================================================
-- Migration 016: Maison Extended - Meubles, Dépenses, Éco-Tips
-- ============================================================
-- Nouvelles tables pour la refonte Maison:
-- - furniture: Wishlist meubles par pièce avec budget
-- - house_expenses: Dépenses récurrentes (gaz, eau, électricité)
-- - eco_actions: Actions écologiques avec suivi économies
-- - garden_zones: Zones jardin (2600m²) avec état
-- - maintenance_tasks: Tâches entretien planifiées
-- - house_stock: Stock consommables maison
-- ============================================================

-- 1. Table furniture (wishlist meubles)
CREATE TABLE IF NOT EXISTS furniture (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    piece VARCHAR(50),  -- salon, cuisine, chambre_parentale, chambre_jules, etc.
    description TEXT,
    priorite VARCHAR(20) DEFAULT 'normale',  -- urgent, haute, normale, basse, plus_tard
    statut VARCHAR(20) DEFAULT 'souhaite',   -- souhaite, recherche, trouve, commande, achete, annule
    prix_estime DECIMAL(10,2),
    prix_max DECIMAL(10,2),
    prix_reel DECIMAL(10,2),
    magasin VARCHAR(200),
    url TEXT,
    dimensions VARCHAR(100),
    date_achat DATE,
    image_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour filtres par pièce et statut
CREATE INDEX IF NOT EXISTS idx_furniture_piece ON furniture(piece);
CREATE INDEX IF NOT EXISTS idx_furniture_statut ON furniture(statut);
CREATE INDEX IF NOT EXISTS idx_furniture_priorite ON furniture(priorite);


-- 2. Table house_expenses (dépenses maison)
CREATE TABLE IF NOT EXISTS house_expenses (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL,  -- gaz, electricite, eau, internet, loyer, creche, etc.
    montant DECIMAL(10,2) NOT NULL,
    consommation DECIMAL(10,2),  -- kWh pour élec, m³ pour gaz/eau
    mois INTEGER NOT NULL,       -- 1-12
    annee INTEGER NOT NULL,
    date_facture DATE,
    fournisseur VARCHAR(100),
    numero_facture VARCHAR(50),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherches par période
CREATE INDEX IF NOT EXISTS idx_house_expenses_periode ON house_expenses(annee, mois);
CREATE INDEX IF NOT EXISTS idx_house_expenses_categorie ON house_expenses(categorie);

-- Contrainte unicité: une seule entrée par catégorie/mois/année
CREATE UNIQUE INDEX IF NOT EXISTS idx_house_expenses_unique 
    ON house_expenses(categorie, mois, annee);


-- 3. Table eco_actions (actions écologiques)
CREATE TABLE IF NOT EXISTS eco_actions (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_action VARCHAR(50),  -- lavable, energie, eau, dechets, alimentation
    description TEXT,
    economie_mensuelle DECIMAL(10,2),  -- économie estimée €/mois
    cout_initial DECIMAL(10,2),         -- investissement initial
    date_debut DATE,
    actif BOOLEAN DEFAULT true,
    impact_environnemental TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour filtres
CREATE INDEX IF NOT EXISTS idx_eco_actions_type ON eco_actions(type_action);
CREATE INDEX IF NOT EXISTS idx_eco_actions_actif ON eco_actions(actif);


-- 4. Table garden_zones (zones jardin 2600m²)
CREATE TABLE IF NOT EXISTS garden_zones (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    type_zone VARCHAR(50),  -- pelouse, potager, arbres, piscine, terrain_boules, terrasse
    surface_m2 INTEGER,
    etat_note INTEGER DEFAULT 3 CHECK (etat_note BETWEEN 1 AND 5),  -- 1=critique, 5=parfait
    description TEXT,
    objectif TEXT,  -- ce qu'on veut en faire
    prochaine_action TEXT,
    date_derniere_action DATE,
    photos_url TEXT[],  -- array de URLs photos
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour filtres
CREATE INDEX IF NOT EXISTS idx_garden_zones_type ON garden_zones(type_zone);
CREATE INDEX IF NOT EXISTS idx_garden_zones_etat ON garden_zones(etat_note);


-- 5. Table maintenance_tasks (tâches entretien)
CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),  -- vitres, menage, jardin, garage, rangement, etc.
    description TEXT,
    frequence_jours INTEGER,  -- tous les X jours (NULL = ponctuel)
    derniere_fois DATE,
    prochaine_fois DATE,
    responsable VARCHAR(50),  -- anne, mathieu, tous
    priorite VARCHAR(20) DEFAULT 'normale',
    fait BOOLEAN DEFAULT false,
    duree_minutes INTEGER DEFAULT 30,  -- durée estimée pour planning
    piece VARCHAR(50),  -- pour le ménage: salon, cuisine, etc.
    integrer_planning BOOLEAN DEFAULT false,  -- sync avec planning général
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour filtres
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_categorie ON maintenance_tasks(categorie);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_prochaine ON maintenance_tasks(prochaine_fois);
CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_fait ON maintenance_tasks(fait);


-- 6. Table house_stock (stock consommables)
CREATE TABLE IF NOT EXISTS house_stock (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),  -- ampoules, piles, produits_menage, bricolage, etc.
    quantite INTEGER DEFAULT 0,
    seuil_alerte INTEGER DEFAULT 1,
    unite VARCHAR(20),  -- pieces, boites, litres, etc.
    localisation VARCHAR(100),  -- garage, buanderie, etc.
    derniere_verification DATE,
    prix_unitaire DECIMAL(10,2),
    fournisseur VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour filtres
CREATE INDEX IF NOT EXISTS idx_house_stock_categorie ON house_stock(categorie);


-- ============================================================
-- DONNÉES INITIALES - Zones jardin (2600m²)
-- ============================================================

INSERT INTO garden_zones (nom, type_zone, surface_m2, etat_note, description, objectif, prochaine_action, notes) VALUES
-- Pelouses
('Pelouse principale', 'pelouse', 1200, 2, 'Grande pelouse devant et derrière maison', 'Avoir une pelouse verte et entretenue', 'Scarifier et ressemer', 'Herbe jaunie, besoin amélioration terre. Conseil: tondre mulching pour enrichir sol naturellement'),
('Zone libre arrière', 'pelouse', 500, 2, 'Zone non aménagée derrière', 'Espace jeux Jules / détente', 'Tondre régulièrement', 'Potentiel pour balançoire ou bac à sable'),

-- Piscine
('Piscine et terrasse', 'piscine', 100, 3, 'Zone piscine avec terrasse', 'Zone baignade propre et sécurisée', 'Vérifier pH et nettoyer', 'Entretien hebdo en saison'),

-- Potager
('Potager abandonné', 'potager', 50, 1, 'Ancien potager non entretenu', 'Recréer un potager productif', 'Désherber complètement', 'AMÉLIORATION TERRE: 1) Désherber, 2) Apporter compost/fumier, 3) Pailler pour protéger sol'),

-- Arbres décoratifs
('Arbres décoratifs', 'arbres_deco', 150, 2, 'Haies, arbustes, conifères', 'Arbres taillés et esthétiques', 'Tailler haies au printemps', 'Taille légère mars + septembre'),

-- Arbres fruitiers  
('Verger fruitiers', 'arbres_fruitiers', 150, 2, 'Pommiers, poiriers, cerisiers...', 'Récolte fruits chaque année', 'Tailler en février (hors gel)', 'Taille hiver + traitement bouillie bordelaise'),

-- Terrain boules
('Terrain de boules', 'terrain_boules', 50, 1, 'Envahi par les mauvaises herbes', 'Terrain jouable pour pétanque', 'Désherber et aplanir', 'Option: bâche géotextile + sable ou gravier'),

-- Zone compost (pour améliorer la terre!)
('Zone compost', 'compost', 10, 1, 'Pas encore installé', 'Créer du compost pour le potager', 'Acheter ou fabriquer composteur', 'ESSENTIEL pour améliorer la terre! Déchets verts + bruns = or noir du jardinier')
ON CONFLICT DO NOTHING;


-- ============================================================
-- DONNÉES INITIALES - Tâches maintenance + Routine ménage
-- ============================================================

-- Tâches ponctuelles (bordel à ranger)
INSERT INTO maintenance_tasks (nom, categorie, description, frequence_jours, priorite, integrer_planning) VALUES
('Tri des caisses carton', 'rangement', 'Vider et trier les caisses du déménagement', NULL, 'haute', false),
('Ranger le garage', 'garage', 'Organiser les outils et le stockage', NULL, 'haute', false),
('Centraliser les médicaments', 'rangement', 'Regrouper tous les médicaments dans une armoire', NULL, 'urgent', false),
('Repeindre salle de bain', 'travaux', 'La peinture s''écaille', NULL, 'normale', false)
ON CONFLICT DO NOTHING;

-- Routine ménage hebdomadaire (à intégrer au planning)
INSERT INTO maintenance_tasks (nom, categorie, description, frequence_jours, priorite, duree_minutes, piece, integrer_planning) VALUES
-- LUNDI - Salon
('Aspirateur salon', 'menage', 'Aspirer sol et canapé', 7, 'normale', 20, 'salon', true),
('Poussières salon', 'menage', 'Meubles TV, étagères, bibelots', 7, 'normale', 15, 'salon', true),

-- MARDI - Cuisine
('Nettoyage plan de travail', 'menage', 'Dégraisser et désinfecter', 1, 'haute', 10, 'cuisine', true),
('Nettoyage évier cuisine', 'menage', 'Frotter et désinfecter', 3, 'normale', 5, 'cuisine', true),
('Sol cuisine', 'menage', 'Balai + serpillère', 3, 'normale', 15, 'cuisine', true),

-- MERCREDI - Chambres
('Aspirateur chambre parentale', 'menage', 'Sol et sous le lit', 7, 'normale', 15, 'chambre_parentale', true),
('Aspirateur chambre Jules', 'menage', 'Sol et coin jouets', 7, 'normale', 15, 'chambre_jules', true),
('Changer draps', 'menage', 'Lits parents + Jules', 14, 'normale', 20, 'chambre_parentale', true),

-- JEUDI - Salle de bain
('Nettoyage WC', 'menage', 'Cuvette, abattant, sol autour', 3, 'haute', 10, 'salle_de_bain', true),
('Nettoyage douche/baignoire', 'menage', 'Parois, bac, robinetterie', 7, 'normale', 15, 'salle_de_bain', true),
('Lavabo + miroir', 'menage', 'Vasque et miroir salle de bain', 3, 'normale', 10, 'salle_de_bain', true),

-- VENDREDI - Entrée/Couloirs
('Aspirateur entrée', 'menage', 'Entrée et couloirs', 7, 'normale', 10, 'entree', true),
('Poussières meubles entrée', 'menage', 'Meuble chaussures, porte-manteau', 14, 'basse', 10, 'entree', true),

-- SAMEDI - Buanderie/Garage
('Ranger buanderie', 'menage', 'Plier linge, ranger produits', 7, 'normale', 20, 'buanderie', true),

-- Tâches périodiques
('Nettoyer les vitres', 'vitres', 'Toutes les vitres intérieures et extérieures', 90, 'normale', 60, NULL, true),
('Révision chaudière', 'entretien', 'Maintenance annuelle obligatoire', 365, 'haute', 120, NULL, true),
('Nettoyer filtres VMC', 'entretien', 'Nettoyage des filtres de ventilation', 180, 'normale', 30, NULL, true),
('Vérifier détecteurs fumée', 'securite', 'Test des piles et fonctionnement', 180, 'haute', 15, NULL, true),
('Nettoyage frigo', 'menage', 'Vider, nettoyer, réorganiser', 30, 'normale', 30, 'cuisine', true),
('Nettoyage four', 'menage', 'Dégraisser intérieur four', 30, 'normale', 45, 'cuisine', true),
('Nettoyage machine à laver', 'menage', 'Cycle vide + vinaigre', 30, 'normale', 5, 'buanderie', true)
ON CONFLICT DO NOTHING;


-- ============================================================
-- DONNÉES INITIALES - Éco-actions
-- ============================================================

INSERT INTO eco_actions (nom, type_action, description, economie_mensuelle, cout_initial, actif) VALUES
('Chauffage -1°C', 'energie', 'Baisser le chauffage de 1°C = -7% gaz', 30.00, 0, false),
('Essuie-tout lavables', 'lavable', 'Remplacer les rouleaux jetables', 8.00, 25.00, false),
('Réducteur débit douche', 'eau', 'Économiser 50% eau douche', 12.00, 15.00, false),
('Composteur jardin', 'dechets', 'Créer compost pour améliorer terre jardin - déchets verts + bruns = or noir!', 10.00, 50.00, false),
('Tonte mulching', 'dechets', 'Tondre sans ramasser pour enrichir la pelouse naturellement', 5.00, 0, false)
ON CONFLICT DO NOTHING;


-- ============================================================
-- CONSEILS AMÉLIORATION TERRE (dans notes garden_zones)
-- ============================================================
-- Les conseils sont inclus dans les notes des garden_zones ci-dessus.
-- Résumé technique pour améliorer terre pauvre:
-- 
-- 🌱 ÉTAPE 1 - DIAGNOSTIC
-- - Sol argileux: compact, mal drainé
-- - Sol sableux: ne retient pas l'eau
-- - Sol calcaire: bloque certains nutriments
-- 
-- 🌱 ÉTAPE 2 - AMÉLIORATION
-- 1. COMPOST maison (6-12 mois pour un bon compost)
--    - Déchets verts: tontes, épluchures, feuilles
--    - Déchets bruns: carton, branches broyées, paille
--    - Ratio: 2/3 bruns, 1/3 verts
--    
-- 2. FUMIER bien décomposé (automne)
--    - Cheval, vache ou mouton
--    - Épandre et incorporer légèrement
--    
-- 3. PAILLAGE permanent
--    - BRF (bois raméal fragmenté)
--    - Paille, feuilles mortes
--    - Limite évaporation + nourrit le sol
--    
-- 4. ENGRAIS VERTS (hiver)
--    - Moutarde, phacélie, trèfle
--    - Semer en automne, faucher au printemps
--    - Améliore structure + fixe azote
--
-- 🌱 PLANNING AMÉLIORATION PELOUSE 2600m²:
-- - Mars: Scarifier (arracher mousse/feutre)
-- - Avril: Aérer + semer gazon regarnissant
-- - Mai-Sept: Tonte mulching régulière (3-4cm)
-- - Automne: Épandre compost fin (1-2cm)
-- - Hiver: Laisser reposer


-- ============================================================
-- Mise à jour trigger updated_at
-- ============================================================

-- Fonction trigger si elle n'existe pas
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour les nouvelles tables
DROP TRIGGER IF EXISTS update_furniture_updated_at ON furniture;
CREATE TRIGGER update_furniture_updated_at
    BEFORE UPDATE ON furniture
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_house_expenses_updated_at ON house_expenses;
CREATE TRIGGER update_house_expenses_updated_at
    BEFORE UPDATE ON house_expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_eco_actions_updated_at ON eco_actions;
CREATE TRIGGER update_eco_actions_updated_at
    BEFORE UPDATE ON eco_actions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_garden_zones_updated_at ON garden_zones;
CREATE TRIGGER update_garden_zones_updated_at
    BEFORE UPDATE ON garden_zones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_maintenance_tasks_updated_at ON maintenance_tasks;
CREATE TRIGGER update_maintenance_tasks_updated_at
    BEFORE UPDATE ON maintenance_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_house_stock_updated_at ON house_stock;
CREATE TRIGGER update_house_stock_updated_at
    BEFORE UPDATE ON house_stock
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- Vérification
-- ============================================================
-- SELECT 'furniture' as table_name, count(*) FROM furniture
-- UNION ALL SELECT 'house_expenses', count(*) FROM house_expenses
-- UNION ALL SELECT 'eco_actions', count(*) FROM eco_actions
-- UNION ALL SELECT 'garden_zones', count(*) FROM garden_zones
-- UNION ALL SELECT 'maintenance_tasks', count(*) FROM maintenance_tasks
-- UNION ALL SELECT 'house_stock', count(*) FROM house_stock;
