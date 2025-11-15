# core/schema_manager.py

import sqlite3
from core.database import get_connection
from core.helpers import log_event

# --- Définition du schéma global de la base ---
SCHEMA = {
    # Recettes et ingrédients
    "recipes": """
               CREATE TABLE IF NOT EXISTS recipes (
                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      name TEXT,
                                                      category TEXT,
                                                      instructions TEXT
               )
               """,
    "ingredients": """
                   CREATE TABLE IF NOT EXISTS ingredients (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              name TEXT,
                                                              unit TEXT
                   )
                   """,
    "recipe_ingredients": """
                          CREATE TABLE IF NOT EXISTS recipe_ingredients (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                            recipe_id INTEGER,
                                                                            ingredient_id INTEGER,
                                                                            quantity REAL,
                                                                            FOREIGN KEY(recipe_id) REFERENCES recipes(id),
                              FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
                              )
                          """,

    # Inventaire et courses
    "inventory_items": """
                       CREATE TABLE IF NOT EXISTS inventory_items (
                                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                      name TEXT,
                                                                      category TEXT,
                                                                      quantity REAL,
                                                                      unit TEXT
                       )
                       """,
    "courses": """
               CREATE TABLE IF NOT EXISTS courses (
                                                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      item_id INTEGER,
                                                      needed_quantity REAL,
                                                      FOREIGN KEY(item_id) REFERENCES inventory_items(id)
                   )
               """,

    # Repas batch
    "batch_meals": """
                   CREATE TABLE IF NOT EXISTS batch_meals (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              recipe_id INTEGER,
                                                              scheduled_date TEXT,
                                                              FOREIGN KEY(recipe_id) REFERENCES recipes(id)
                       )
                   """,
    "batch_meal_items": """
                        CREATE TABLE IF NOT EXISTS batch_meal_items (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        batch_meal_id INTEGER,
                                                                        ingredient_id INTEGER,
                                                                        quantity REAL,
                                                                        FOREIGN KEY(batch_meal_id) REFERENCES batch_meals(id),
                            FOREIGN KEY(ingredient_id) REFERENCES ingredients(id)
                            )
                        """,

    # Suggestions
    "suggestions": """
                   CREATE TABLE IF NOT EXISTS suggestions (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              batch_meal_id INTEGER,
                                                              child_id INTEGER,
                                                              suggested_on TEXT,
                                                              status TEXT,
                                                              FOREIGN KEY(batch_meal_id) REFERENCES batch_meals(id),
                       FOREIGN KEY(child_id) REFERENCES child_profiles(id)
                       )
                   """,
    "suggestion_history": """
                          CREATE TABLE IF NOT EXISTS suggestion_history (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                            suggestion_id INTEGER,
                                                                            acted_on TEXT,
                                                                            outcome TEXT,
                                                                            FOREIGN KEY(suggestion_id) REFERENCES suggestions(id)
                              )
                          """,

    # Routines et tâches
    "routines": """
                CREATE TABLE IF NOT EXISTS routines (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        name TEXT,
                                                        child_id INTEGER,
                                                        FOREIGN KEY(child_id) REFERENCES child_profiles(id)
                    )
                """,
    "routine_tasks": """
                     CREATE TABLE IF NOT EXISTS routine_tasks (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  routine_id INTEGER,
                                                                  task_name TEXT,
                                                                  scheduled_time TEXT,
                                                                  status TEXT,
                                                                  FOREIGN KEY(routine_id) REFERENCES routines(id)
                         )
                     """,
    "routine_logs": """
                    CREATE TABLE IF NOT EXISTS routine_logs (
                                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                routine_task_id INTEGER,
                                                                completed_on TEXT,
                                                                FOREIGN KEY(routine_task_id) REFERENCES routine_tasks(id)
                        )
                    """,

    # Profil enfant
    "child_profiles": """
                      CREATE TABLE IF NOT EXISTS child_profiles (
                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    name TEXT,
                                                                    birth_date TEXT
                      )
                      """,

    # Projets maison
    "projects": """
                CREATE TABLE IF NOT EXISTS projects (
                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        name TEXT,
                                                        description TEXT,
                                                        start_date TEXT,
                                                        end_date TEXT,
                                                        priority TEXT
                )
                """,

    "project_tasks": """
                     CREATE TABLE IF NOT EXISTS project_tasks (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  project_id INTEGER,
                                                                  task_name TEXT,
                                                                  status TEXT,
                                                                  due_date TEXT,
                                                                  FOREIGN KEY(project_id) REFERENCES projects(id)
                         )
                     """,

    # Bien-être
    "wellbeing_entries": """
                         CREATE TABLE IF NOT EXISTS wellbeing_entries (
                                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                          child_id INTEGER,
                                                                          date TEXT,
                                                                          mood TEXT,
                                                                          notes TEXT,
                                                                          sleep_hours REAL,
                                                                          activity TEXT,
                                                                          username TEXT,
                                                                          FOREIGN KEY(child_id) REFERENCES child_profiles(id)
                             )
                         """,

    # Jardin
    "garden_items": """
                    CREATE TABLE IF NOT EXISTS garden_items (
                                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                name TEXT,
                                                                category TEXT,
                                                                quantity REAL,
                                                                unit TEXT,
                                                                planting_date TEXT,
                                                                harvest_date TEXT,
                                                                watering_frequency_days INTEGER  -- fréquence d'arrosage en jours
                    )
                    """,

    "garden_reminders": """
                        CREATE TABLE IF NOT EXISTS garden_reminders (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                        item_id INTEGER,
                                                                        reminder_type TEXT,        -- "arrosage" ou "recolte"
                                                                        scheduled_date TEXT,
                                                                        status TEXT DEFAULT 'pending',
                                                                        created_at TEXT DEFAULT (datetime('now')),
                            FOREIGN KEY(item_id) REFERENCES garden_items(id)
                            )
                        """,

    "garden_logs": """
                   CREATE TABLE IF NOT EXISTS garden_logs (
                                                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              item_id INTEGER,
                                                              action TEXT,               -- "arrose", "recolte", "seme", etc.
                                                              date TEXT,
                                                              notes TEXT,
                                                              created_at TEXT DEFAULT (datetime('now')),
                       FOREIGN KEY(item_id) REFERENCES garden_items(id)
                       )
                   """,

    # Notifications
    "notifications": """
                     CREATE TABLE IF NOT EXISTS notifications (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  type TEXT,
                                                                  message TEXT,
                                                                  created_at TEXT,
                                                                  read INTEGER DEFAULT 0
                     )
                     """,

    # Analytics / dashboards
    "analytics": """
                 CREATE TABLE IF NOT EXISTS analytics (
                                                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          module TEXT,
                                                          data TEXT,
                                                          created_at TEXT
                 )
                 """,

    # Utilisateurs / paramètres
    "users": """
             CREATE TABLE IF NOT EXISTS users (
                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                  username TEXT,
                                                  settings TEXT
             )
             """,

    # Profils utilisateurs (multi-profils)
    "user_profiles": """
                     CREATE TABLE IF NOT EXISTS user_profiles (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  user_id INTEGER,
                                                                  profile_name TEXT,
                                                                  role TEXT,
                                                                  preferences TEXT,
                                                                  FOREIGN KEY(user_id) REFERENCES users(id)
                         )
                     """,

    # Notifications liées aux utilisateurs
    "user_notifications": """
                          CREATE TABLE IF NOT EXISTS user_notifications (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                            user_id INTEGER,
                                                                            module TEXT,
                                                                            message TEXT,
                                                                            created_at TEXT DEFAULT (datetime('now')),
                                                                            read INTEGER DEFAULT 0,
                                                                            FOREIGN KEY(user_id) REFERENCES users(id)
                              )
                          """,
    # Événements de calendrier externes (Google Calendar)
    "external_calendar_events": """
                                CREATE TABLE IF NOT EXISTS external_calendar_events (
                                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                                        gcal_id TEXT UNIQUE,
                                                                                        title TEXT,
                                                                                        start_date TEXT,
                                                                                        end_date TEXT,
                                                                                        raw_json TEXT
                                )
                                """,
}

# --- Fonctions utilitaires ---
def create_all_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Création de toutes les tables
    for name, ddl in SCHEMA.items():
        cursor.execute(ddl)
        log_event(f"Table '{name}' vérifiée/créée")

    # Important : valider d'abord la création des tables
    conn.commit()

    # Maintenant que les tables existent, on peut créer les index
    cursor.execute("""
                   CREATE INDEX IF NOT EXISTS idx_external_events_start
                       ON external_calendar_events(start_date)
                   """)

    conn.commit()
    conn.close()



def drop_all_tables():
    conn = get_connection()
    cursor = conn.cursor()
    for name in SCHEMA.keys():
        cursor.execute(f"DROP TABLE IF EXISTS {name}")
        log_event(f"Table '{name}' supprimée")
    conn.commit()
    conn.close()

def reset_tables():
    drop_all_tables()
    create_all_tables()

def check_missing_tables():
    conn = get_connection()
    cursor = conn.cursor()
    existing_tables = [row[0] for row in cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()]
    missing = [name for name in SCHEMA.keys() if name not in existing_tables]
    conn.close()
    return missing
