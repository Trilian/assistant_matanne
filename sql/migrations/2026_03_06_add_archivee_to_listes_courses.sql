-- Migration: add `archivee` to `listes_courses`
-- Fixes ProgrammingError: column listes_courses.archivee does not exist
BEGIN;
ALTER TABLE IF EXISTS listes_courses
ADD COLUMN IF NOT EXISTS archivee BOOLEAN DEFAULT FALSE;
CREATE INDEX IF NOT EXISTS ix_listes_courses_archivee ON listes_courses (archivee);
COMMIT;
