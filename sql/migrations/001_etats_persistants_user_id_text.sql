-- Migration: Changer user_id UUID → VARCHAR(255) dans etats_persistants
-- Raison: le code utilise des valeurs non-UUID comme "global", "default",
--         et des event_ids comme "planning.modifie_1775655694650".
--
-- PostgreSQL interdit ALTER COLUMN sur une colonne référencée dans une policy RLS.
-- Solution : supprimer les policies, modifier la colonne, recréer les policies.

-- 1. Supprimer les policies RLS qui référencent user_id
DROP POLICY IF EXISTS "authenticated_access_etats_persistants" ON public.etats_persistants;
DROP POLICY IF EXISTS "service_role_access_etats_persistants" ON public.etats_persistants;

-- 2. Modifier le type de la colonne
ALTER TABLE etats_persistants
    ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::text;

-- 3. Recréer les policies RLS
CREATE POLICY "service_role_access_etats_persistants"
    ON public.etats_persistants FOR ALL TO service_role
    USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_access_etats_persistants"
    ON public.etats_persistants FOR ALL TO authenticated
    USING (user_id = auth.uid()::text) WITH CHECK (user_id = auth.uid()::text);
