-- Migration 001 : Ajout colonne rappel_expiration_jours sur documents_famille
-- Alignement entre le modèle ORM SQLAlchemy et le schéma PostgreSQL réel.
-- Colonne présente dans DocumentFamille (src/core/models/documents.py) mais
-- absente de la table en production.

ALTER TABLE documents_famille
    ADD COLUMN IF NOT EXISTS rappel_expiration_jours INTEGER DEFAULT 30;
