-- ============================================================================
-- ASSISTANT MATANNE — Maison : Energie & Charges
-- ============================================================================
-- Contient : dépenses, abonnements, écologie, entretiens saisonniers, compteurs
-- ============================================================================
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
CREATE TABLE abonnements (
    id SERIAL PRIMARY KEY,
    type_abonnement VARCHAR(50) NOT NULL,
    fournisseur VARCHAR(200) NOT NULL,
    numero_contrat VARCHAR(100),
    prix_mensuel NUMERIC(10, 2),
    date_debut DATE,
    date_fin_engagement DATE,
    meilleur_prix_trouve NUMERIC(10, 2),
    fournisseur_alternatif VARCHAR(200),
    notes TEXT,
    cree_le TIMESTAMP NOT NULL DEFAULT NOW(),
    modifie_le TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_abonnements_type ON abonnements(type_abonnement);


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



