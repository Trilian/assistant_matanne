-- Migration 006: Équilibre nutritionnel des repas (PNNS4)
-- Date: 2026-04-15
-- Objectif:
--   Ajouter sur la table `recettes` une catégorie nutritionnelle pour l'équilibre assiette.
--   Ajouter sur la table `repas` les champs accompagnements (légumes + féculents + protéine),
--   goûter PNNS, et le score d'équilibre calculé.
-- Note: les colonnes `fruit` et `legumes` (base) viennent de la migration 005.

-- ── recettes ──────────────────────────────────────────────────────────────────
-- Catégorie nutritionnelle (pour détecter le type du plat principal)
-- Valeurs : proteines_poisson, proteines_viande_rouge, proteines_volaille,
--           proteines_oeuf, proteines_legumineuses, feculents, legumes_principaux, mixte
ALTER TABLE recettes ADD COLUMN IF NOT EXISTS categorie_nutritionnelle VARCHAR(50);

-- Backfill automatique depuis type_proteines existant
UPDATE recettes
SET categorie_nutritionnelle = CASE type_proteines
    WHEN 'poisson'     THEN 'proteines_poisson'
    WHEN 'viande'      THEN 'proteines_viande_rouge'
    WHEN 'volaille'    THEN 'proteines_volaille'
    WHEN 'vegetarien'  THEN 'proteines_legumineuses'
    ELSE NULL
END
WHERE type_proteines IS NOT NULL AND categorie_nutritionnelle IS NULL;

COMMENT ON COLUMN recettes.categorie_nutritionnelle IS
  'Type nutritionnel du plat : proteines_poisson | proteines_viande_rouge | proteines_volaille | proteines_oeuf | proteines_legumineuses | feculents | legumes_principaux | mixte';

-- ── repas ─────────────────────────────────────────────────────────────────────
-- FK recette pour les légumes (si légume = une recette de la base)
ALTER TABLE repas ADD COLUMN IF NOT EXISTS legumes_recette_id        INTEGER REFERENCES recettes(id) ON DELETE SET NULL;
-- Féculents : texte libre + FK optionnelle
ALTER TABLE repas ADD COLUMN IF NOT EXISTS feculents                  VARCHAR(200);
ALTER TABLE repas ADD COLUMN IF NOT EXISTS feculents_recette_id       INTEGER REFERENCES recettes(id) ON DELETE SET NULL;
-- Protéine accompagnement (cas plat = féculent/légume, ex: gratin dauphinois)
ALTER TABLE repas ADD COLUMN IF NOT EXISTS proteine_accompagnement    VARCHAR(200);
ALTER TABLE repas ADD COLUMN IF NOT EXISTS proteine_accompagnement_recette_id INTEGER REFERENCES recettes(id) ON DELETE SET NULL;
-- Goûter PNNS (laitage existe déjà — fruit existe déjà via migration 005)
ALTER TABLE repas ADD COLUMN IF NOT EXISTS fruit_gouter               VARCHAR(100);
ALTER TABLE repas ADD COLUMN IF NOT EXISTS gateau_gouter              VARCHAR(100);
-- Score équilibre calculé (0-100, NULL si non applicable : petit_dejeuner)
ALTER TABLE repas ADD COLUMN IF NOT EXISTS score_equilibre            SMALLINT;
-- Alertes texte sous forme JSONB (ex: ["Pas de légumes", "Protéine manquante"])
ALTER TABLE repas ADD COLUMN IF NOT EXISTS alertes_equilibre          JSONB;

-- Backfill : copier `fruit` → `fruit_gouter` pour les repas de type goûter existants
UPDATE repas
SET fruit_gouter = fruit
WHERE type_repas = 'gouter'
  AND fruit IS NOT NULL
  AND fruit_gouter IS NULL;

COMMENT ON COLUMN repas.legumes_recette_id              IS 'Recette liée pour les légumes (optionnel, sinon texte libre dans `legumes`)';
COMMENT ON COLUMN repas.feculents                       IS 'Féculents accompagnement — texte libre (ex: Riz basmati, Pommes de terre vapeur)';
COMMENT ON COLUMN repas.feculents_recette_id            IS 'Recette liée pour les féculents (optionnel)';
COMMENT ON COLUMN repas.proteine_accompagnement         IS 'Protéine quand le plat est féculent/légume (ex: Escalope de dinde, Lentilles)';
COMMENT ON COLUMN repas.proteine_accompagnement_recette_id IS 'Recette liée pour la protéine accompagnement';
COMMENT ON COLUMN repas.fruit_gouter                    IS 'Fruit frais ou compote au goûter (PNNS) — ex: Pomme, Compote poire sans sucre';
COMMENT ON COLUMN repas.gateau_gouter                   IS 'Gâteau/biscuit sain au goûter (PNNS) — ex: Cake maison, Barre céréales';
COMMENT ON COLUMN repas.score_equilibre                 IS 'Score PNNS calculé 0-100 (NULL=non applicable). Vert≥80, Orange 50-79, Rouge<50';
COMMENT ON COLUMN repas.alertes_equilibre               IS 'Liste alertes équilibre : ["Pas de légumes", "Féculents manquants", "Protéine manquante"]';
