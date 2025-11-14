# core/tests/test_suivi_enfant.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection
from core.helpers import log_event

def run_test():
    start = time()
    errors = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        # Insert a child if none
        cur.execute("SELECT id FROM child_profiles WHERE name = ?", ("Jules",))
        r = cur.fetchone()
        if not r:
            cur.execute("INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)", ("Jules", "2024-06-22"))
            conn.commit()
        # Add a sample development entry (non destructive)
        cur.execute("INSERT INTO child_profiles (name, birth_date) VALUES (?, ?)", ("test_child_for_tests", "2024-01-01"))
        cid = cur.lastrowid
        conn.commit()
        # basic read
        cur.execute("SELECT id, name FROM child_profiles WHERE id = ?", (cid,))
        _ = cur.fetchone()
        # cleanup minimal (delete the test child)
        cur.execute("DELETE FROM child_profiles WHERE id = ?", (cid,))
        conn.commit()
        conn.close()
        return TestResult(module="suivi_enfant", success=True, duration=time() - start, errors=[])
    except Exception as e:
        log_event(f"[TEST suivi_enfant] error: {e}")
        errors.append(str(e))
        try:
            conn.close()
        except:
            pass
        return TestResult(module="suivi_enfant", success=False, duration=time() - start, errors=errors)