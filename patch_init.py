import re

path = "sql/INIT_COMPLET.sql"
with open(path, encoding="utf-8") as f:
    sql = f.read()

# 1. voyages - budget_reel
if (
    "CREATE TABLE voyages (" in sql
    and "budget_reel" not in sql.split("CREATE TABLE voyages (")[1].split(");")[0]
):
    sql = re.sub(r"(CREATE TABLE voyages \([^;]+)(cree_le)", r"\1budget_reel FLOAT,\n    \2", sql)

# 2. albums_famille - date_debut, date_fin
if (
    "CREATE TABLE albums_famille (" in sql
    and "date_debut" not in sql.split("CREATE TABLE albums_famille (")[1].split(");")[0]
):
    sql = re.sub(
        r"(CREATE TABLE albums_famille \([^;]+)(cree_le)",
        r"\1date_debut DATE,\n    date_fin DATE,\n    \2",
        sql,
    )

# 3. contacts_famille - sous_categorie
if (
    "CREATE TABLE contacts_famille (" in sql
    and "sous_categorie" not in sql.split("CREATE TABLE contacts_famille (")[1].split(");")[0]
):
    sql = re.sub(
        r"(CREATE TABLE contacts_famille \([^;]+)(cree_le)",
        r"\1sous_categorie VARCHAR(100),\n    \2",
        sql,
    )

# 4. documents_famille - titre
if (
    "CREATE TABLE documents_famille (" in sql
    and "titre VARCHAR" not in sql.split("CREATE TABLE documents_famille (")[1].split(");")[0]
):
    sql = re.sub(
        r"(CREATE TABLE documents_famille \([^;]+)(fichier_nom)",
        r"\1titre VARCHAR(200),\n    \2",
        sql,
    )

# 5. unite_mesure -> unite
sql = re.sub(r"unite_mesure(.*?)(VARCHAR[^\n]+)", r"unite\1\2", sql)

# 6. taches_entretien - created_at -> cree_le, updated_at -> modifie_le
if "CREATE TABLE taches_entretien (" in sql:
    taches_part = sql.split("CREATE TABLE taches_entretien (")[1].split(");")[0]
    new_taches_part = taches_part.replace("created_at", "cree_le").replace(
        "updated_at", "modifie_le"
    )
    sql = sql.replace(taches_part, new_taches_part)

# 7. profils_enfants - taille_vetements, pointure
if (
    "CREATE TABLE profils_enfants (" in sql
    and "taille_vetements" not in sql.split("CREATE TABLE profils_enfants (")[1].split(");")[0]
):
    sql = re.sub(
        r"(CREATE TABLE profils_enfants \([^;]+)(cree_le)",
        r"\1taille_vetements JSONB DEFAULT \'{}\'::jsonb,\n    pointure VARCHAR(50),\n    \2",
        sql,
    )

# 8. plannings
if "CREATE TABLE plannings (" in sql:
    plannings_part = sql.split("CREATE TABLE plannings (")[1].split(");")[0]
    if "nom VARCHAR" not in plannings_part:
        new_plan = re.sub(r"(semaine_debut)", r"nom VARCHAR(200),\n    \1", plannings_part)
        new_plan = new_plan.replace("semaine_du", "semaine_debut").replace(
            "semaine_au", "semaine_fin"
        )
        if "actif BOOLEAN" not in new_plan:
            new_plan = re.sub(
                r"(cree_le)", r"actif BOOLEAN DEFAULT FALSE,\n    notes TEXT,\n    \1", new_plan
            )
        sql = sql.replace(plannings_part, new_plan)

# 9. preferences_notifications - cree_le, modifie_le
if "CREATE TABLE preferences_notifications (" in sql:
    pref_part = sql.split("CREATE TABLE preferences_notifications (")[1].split(");")[0]
    if "cree_le" not in pref_part:
        # replace the last line or just append before )
        new_pref = pref_part.rstrip()
        if new_pref.endswith(","):
            new_pref += "\n    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),\n    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()\n"
        else:
            new_pref += ",\n    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),\n    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()\n"
        sql = sql.replace(pref_part, new_pref)

        trigger_def = """
CREATE TRIGGER trg_update_modifie_le_preferences_notifications
BEFORE UPDATE ON preferences_notifications
FOR EACH ROW
EXECUTE FUNCTION update_modifie_le_column();"""
        if "trg_update_modifie_le_preferences_notifications" not in sql:
            sql += trigger_def + "\n"

with open(path, "w", encoding="utf-8") as f:
    f.write(sql)
print("done!")
