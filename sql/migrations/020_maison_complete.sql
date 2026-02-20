-- ═══════════════════════════════════════════════════════════════════════════════
-- MODULE MAISON - SCHÉMA COMPLET
-- Version: 020
-- Date: 2026-02-16
-- Description: Refonte complète module maison avec planning intelligent
-- ═══════════════════════════════════════════════════════════════════════════════
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 1: AJOUTS AUX TABLES EXISTANTES (Canvas 2D)                           ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Ajout colonnes position 2D pour zones_jardin (si pas déjà présentes)
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'zones_jardin'
        AND column_name = 'position_x'
) THEN
ALTER TABLE zones_jardin
ADD COLUMN position_x INTEGER DEFAULT 0;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'zones_jardin'
        AND column_name = 'position_y'
) THEN
ALTER TABLE zones_jardin
ADD COLUMN position_y INTEGER DEFAULT 0;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'zones_jardin'
        AND column_name = 'largeur_px'
) THEN
ALTER TABLE zones_jardin
ADD COLUMN largeur_px INTEGER DEFAULT 100;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'zones_jardin'
        AND column_name = 'hauteur_px'
) THEN
ALTER TABLE zones_jardin
ADD COLUMN hauteur_px INTEGER DEFAULT 100;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'zones_jardin'
        AND column_name = 'couleur'
) THEN
ALTER TABLE zones_jardin
ADD COLUMN couleur VARCHAR(20) DEFAULT '#4CAF50';
END IF;
END $$;
-- Ajout colonnes position 2D pour pieces_maison (si pas déjà présentes)
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'pieces_maison'
        AND column_name = 'position_x'
) THEN
ALTER TABLE pieces_maison
ADD COLUMN position_x INTEGER DEFAULT 0;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'pieces_maison'
        AND column_name = 'position_y'
) THEN
ALTER TABLE pieces_maison
ADD COLUMN position_y INTEGER DEFAULT 0;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'pieces_maison'
        AND column_name = 'largeur_px'
) THEN
ALTER TABLE pieces_maison
ADD COLUMN largeur_px INTEGER DEFAULT 100;
END IF;
IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name = 'pieces_maison'
        AND column_name = 'hauteur_px'
) THEN
ALTER TABLE pieces_maison
ADD COLUMN hauteur_px INTEGER DEFAULT 100;
END IF;
END $$;
COMMENT ON COLUMN zones_jardin.position_x IS 'Position X sur le canvas en pixels';
COMMENT ON COLUMN zones_jardin.position_y IS 'Position Y sur le canvas en pixels';
COMMENT ON COLUMN zones_jardin.largeur_px IS 'Largeur sur le canvas en pixels';
COMMENT ON COLUMN zones_jardin.hauteur_px IS 'Hauteur sur le canvas en pixels';
COMMENT ON COLUMN zones_jardin.couleur IS 'Couleur hex pour affichage canvas';
COMMENT ON COLUMN pieces_maison.position_x IS 'Position X sur le plan en pixels';
COMMENT ON COLUMN pieces_maison.position_y IS 'Position Y sur le plan en pixels';
COMMENT ON COLUMN pieces_maison.largeur_px IS 'Largeur sur le plan en pixels';
COMMENT ON COLUMN pieces_maison.hauteur_px IS 'Hauteur sur le plan en pixels';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 2: TABLES HUB & PLANNING INTELLIGENT                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Préférences planning maison
CREATE TABLE IF NOT EXISTS preferences_home (
    id SERIAL PRIMARY KEY,
    -- Limites charge mentale
    max_taches_jour INTEGER DEFAULT 3,
    max_heures_jour DECIMAL(4, 2) DEFAULT 2.0,
    -- Préférences horaires (JSON arrays d'heures 0-23)
    heures_jardin JSONB DEFAULT '[7, 8, 18, 19]',
    heures_menage JSONB DEFAULT '[9, 10, 14, 15]',
    heures_admin JSONB DEFAULT '[20, 21]',
    -- Jours préférés par domaine
    jours_jardin JSONB DEFAULT '[6, 7]',
    -- Samedi, Dimanche
    jours_menage JSONB DEFAULT '[6]',
    -- Samedi
    -- Config notifications
    notification_matin BOOLEAN DEFAULT true,
    heure_briefing INTEGER DEFAULT 7,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE preferences_home IS 'Préférences de planning et charge mentale pour le module maison';
-- Tâches maison (tous domaines)
CREATE TABLE IF NOT EXISTS taches_home (
    id SERIAL PRIMARY KEY,
    -- Catégorisation
    domaine VARCHAR(20) NOT NULL CHECK (
        domaine IN ('jardin', 'entretien', 'charges', 'depenses')
    ),
    type_tache VARCHAR(50) NOT NULL,
    -- Détails
    titre VARCHAR(200) NOT NULL,
    description TEXT,
    duree_min INTEGER DEFAULT 15,
    -- Priorité et échéance
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
    -- Statut
    statut VARCHAR(20) DEFAULT 'a_faire' CHECK (
        statut IN (
            'a_faire',
            'en_cours',
            'fait',
            'reporte',
            'annule'
        )
    ),
    -- Source (pour intégrations)
    generee_auto BOOLEAN DEFAULT false,
    source VARCHAR(50),
    -- 'meteo', 'calendrier', 'routine', 'manuel'
    source_id INTEGER,
    -- ID de l'élément source
    -- Liens optionnels
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE
    SET NULL,
        piece_id INTEGER REFERENCES pieces_maison(id) ON DELETE
    SET NULL,
        -- Métadonnées
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_taches_home_domaine ON taches_home(domaine);
CREATE INDEX IF NOT EXISTS idx_taches_home_statut ON taches_home(statut);
CREATE INDEX IF NOT EXISTS idx_taches_home_date_due ON taches_home(date_due);
CREATE INDEX IF NOT EXISTS idx_taches_home_source ON taches_home(source, source_id);
COMMENT ON TABLE taches_home IS 'Tâches unifiées maison (jardin, entretien, charges, dépenses)';
-- Stats quotidiennes maison
CREATE TABLE IF NOT EXISTS stats_home (
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
    -- Temps
    temps_prevu_min INTEGER DEFAULT 0,
    temps_reel_min INTEGER DEFAULT 0,
    -- Tâches
    taches_prevues INTEGER DEFAULT 0,
    taches_completees INTEGER DEFAULT 0,
    taches_reportees INTEGER DEFAULT 0,
    -- Score (pourcentage d'accomplissement)
    score_jour INTEGER DEFAULT 0,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, domaine)
);
CREATE INDEX IF NOT EXISTS idx_stats_home_date ON stats_home(date);
COMMENT ON TABLE stats_home IS 'Statistiques quotidiennes par domaine pour dashboard';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 3: TABLES JARDIN - AUTONOMIE ALIMENTAIRE                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Catalogue de plantes (référentiel)
CREATE TABLE IF NOT EXISTS plantes_catalogue (
    id SERIAL PRIMARY KEY,
    -- Identification
    nom VARCHAR(100) NOT NULL UNIQUE,
    nom_latin VARCHAR(150),
    famille VARCHAR(50),
    -- Variétés populaires
    varietes JSONB DEFAULT '[]',
    -- Calendrier (mois 1-12)
    mois_semis_interieur JSONB DEFAULT '[]',
    -- [2, 3]
    mois_semis_exterieur JSONB DEFAULT '[]',
    -- [4, 5]
    mois_plantation JSONB DEFAULT '[]',
    -- [5, 6]
    mois_recolte JSONB DEFAULT '[]',
    -- [7, 8, 9]
    -- Compagnonnage
    compagnons_positifs JSONB DEFAULT '[]',
    -- ["Basilic", "Carotte"]
    compagnons_negatifs JSONB DEFAULT '[]',
    -- ["Fenouil"]
    -- Caractéristiques culture
    espacement_cm INTEGER DEFAULT 30,
    profondeur_semis_cm INTEGER DEFAULT 2,
    jours_germination INTEGER DEFAULT 10,
    jours_jusqu_recolte INTEGER DEFAULT 60,
    -- Arrosage
    arrosage VARCHAR(20) DEFAULT 'regulier' CHECK (
        arrosage IN ('quotidien', 'regulier', 'modere', 'faible')
    ),
    exposition VARCHAR(20) DEFAULT 'soleil' CHECK (exposition IN ('soleil', 'mi_ombre', 'ombre')),
    -- Production
    rendement_kg_m2 DECIMAL(4, 2) DEFAULT 2.0,
    besoin_famille_4_kg_an DECIMAL(6, 2),
    -- Consommation estimée famille 4 personnes
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plantes_catalogue_famille ON plantes_catalogue(famille);
COMMENT ON TABLE plantes_catalogue IS 'Catalogue de référence des plantes potagères avec calendrier et rendements';
-- Récoltes jardin
CREATE TABLE IF NOT EXISTS recoltes (
    id SERIAL PRIMARY KEY,
    -- Liens
    plante_jardin_id INTEGER REFERENCES plantes_jardin(id) ON DELETE CASCADE,
    zone_jardin_id INTEGER REFERENCES zones_jardin(id) ON DELETE CASCADE,
    -- Détails récolte
    legume VARCHAR(100) NOT NULL,
    -- Nom du légume récolté
    date_recolte DATE NOT NULL DEFAULT CURRENT_DATE,
    quantite_kg DECIMAL(6, 2) NOT NULL,
    -- Qualité
    qualite VARCHAR(20) DEFAULT 'bonne' CHECK (
        qualite IN ('excellente', 'bonne', 'moyenne', 'passable')
    ),
    -- Destination
    destination VARCHAR(20) DEFAULT 'frais' CHECK (
        destination IN ('frais', 'conserve', 'congele', 'donne', 'perdu')
    ),
    -- Notes
    notes TEXT,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_recoltes_date ON recoltes(date_recolte);
CREATE INDEX IF NOT EXISTS idx_recoltes_legume ON recoltes(legume);
COMMENT ON TABLE recoltes IS 'Suivi des récoltes pour calcul autonomie alimentaire';
-- Objectifs autonomie alimentaire
CREATE TABLE IF NOT EXISTS objectifs_autonomie (
    id SERIAL PRIMARY KEY,
    -- Légume
    legume VARCHAR(100) NOT NULL UNIQUE,
    -- Objectifs annuels
    besoin_kg_an DECIMAL(6, 2) NOT NULL,
    -- Consommation famille visée
    surface_ideale_m2 DECIMAL(6, 2),
    -- Surface nécessaire selon rendement
    -- Production actuelle (année en cours)
    production_kg_an DECIMAL(6, 2) DEFAULT 0,
    surface_actuelle_m2 DECIMAL(6, 2) DEFAULT 0,
    -- Calculs
    pourcentage_atteint INTEGER GENERATED ALWAYS AS (
        CASE
            WHEN besoin_kg_an > 0 THEN LEAST(
                100,
                ROUND((production_kg_an / besoin_kg_an) * 100)
            )
            ELSE 0
        END
    ) STORED,
    -- Notes
    notes TEXT,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE objectifs_autonomie IS 'Suivi des objectifs d autonomie alimentaire par légume';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 4: TABLES CHARGES (ex-ÉNERGIE)                                        ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Contrats (énergie, assurances, abonnements)
CREATE TABLE IF NOT EXISTS contrats (
    id SERIAL PRIMARY KEY,
    -- Type de contrat
    type_contrat VARCHAR(30) NOT NULL CHECK (
        type_contrat IN (
            'electricite',
            'gaz',
            'eau',
            'internet',
            'telephone',
            'mobile',
            'assurance_habitation',
            'assurance_auto',
            'assurance_sante',
            'abonnement',
            'autre'
        )
    ),
    -- Fournisseur
    fournisseur VARCHAR(100) NOT NULL,
    reference_contrat VARCHAR(100),
    -- Dates
    date_debut DATE,
    date_fin DATE,
    date_renouvellement DATE,
    -- Montants
    montant_mensuel DECIMAL(10, 2),
    montant_annuel DECIMAL(10, 2),
    -- Statut
    actif BOOLEAN DEFAULT true,
    tacite_reconduction BOOLEAN DEFAULT true,
    -- Document
    fichier_url TEXT,
    -- Notes
    notes TEXT,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contrats_type ON contrats(type_contrat);
CREATE INDEX IF NOT EXISTS idx_contrats_actif ON contrats(actif);
COMMENT ON TABLE contrats IS 'Contrats énergie, assurances et abonnements';
-- Factures
CREATE TABLE IF NOT EXISTS factures (
    id SERIAL PRIMARY KEY,
    -- Lien contrat
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE CASCADE,
    -- Détails facture
    date_facture DATE NOT NULL,
    date_echeance DATE,
    periode_debut DATE,
    periode_fin DATE,
    -- Montants
    montant_ht DECIMAL(10, 2),
    montant_ttc DECIMAL(10, 2) NOT NULL,
    -- Consommations (selon type)
    conso_kwh DECIMAL(10, 2),
    -- Électricité
    conso_m3 DECIMAL(10, 2),
    -- Eau/Gaz
    -- Statut
    payee BOOLEAN DEFAULT false,
    date_paiement DATE,
    -- Document
    fichier_url TEXT,
    -- Notes
    notes TEXT,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_factures_contrat ON factures(contrat_id);
CREATE INDEX IF NOT EXISTS idx_factures_date ON factures(date_facture);
CREATE INDEX IF NOT EXISTS idx_factures_payee ON factures(payee);
COMMENT ON TABLE factures IS 'Historique des factures avec consommations';
-- Comparatifs fournisseurs (suggestions IA)
CREATE TABLE IF NOT EXISTS comparatifs (
    id SERIAL PRIMARY KEY,
    -- Contrat concerné
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE CASCADE,
    -- Analyse
    date_analyse DATE DEFAULT CURRENT_DATE,
    -- Suggestion
    fournisseur_suggere VARCHAR(100),
    offre_nom VARCHAR(200),
    -- Économies
    economie_mensuelle DECIMAL(10, 2),
    economie_annuelle DECIMAL(10, 2),
    -- Détails
    avantages TEXT,
    inconvenients TEXT,
    lien_offre TEXT,
    -- Statut
    applique BOOLEAN DEFAULT false,
    date_application DATE,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE comparatifs IS 'Suggestions IA de changement de fournisseur avec économies estimées';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 5: TABLES DÉPENSES                                                    ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Dépenses maison
CREATE TABLE IF NOT EXISTS depenses_home (
    id SERIAL PRIMARY KEY,
    -- Date et montant
    date_depense DATE NOT NULL DEFAULT CURRENT_DATE,
    montant DECIMAL(10, 2) NOT NULL,
    -- Catégorisation
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
    -- Détails
    description TEXT,
    magasin VARCHAR(100),
    -- Récurrence
    recurrent BOOLEAN DEFAULT false,
    frequence_mois INTEGER,
    -- Tous les X mois
    -- Liens optionnels
    contrat_id INTEGER REFERENCES contrats(id) ON DELETE
    SET NULL,
        facture_id INTEGER REFERENCES factures(id) ON DELETE
    SET NULL,
        -- Métadonnées
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_depenses_home_date ON depenses_home(date_depense);
CREATE INDEX IF NOT EXISTS idx_depenses_home_categorie ON depenses_home(categorie);
COMMENT ON TABLE depenses_home IS 'Suivi des dépenses maison et jardin';
-- Budgets par catégorie
CREATE TABLE IF NOT EXISTS budgets_home (
    id SERIAL PRIMARY KEY,
    -- Catégorie
    categorie VARCHAR(50) NOT NULL UNIQUE,
    -- Budget mensuel
    montant_mensuel DECIMAL(10, 2) NOT NULL,
    -- Alertes
    alerte_pourcent INTEGER DEFAULT 80,
    -- Alerte à X% du budget
    -- Notes
    notes TEXT,
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE budgets_home IS 'Budgets mensuels par catégorie avec seuils alertes';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 6: VUES INTELLIGENTES                                                 ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Vue: Tâches du jour
CREATE OR REPLACE VIEW v_taches_jour AS
SELECT t.*,
    z.nom as zone_nom,
    p.nom as piece_nom,
    CASE
        WHEN t.priorite = 'urgente' THEN 1
        WHEN t.priorite = 'haute' THEN 2
        WHEN t.priorite = 'normale' THEN 3
        WHEN t.priorite = 'basse' THEN 4
        ELSE 5
    END as priorite_ordre
FROM taches_home t
    LEFT JOIN zones_jardin z ON t.zone_jardin_id = z.id
    LEFT JOIN pieces_maison p ON t.piece_id = p.id
WHERE t.statut IN ('a_faire', 'en_cours')
    AND (
        t.date_due IS NULL
        OR t.date_due <= CURRENT_DATE + INTERVAL '1 day'
    )
ORDER BY priorite_ordre,
    t.date_due NULLS LAST;
COMMENT ON VIEW v_taches_jour IS 'Tâches à faire aujourd hui triées par priorité';
-- Vue: Charge semaine
CREATE OR REPLACE VIEW v_charge_semaine AS
SELECT d.jour,
    COALESCE(SUM(t.duree_min), 0) as temps_prevu_min,
    COUNT(t.id) as nb_taches,
    CASE
        WHEN COALESCE(SUM(t.duree_min), 0) > 120 THEN 'surcharge'
        WHEN COALESCE(SUM(t.duree_min), 0) > 90 THEN 'charge'
        WHEN COALESCE(SUM(t.duree_min), 0) > 60 THEN 'normal'
        ELSE 'leger'
    END as niveau_charge
FROM (
        SELECT generate_series(
                CURRENT_DATE,
                CURRENT_DATE + INTERVAL '6 days',
                INTERVAL '1 day'
            )::DATE as jour
    ) d
    LEFT JOIN taches_home t ON t.date_due = d.jour
    AND t.statut IN ('a_faire', 'en_cours')
GROUP BY d.jour
ORDER BY d.jour;
COMMENT ON VIEW v_charge_semaine IS 'Répartition de la charge sur les 7 prochains jours';
-- Vue: Stats par domaine (mois courant)
CREATE OR REPLACE VIEW v_stats_domaine_mois AS
SELECT domaine,
    SUM(temps_reel_min) as temps_total_min,
    SUM(taches_completees) as taches_total,
    ROUND(AVG(score_jour), 0) as score_moyen
FROM stats_home
WHERE date >= date_trunc('month', CURRENT_DATE)
    AND domaine != 'total'
GROUP BY domaine;
COMMENT ON VIEW v_stats_domaine_mois IS 'Statistiques par domaine pour le mois en cours';
-- Vue: Pourcentage autonomie alimentaire
CREATE OR REPLACE VIEW v_autonomie AS
SELECT COALESCE(SUM(production_kg_an), 0) as production_totale_kg,
    COALESCE(SUM(besoin_kg_an), 0) as besoin_total_kg,
    CASE
        WHEN COALESCE(SUM(besoin_kg_an), 0) > 0 THEN ROUND(
            (SUM(production_kg_an) / SUM(besoin_kg_an)) * 100
        )
        ELSE 0
    END as pourcentage_global,
    COUNT(*) as nb_legumes_suivis,
    COUNT(*) FILTER (
        WHERE pourcentage_atteint >= 100
    ) as nb_objectifs_atteints
FROM objectifs_autonomie;
COMMENT ON VIEW v_autonomie IS 'Résumé global objectif autonomie alimentaire';
-- Vue: Factures avec alertes hausse
CREATE OR REPLACE VIEW v_factures_alertes AS WITH factures_avec_moyenne AS (
        SELECT f.*,
            c.type_contrat,
            c.fournisseur,
            AVG(f.montant_ttc) OVER (
                PARTITION BY f.contrat_id
                ORDER BY f.date_facture ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
            ) as moyenne_3_precedentes
        FROM factures f
            JOIN contrats c ON f.contrat_id = c.id
    )
SELECT *,
    ROUND(
        (
            (montant_ttc - moyenne_3_precedentes) / NULLIF(moyenne_3_precedentes, 0)
        ) * 100,
        1
    ) as variation_pourcent,
    CASE
        WHEN montant_ttc > moyenne_3_precedentes * 1.15 THEN 'hausse'
        WHEN montant_ttc < moyenne_3_precedentes * 0.85 THEN 'baisse'
        ELSE 'stable'
    END as tendance
FROM factures_avec_moyenne
WHERE moyenne_3_precedentes IS NOT NULL
ORDER BY date_facture DESC;
COMMENT ON VIEW v_factures_alertes IS 'Factures avec détection de hausse/baisse vs moyenne';
-- Vue: État budgets
CREATE OR REPLACE VIEW v_budgets_status AS
SELECT b.categorie,
    b.montant_mensuel as budget,
    COALESCE(SUM(d.montant), 0) as depense_mois,
    b.montant_mensuel - COALESCE(SUM(d.montant), 0) as reste,
    ROUND(
        (COALESCE(SUM(d.montant), 0) / b.montant_mensuel) * 100,
        1
    ) as pourcentage_utilise,
    CASE
        WHEN COALESCE(SUM(d.montant), 0) >= b.montant_mensuel THEN 'depasse'
        WHEN COALESCE(SUM(d.montant), 0) >= b.montant_mensuel * (b.alerte_pourcent / 100.0) THEN 'alerte'
        ELSE 'ok'
    END as statut
FROM budgets_home b
    LEFT JOIN depenses_home d ON d.categorie = b.categorie
    AND d.date_depense >= date_trunc('month', CURRENT_DATE)
GROUP BY b.id,
    b.categorie,
    b.montant_mensuel,
    b.alerte_pourcent;
COMMENT ON VIEW v_budgets_status IS 'État des budgets vs dépenses du mois';
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 7: TRIGGERS                                                           ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Fonction générique updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ language 'plpgsql';
-- Triggers updated_at pour tables avec ce champ
DO $$
DECLARE t text;
BEGIN FOR t IN
SELECT unnest(
        ARRAY [
        'preferences_home', 'taches_home', 'objectifs_autonomie',
        'contrats', 'budgets_home'
    ]
    ) LOOP EXECUTE format(
        '
            DROP TRIGGER IF EXISTS update_%s_updated_at ON %s;
            CREATE TRIGGER update_%s_updated_at
            BEFORE UPDATE ON %s
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        ',
        t,
        t,
        t,
        t
    );
END LOOP;
END $$;
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 8: DONNÉES INITIALES                                                  ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Préférences par défaut (si pas encore créées)
INSERT INTO preferences_home (id, max_taches_jour, max_heures_jour)
VALUES (1, 3, 2.0) ON CONFLICT (id) DO NOTHING;
-- Budgets par défaut
INSERT INTO budgets_home (categorie, montant_mensuel, alerte_pourcent)
VALUES ('jardin', 100.00, 80),
    ('entretien', 50.00, 80),
    ('energie', 200.00, 90),
    ('travaux', 150.00, 80),
    ('equipement', 100.00, 80),
    ('decoration', 50.00, 80),
    ('assurance', 150.00, 95),
    ('autre', 50.00, 80) ON CONFLICT (categorie) DO NOTHING;
-- Objectifs autonomie (exemples)
INSERT INTO objectifs_autonomie (legume, besoin_kg_an, surface_ideale_m2)
VALUES ('Tomate', 40.00, 8.00),
    ('Courgette', 25.00, 6.00),
    ('Haricot vert', 15.00, 5.00),
    ('Pomme de terre', 80.00, 20.00),
    ('Carotte', 20.00, 4.00),
    ('Salade', 30.00, 3.00),
    ('Poireau', 15.00, 3.00),
    ('Oignon', 10.00, 2.00),
    ('Ail', 3.00, 1.00),
    ('Fraise', 10.00, 4.00) ON CONFLICT (legume) DO NOTHING;
-- ╔═══════════════════════════════════════════════════════════════════════════════╗
-- ║ PARTIE 9: GRANTS (Supabase RLS)                                              ║
-- ╚═══════════════════════════════════════════════════════════════════════════════╝
-- Accès pour utilisateurs authentifiés
GRANT SELECT,
    INSERT,
    UPDATE,
    DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE,
    SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- Accès aux vues
GRANT SELECT ON v_taches_jour TO authenticated;
GRANT SELECT ON v_charge_semaine TO authenticated;
GRANT SELECT ON v_stats_domaine_mois TO authenticated;
GRANT SELECT ON v_autonomie TO authenticated;
GRANT SELECT ON v_factures_alertes TO authenticated;
GRANT SELECT ON v_budgets_status TO authenticated;
-- ═══════════════════════════════════════════════════════════════════════════════
-- FIN DU SCRIPT
-- À exécuter dans Supabase SQL Editor
-- ═══════════════════════════════════════════════════════════════════════════════
