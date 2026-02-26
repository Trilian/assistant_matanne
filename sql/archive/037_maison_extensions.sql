-- ═══════════════════════════════════════════════════════════
-- Migration: Nouvelles fonctionnalités Maison
-- Date: 2026-02-26
-- Description: Ajoute 14 nouvelles tables pour les fonctionnalités maison:
--   - Contrats, Artisans, Garanties/SAV
--   - Cellier, Diagnostics, Estimations immobilières
--   - Checklists vacances, Traitements nuisibles
--   - Devis comparatifs, Entretiens saisonniers, Relevés compteurs
-- ═══════════════════════════════════════════════════════════

-- ─── CONTRATS MAISON ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS contrats_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_contrat VARCHAR(50) NOT NULL,
    fournisseur VARCHAR(200) NOT NULL,
    numero_contrat VARCHAR(100),
    numero_client VARCHAR(100),
    date_debut DATE NOT NULL,
    date_fin DATE,
    date_renouvellement DATE,
    duree_engagement_mois INTEGER,
    tacite_reconduction BOOLEAN DEFAULT TRUE,
    preavis_resiliation_jours INTEGER,
    date_limite_resiliation DATE,
    montant_mensuel NUMERIC(10, 2),
    montant_annuel NUMERIC(10, 2),
    telephone VARCHAR(20),
    email VARCHAR(200),
    espace_client_url VARCHAR(500),
    statut VARCHAR(30) DEFAULT 'actif',
    alerte_jours_avant INTEGER DEFAULT 30,
    alerte_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    document_path VARCHAR(500),
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_contrats_maison_type ON contrats_maison(type_contrat);
CREATE INDEX IF NOT EXISTS ix_contrats_maison_statut ON contrats_maison(statut);
CREATE INDEX IF NOT EXISTS ix_contrats_maison_renouvellement ON contrats_maison(date_renouvellement);

