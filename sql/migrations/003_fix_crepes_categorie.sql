-- Migration 003 : Correction catégorie "Crêpes au sucre"
-- Recette créée via seed sans champ categorie → défaut "Plat" au lieu de "Dessert"

UPDATE recettes
SET categorie = 'Dessert',
    nom       = 'Crêpes au sucre'
WHERE nom ILIKE '%crêpe%'
  AND categorie = 'Plat';
