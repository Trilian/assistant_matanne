-- ============================================================================
-- ASSISTANT MATANNE — Tables Maison
-- ============================================================================
-- Contient : projets, routines, jardin, entretien, stocks, pièces,
--            objets, artisans, énergie, maison extensions
-- ============================================================================
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE projets (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'en_cours',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_debut DATE,
    date_fin DATE,
    budget_estime FLOAT,
    budget_reel FLOAT,
    categorie VARCHAR(100),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_projects_statut ON projets(statut);
CREATE INDEX IF NOT EXISTS ix_projects_categorie ON projets(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE routines (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_routine VARCHAR(100) NOT NULL,
    jours JSONB DEFAULT '[]',
    heure_debut VARCHAR(10),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    moment_journee VARCHAR(20) NOT NULL DEFAULT 'flexible',
    jour_semaine INTEGER,
    derniere_completion DATE,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_routines_type ON routines(type_routine);
CREATE INDEX IF NOT EXISTS ix_routines_actif ON routines(actif);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE elements_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    type_plante VARCHAR(100) NOT NULL,
    emplacement VARCHAR(200),
    date_plantation DATE,
    frequence_arrosage VARCHAR(50),
    derniere_action DATE,
    statut VARCHAR(50) NOT NULL DEFAULT 'actif',
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_garden_items_type ON elements_jardin(type_plante);
CREATE INDEX IF NOT EXISTS ix_garden_items_statut ON elements_jardin(statut);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE meubles (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE depenses_maison (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL,
    mois INTEGER NOT NULL,
    annee INTEGER NOT NULL,
    montant NUMERIC(10, 2) NOT NULL,
    consommation FLOAT,
    unite_consommation VARCHAR(20),
    fournisseur VARCHAR(200),
    numero_contrat VARCHAR(100),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_house_mois_valide CHECK (
        mois >= 1
        AND mois <= 12
    ),
    CONSTRAINT ck_house_montant_positif CHECK (montant >= 0),
    CONSTRAINT ck_house_consommation_positive CHECK (
        consommation IS NULL
        OR consommation >= 0
    )
);
CREATE INDEX IF NOT EXISTS ix_house_expenses_categorie ON depenses_maison(categorie);
CREATE INDEX IF NOT EXISTS ix_house_expenses_annee ON depenses_maison(annee);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE actions_ecologiques (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    type_action VARCHAR(50) NOT NULL,
    ancien_produit VARCHAR(200),
    nouveau_produit VARCHAR(200),
    cout_ancien_mensuel NUMERIC(10, 2),
    cout_nouveau_initial NUMERIC(10, 2),
    economie_mensuelle NUMERIC(10, 2),
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_eco_actions_type ON actions_ecologiques(type_action);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_entretien (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    categorie VARCHAR(50) NOT NULL,
    piece VARCHAR(50),
    frequence_jours INTEGER,
    derniere_fois DATE,
    prochaine_fois DATE,
    duree_minutes INTEGER NOT NULL DEFAULT 30,
    responsable VARCHAR(50),
    priorite VARCHAR(20) NOT NULL DEFAULT 'normale',
    fait BOOLEAN NOT NULL DEFAULT FALSE,
    integrer_planning BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_categorie ON taches_entretien(categorie);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_prochaine ON taches_entretien(prochaine_fois);
CREATE INDEX IF NOT EXISTS ix_maintenance_tasks_fait ON taches_entretien(fait);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE stocks_maison (
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
CREATE TABLE plans_jardin (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    largeur NUMERIC(6, 2) NOT NULL,
    hauteur NUMERIC(6, 2) NOT NULL,
    description TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modifie_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_plans_jardin_nom ON plans_jardin(nom);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE pieces_maison (
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
CREATE TABLE taches_projets (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    statut VARCHAR(50) NOT NULL DEFAULT 'à_faire',
    priorite VARCHAR(50) NOT NULL DEFAULT 'moyenne',
    date_echeance DATE,
    assigne_a VARCHAR(200),
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_project_tasks_project FOREIGN KEY (project_id) REFERENCES projets(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_project_tasks_project ON taches_projets(project_id);
CREATE INDEX IF NOT EXISTS ix_project_tasks_statut ON taches_projets(statut);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_routines (
    id SERIAL PRIMARY KEY,
    routine_id INTEGER NOT NULL,
    nom VARCHAR(200) NOT NULL,
    description TEXT,
    ordre INTEGER NOT NULL DEFAULT 1,
    heure_prevue VARCHAR(5),
    fait_le DATE,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_routine_tasks_routine FOREIGN KEY (routine_id) REFERENCES routines(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_routine_tasks_routine ON taches_routines(routine_id);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE journaux_jardin (
    id SERIAL PRIMARY KEY,
    garden_item_id INTEGER,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    action VARCHAR(200) NOT NULL,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_garden_logs_item FOREIGN KEY (garden_item_id) REFERENCES elements_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_garden_logs_item ON journaux_jardin(garden_item_id);
CREATE INDEX IF NOT EXISTS ix_garden_logs_date ON journaux_jardin(date);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE zones_jardin (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER,
    nom VARCHAR(100) NOT NULL,
    type_zone VARCHAR(50) NOT NULL,
    superficie_m2 NUMERIC(8, 2),
    exposition VARCHAR(10),
    type_sol VARCHAR(50),
    arrosage_auto BOOLEAN DEFAULT FALSE,
    description TEXT,
    -- Positions 2D (canvas)
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    largeur_px INTEGER DEFAULT 100,
    hauteur_px INTEGER DEFAULT 100,
    couleur VARCHAR(20) DEFAULT '#4CAF50',
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_zones_jardin_plan_id FOREIGN KEY (plan_id) REFERENCES plans_jardin(id) ON DELETE
    SET NULL
);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_type ON zones_jardin(type_zone);
CREATE INDEX IF NOT EXISTS idx_zones_jardin_plan_id ON zones_jardin(plan_id);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plantes_jardin (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL,
    nom VARCHAR(100) NOT NULL,
    variete VARCHAR(100),
    etat VARCHAR(20) DEFAULT 'bon',
    date_plantation DATE,
    mois_semis VARCHAR(100),
    mois_recolte VARCHAR(100),
    arrosage VARCHAR(50),
    notes TEXT,
    position_x NUMERIC(8, 2),
    position_y NUMERIC(8, 2),
    cree_le TIMESTAMP DEFAULT NOW(),
    modifie_le TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_plantes_jardin_zone FOREIGN KEY (zone_id) REFERENCES zones_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_plantes_jardin_zone ON plantes_jardin(zone_id);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE actions_plantes (
    id SERIAL PRIMARY KEY,
    plante_id INTEGER NOT NULL,
    type_action VARCHAR(50) NOT NULL,
    date_action DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite NUMERIC(8, 2),
    notes TEXT,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_actions_plantes_plante_id FOREIGN KEY (plante_id) REFERENCES plantes_jardin(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_plante_id ON actions_plantes(plante_id);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_type_action ON actions_plantes(type_action);
CREATE INDEX IF NOT EXISTS idx_actions_plantes_date_action ON actions_plantes(date_action);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE objets_maison (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE sessions_travail (
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
CREATE TABLE versions_pieces (
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
CREATE TABLE couts_travaux (
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
CREATE TABLE logs_statut_objets (
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
CREATE TABLE preferences_home (
    id SERIAL PRIMARY KEY,
    max_taches_jour INTEGER DEFAULT 3,
    max_heures_jour DECIMAL(4, 2) DEFAULT 2.0,
    heures_jardin JSONB DEFAULT '[7, 8, 18, 19]',
    heures_menage JSONB DEFAULT '[9, 10, 14, 15]',
    heures_admin JSONB DEFAULT '[20, 21]',
    jours_jardin JSONB DEFAULT '[6, 7]',
    jours_menage JSONB DEFAULT '[6]',
    notification_matin BOOLEAN DEFAULT TRUE,
    heure_briefing INTEGER DEFAULT 7,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE taches_home (
    id SERIAL PRIMARY KEY,
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN ('jardin', 'entretien', 'charges', 'depenses')
    ),
    type_tache VARCHAR(50) NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_min INTEGER DEFAULT 15,
    priorite VARCHAR(20) DEFAULT 'normale' CHECK (
        priorite IN (
            'urgente',
            'haute',
            'normale',
            'basse',
            'optionnelle'
        )
    ),
    date_due DATE,
    date_faite DATE,
    statut VARCHAR(20) DEFAULT 'a_faire' CHECK (
        statut IN (
            'a_faire',
            'en_cours',
            'fait',
            'reporte',
            'annule'
        )
    ),
    generee_auto BOOLEAN DEFAULT FALSE,
    source VARCHAR(50),
    source_id INTEGER,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE
    SET NULL,
        piece_id INTEGER REFERENCES pieces_maison(id) ON DELETE
    SET NULL,
        cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_taches_home_domaine ON taches_home(domaine);
CREATE INDEX IF NOT EXISTS idx_taches_home_statut ON taches_home(statut);
CREATE INDEX IF NOT EXISTS idx_taches_home_date_due ON taches_home(date_due);
CREATE INDEX IF NOT EXISTS idx_taches_home_source ON taches_home(source, source_id);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE stats_home (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN (
            'jardin',
            'entretien',
            'charges',
            'depenses',
            'total'
        )
    ),
    temps_prevu_min INTEGER DEFAULT 0,
    temps_reel_min INTEGER DEFAULT 0,
    taches_prevues INTEGER DEFAULT 0,
    taches_completees INTEGER DEFAULT 0,
    taches_reportees INTEGER DEFAULT 0,
    score_jour INTEGER DEFAULT 0,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, domaine)
);
CREATE INDEX IF NOT EXISTS idx_stats_home_date ON stats_home(date);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE plantes_catalogue (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE,
    nom_latin VARCHAR(150),
    famille VARCHAR(50),
    varietes JSONB DEFAULT '[]',
    mois_semis_interieur JSONB DEFAULT '[]',
    mois_semis_exterieur JSONB DEFAULT '[]',
    mois_plantation JSONB DEFAULT '[]',
    mois_recolte JSONB DEFAULT '[]',
    compagnons_positifs JSONB DEFAULT '[]',
    compagnons_negatifs JSONB DEFAULT '[]',
    espacement_cm INTEGER DEFAULT 30,
    profondeur_semis_cm INTEGER DEFAULT 2,
    jours_germination INTEGER DEFAULT 10,
    jours_jusqu_recolte INTEGER DEFAULT 60,
    arrosage VARCHAR(20) DEFAULT 'regulier' CHECK (
        arrosage IN ('quotidien', 'regulier', 'modere', 'faible')
    ),
    exposition VARCHAR(20) DEFAULT 'soleil' CHECK (
        exposition IN ('soleil', 'mi_ombre', 'ombre')
    ),
    rendement_kg_m2 DECIMAL(4, 2) DEFAULT 2.0,
    besoin_famille_4_kg_an DECIMAL(6, 2),
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plantes_catalogue_famille ON plantes_catalogue(famille);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE recoltes (
    id SERIAL PRIMARY KEY,
    plante_jardin_id INTEGER REFERENCES plantes_jardin(id) ON DELETE CASCADE,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE CASCADE,
    legume VARCHAR(100) NOT NULL,
    date_recolte DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite_kg DECIMAL(6, 2) NOT NULL,
    qualite VARCHAR(20) DEFAULT 'bonne' CHECK (
        qualite IN ('excellente', 'bonne', 'moyenne', 'passable')
    ),
    destination VARCHAR(20) DEFAULT 'frais' CHECK (
        destination IN ('frais', 'conserve', 'congele', 'donne', 'perdu')
    ),
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_recoltes_date ON recoltes(date_recolte);
CREATE INDEX IF NOT EXISTS idx_recoltes_legume ON recoltes(legume);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE objectifs_autonomie (
    id SERIAL PRIMARY KEY,
    legume VARCHAR(100) NOT NULL UNIQUE,
    besoin_kg_an DECIMAL(6, 2) NOT NULL,
    surface_ideale_m2 DECIMAL(6, 2),
    production_kg_an DECIMAL(6, 2) DEFAULT 0,
    surface_actuelle_m2 DECIMAL(6, 2) DEFAULT 0,
    pourcentage_atteint INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN besoin_kg_an > 0 THEN LEAST(
                100,
                ROUND((production_kg_an / besoin_kg_an) * 100)
            )
            ELSE 0
        END
    ) STORED,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE depenses_home (
    id SERIAL PRIMARY KEY,
    date_depense DATE NOT NULL DEFAULT CURRENT_DATE,
    montant DECIMAL(10, 2) NOT NULL,
    categorie VARCHAR(50) NOT NULL CHECK (
        categorie IN (
            'jardin',
            'entretien',
            'energie',
            'travaux',
            'equipement',
            'decoration',
            'assurance',
            'autre'
        )
    ),
    sous_categorie VARCHAR(50),
    description TEXT,
    magasin VARCHAR(100),
    recurrent BOOLEAN DEFAULT FALSE,
    frequence_mois INTEGER,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_depenses_home_date ON depenses_home(date_depense);
CREATE INDEX IF NOT EXISTS idx_depenses_home_categorie ON depenses_home(categorie);

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE budgets_home (
    id SERIAL PRIMARY KEY,
    categorie VARCHAR(50) NOT NULL UNIQUE,
    montant_mensuel DECIMAL(10, 2) NOT NULL,
    alerte_pourcent INTEGER DEFAULT 80,
    notes TEXT,
    cree_le TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modifie_le TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- ============================================================================
-- PARTIE 5B : TABLES JEUX EXTENSIONS (Euromillions, Cotes, Mise Responsable)
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE artisans (
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
CREATE TABLE interventions_artisans (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE articles_cellier (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE diagnostics_maison (
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
CREATE TABLE estimations_immobilieres (
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
CREATE TABLE checklists_vacances (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE items_checklist (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE traitements_nuisibles (
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
CREATE TABLE devis_comparatifs (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE lignes_devis (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE entretiens_saisonniers (
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

-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE releves_compteurs (
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
-- ============================================================================
-- PARTIE 5D : TABLES UTILITAIRES (notes, journal, contacts, liens, etc.)
-- ============================================================================

