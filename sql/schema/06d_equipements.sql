-- ============================================================================
-- ASSISTANT MATANNE — Maison : Equipements & Travaux
-- ============================================================================
-- Contient : meubles, stocks, pièces, objets, artisans, devis, diagnostics
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meubles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    piece VARCHAR(50) NOT NULL,
    categorie VARCHAR(100),
    prix_estime NUMERIC(10, 2),
    prix_max NUMERIC(10, 2),
    prix_reel NUMERIC(10, 2),
    statut VARCHAR(20) NOT NULL DEFAULT 'souhaite',
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    magasin VARCHAR(200),
    url VARCHAR(500),
    reference VARCHAR(100),
    largeur_cm INTEGER,
    hauteur_cm INTEGER,
    profondeur_cm INTEGER,
    date_souhait DATE NOT NULL DEFAULT CURRENT_DATE,
    date_achat DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_furniture_piece ON meubles(piece);
CREATE INDEX IF NOT EXISTS ix_furniture_statut ON meubles(statut);
CREATE INDEX IF NOT EXISTS ix_furniture_priorite ON meubles(priorite);
CREATE INDEX IF NOT EXISTS ix_furniture_date_achat ON meubles(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stocks_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(100) NOT NULL,
    quantite INTEGER NOT NULL DEFAULT 0,
    unite VARCHAR(20) NOT NULL DEFAULT 'unité',
    seuil_alerte INTEGER NOT NULL DEFAULT 1,
    emplacement VARCHAR(200),
    prix_unitaire NUMERIC(10, 2),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_house_stocks_categorie ON stocks_maison(categorie);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pieces_maison (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    etage INTEGER DEFAULT 0,
    superficie_m2 NUMERIC(6, 2),
    type_piece VARCHAR(50),
    description TEXT,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pieces_maison_type ON pieces_maison(type_piece);
-- ============================================================================
-- PARTIE 4 : TABLES AVEC DÉPENDANCES FK
-- ============================================================================


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS objets_maison (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    categorie VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'fonctionne',
    priorite_remplacement VARCHAR(20),
    date_achat DATE,
    duree_garantie_mois INTEGER,
    prix_achat NUMERIC(10, 2),
    prix_remplacement_estime NUMERIC(10, 2),
    marque VARCHAR(100),
    modele VARCHAR(100),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_objets_maison_piece FOREIGN KEY (piece_id) REFERENCES pieces_maison(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_objets_maison_piece ON objets_maison(piece_id);
CREATE INDEX IF NOT EXISTS idx_objets_maison_categorie ON objets_maison(categorie);
CREATE INDEX IF NOT EXISTS idx_objets_maison_statut ON objets_maison(statut);
CREATE INDEX IF NOT EXISTS idx_objets_maison_date_achat ON objets_maison(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions_travail (
    id SERIAL PRIMARY KEY,
    type_activite VARCHAR(50) NOT NULL,
    zone_jardin_id INTEGER,
    piece_id INTEGER,
    description TEXT,
    debut TIMESTAMP NOT NULL,
    fin TIMESTAMP,
    duree_minutes INTEGER,
    notes TEXT,
    difficulte INTEGER,
    satisfaction INTEGER,
    cree_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ck_sessions_duree_positive CHECK (
        duree_minutes IS NULL
        OR duree_minutes >= 0
    ),
    CONSTRAINT ck_difficulte_range CHECK (
        difficulte IS NULL
        OR (
            difficulte >= 1
            AND difficulte <= 5
        )
    ),
    CONSTRAINT ck_satisfaction_range CHECK (
        satisfaction IS NULL
        OR (
            satisfaction >= 1
            AND satisfaction <= 5
        )
    )
);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type ON sessions_travail(type_activite);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_zone ON sessions_travail(zone_jardin_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_piece ON sessions_travail(piece_id);
CREATE INDEX IF NOT EXISTS idx_sessions_travail_type_debut ON sessions_travail(type_activite, debut);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS versions_pieces (
    id SERIAL PRIMARY KEY,
    piece_id INTEGER NOT NULL REFERENCES pieces_maison(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    type_modification VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    date_modification DATE NOT NULL,
    cout_total NUMERIC(10, 2),
    photo_avant_url VARCHAR(500),
    photo_apres_url VARCHAR(500),
    cree_le TIMESTAMP DEFAULT NOW(),
    cree_par VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece ON versions_pieces(piece_id);
CREATE INDEX IF NOT EXISTS idx_versions_pieces_piece_version ON versions_pieces(piece_id, version);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS couts_travaux (
    id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL,
    categorie VARCHAR(50) NOT NULL,
    libelle VARCHAR(200) NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    fournisseur VARCHAR(200),
    facture_ref VARCHAR(100),
    date_paiement DATE,
    cree_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_couts_travaux_version FOREIGN KEY (version_id) REFERENCES versions_pieces(id) ON DELETE CASCADE,
    CONSTRAINT ck_cout_montant_positif CHECK (montant >= 0)
);
CREATE INDEX IF NOT EXISTS idx_couts_travaux_version ON couts_travaux(version_id);


-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS logs_statut_objets (
    id SERIAL PRIMARY KEY,
    objet_id INTEGER NOT NULL,
    ancien_statut VARCHAR(50),
    nouveau_statut VARCHAR(50) NOT NULL,
    raison TEXT,
    prix_estime NUMERIC(10, 2),
    priorite VARCHAR(20),
    ajoute_courses BOOLEAN DEFAULT FALSE,
    ajoute_budget BOOLEAN DEFAULT FALSE,
    date_changement TIMESTAMP DEFAULT NOW(),
    change_par VARCHAR(100)
);
CREATE INDEX IF NOT EXISTS idx_logs_statut_objet ON logs_statut_objets(objet_id);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS ix_interventions_artisans_date ON interventions_artisans(date_intervention);


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS ix_articles_cellier_date_achat ON articles_cellier(date_achat);


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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


-- ─────────────────────────────────────────────────────────────────────────────
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
CREATE INDEX IF NOT EXISTS ix_devis_date_validite ON devis_comparatifs(date_validite)
    WHERE date_validite IS NOT NULL;


-- ─────────────────────────────────────────────────────────────────────────────
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


