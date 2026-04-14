-- Migration 004 : Correction doublons ingrédients + contrainte d'unicité
-- Problème : la même recette pouvait être importée plusieurs fois, créant des
-- lignes dupliquées dans recette_ingredients. Le parser créait aussi des noms
-- d'ingrédients corrompus du type "(11g) levure chimique".
--
-- Étapes :
--   1. Dédupliquer recette_ingredients (sommer quantite par recette_id + ingredient_id)
--   2. Nettoyer les noms d'ingrédients avec spécificatifs entre parenthèses en tête
--   3. Fusionner les doublons d'ingrédients nés du parser (case-insensitive)
--   4. Redédupliquer recette_ingredients après fusion d'ingrédients
--   5. Supprimer les ingrédients orphelins non utilisés ailleurs
--   6. Ajouter la contrainte UNIQUE(recette_id, ingredient_id)
--
-- Idempotent : peut être exécuté plusieurs fois sans risque.
-- ─────────────────────────────────────────────────────────────────────────────

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 1 : Dédupliquer recette_ingredients
-- Pour chaque (recette_id, ingredient_id) avec plusieurs lignes :
-- → Sommer les quantites sur la ligne MIN(id), supprimer les autres.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1a. Mettre à jour la ligne gardée avec la quantite totale
UPDATE recette_ingredients ri
SET
    quantite  = agg.quantite_totale,
    unite     = agg.unite_ref,
    optionnel = agg.optionnel_ref
FROM (
    SELECT
        MIN(id)                          AS id_a_garder,
        recette_id,
        ingredient_id,
        SUM(quantite)                    AS quantite_totale,
        (ARRAY_AGG(unite ORDER BY id))[1] AS unite_ref,
        BOOL_OR(optionnel)               AS optionnel_ref
    FROM recette_ingredients
    GROUP BY recette_id, ingredient_id
    HAVING COUNT(*) > 1
) agg
WHERE ri.id = agg.id_a_garder;

-- 1b. Supprimer les lignes en double (non MIN(id))
DELETE FROM recette_ingredients ri
WHERE EXISTS (
    SELECT 1
    FROM (
        SELECT MIN(id) AS id_a_garder, recette_id, ingredient_id
        FROM recette_ingredients
        GROUP BY recette_id, ingredient_id
        HAVING COUNT(*) > 1
    ) doublons
    WHERE doublons.recette_id    = ri.recette_id
      AND doublons.ingredient_id = ri.ingredient_id
      AND doublons.id_a_garder  <> ri.id
);

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 2 : Nettoyer les noms d'ingrédients avec spécificatifs en tête
-- Ex : "(11g) levure chimique" → "levure chimique"
--      "sel (fin)" reste inchangé (parenthèse non en tête)
-- ─────────────────────────────────────────────────────────────────────────────

UPDATE ingredients
SET nom = TRIM(regexp_replace(nom, '^\s*\([^)]*\)\s*', '', 'g'))
WHERE nom ~ '^\s*\(';

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 3 : Fusionner les ingrédients devenus doublons après nettoyage
-- (même nom insensible à la casse)
-- → Réattribuer toutes les FK vers MIN(id), puis supprimer les doublons.
-- ─────────────────────────────────────────────────────────────────────────────

-- 3a. Réattribuer recette_ingredients
UPDATE recette_ingredients ri
SET ingredient_id = doublons_ing.id_a_garder
FROM (
    SELECT
        LOWER(TRIM(nom)) AS nom_normalise,
        MIN(id)          AS id_a_garder,
        ARRAY_AGG(id)    AS tous_ids
    FROM ingredients
    GROUP BY LOWER(TRIM(nom))
    HAVING COUNT(*) > 1
) doublons_ing
WHERE ri.ingredient_id = ANY(doublons_ing.tous_ids)
  AND ri.ingredient_id <> doublons_ing.id_a_garder;

-- 3b. Réattribuer articles_courses
UPDATE articles_courses ac
SET ingredient_id = doublons_ing.id_a_garder
FROM (
    SELECT
        LOWER(TRIM(nom)) AS nom_normalise,
        MIN(id)          AS id_a_garder,
        ARRAY_AGG(id)    AS tous_ids
    FROM ingredients
    GROUP BY LOWER(TRIM(nom))
    HAVING COUNT(*) > 1
) doublons_ing
WHERE ac.ingredient_id = ANY(doublons_ing.tous_ids)
  AND ac.ingredient_id <> doublons_ing.id_a_garder;

-- 3c. Réattribuer inventaire (UNIQUE sur ingredient_id → supprimer le doublon)
-- Si les deux ingrédients ont une entrée inventaire, on supprime le doublon
-- et on laisse l'inventaire de l'id_a_garder intact.
DELETE FROM inventaire inv
WHERE EXISTS (
    SELECT 1
    FROM (
        SELECT MIN(id) AS id_a_garder, ARRAY_AGG(id) AS tous_ids
        FROM ingredients
        GROUP BY LOWER(TRIM(nom))
        HAVING COUNT(*) > 1
    ) doublons_ing
    JOIN inventaire inv2 ON inv2.ingredient_id = doublons_ing.id_a_garder
    WHERE inv.ingredient_id = ANY(doublons_ing.tous_ids)
      AND inv.ingredient_id <> doublons_ing.id_a_garder
);

