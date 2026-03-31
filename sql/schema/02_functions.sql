-- PARTIE 1 : FONCTIONS TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION update_modifie_le_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE OR REPLACE FUNCTION update_modifie_le_bis_column() RETURNS TRIGGER AS $$ BEGIN NEW.modifie_le = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- ============================================================================
-- PARTIE 8 : FONCTIONS HELPER
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_temps_entretien_par_mois(
        p_annee INTEGER DEFAULT EXTRACT(
            YEAR
            FROM NOW()
        )::INTEGER,
        p_mois INTEGER DEFAULT NULL
    ) RETURNS TABLE (
        mois INTEGER,
        annee INTEGER,
        type_activite VARCHAR,
        nb_sessions BIGINT,
        duree_totale_minutes BIGINT
    ) AS $$ BEGIN RETURN QUERY
SELECT EXTRACT(
        MONTH
        FROM s.debut
    )::INTEGER AS mois,
    EXTRACT(
        YEAR
        FROM s.debut
    )::INTEGER AS annee,
    s.type_activite,
    COUNT(*)::BIGINT AS nb_sessions,
    COALESCE(SUM(s.duree_minutes), 0)::BIGINT AS duree_totale_minutes
FROM sessions_travail s
WHERE EXTRACT(
        YEAR
        FROM s.debut
    )::INTEGER = p_annee
    AND (
        p_mois IS NULL
        OR EXTRACT(
            MONTH
            FROM s.debut
        )::INTEGER = p_mois
    )
    AND s.fin IS NOT NULL
GROUP BY EXTRACT(
        MONTH
        FROM s.debut
    ),
    EXTRACT(
        YEAR
        FROM s.debut
    ),
    s.type_activite
ORDER BY mois,
    type_activite;
END;
$$ LANGUAGE plpgsql;
-- ============================================================================
