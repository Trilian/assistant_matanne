# core/tests/test_parametres.py
from time import time
from core.test_manager import TestResult
from core.database import get_connection
import json

def run_test():
    start = time()
    errors = []
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        # ensure users row exists
        cur.execute("SELECT id FROM users LIMIT 1")
        r = cur.fetchone()
        if not r:
            cur.execute("INSERT INTO users (username, settings) VALUES (?, ?)", ("Anne", json.dumps({"theme":"light"})))
            conn.commit()
            r = cur.lastrowid
        # create profile
        cur.execute("INSERT INTO user_profiles (user_id, profile_name, role, preferences) VALUES (?, ?, ?, ?)",
                    (r if isinstance(r, int) else r[0], "test_profile", "parent", json.dumps({"theme":"dark"})))
        pid = cur.lastrowid
        conn.commit()
        # cleanup
        cur.execute("DELETE FROM user_profiles WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        return TestResult(module="parametres", success=True, duration=time() - start, errors=[])
    except Exception as e:
        if conn:
            try:
                conn.close()
            except:
                pass
        return TestResult(module="parametres", success=False, duration=time() - start, errors=[str(e)])