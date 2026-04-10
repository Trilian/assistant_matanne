-- Migration 003 : Ajout colonne user_id sur jeux_paris_sportifs
-- Alignement entre le modèle ORM SQLAlchemy (PariSportif.user_id) et le schéma
-- PostgreSQL réel. La colonne était présente dans le modèle mais absente en base.

ALTER TABLE jeux_paris_sportifs
    ADD COLUMN IF NOT EXISTS user_id INTEGER;