-- ─── ARTISANS ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS artisans (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    entreprise VARCHAR(200),
    metier VARCHAR(50) NOT NULL,
    specialite VARCHAR(200),
    telephone VARCHAR(20),
    telephone2 VARCHAR(20),
    email VARCHAR(200),
    adresse TEXT,
    zone_intervention VARCHAR(200),
    note INTEGER,
    recommande BOOLEAN DEFAULT TRUE,
    site_web VARCHAR(500),
    siret VARCHAR(20),
    assurance_decennale BOOLEAN DEFAULT FALSE,
    qualifications TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_artisans_metier ON artisans(metier);

-- ─── INTERVENTIONS ARTISANS ──────────────────────────────
CREATE TABLE IF NOT EXISTS interventions_artisans (
    id SERIAL PRIMARY KEY,
    artisan_id INTEGER NOT NULL REFERENCES artisans(id) ON DELETE CASCADE,
    date_intervention DATE NOT NULL,
    description TEXT NOT NULL,
    piece VARCHAR(50),
    montant_devis NUMERIC(10, 2),
    montant_facture NUMERIC(10, 2),
    paye BOOLEAN DEFAULT FALSE,
    satisfaction INTEGER,
    commentaire TEXT,
    facture_path VARCHAR(500),
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_interventions_artisans_artisan ON interventions_artisans(artisan_id);

-- ─── GARANTIES ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS garanties (
    id SERIAL PRIMARY KEY,
    nom_appareil VARCHAR(200) NOT NULL,
    marque VARCHAR(100),
    modele VARCHAR(100),
    numero_serie VARCHAR(100),
    piece VARCHAR(50),
    date_achat DATE NOT NULL,
    lieu_achat VARCHAR(200),
    prix_achat NUMERIC(10, 2),
    preuve_achat_path VARCHAR(500),
    duree_garantie_mois INTEGER DEFAULT 24,
    date_fin_garantie DATE NOT NULL,
    garantie_etendue BOOLEAN DEFAULT FALSE,
    date_fin_garantie_etendue DATE,
    statut VARCHAR(20) DEFAULT 'active',
    alerte_jours_avant INTEGER DEFAULT 30,
    alerte_active BOOLEAN DEFAULT TRUE,
    cout_remplacement NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_garanties_piece ON garanties(piece);
CREATE INDEX IF NOT EXISTS ix_garanties_fin ON garanties(date_fin_garantie);
CREATE INDEX IF NOT EXISTS ix_garanties_statut ON garanties(statut);

-- ─── INCIDENTS SAV ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS incidents_sav (
    id SERIAL PRIMARY KEY,
    garantie_id INTEGER NOT NULL REFERENCES garanties(id) ON DELETE CASCADE,
    date_incident DATE NOT NULL,
    description TEXT NOT NULL,
    sous_garantie BOOLEAN DEFAULT TRUE,
    date_resolution DATE,
    reparateur VARCHAR(200),
    artisan_id INTEGER REFERENCES artisans(id),
    cout_reparation NUMERIC(10, 2),
    pris_en_charge BOOLEAN DEFAULT FALSE,
    statut VARCHAR(20) DEFAULT 'ouvert',
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_incidents_sav_garantie ON incidents_sav(garantie_id);
CREATE INDEX IF NOT EXISTS ix_incidents_sav_statut ON incidents_sav(statut);

-- ─── ARTICLES CELLIER ────────────────────────────────────
CREATE TABLE IF NOT EXISTS articles_cellier (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    sous_categorie VARCHAR(100),
    marque VARCHAR(100),
    code_barres VARCHAR(50),
    quantite INTEGER DEFAULT 1,
    unite VARCHAR(20) DEFAULT 'unité',
    seuil_alerte INTEGER DEFAULT 1,
    date_achat DATE,
    dlc DATE,
    dluo DATE,
    emplacement VARCHAR(100),
    prix_unitaire NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_articles_cellier_categorie ON articles_cellier(categorie);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_code_barres ON articles_cellier(code_barres);
CREATE INDEX IF NOT EXISTS ix_articles_cellier_dlc ON articles_cellier(dlc);

-- ─── DIAGNOSTICS MAISON ─────────────────────────────────
CREATE TABLE IF NOT EXISTS diagnostics_maison (
    id SERIAL PRIMARY KEY,
    type_diagnostic VARCHAR(50) NOT NULL,
    resultat VARCHAR(100),
    resultat_detail TEXT,
    diagnostiqueur VARCHAR(200),
    numero_certification VARCHAR(100),
    date_realisation DATE NOT NULL,
    date_validite DATE,
    duree_validite_ans INTEGER,
    score_energie VARCHAR(5),
    score_ges VARCHAR(5),
    consommation_kwh_m2 FLOAT,
    emission_co2_m2 FLOAT,
    surface_m2 FLOAT,
    document_path VARCHAR(500),
    alerte_active BOOLEAN DEFAULT TRUE,
    alerte_jours_avant INTEGER DEFAULT 60,
    recommandations TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_diagnostics_type ON diagnostics_maison(type_diagnostic);
CREATE INDEX IF NOT EXISTS ix_diagnostics_validite ON diagnostics_maison(date_validite);

-- ─── ESTIMATIONS IMMOBILIÈRES ────────────────────────────
CREATE TABLE IF NOT EXISTS estimations_immobilieres (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    date_estimation DATE NOT NULL,
    valeur_basse NUMERIC(12, 2),
    valeur_moyenne NUMERIC(12, 2) NOT NULL,
    valeur_haute NUMERIC(12, 2),
    prix_m2 NUMERIC(10, 2),
    surface_m2 FLOAT,
    nb_pieces INTEGER,
    code_postal VARCHAR(10),
    commune VARCHAR(100),
    nb_transactions_comparees INTEGER,
    prix_m2_quartier NUMERIC(10, 2),
    evolution_annuelle_pct FLOAT,
    investissement_travaux NUMERIC(12, 2),
    plus_value_estimee NUMERIC(12, 2),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ─── CHECKLISTS VACANCES ─────────────────────────────────
CREATE TABLE IF NOT EXISTS checklists_vacances (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_voyage VARCHAR(50) NOT NULL,
    destination VARCHAR(200),
    duree_jours INTEGER,
    date_depart DATE,
    date_retour DATE,
    terminee BOOLEAN DEFAULT FALSE,
    archivee BOOLEAN DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_checklists_type_voyage ON checklists_vacances(type_voyage);

-- ─── ITEMS CHECKLIST ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS items_checklist (
    id SERIAL PRIMARY KEY,
    checklist_id INTEGER NOT NULL REFERENCES checklists_vacances(id) ON DELETE CASCADE,
    libelle VARCHAR(300) NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    ordre INTEGER DEFAULT 0,
    fait BOOLEAN DEFAULT FALSE,
    responsable VARCHAR(50),
    quand VARCHAR(20),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_items_checklist_checklist ON items_checklist(checklist_id);

-- ─── TRAITEMENTS NUISIBLES ──────────────────────────────
CREATE TABLE IF NOT EXISTS traitements_nuisibles (
    id SERIAL PRIMARY KEY,
    type_nuisible VARCHAR(50) NOT NULL,
    zone VARCHAR(100),
    est_preventif BOOLEAN DEFAULT FALSE,
    produit VARCHAR(200),
    methode VARCHAR(200),
    est_bio BOOLEAN DEFAULT FALSE,
    date_traitement DATE NOT NULL,
    date_prochain_traitement DATE,
    frequence_jours INTEGER,
    efficacite INTEGER,
    probleme_resolu BOOLEAN DEFAULT FALSE,
    fait_par VARCHAR(100),
    artisan_id INTEGER REFERENCES artisans(id),
    cout NUMERIC(10, 2),
    fiche_securite TEXT,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_traitements_type ON traitements_nuisibles(type_nuisible);
CREATE INDEX IF NOT EXISTS ix_traitements_prochain ON traitements_nuisibles(date_prochain_traitement);

-- ─── DEVIS COMPARATIFS ───────────────────────────────────
CREATE TABLE IF NOT EXISTS devis_comparatifs (
    id SERIAL PRIMARY KEY,
    projet_id INTEGER REFERENCES projets(id),
    artisan_id INTEGER REFERENCES artisans(id),
    reference VARCHAR(100),
    description TEXT NOT NULL,
    date_demande DATE,
    date_reception DATE,
    date_validite DATE,
    montant_ht NUMERIC(12, 2),
    montant_ttc NUMERIC(12, 2) NOT NULL,
    tva_pct FLOAT,
    delai_travaux_jours INTEGER,
    date_debut_prevue DATE,
    statut VARCHAR(20) DEFAULT 'demande',
    choisi BOOLEAN DEFAULT FALSE,
    note_globale INTEGER,
    commentaire TEXT,
    document_path VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_devis_projet ON devis_comparatifs(projet_id);
CREATE INDEX IF NOT EXISTS ix_devis_artisan ON devis_comparatifs(artisan_id);
CREATE INDEX IF NOT EXISTS ix_devis_statut ON devis_comparatifs(statut);

-- ─── LIGNES DEVIS ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lignes_devis (
    id SERIAL PRIMARY KEY,
    devis_id INTEGER NOT NULL REFERENCES devis_comparatifs(id) ON DELETE CASCADE,
    description VARCHAR(500) NOT NULL,
    quantite FLOAT DEFAULT 1.0,
    unite VARCHAR(20),
    prix_unitaire_ht NUMERIC(10, 2) NOT NULL,
    montant_ht NUMERIC(10, 2) NOT NULL,
    type_ligne VARCHAR(30) DEFAULT 'fourniture',
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_lignes_devis_devis ON lignes_devis(devis_id);

-- ─── ENTRETIENS SAISONNIERS ─────────────────────────────
CREATE TABLE IF NOT EXISTS entretiens_saisonniers (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    saison VARCHAR(20) NOT NULL,
    mois_recommande INTEGER,
    mois_rappel INTEGER,
    frequence VARCHAR(30) DEFAULT 'annuel',
    fait_cette_annee BOOLEAN DEFAULT FALSE,
    date_derniere_realisation DATE,
    date_prochaine DATE,
    professionnel_requis BOOLEAN DEFAULT FALSE,
    artisan_id INTEGER REFERENCES artisans(id),
    cout_estime NUMERIC(10, 2),
    duree_minutes INTEGER,
    obligatoire BOOLEAN DEFAULT FALSE,
    reglementation TEXT,
    alerte_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_categorie ON entretiens_saisonniers(categorie);
CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_saison ON entretiens_saisonniers(saison);
CREATE INDEX IF NOT EXISTS ix_entretiens_saisonniers_prochaine ON entretiens_saisonniers(date_prochaine);

-- ─── RELEVÉS COMPTEURS ──────────────────────────────────
CREATE TABLE IF NOT EXISTS releves_compteurs (
    id SERIAL PRIMARY KEY,
    type_compteur VARCHAR(30) NOT NULL,
    numero_compteur VARCHAR(50),
    date_releve DATE NOT NULL,
    valeur FLOAT NOT NULL,
    unite VARCHAR(10) DEFAULT 'm³',
    consommation_periode FLOAT,
    nb_jours_periode INTEGER,
    consommation_jour FLOAT,
    objectif_jour FLOAT,
    anomalie_detectee BOOLEAN DEFAULT FALSE,
    commentaire_anomalie TEXT,
    photo_path VARCHAR(500),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_releves_type ON releves_compteurs(type_compteur);
CREATE INDEX IF NOT EXISTS ix_releves_date ON releves_compteurs(date_releve);

-- ═══════════════════════════════════════════════════════════
-- DONNÉES INITIALES: ENTRETIENS SAISONNIERS PRÉDÉFINIS
-- ═══════════════════════════════════════════════════════════

INSERT INTO entretiens_saisonniers (nom, description, categorie, saison, mois_recommande, mois_rappel, frequence, professionnel_requis, obligatoire, cout_estime, duree_minutes) VALUES
-- AUTOMNE
('Entretien chaudière', 'Visite annuelle obligatoire de la chaudière gaz/fioul', 'chauffage', 'automne', 9, 8, 'annuel', TRUE, TRUE, 150.00, 60),
('Ramonage cheminée', 'Ramonage obligatoire des conduits de fumée (1 à 2 fois/an)', 'chauffage', 'automne', 10, 9, 'annuel', TRUE, TRUE, 80.00, 45),
('Purge des radiateurs', 'Purger les radiateurs avant mise en route du chauffage', 'chauffage', 'automne', 10, 9, 'annuel', FALSE, FALSE, 0.00, 30),
('Nettoyage gouttières', 'Retirer les feuilles mortes des gouttières', 'toiture', 'automne', 11, 10, 'semestriel', FALSE, FALSE, 0.00, 60),
('Vérification toiture', 'Contrôle visuel tuiles/ardoises, étanchéité', 'toiture', 'automne', 10, 9, 'annuel', FALSE, FALSE, 0.00, 30),
('Isolation fenêtres', 'Vérifier joints fenêtres, calfeutrage si nécessaire', 'isolation', 'automne', 10, 9, 'annuel', FALSE, FALSE, 20.00, 60),
('Rentrer plantes fragiles', 'Mettre à l''abri les plantes gélives', 'jardin', 'automne', 10, 9, 'annuel', FALSE, FALSE, 0.00, 30),
('Préparer la tondeuse (hivernage)', 'Vidanger, nettoyer, ranger la tondeuse pour l''hiver', 'jardin', 'automne', 11, 10, 'annuel', FALSE, FALSE, 0.00, 45),
-- HIVER
('Vérification détecteurs fumée', 'Tester les détecteurs, changer les piles si besoin', 'securite', 'hiver', 1, 12, 'semestriel', FALSE, TRUE, 10.00, 15),
('Contrôle VMC', 'Nettoyage bouches VMC et vérification fonctionnement', 'ventilation', 'hiver', 1, 12, 'annuel', FALSE, FALSE, 0.00, 30),
('Couper eau extérieure', 'Fermer les robinets extérieurs et purger pour éviter le gel', 'plomberie', 'hiver', 12, 11, 'annuel', FALSE, FALSE, 0.00, 15),
('Vérifier isolation combles', 'Contrôle visuel isolation toiture/combles', 'isolation', 'hiver', 1, 12, 'annuel', FALSE, FALSE, 0.00, 30),
-- PRINTEMPS
('Entretien climatisation', 'Nettoyage filtres et vérification avant été', 'climatisation', 'printemps', 4, 3, 'annuel', FALSE, FALSE, 0.00, 30),
('Nettoyage terrasse', 'Nettoyage haute pression terrasse, dalles, mobilier', 'exterieur', 'printemps', 4, 3, 'annuel', FALSE, FALSE, 0.00, 120),
('Révision tondeuse', 'Remise en service tondeuse, affûtage lame, huile', 'jardin', 'printemps', 3, 2, 'annuel', FALSE, FALSE, 15.00, 30),
('Vernissage/traitement bois extérieur', 'Traitement mobilier jardin, clôtures, portail bois', 'exterieur', 'printemps', 4, 3, 'annuel', FALSE, FALSE, 50.00, 180),
('Vérification étanchéité toiture', 'Post-hiver: contrôle fuites après gel/neige', 'toiture', 'printemps', 3, 2, 'annuel', FALSE, FALSE, 0.00, 30),
('Nettoyage gouttières (printemps)', 'Second nettoyage annuel des gouttières', 'toiture', 'printemps', 4, 3, 'semestriel', FALSE, FALSE, 0.00, 60),
('Traitement anti-mousse toiture', 'Application produit anti-mousse sur tuiles', 'toiture', 'printemps', 4, 3, 'annuel', FALSE, FALSE, 40.00, 120),
('Remettre eau extérieure', 'Réouvrir robinets extérieurs après risque gel', 'plomberie', 'printemps', 3, 2, 'annuel', FALSE, FALSE, 0.00, 10),
-- ÉTÉ
('Entretien portail automatique', 'Graissage, vérification cellules, télécommandes', 'exterieur', 'ete', 6, 5, 'annuel', FALSE, FALSE, 0.00, 30),
('Contrôle extincteurs', 'Vérification pression, date péremption', 'securite', 'ete', 6, 5, 'annuel', FALSE, FALSE, 0.00, 15),
('Traitement bois charpente', 'Traitement préventif anti-insectes xylophages', 'toiture', 'ete', 7, 6, 'annuel', TRUE, FALSE, 200.00, 240),
('Vérification tableau électrique', 'Contrôle visuel disjoncteurs, test différentiel', 'electricite', 'ete', 6, 5, 'annuel', FALSE, FALSE, 0.00, 20),
('Nettoyage chauffe-eau', 'Vidange partielle et détartrage', 'plomberie', 'ete', 7, 6, 'annuel', FALSE, FALSE, 0.00, 45),
-- TOUTE L'ANNÉE
('Relevé compteurs eau', 'Relevé index compteurs pour suivi consommation', 'plomberie', 'toute_annee', NULL, NULL, 'trimestriel', FALSE, FALSE, 0.00, 5),
('Test alarme', 'Tester le système d''alarme et changer piles détecteurs', 'securite', 'toute_annee', NULL, NULL, 'trimestriel', FALSE, FALSE, 0.00, 15),
('Contrôle pression chaudière', 'Vérifier entre 1 et 1.5 bar', 'chauffage', 'toute_annee', NULL, NULL, 'trimestriel', FALSE, FALSE, 0.00, 5),
('Nettoyage filtres aspirateur', 'Nettoyer/remplacer les filtres', 'menage', 'toute_annee', NULL, NULL, 'trimestriel', FALSE, FALSE, 10.00, 15),
('Vérification joints salle de bain', 'Contrôle moisissures, étanchéité joints silicone', 'plomberie', 'toute_annee', NULL, NULL, 'semestriel', FALSE, FALSE, 15.00, 20)
ON CONFLICT DO NOTHING;
