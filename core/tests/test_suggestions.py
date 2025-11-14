# core/tests/test_suggestions.py
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
        # ensure child exists
        cur.execute("SELECT id FROM child_profiles LIMIT 1")
        r = cur.fetchone()
        if not r:
            cur.execute("INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)", ("test_child_sugg", "2024-01-01"))
            child_id = cur.lastrowid
        else:
            child_id = r[0]
        # ensure a batch meal exists
        cur.execute("SELECT id FROM batch_meals LIMIT 1")
        br = cur.fetchone()
        if not br:
            # create minimal recipe and batch meal
            cur.execute("INSERT INTO recipes (name, category, instructions) VALUES (?, ?, ?)",
                        ("suggest_recipe", "Test", "Do"))
            rid = cur.lastrowid
            cur.execute("INSERT INTO batch_meals (recipe_id, scheduled_date) VALUES (?, ?)", (rid, "2025-01-02"))
            conn.commit()
            br = cur.lastrowid
        batch_id = br[0] if isinstance(br, tuple) else br
        # Insert suggestion
        cur.execute("INSERT INTO suggestions (batch_meal_id, child_id, suggested_on, status) VALUES (?, ?, ?, ?)",
                    (batch_id, child_id, "2025-01-01T00:00:00", "proposé"))
        sid = cur.lastrowid
        conn.commit()
        # Update suggestion to accepted and create history
        cur.execute("UPDATE suggestions SET status = ? WHERE id = ?", ("accepté", sid))
        cur.execute("INSERT INTO suggestion_history (suggestion_id, acted_on, outcome) VALUES (?, ?, ?)",
                    (sid, "2025-01-01T01:00:00", "accepté"))
        conn.commit()
        # cleanup
        cur.execute("DELETE FROM suggestion_history WHERE suggestion_id = ?", (sid,))
        cur.execute("DELETE FROM suggestions WHERE id = ?", (sid,))
        conn.commit()
        conn.close()
        return TestResult(module="suggestions", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="suggestions", success=False, duration=time() - start, errors=[str(e)])