UPDATE inventaire inv
SET ingredient_id = doublons_ing.id_a_garder
FROM (
    SELECT
        LOWER(TRIM(nom)) AS nom_normalise,
        MIN(id)          AS id_a_garder,
        ARRAY_AGG(id)    AS tous_ids
    FROM ingredients
    GROUP BY LOWER(TRIM(nom))
    HAVING COUNT(*) > 1
) doublons_ing
WHERE inv.ingredient_id = ANY(doublons_ing.tous_ids)
  AND inv.ingredient_id <> doublons_ing.id_a_garder;

-- 3d. Réattribuer articles_modeles
UPDATE articles_modeles am
SET ingredient_id = doublons_ing.id_a_garder
FROM (
    SELECT
        LOWER(TRIM(nom)) AS nom_normalise,
        MIN(id)          AS id_a_garder,
        ARRAY_AGG(id)    AS tous_ids
    FROM ingredients
    GROUP BY LOWER(TRIM(nom))
    HAVING COUNT(*) > 1
) doublons_ing
WHERE am.ingredient_id = ANY(doublons_ing.tous_ids)
  AND am.ingredient_id <> doublons_ing.id_a_garder;

-- 3e. Supprimer les ingrédients doublons (devenus orphelins après réattribution)
DELETE FROM ingredients ing
WHERE EXISTS (
    SELECT 1
    FROM (
        SELECT MIN(id) AS id_a_garder, ARRAY_AGG(id) AS tous_ids
        FROM ingredients
        GROUP BY LOWER(TRIM(nom))
        HAVING COUNT(*) > 1
    ) doublons_ing
    WHERE ing.id = ANY(doublons_ing.tous_ids)
      AND ing.id <> doublons_ing.id_a_garder
);

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 4 : Redédupliquer recette_ingredients après fusion d'ingrédients
-- (un même ingredient_id peut maintenant apparaître deux fois dans la même recette)
-- ─────────────────────────────────────────────────────────────────────────────

-- 4a. Mettre à jour la ligne gardée
UPDATE recette_ingredients ri
SET
    quantite  = agg.quantite_totale,
    unite     = agg.unite_ref,
    optionnel = agg.optionnel_ref
FROM (
    SELECT
        MIN(id)                          AS id_a_garder,
        recette_id,
        ingredient_id,
        SUM(quantite)                    AS quantite_totale,
        (ARRAY_AGG(unite ORDER BY id))[1] AS unite_ref,
        BOOL_OR(optionnel)               AS optionnel_ref
    FROM recette_ingredients
    GROUP BY recette_id, ingredient_id
    HAVING COUNT(*) > 1
) agg
WHERE ri.id = agg.id_a_garder;

-- 4b. Supprimer les lignes restantes en double
DELETE FROM recette_ingredients ri
WHERE EXISTS (
    SELECT 1
    FROM (
        SELECT MIN(id) AS id_a_garder, recette_id, ingredient_id
        FROM recette_ingredients
        GROUP BY recette_id, ingredient_id
        HAVING COUNT(*) > 1
    ) doublons
    WHERE doublons.recette_id    = ri.recette_id
      AND doublons.ingredient_id = ri.ingredient_id
      AND doublons.id_a_garder  <> ri.id
);

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 5 : Supprimer les ingrédients orphelins (aucune référence nulle part)
-- ─────────────────────────────────────────────────────────────────────────────

DELETE FROM ingredients ing
WHERE NOT EXISTS (SELECT 1 FROM recette_ingredients ri  WHERE ri.ingredient_id  = ing.id)
  AND NOT EXISTS (SELECT 1 FROM inventaire          inv WHERE inv.ingredient_id = ing.id)
  AND NOT EXISTS (SELECT 1 FROM articles_courses    ac  WHERE ac.ingredient_id  = ing.id)
  AND NOT EXISTS (SELECT 1 FROM articles_modeles    am  WHERE am.ingredient_id  = ing.id);

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉTAPE 6 : Ajouter la contrainte UNIQUE(recette_id, ingredient_id)
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE recette_ingredients
    DROP CONSTRAINT IF EXISTS uq_recette_ingredient;

ALTER TABLE recette_ingredients
    ADD CONSTRAINT uq_recette_ingredient UNIQUE (recette_id, ingredient_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Enregistrement de la migration
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO schema_migrations (version, description)
VALUES ('004', 'Contrainte unicité recette_ingredients + nettoyage doublons ingrédients')
ON CONFLICT (version) DO NOTHING;

COMMIT;
