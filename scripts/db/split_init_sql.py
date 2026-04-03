#!/usr/bin/env python3
"""Découpe INIT_COMPLET.sql en fichiers thématiques dans sql/schema/.

Ce script lit sql/INIT_COMPLET.sql et génère des fichiers par domaine
dans sql/schema/. Les fichiers sont ordonnés pour que l'outil
regenerate_init.py puisse les reconstituer dans le bon ordre.

Usage:
    python scripts/db/split_init_sql.py [--dry-run]

Structure générée:
    sql/schema/
    ├── 01_extensions.sql        → Extensions PostgreSQL + BEGIN
    ├── 02_functions.sql         → Fonctions trigger + helpers
    ├── 03_systeme.sql           → Tables système (migrations, profils, config)
    ├── 04_cuisine.sql           → Tables cuisine (recettes, inventaire, courses, planning)
    ├── 05_famille.sql           → Tables famille (profils enfants, activités, santé, Garmin)
    ├── 06a_projets.sql          → Maison : projets et routines
    ├── 06b_entretien.sql        → Maison : entretien et organisation
    ├── 06c_jardin.sql           → Maison : jardin et autonomie
    ├── 06d_equipements.sql      → Maison : équipements, travaux et diagnostics
    ├── 06e_energie.sql          → Maison : énergie, abonnements et charges
    ├── 07_habitat.sql           → Tables habitat (scénarios, plans, annonces)
    ├── 08_jeux.sql              → Tables jeux (paris, loto, euromillions)
    ├── 09_notifications.sql     → Tables notifications (push, webhooks, préférences)
    ├── 10_finances.sql          → Tables finances (dépenses, budgets, calendriers)
    ├── 11_utilitaires.sql       → Tables utilitaires (notes, journal, contacts, énergie)
    ├── 12_triggers.sql          → Triggers modifie_le
    ├── 13_views.sql             → Vues utiles
    ├── 14_indexes.sql           → Index supplémentaires
    ├── 15_rls_policies.sql      → Politiques Row Level Security
    ├── 16_seed_data.sql         → Données de référence
    └── 17_migrations_absorbees.sql → Migrations V005-V007 absorbées
"""

import argparse
import re
import sys
from pathlib import Path

# ─── Chemins ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
SQL_SOURCE = ROOT / "sql" / "INIT_COMPLET.sql"
SCHEMA_DIR = ROOT / "sql" / "schema"

# ─── Mapping table → domaine ─────────────────────────────────────────────────
# Chaque table est assignée à un fichier de domaine.
# Les tables non listées ici vont dans le domaine de la PARTIE où elles se trouvent.

