# core/tests/test_repas_batch.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection

def run_test():
    start = time()
    errors = []
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # ensure at least one recipe exists; create minimal if needed
        cur.execute("SELECT id FROM recipes LIMIT 1")
        r = cur.fetchone()
        if not r:
            cur.execute("INSERT INTO recipes (name, category, instructions) VALUES (?, ?, ?)",
                        ("test_recipe_for_batch", "Test", "Do test"))
            rid = cur.lastrowid
            # create ingredient and link
            cur.execute("INSERT INTO ingredients (name, unit) VALUES (?, ?)", ("test_ing", "u"))
            iid = cur.lastrowid
            cur.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                        (rid, iid, 1.0))
            conn.commit()
        else:
            rid = r[0]
        # Create a batch meal
        cur.execute("INSERT INTO batch_meals (recipe_id, scheduled_date) VALUES (?, ?)", (rid, "2025-01-01"))
        bid = cur.lastrowid
        conn.commit()
        # Add meal items based on recipe ingredients (if any)
        cur.execute("SELECT ingredient_id, quantity FROM recipe_ingredients WHERE recipe_id = ?", (rid,))
        ingrows = cur.fetchall()
        for ing_id, qty in ingrows:
            cur.execute("INSERT INTO batch_meal_items (batch_meal_id, ingredient_id, quantity) VALUES (?, ?, ?)",
                        (bid, ing_id, qty))
        conn.commit()
        # cleanup: remove batch meal and items
        cur.execute("DELETE FROM batch_meal_items WHERE batch_meal_id = ?", (bid,))
        cur.execute("DELETE FROM batch_meals WHERE id = ?", (bid,))
        conn.commit()
        conn.close()
        return TestResult(module="repas_batch", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="repas_batch", success=False, duration=time() - start, errors=[str(e)])