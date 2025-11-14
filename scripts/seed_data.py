# scripts/seed_data.py

from core.database import get_connection
from core.schema_manager import log_event

def seed_ingredients(cursor):
    ingredients = [
        ("Carotte", "kg"),
        ("Pomme", "pcs"),
        ("Oeuf", "pcs"),
        ("Lait", "L"),
        ("Farine", "g")
    ]
    cursor.executemany(
        "INSERT INTO ingredients (name, unit) VALUES (?, ?)", ingredients
    )
    log_event(f"{len(ingredients)} ingrédients insérés.")

def seed_recipes(cursor):
    recipes = [
        ("Purée de carottes", "Purée", "Éplucher, cuire, mixer"),
        ("Compote de pommes", "Dessert", "Éplucher, cuire, mixer"),
        ("Omelette", "Plat", "Battre, cuire à la poêle")
    ]
    cursor.executemany(
        "INSERT INTO recipes (name, category, instructions) VALUES (?, ?, ?)", recipes
    )
    log_event(f"{len(recipes)} recettes insérées.")

def seed_recipe_ingredients(cursor):
    mappings = [
        (1, 1, 0.3),  # Purée de carottes → Carotte 0.3kg
        (2, 2, 2),    # Compote de pommes → Pomme 2 pcs
        (3, 3, 2),    # Omelette → Oeuf 2 pcs
        (3, 5, 50)    # Omelette → Farine 50g
    ]
    cursor.executemany(
        "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
        mappings
    )
    log_event(f"{len(mappings)} liaisons recettes-ingredients insérées.")

def seed_inventory(cursor):
    items = [
        ("Carotte", "Légume", 10, "pcs"),
        ("Pomme", "Fruit", 5, "pcs"),
        ("Oeuf", "Protéine", 12, "pcs"),
        ("Lait", "Laitier", 2, "L"),
        ("Farine", "Farine", 1000, "g")
    ]
    cursor.executemany(
        "INSERT INTO inventory_items (name, category, quantity, unit) VALUES (?, ?, ?, ?)", items
    )
    log_event(f"{len(items)} items d'inventaire insérés.")

def seed_children(cursor):
    children = [
        ("Jules", "2024-06-22")
    ]
    cursor.executemany(
        "INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)", children
    )
    log_event(f"{len(children)} profils enfants insérés.")

def seed_wellbeing(cursor):
    entries = [
        (1, "2025-11-13", "Heureux", "Bonne journée")
    ]
    cursor.executemany(
        "INSERT INTO wellbeing_entries (child_id, date, mood, notes) VALUES (?, ?, ?, ?)", entries
    )
    log_event(f"{len(entries)} entrées bien-être insérées.")

def seed_projects(cursor):
    projects = [
        ("Aménagement jardin", "Créer un potager et une zone détente", "2025-04-01", "2025-12-31")
    ]
    cursor.executemany(
        "INSERT INTO projects (name, description, start_date, end_date) VALUES (?, ?, ?, ?)", projects
    )
    log_event(f"{len(projects)} projets insérés.")

def seed_project_tasks(cursor):
    tasks = [
        (1, "Préparer le sol", "En cours"),
        (1, "Planter les légumes", "À faire")
    ]
    cursor.executemany(
        "INSERT INTO project_tasks (project_id, task_name, status) VALUES (?, ?, ?)", tasks
    )
    log_event(f"{len(tasks)} tâches projets insérées.")

def seed_routines(cursor):
    routines = [
        ("Brossage de dents", 1),
        ("Lecture du soir", 1)
    ]
    cursor.executemany(
        "INSERT INTO routines (name, child_id) VALUES (?, ?)", routines
    )
    log_event(f"{len(routines)} routines insérées.")

def seed_routine_tasks(cursor):
    tasks = [
        (1, "Se brosser les dents", "20:00", "À faire"),
        (2, "Lire 1 histoire", "20:30", "À faire")
    ]
    cursor.executemany(
        "INSERT INTO routine_tasks (routine_id, task_name, scheduled_time, status) VALUES (?, ?, ?, ?)", tasks
    )
    log_event(f"{len(tasks)} tâches routines insérées.")

def seed_batch_meals(cursor):
    meals = [
        (1, "2025-11-14"),
        (2, "2025-11-15")
    ]
    cursor.executemany(
        "INSERT INTO batch_meals (recipe_id, scheduled_date) VALUES (?, ?)", meals
    )
    log_event(f"{len(meals)} repas batch insérés.")

def seed_batch_meal_items(cursor):
    items = [
        (1, 1, 0.3),
        (2, 2, 2)
    ]
    cursor.executemany(
        "INSERT INTO batch_meal_items (batch_meal_id, ingredient_id, quantity) VALUES (?, ?, ?)", items
    )
    log_event(f"{len(items)} items repas batch insérés.")

def seed_suggestions(cursor):
    suggestions = [
        (1, 1, "2025-11-13", "pending"),
        (2, 1, "2025-11-13", "pending")
    ]
    cursor.executemany(
        "INSERT INTO suggestions (batch_meal_id, child_id, suggested_on, status) VALUES (?, ?, ?, ?)", suggestions
    )
    log_event(f"{len(suggestions)} suggestions insérées.")

def seed_suggestion_history(cursor):
    history = [
        (1, "2025-11-13", "accepted")
    ]
    cursor.executemany(
        "INSERT INTO suggestion_history (suggestion_id, acted_on, outcome) VALUES (?, ?, ?)", history
    )
    log_event(f"{len(history)} historiques de suggestions insérés.")

def seed_notifications(cursor):
    notifications = [
        ("info", "Nouveau repas ajouté", "2025-11-13", 0)
    ]
    cursor.executemany(
        "INSERT INTO notifications (type, message, created_at, read) VALUES (?, ?, ?, ?)", notifications
    )
    log_event(f"{len(notifications)} notifications insérées.")

def seed_analytics(cursor):
    analytics = [
        ("recipes", '{"total":3}', "2025-11-13")
    ]
    cursor.executemany(
        "INSERT INTO analytics (module, data, created_at) VALUES (?, ?, ?)", analytics
    )
    log_event(f"{len(analytics)} entrées analytics insérées.")

def main():
    conn = get_connection()
    cursor = conn.cursor()

    # Appel de toutes les fonctions de seed
    seed_ingredients(cursor)
    seed_recipes(cursor)
    seed_recipe_ingredients(cursor)
    seed_inventory(cursor)
    seed_children(cursor)
    seed_wellbeing(cursor)
    seed_projects(cursor)
    seed_project_tasks(cursor)
    seed_routines(cursor)
    seed_routine_tasks(cursor)
    seed_batch_meals(cursor)
    seed_batch_meal_items(cursor)
    seed_suggestions(cursor)
    seed_suggestion_history(cursor)
    seed_notifications(cursor)
    seed_analytics(cursor)

    conn.commit()
    conn.close()
    log_event("Seed data complet de la phase 5 inséré avec succès.")

if __name__ == "__main__":
    main()