TABLE_DOMAIN: dict[str, str] = {
    # --- SYSTÈME ---
    "schema_migrations": "systeme",
    "profils_utilisateurs": "systeme",
    "preferences_utilisateurs": "systeme",
    "alertes_meteo": "systeme",
    "config_meteo": "systeme",
    "sauvegardes": "systeme",
    "historique_actions": "systeme",
    "etats_persistants": "systeme",
    "points_utilisateurs": "systeme",
    "badges_utilisateurs": "systeme",
    "automations": "systeme",
    "logs_securite": "systeme",
    "job_executions": "systeme",
    "openfoodfacts_cache": "systeme",
    # --- CUISINE ---
    "ingredients": "cuisine",
    "recettes": "cuisine",
    "plannings": "cuisine",
    "listes_courses": "cuisine",
    "modeles_courses": "cuisine",
    "templates_semaine": "cuisine",
    "config_batch_cooking": "cuisine",
    "recette_ingredients": "cuisine",
    "etapes_recette": "cuisine",
    "versions_recette": "cuisine",
    "historique_recettes": "cuisine",
    "repas_batch": "cuisine",
    "retours_recettes": "cuisine",
    "inventaire": "cuisine",
    "historique_inventaire": "cuisine",
    "articles_courses": "cuisine",
    "articles_modeles": "cuisine",
    "repas": "cuisine",
    "elements_templates": "cuisine",
    "sessions_batch_cooking": "cuisine",
    "etapes_batch_cooking": "cuisine",
    "preparations_batch": "cuisine",
    # --- FAMILLE ---
    "profils_enfants": "famille",
    "routines_sante": "famille",
    "objectifs_sante": "famille",
    "activites_weekend": "famille",
    "achats_famille": "famille",
    "activites_famille": "famille",
    "budgets_famille": "famille",
    "articles_achats_famille": "famille",
    "historique_achats": "famille",
    "garmin_tokens": "famille",
    "activites_garmin": "famille",
    "resumes_quotidiens_garmin": "famille",
    "journaux_alimentaires": "famille",
    "entrees_bien_etre": "famille",
    "jalons": "famille",
    "entrees_sante": "famille",
    "vaccins": "famille",
    "rendez_vous_medicaux": "famille",
    "mesures_croissance": "famille",
    "contacts_famille": "famille",
    "anniversaires_famille": "famille",
    "evenements_familiaux": "famille",
    "documents_famille": "famille",
    # --- MAISON : PROJETS & ROUTINES ---
    "projets": "maison_projets",
    "routines": "maison_projets",
    "taches_projets": "maison_projets",
    "taches_routines": "maison_projets",
    # --- MAISON : ENTRETIEN & ORGANISATION ---
    "taches_entretien": "maison_entretien",
    "preferences_home": "maison_entretien",
    "taches_home": "maison_entretien",
    "stats_home": "maison_entretien",
    "checklists_vacances": "maison_entretien",
    "items_checklist": "maison_entretien",
    # --- MAISON : JARDIN & AUTONOMIE ---
    "elements_jardin": "maison_jardin",
    "plans_jardin": "maison_jardin",
    "journaux_jardin": "maison_jardin",
    "zones_jardin": "maison_jardin",
    "plantes_jardin": "maison_jardin",
    "actions_plantes": "maison_jardin",
    "plantes_catalogue": "maison_jardin",
    "recoltes": "maison_jardin",
    "objectifs_autonomie": "maison_jardin",
    # --- MAISON : EQUIPEMENTS & TRAVAUX ---
    "meubles": "maison_equipements",
    "stocks_maison": "maison_equipements",
    "pieces_maison": "maison_equipements",
    "objets_maison": "maison_equipements",
    "sessions_travail": "maison_equipements",
    "versions_pieces": "maison_equipements",
    "couts_travaux": "maison_equipements",
    "logs_statut_objets": "maison_equipements",
    "artisans": "maison_equipements",
    "interventions_artisans": "maison_equipements",
    "articles_cellier": "maison_equipements",
    "diagnostics_maison": "maison_equipements",
    "estimations_immobilieres": "maison_equipements",
    "traitements_nuisibles": "maison_equipements",
    "devis_comparatifs": "maison_equipements",
    "lignes_devis": "maison_equipements",
    # --- MAISON : ENERGIE & CHARGES ---
    "depenses_maison": "maison_energie",
    "actions_ecologiques": "maison_energie",
    "depenses_home": "maison_energie",
    "budgets_home": "maison_energie",
    "entretiens_saisonniers": "maison_energie",
    "releves_compteurs": "maison_energie",
    "abonnements": "maison_energie",
    "contrats": "maison_energie",
    "factures": "maison_energie",
    "comparatifs": "maison_energie",
    "contrats_maison": "maison_energie",
    "garanties": "maison_equipements",
    "incidents_sav": "maison_equipements",
    # --- HABITAT ---
    "habitat_scenarios": "habitat",
    "habitat_criteres": "habitat",
    "habitat_criteres_immo": "habitat",
    "habitat_annonces": "habitat",
    "habitat_plans": "habitat",
    "habitat_pieces": "habitat",
    "habitat_modifications_plan": "habitat",
    "habitat_projets_deco": "habitat",
    "habitat_zones_jardin": "habitat",
    # --- JEUX ---
    "jeux_equipes": "jeux",
    "jeux_tirages_loto": "jeux",
    "jeux_stats_loto": "jeux",
    "jeux_historique": "jeux",
    "jeux_series": "jeux",
    "jeux_configuration": "jeux",
    "jeux_matchs": "jeux",
    "jeux_paris_sportifs": "jeux",
    "jeux_grilles_loto": "jeux",
    "jeux_alertes": "jeux",
    "jeux_tirages_euromillions": "jeux",
    "jeux_grilles_euromillions": "jeux",
    "jeux_stats_euromillions": "jeux",
    "jeux_cotes_historique": "jeux",
    # --- NOTIFICATIONS ---
    "abonnements_push": "notifications",
    "preferences_notifications": "notifications",
    "webhooks_abonnements": "notifications",
    # --- FINANCES ---
    "depenses": "finances",
    "budgets_mensuels": "finances",
    "calendriers_externes": "finances",
    "configs_calendriers_externes": "finances",
    "evenements_calendrier": "finances",
    # --- UTILITAIRES ---
    "notes_memos": "utilitaires",
    "journal_bord": "utilitaires",
    "contacts_utiles": "utilitaires",
    "liens_favoris": "utilitaires",
    "mots_de_passe_maison": "utilitaires",
    "presse_papier_entrees": "utilitaires",
    "releves_energie": "utilitaires",
    "voyages": "utilitaires",
    "checklists_voyage": "utilitaires",
    "templates_checklist": "utilitaires",
}

