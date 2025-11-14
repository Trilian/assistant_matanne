# core/test_manager.py
import time
import traceback
from dataclasses import dataclass, asdict

from core.schema_manager import reset_tables, create_all_tables
from core.database import get_connection
from core.helpers import log_event

# Chaque test renvoie ce format
@dataclass
class TestResult:
    module: str
    success: bool
    duration: float
    errors: list

    def to_dict(self):
        return asdict(self)


# Import dynamique des tests par module
MODULE_TEST_MAP = {
    "suivi_enfant": "core.tests.test_suivi_enfant",
    "bien_etre": "core.tests.test_bien_etre",
    "inventaire": "core.tests.test_inventaire",
    "repas_batch": "core.tests.test_repas_batch",
    "suggestions": "core.tests.test_suggestions",
    "routines": "core.tests.test_routines",
    "projets_maison": "core.tests.test_projets_maison",
    "jardin": "core.tests.test_jardin",
    "parametres": "core.tests.test_parametres",
    "notifications": "core.tests.test_notifications",
}


# ========================================
#           FONCTIONS PRINCIPALES
# ========================================

def run_module_test(module_name: str) -> TestResult:
    """
    Lance un test pour un module.
    Chaque test_xxx.py contient une fonction run_test() qui renvoie un TestResult.
    """
    start = time.time()
    errors = []

    try:
        if module_name not in MODULE_TEST_MAP:
            raise Exception(f"Module inconnu : {module_name}")

        module_path = MODULE_TEST_MAP[module_name]

        mod = __import__(module_path, fromlist=["run_test"])
        result: TestResult = mod.run_test()

        duration = time.time() - start
        log_event(f"[TEST] {module_name} réussi ({duration:.2f}s)")

        return result

    except Exception as e:
        duration = time.time() - start
        tb = traceback.format_exc()
        errors.append(str(e))
        errors.append(tb)

        log_event(f"[TEST] Échec module {module_name} : {e}", level="error")

        return TestResult(
            module=module_name,
            success=False,
            duration=duration,
            errors=errors,
        )


def run_all_tests():
    """Lance tous les tests automatiquement."""
    results = []

    for module in MODULE_TEST_MAP.keys():
        result = run_module_test(module)
        results.append(result)

    return results


# ========================================
#         GESTION BASE DE DONNÉES
# ========================================

def reset_and_seed_db():
    """Réinitialise entièrement la base + données de test légère."""
    log_event("[TEST_MODE] Reset complet DB")
    reset_tables()
    generate_fake_data(level=1)


def check_db_integrity():
    """Vérifie l’intégrité de la base : tables, colonnes, incohérences."""
    conn = get_connection()
    cursor = conn.cursor()

    errors = []

    # Vérifie listes des tables déclarées vs existantes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing = [row[0] for row in cursor.fetchall()]

    missing = []
    from core.schema_manager import SCHEMA
    for table in SCHEMA.keys():
        if table not in existing:
            missing.append(table)

    if missing:
        errors.append(f"Tables manquantes : {missing}")

    # Vérifie quelques colonnes critiques pour éviter erreurs runtime
    critical_columns = {
        "wellbeing_adults": ["mood", "sleep_hours", "activity"],
        "batch_meals": ["recipe_id"],
        "routines": ["name"],
        "routine_tasks": ["task_name", "scheduled_time"],
    }

    for table, cols in critical_columns.items():
        try:
            cursor.execute(f"PRAGMA table_info({table});")
            existing_cols = [row[1] for row in cursor.fetchall()]

            for col in cols:
                if col not in existing_cols:
                    errors.append(f"Colonne manquante {col} dans {table}")

        except Exception as e:
            errors.append(f"Impossible de lire {table} : {e}")

    conn.close()
    return errors


# ========================================
#       GÉNÉRATION DE FAUSSES DONNÉES
# ========================================

def generate_fake_data(level=1):
    """
    Génère des données factices :
    - level 1 : léger
    - level 2 : réaliste
    - level 3 : stress test
    """
    import random
    conn = get_connection()
    cursor = conn.cursor()

    log_event(f"[TEST_MODE] Génération données niveau {level}")

    # Niveau 1 → données minimales
    if level >= 1:
        cursor.execute("INSERT INTO wellbeing_adults (person, date, mood, sleep_hours, activity) VALUES "
                       "('Anne', '2025-01-01', 'Content', 7.5, 'Yoga');")

        cursor.execute("INSERT INTO inventory_items (name, category, quantity, unit) VALUES "
                       "('Pâtes', 'Aliments', 0.1, 'kg');")

        cursor.execute("INSERT INTO recipes (name, category, instructions) VALUES "
                       "('Pâtes tomate', 'Dîner', 'Cuire, mélanger sauce');")

    # Niveau 2 → données réalistes
    if level >= 2:
        moods = ["Fatigué", "Content", "Stressé", "Énergique"]

        for i in range(10):
            cursor.execute(
                "INSERT INTO wellbeing_adults (person, date, mood, sleep_hours, activity) VALUES (?, ?, ?, ?, ?)",
                ("Mathieu", f"2025-01-{i+1:02d}", random.choice(moods), random.uniform(5, 8), "Sport")
            )

    # Niveau 3 → stress test
    if level == 3:
        for i in range(100):
            cursor.execute(
                "INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)",
                (f"Item {i}", "Divers", random.uniform(0, 10), "u")
            )

    conn.commit()
    conn.close()

    return True


# ========================================
#               RAPPORT
# ========================================

def get_test_report(results):
    """Transforme les résultats en structure pour affichage."""
    return [r.to_dict() for r in results]

# ========================================
#        DASHBOARD APRÈS LES TESTS
# ========================================

def open_test_dashboard(results):
    """
    Prépare les données pour affichage Streamlit.
    Ne dépend pas de Streamlit directement → propre et testable.
    """
    dashboard = {
        "total": len(results),
        "success_count": sum(1 for r in results if r.success),
        "fail_count": sum(1 for r in results if not r.success),
        "modules": []
    }

    for r in results:
        dashboard["modules"].append({
            "module": r.module,
            "success": r.success,
            "duration": r.duration,
            "errors": r.errors
        })

    return dashboard
