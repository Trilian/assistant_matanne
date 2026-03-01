import re

file_path = "d:\\Projet_streamlit\\assistant_matanne\\sql\\INIT_COMPLET.sql"

with open(file_path, encoding="utf-8") as f:
    content = f.read()

# 1. voyages table: Add budget_reel FLOAT, before cree_le.
if "budget_reel FLOAT" not in content:
    content = re.sub(
        r"(CREATE TABLE voyages\s*\(.*?)(\s*cree_le TIMESTAMP)",
        r"\1    budget_reel FLOAT,\2",
        content,
        flags=re.DOTALL,
    )

# 2. albums_famille table: Add date_debut DATE, and date_fin DATE, before cree_le.
if "date_debut DATE" not in content:
    content = re.sub(
        r"(CREATE TABLE albums_famille\s*\(.*?)(\s*cree_le TIMESTAMP)",
        r"\1    date_debut DATE,\n    date_fin DATE,\2",
        content,
        flags=re.DOTALL,
    )

# 3. contacts_famille table: Add sous_categorie VARCHAR(100), before cree_le.
if "sous_categorie VARCHAR(100)" not in content:
    content = re.sub(
        r"(CREATE TABLE contacts_famille\s*\(.*?)(\s*cree_le TIMESTAMP)",
        r"\1    sous_categorie VARCHAR(100),\2",
        content,
        flags=re.DOTALL,
    )

# 4. documents_famille table: Add titre VARCHAR(200), before fichier_nom.
if "titre VARCHAR(200)" not in content:
    content = re.sub(
        r"(CREATE TABLE documents_famille\s*\(.*?)(\s*fichier_nom VARCHAR)",
        r"\1    titre VARCHAR(200),\2",
        content,
        flags=re.DOTALL,
    )

# 5. ingredients table: Rename unite_mesure column to unite
if "unite VARCHAR(50)" not in content and "unite_mesure" in content:
    content = re.sub(
        r"(CREATE TABLE ingredients\s*\(.*?)(unite_mesure)(\s+VARCHAR)",
        r"\1unite\3",
        content,
        flags=re.DOTALL,
    )

# 6. taches_entretien table: Rename created_at -> cree_le, updated_at -> modifie_le.
if "CREATE TABLE taches_entretien" in content:
    match = re.search(r"CREATE TABLE taches_entretien\s*\((.*?)\);", content, re.DOTALL)
    if match:
        table_content = match.group(1)
        if "created_at" in table_content:
            new_table_content = table_content.replace("created_at", "cree_le").replace(
                "updated_at", "modifie_le"
            )
            content = content.replace(table_content, new_table_content)

# 7. profils_enfants table: Add taille_vetements JSONB DEFAULT '{}'::jsonb, and pointure VARCHAR(50), before cree_le.
if "taille_vetements JSONB" not in content:
    content = re.sub(
        r"(CREATE TABLE profils_enfants\s*\(.*?)(\s*cree_le TIMESTAMP)",
        r"\1    taille_vetements JSONB DEFAULT \'{}\'::jsonb,\n    pointure VARCHAR(50),\2",
        content,
        flags=re.DOTALL,
    )

# 8. plannings table: Rename semaine_du -> semaine_debut and semaine_au -> semaine_fin (if present).
# Add nom VARCHAR(200), before semaine_debut. Add actif BOOLEAN DEFAULT FALSE, and notes TEXT, before cree_le.
# Ensure there is an ix_plannings_semaine_debut index on semaine_debut.
if "CREATE TABLE plannings" in content:
    match = re.search(r"CREATE TABLE plannings\s*\((.*?)\);", content, re.DOTALL)
    if match:
        table_content = match.group(1)
        new_table_content = table_content.replace("semaine_du", "semaine_debut").replace(
            "semaine_au", "semaine_fin"
        )

        if "nom VARCHAR" not in new_table_content:
            new_table_content = re.sub(
                r"(\s*semaine_debut DATE)", r"\n    nom VARCHAR(200),\1", new_table_content
            )

        if "notes TEXT" not in new_table_content:
            new_table_content = re.sub(
                r"(\s*cree_le TIMESTAMP)",
                r"\n    actif BOOLEAN DEFAULT FALSE,\n    notes TEXT,\1",
                new_table_content,
            )

        content = content.replace(table_content, new_table_content)

    if "ix_plannings_semaine_du" in content:
        content = content.replace("ix_plannings_semaine_du", "ix_plannings_semaine_debut")
        content = content.replace("ON plannings(semaine_du)", "ON plannings(semaine_debut)")

    if "ix_plannings_semaine_debut" not in content:
        content += "\nCREATE INDEX ix_plannings_semaine_debut ON plannings(semaine_debut);\n"

# 9. preferences_notifications table: Rename created_at -> cree_le and updated_at -> modifie_le.
# Add them if they do not exist. Also add the trigger.
if "CREATE TABLE preferences_notifications" in content:
    match = re.search(r"CREATE TABLE preferences_notifications\s*\((.*?)\);", content, re.DOTALL)
    if match:
        table_content = match.group(1)
        new_table_content = table_content.replace("created_at", "cree_le").replace(
            "updated_at", "modifie_le"
        )

        if "cree_le TIMESTAMP" not in new_table_content:
            # Need to handle removing trailing comma or adding it
            if new_table_content.strip().endswith(","):
                new_table_content += "\n    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),\n    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()"
            else:
                new_table_content += ",\n    cree_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),\n    modifie_le TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()"

        content = content.replace(table_content, new_table_content)

if "CREATE TRIGGER trg_update_modifie_le_preferences_notifications" not in content:
    trigger_sql = """
CREATE TRIGGER trg_update_modifie_le_preferences_notifications
BEFORE UPDATE ON preferences_notifications
FOR EACH ROW EXECUTE FUNCTION update_modifie_le_column();
"""
    content += trigger_sql

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