# ─── Headers des fichiers de domaine ─────────────────────────────────────────
DOMAIN_HEADERS: dict[str, str] = {
    "systeme": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Système
-- ============================================================================
-- Contient : schema_migrations, profils_utilisateurs, preferences_utilisateurs,
--            config_meteo, alertes_meteo, sauvegardes, historique_actions,
--            etats_persistants, gamification, automations, logs_securite,
--            job_executions, openfoodfacts_cache
-- ============================================================================
""",
    "cuisine": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Cuisine
-- ============================================================================
-- Contient : ingredients, recettes, inventaire, listes_courses, plannings,
--            modeles_courses, templates_semaine, batch_cooking, ...
-- ============================================================================
""",
    "famille": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Famille
-- ============================================================================
-- Contient : profils_enfants, activités_famille, budgets_famille, Garmin,
--            santé, jalons, contacts, documents, anniversaires
-- ============================================================================
""",
    "maison_projets": """\
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Projets & Routines
-- ============================================================================
-- Contient : projets, routines, tâches projet, tâches routine
-- ============================================================================
""",
    "maison_entretien": """\
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Entretien & Organisation
-- ============================================================================
-- Contient : entretien, préférences home, tâches home, stats, checklists
-- ============================================================================
""",
    "maison_jardin": """\
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Jardin & Autonomie
-- ============================================================================
-- Contient : jardin, plans, zones, plantes, récoltes, autonomie alimentaire
-- ============================================================================
""",
    "maison_equipements": """\
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Equipements & Travaux
-- ============================================================================
-- Contient : meubles, stocks, pièces, objets, artisans, devis, diagnostics
-- ============================================================================
""",
    "maison_energie": """\
-- ============================================================================
-- ASSISTANT MATANNE — Maison : Energie & Charges
-- ============================================================================
-- Contient : dépenses, abonnements, écologie, entretiens saisonniers, compteurs
-- ============================================================================
""",
    "habitat": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Habitat
-- ============================================================================
-- Contient : habitat_scenarios, habitat_plans, habitat_pieces,
--            habitat_criteres_immo, habitat_annonces, habitat_projets_deco
-- ============================================================================
""",
    "jeux": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Jeux
-- ============================================================================
-- Contient : jeux_equipes, jeux_matchs, paris_sportifs, loto, euromillions,
--            séries, alertes, cotes_historique
-- ============================================================================
""",
    "notifications": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Notifications
-- ============================================================================
-- Contient : abonnements_push, preferences_notifications, webhooks_abonnements
-- ============================================================================
""",
    "finances": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Finances
-- ============================================================================
-- Contient : depenses, budgets_mensuels, calendriers_externes,
--            configs_calendriers_externes, evenements_calendrier
-- ============================================================================
""",
    "utilitaires": """\
-- ============================================================================
-- ASSISTANT MATANNE — Tables Utilitaires
-- ============================================================================
-- Contient : notes_memos, journal_bord, contacts_utiles, liens_favoris,
--            mots_de_passe_maison, presse_papier_entrees, releves_energie,
--            voyages, checklists_voyage, templates_checklist
-- ============================================================================
""",
}

# ─── Ordre de génération pour regenerate_init.py ────────────────────────────
GENERATION_ORDER = [
    ("01_extensions.sql", "BEGIN; + extensions"),
    ("02_functions.sql", "Fonctions trigger + helpers"),
    ("03_systeme.sql", "Tables système"),
    ("04_cuisine.sql", "Tables cuisine"),
    ("05_famille.sql", "Tables famille"),
    ("06a_projets.sql", "Maison : projets & routines"),
    ("06b_entretien.sql", "Maison : entretien & organisation"),
    ("06c_jardin.sql", "Maison : jardin & autonomie"),
    ("06d_equipements.sql", "Maison : équipements & travaux"),
    ("06e_energie.sql", "Maison : énergie & charges"),
    ("07_habitat.sql", "Tables habitat"),
    ("08_jeux.sql", "Tables jeux"),
    ("09_notifications.sql", "Tables notifications"),
    ("10_finances.sql", "Tables finances"),
    ("11_utilitaires.sql", "Tables utilitaires"),
    ("12_triggers.sql", "Triggers modifie_le"),
    ("13_views.sql", "Vues utiles"),
    ("14_indexes.sql", "Index supplémentaires"),
    ("15_rls_policies.sql", "Row Level Security"),
    ("16_seed_data.sql", "Données de référence"),
    ("17_migrations_absorbees.sql", "V005-V007 migrations absorbées"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans écriture")
    parser.add_argument("--source", default=str(SQL_SOURCE), help="Fichier SQL source")
    parser.add_argument("--output", default=str(SCHEMA_DIR), help="Répertoire de sortie")
    return parser.parse_args()


def detect_table_name(block: str) -> str | None:
    """Extrait le nom de table d'un bloc CREATE TABLE."""
    m = re.search(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(", block, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return None


def split_into_sections(lines: list[str]) -> dict[str, str]:
    """Découpe les lignes en sections nommées selon les PARTIE markers."""
    sections: dict[str, list[str]] = {
        "header": [],
        "drop_all": [],
        "functions": [],
        "tables_all": [],
        "triggers": [],
        "views": [],
        "rls": [],
        "seed_data": [],
        "extra": [],
    }

    PARTIE_MAP = {
        "PARTIE 0": "drop_all",
        "PARTIE 1": "functions",
        "PARTIE 2": "tables_all",
        "PARTIE 3": "tables_all",
        "PARTIE 4": "tables_all",
        "PARTIE 5": "tables_all",
        "PARTIE 5B": "tables_all",
        "PARTIE 5C": "tables_all",
        "PARTIE 5D": "tables_all",
        "PARTIE 6": "triggers",
        "PARTIE 7": "views",
        "PARTIE 8": "functions",
        "PARTIE 9": "rls",
        "PARTIE 10": "seed_data",
        "PARTIE 11": "extra",
    }

    current_section = "header"

    for line in lines:
        # Détecter changement de PARTIE
        m = re.match(r"^-- PARTIE (\d+[B-D]?)\s*:", line)
        if m:
            partie_key = f"PARTIE {m.group(1)}"
            current_section = PARTIE_MAP.get(partie_key, "extra")

        sections[current_section].append(line)

    return {k: "".join(v) for k, v in sections.items()}


def assign_table_blocks_to_domains(tables_sql: str) -> dict[str, list[str]]:
    """Assigne chaque bloc CREATE TABLE au domaine approprié."""
    domain_blocks: dict[str, list[str]] = {
        "systeme": [],
        "cuisine": [],
        "famille": [],
        "maison_projets": [],
        "maison_entretien": [],
        "maison_jardin": [],
        "maison_equipements": [],
        "maison_energie": [],
        "habitat": [],
        "jeux": [],
        "notifications": [],
        "finances": [],
        "utilitaires": [],
    }

    # Tokeniser en blocs : chaque commentaire "-- N.NN" ou "-- PARTIE" commence un bloc
    # On split par sections numérotées
    block_pattern = re.compile(r"(-- [─\-].*?\n(?:-- [^─\-\n].*?\n)*)", re.MULTILINE)

    # Approche plus simple : on garde les blocs délimités par les séparateurs "──"
    # et on regarde le CREATE TABLE dans chaque bloc

    # Split par les séparateurs "──────..." ou "PARTIE" sous-sections
    separator_re = re.compile(
        r"(?=-- [─]{20,}|(?=-- (?:PARTIE )))",
        re.MULTILINE
    )

    current_block: list[str] = []
    current_domain = "systeme"  # défaut

    for line in tables_sql.splitlines(keepends=True):
        # Détecter les commentaires de section
        if re.match(r"^-- [─]{10,}", line):
            # Fin du bloc précédent
            block_text = "".join(current_block)
            if block_text.strip():
                table_name = detect_table_name(block_text)
                if table_name:
                    domain = TABLE_DOMAIN.get(table_name, "systeme")
                else:
                    domain = current_domain
                domain_blocks[domain].append(block_text)
            current_block = [line]
        else:
            current_block.append(line)

    # Dernier bloc
    if current_block:
        block_text = "".join(current_block)
        if block_text.strip():
            table_name = detect_table_name(block_text)
            if table_name:
                domain = TABLE_DOMAIN.get(table_name, "systeme")
            else:
                domain = current_domain
            domain_blocks[domain].append(block_text)

    return domain_blocks


def find_extra_migrations_start(lines: list[str]) -> int:
    """Trouve la ligne de début des migrations absorbées (après COMMIT)."""
    for i, line in enumerate(lines):
        if line.strip() == "COMMIT;":
            return i + 1
    return len(lines)


def main() -> int:
    args = parse_args()
    source_path = Path(args.source)
    output_dir = Path(args.output)

    if not source_path.exists():
        print(f"Erreur: {source_path} introuvable", file=sys.stderr)
        return 1

    print(f"Lecture de {source_path} ({source_path.stat().st_size // 1024} Ko)...")
    content = source_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    print(f"  → {len(lines)} lignes")

    # ── Sections brutes ──────────────────────────────────────────────────────
    sections = split_into_sections(lines)

    # ── Domaines pour les tables ─────────────────────────────────────────────
    domain_blocks = assign_table_blocks_to_domains(sections["tables_all"])

    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    def write_file(filename: str, content_str: str) -> None:
        target = output_dir / filename
        if args.dry_run:
            print(f"  [dry-run] {target} ({len(content_str.splitlines())} lignes)")
        else:
            target.write_text(content_str, encoding="utf-8")
            print(f"  → {target} ({len(content_str.splitlines())} lignes)")

    # ── 01_extensions.sql ────────────────────────────────────────────────────
    write_file("01_extensions.sql", """\
-- ============================================================================
-- ASSISTANT MATANNE — Extensions & Transaction
-- ============================================================================
-- Extensions PostgreSQL requises et démarrage de la transaction.
-- Ce fichier est le PREMIER à être exécuté par regenerate_init.py
-- ============================================================================

BEGIN;
""")

    # ── 02_functions.sql ─────────────────────────────────────────────────────
    write_file("02_functions.sql", sections["functions"])

    # ── 03_systeme.sql → 11_utilitaires.sql (domaines) ───────────────────────
    domain_file_map = {
        "systeme": "03_systeme.sql",
        "cuisine": "04_cuisine.sql",
        "famille": "05_famille.sql",
        "maison_projets": "06a_projets.sql",
        "maison_entretien": "06b_entretien.sql",
        "maison_jardin": "06c_jardin.sql",
        "maison_equipements": "06d_equipements.sql",
        "maison_energie": "06e_energie.sql",
        "habitat": "07_habitat.sql",
        "jeux": "08_jeux.sql",
        "notifications": "09_notifications.sql",
        "finances": "10_finances.sql",
        "utilitaires": "11_utilitaires.sql",
    }

    for domain, filename in domain_file_map.items():
        blocks = domain_blocks.get(domain, [])
        header = DOMAIN_HEADERS.get(domain, f"-- {domain}\n")
        content_str = header + "\n".join(blocks) + "\n"
        write_file(filename, content_str)

    # ── 12_triggers.sql ──────────────────────────────────────────────────────
    write_file("12_triggers.sql", sections["triggers"])

    # ── 13_views.sql ─────────────────────────────────────────────────────────
    write_file("13_views.sql", sections["views"])

    # ── 14_indexes.sql ───────────────────────────────────────────────────────
    # Index supplémentaires (inline dans les CREATE TABLE + extra à la fin)
    write_file("14_indexes.sql", """\
-- ============================================================================
-- ASSISTANT MATANNE — Index supplémentaires
-- ============================================================================
-- Index composites et index de performance ajoutés après V005.
-- La majorité des index sont inline avec les CREATE TABLE dans les fichiers
-- de domaine (03-11). Ce fichier contient uniquement les index additionnels.
-- ============================================================================

-- Consolidation V005 : Index composites porte-parole performance
CREATE INDEX IF NOT EXISTS ix_repas_planning_date ON repas(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS ix_repas_planning_type ON repas(planning_id, type_repas);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_achete ON articles_courses(liste_id, achete);
CREATE INDEX IF NOT EXISTS ix_articles_courses_liste_priorite ON articles_courses(liste_id, priorite);
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_quantite ON inventaire(date_peremption, quantite)
    WHERE date_peremption IS NOT NULL;
CREATE INDEX IF NOT EXISTS ix_historique_inventaire_ingredient_date ON historique_inventaire(ingredient_id, date_modification);
CREATE INDEX IF NOT EXISTS ix_listes_courses_statut_semaine ON listes_courses(statut, semaine_du);
CREATE INDEX IF NOT EXISTS ix_plannings_actif_semaine ON plannings(actif, semaine_debut) WHERE actif = TRUE;

-- Index migration V001-V004 (absorbés)
CREATE INDEX IF NOT EXISTS idx_articles_inventaire_peremption
    ON articles_inventaire(date_peremption);
CREATE INDEX IF NOT EXISTS idx_repas_planning_planning_date
    ON repas_planning(planning_id, date_repas);
CREATE INDEX IF NOT EXISTS idx_historique_actions_user_date
    ON historique_actions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_paris_sportifs_statut_user
    ON paris_sportifs(statut, user_id);
""")

    # ── 15_rls_policies.sql ──────────────────────────────────────────────────
    write_file("15_rls_policies.sql", sections["rls"])

    # ── 16_seed_data.sql ─────────────────────────────────────────────────────
    write_file("16_seed_data.sql", sections["seed_data"])

    # ── 17_migrations_absorbees.sql ──────────────────────────────────────────
    extra_content = sections.get("extra", "")
    # Ajouter le COMMIT
    write_file("17_migrations_absorbees.sql", """\
-- ============================================================================
-- ASSISTANT MATANNE — Migrations absorbées (V005-V007)
-- ============================================================================
-- Ce fichier contient les changements des migrations V005, V006, V007
-- qui ont été absorbés dans le script principal.
-- Contexte : stratégie SQL-first (pas d'Alembic auto).
-- ============================================================================

""" + extra_content)

    # ── 99_footer.sql ────────────────────────────────────────────────────────
    write_file("99_footer.sql", """\
-- ============================================================================
-- ASSISTANT MATANNE — Vérification finale & COMMIT
-- ============================================================================

-- Grants Supabase (déjà dans seed_data, ici pour réexécution idempotente)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Vérification finale
SELECT tablename,
    (SELECT COUNT(*) FROM information_schema.columns c
     WHERE c.table_name = t.tablename) AS nb_colonnes
FROM pg_tables t
WHERE schemaname = 'public'
ORDER BY tablename;

COMMIT;
""")

    # ── Rapport ──────────────────────────────────────────────────────────────
    print("\n✅ Découpage terminé!")
    if not args.dry_run:
        files = sorted(output_dir.glob("*.sql"))
        total_lines = sum(f.read_text(encoding="utf-8").count("\n") for f in files)
        print(f"   {len(files)} fichiers créés dans {output_dir}")
        print(f"   {total_lines} lignes au total")

    return 0


if __name__ == "__main__":
    sys.exit(main())
