-- Migration 024: Ajout de CheckConstraints pour l'intégrité des données
-- Ajoute des contraintes de validation sur les champs numériques critiques
-- Utilise IF NOT EXISTS via DO blocks pour être idempotent
-- ═══════════════════════════════════════════════════════════
-- BATCH COOKING
-- ═══════════════════════════════════════════════════════════
-- ConfigBatchCooking
DO $$ BEGIN
ALTER TABLE config_batch_cooking
ADD CONSTRAINT ck_config_batch_duree_positive CHECK (duree_max_session > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE config_batch_cooking
ADD CONSTRAINT ck_config_batch_objectif_positif CHECK (objectif_portions_semaine > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- SessionBatchCooking
DO $$ BEGIN
ALTER TABLE sessions_batch_cooking
ADD CONSTRAINT ck_session_duree_estimee_positive CHECK (duree_estimee > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE sessions_batch_cooking
ADD CONSTRAINT ck_session_duree_reelle_positive CHECK (
        duree_reelle IS NULL
        OR duree_reelle > 0
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE sessions_batch_cooking
ADD CONSTRAINT ck_session_portions_positive CHECK (nb_portions_preparees >= 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE sessions_batch_cooking
ADD CONSTRAINT ck_session_recettes_positive CHECK (nb_recettes_completees >= 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- EtapeBatchCooking
DO $$ BEGIN
ALTER TABLE etapes_batch_cooking
ADD CONSTRAINT ck_etape_batch_ordre_positif CHECK (ordre > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE etapes_batch_cooking
ADD CONSTRAINT ck_etape_batch_duree_positive CHECK (duree_minutes > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE etapes_batch_cooking
ADD CONSTRAINT ck_etape_batch_duree_reelle_positive CHECK (
        duree_reelle IS NULL
        OR duree_reelle > 0
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- PreparationBatch
DO $$ BEGIN
ALTER TABLE preparations_batch
ADD CONSTRAINT ck_prep_portions_initiales_positive CHECK (portions_initiales > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE preparations_batch
ADD CONSTRAINT ck_prep_portions_restantes_positive CHECK (portions_restantes >= 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- ═══════════════════════════════════════════════════════════
-- PLANNING
-- ═══════════════════════════════════════════════════════════
-- Repas
DO $$ BEGIN
ALTER TABLE repas
ADD CONSTRAINT ck_repas_portions_valides CHECK (
        portion_ajustee IS NULL
        OR (
            portion_ajustee > 0
            AND portion_ajustee <= 20
        )
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- CalendarEvent
DO $$ BEGIN
ALTER TABLE calendar_events
ADD CONSTRAINT ck_event_rappel_positif CHECK (
        rappel_avant_minutes IS NULL
        OR rappel_avant_minutes >= 0
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- TemplateItem
DO $$ BEGIN
ALTER TABLE template_items
ADD CONSTRAINT ck_template_jour_valide CHECK (
        jour_semaine >= 0
        AND jour_semaine <= 6
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- ═══════════════════════════════════════════════════════════
-- FINANCES
-- ═══════════════════════════════════════════════════════════
-- Depense (montant positif)
DO $$ BEGIN
ALTER TABLE depenses
ADD CONSTRAINT ck_depense_montant_positif CHECK (montant > 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- BudgetMensuelDB
DO $$ BEGIN
ALTER TABLE budgets_mensuels
ADD CONSTRAINT ck_budget_total_positif CHECK (budget_total >= 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
-- HouseExpense
DO $$ BEGIN
ALTER TABLE house_expenses
ADD CONSTRAINT ck_house_mois_valide CHECK (
        mois >= 1
        AND mois <= 12
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE house_expenses
ADD CONSTRAINT ck_house_montant_positif CHECK (montant >= 0);
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
DO $$ BEGIN
ALTER TABLE house_expenses
ADD CONSTRAINT ck_house_consommation_positive CHECK (
        consommation IS NULL
        OR consommation >= 0
    );
EXCEPTION
WHEN duplicate_object THEN NULL;
END $$;
