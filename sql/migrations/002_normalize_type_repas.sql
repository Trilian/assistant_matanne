-- Migration 002: Normalise les valeurs accentuées de type_repas
-- Remplace 'déjeuner'→'dejeuner', 'dîner'→'diner', etc.
-- Le frontend et les requêtes backend utilisent les formes SANS accent.

UPDATE repas SET type_repas = 'petit_dejeuner' WHERE type_repas = 'petit_déjeuner';
UPDATE repas SET type_repas = 'dejeuner'       WHERE type_repas = 'déjeuner';
UPDATE repas SET type_repas = 'diner'          WHERE type_repas = 'dîner';
UPDATE repas SET type_repas = 'gouter'         WHERE type_repas = 'goûter';
